"""Run pinned merged SmartAuditFlow, then the pinned official Evaluation pipeline."""

import hashlib
import importlib.util
import json
import logging
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent
SAF_REPO = ROOT.parents[1]
WORKSPACE = SAF_REPO.parent
SAF_COMMIT = "6efce2f0e92efe2e26397a6e832f1b533a27480d"
EVAL_COMMIT = "e46fc2702a1c6506f9a56af00990f8218648f697"
SAF = ROOT / "sources/saf/smart-contract-audit"
EVAL = ROOT / "sources/prototype"
MODEL = "openai-codex/gpt-5.6-luna"
VERSION = "smartauditflow-merged-pr1-6efce2f0-20261029"
TOKEN = WORKSPACE / "subscription-gateway-pilot/runtime-home/.omp/auth-gateway.token"


def load(path):
    return json.loads(path.read_text())


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")
    temporary.replace(path)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def import_file(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    helpers = import_file("dataset_helpers", SAF_REPO / "experiment-results/full-latest-gt-20261022/run_full_dataset.py")
    helpers.DETECTOR_VERSION = VERSION
    gt_source = EVAL / "dataset/downstream-stage1/pilot-v1/ground_truth"
    gt_paths = sorted(p for p in gt_source.glob("*.json") if p.stem != "margintrading")
    assert len(gt_paths) == 23
    for p in gt_paths:
        target = ROOT / "ground_truth" / p.name
        target.parent.mkdir(exist_ok=True)
        if target.exists():
            assert sha(target) == sha(p)
        else:
            shutil.copyfile(p, target)
    provenance = {
        "smartauditflow_commit": SAF_COMMIT,
        "evaluator_commit": EVAL_COMMIT,
        "renderer_commit": EVAL_COMMIT,
        "prompt_file_sha256": sha(SAF / "src/workflow/nodes.py"),
        "model": MODEL,
        "transport": "local Codex OAuth gateway; injected OpenAI-compatible client",
        "ground_truth_sha256": {p.name: sha(p) for p in gt_paths},
        "input_bundle_sha256": {
            p.stem: {bid: sha(source) for bid, source in helpers.select_bundles(p.stem)[0]}
            for p in gt_paths
        },
    }
    write(ROOT / "provenance.json", provenance)
    status_path = ROOT / "run_status.json"
    status = load(status_path) if status_path.exists() else {
        "status": "running", "model": MODEL, "detector_version": VERSION,
        "ground_truth_count": 23, "excluded_repositories": ["margintrading"],
        "max_tasks_per_bundle": 12, "max_bundle_attempts": 3,
        "smartauditflow_commit": SAF_COMMIT, "evaluator_commit": EVAL_COMMIT,
        "repos": {},
    }
    status["status"] = "running"
    write(status_path, status)
    for gt in gt_paths:
        repo = gt.stem
        bundles, mode = helpers.select_bundles(repo)
        rs = status["repos"].setdefault(repo, {"status": "running", "input_mode": mode, "bundles": {}})
        if rs["status"] == "completed":
            continue
        for bid, snippet in bundles:
            bs = rs["bundles"].setdefault(bid, {"status": "running", "attempts": []})
            if bs["status"] == "completed":
                continue
            for attempt in range(len(bs["attempts"]) + 1, 4):
                out = ROOT / "raw" / repo / bid / f"attempt-{attempt:02d}"
                out.mkdir(parents=True, exist_ok=False)
                bs["status"] = "running"
                write(status_path, status)
                print(f"RUN {repo}/{bid} attempt {attempt}", flush=True)
                with (out / "execution.log").open("w") as log:
                    proc = subprocess.run([
                        sys.executable, "-u", str(SAF / "scripts/run_dataset_smoke.py"),
                        "--snippet", str(snippet), "--output-dir", str(out / "workflow"),
                        "--token-file", str(TOKEN), "--model", MODEL, "--max-tasks", "12",
                        "--repo-id", repo, "--detector-version", VERSION,
                    ], cwd=SAF, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
                        stdout=log, stderr=subprocess.STDOUT)
                log_text = (out / "execution.log").read_text(errors="replace")
                raw_path = out / "workflow/smartauditflow_raw_result.json"
                raw = load(raw_path) if raw_path.exists() else {}
                summary = raw.get("ExecutionSummary", {})
                warnings = raw.get("OutputWarnings", [])
                infrastructure_failure = any(term in log_text for term in (
                    "Initial analysis failed:", "Audit plan creation failed:", "Report formatting failed:",
                    "usage_limit_reached", "turn_rate_limit_exceeded"))
                good = (proc.returncode == 0 and summary.get("total_tasks", 0) > 0
                        and summary.get("failed_tasks", 0) == 0 and not infrastructure_failure)
                bs["attempts"].append({"attempt": attempt, "returncode": proc.returncode,
                    "accepted": good, "execution_summary": summary,
                    "output_warnings": warnings, "log": str(out / "execution.log")})
                write(status_path, status)
                if good:
                    shutil.copytree(out / "workflow", ROOT / "raw" / repo / bid / "workflow")
                    bs.update(status="completed", task_count=summary["total_tasks"],
                        completed_tasks=summary["completed_tasks"], failed_tasks=0,
                        prediction_count=len(raw.get("Predictions", [])), output_warning_count=len(warnings))
                    write(status_path, status)
                    print(f"DONE {repo}/{bid} predictions={bs['prediction_count']} warnings={len(warnings)}", flush=True)
                    break
                if "usage_limit_reached" in log_text:
                    status["status"] = "quota_blocked"
                    write(status_path, status)
                    raise RuntimeError("Gateway quota exhausted; results preserved, no model substitution")
                time.sleep(30)
            if bs["status"] != "completed":
                status["status"] = "needs_recovery"
                write(status_path, status)
                raise RuntimeError(f"Three attempts failed for {repo}/{bid}; see execution logs")
        prediction = helpers.aggregate_repo(repo, ROOT / "raw", bundles)
        validation = prediction.pop("_validation")
        write(ROOT / "predictions" / f"{repo}.json", prediction)
        rs.update(status="completed", **validation)
        write(status_path, status)
    status["status"] = "completed"
    write(status_path, status)
    print("SMARTAUDITFLOW COMPLETE; starting official LLM Judge", flush=True)
    sys.path.insert(0, str(EVAL))
    from openai import OpenAI
    from src.benchmark_eval import EvaluationConfig, evaluate_directory
    from src.benchmark_eval.scoring import get_weight_profile
    compatibility = import_file("gateway_compatibility", SAF_REPO / "experiment-results/full-latest-gt-20261022/run_llm_judge.py")
    client = OpenAI(api_key=TOKEN.read_text().strip(), base_url="http://127.0.0.1:4000/v1", timeout=240, max_retries=0)
    logging.basicConfig(level=logging.INFO)
    result = evaluate_directory(
        ground_truth_dir=ROOT / "ground_truth", predictions_dir=ROOT / "predictions",
        output_dir=ROOT / "llm-judge",
        config=EvaluationConfig(judge_model=MODEL, weight_profile=get_weight_profile("end-to-end-v2"),
            batch_size=10, temperature=0, max_concurrency=1),
        client=compatibility.JudgeClient(client),
    )
    write(ROOT / "completion.json", {"status": "completed", "corpus_metrics": result.report["corpus_metrics"],
        "report": str(ROOT / "llm-judge/report.md"), "evaluator_commit": EVAL_COMMIT})
    print(json.dumps(load(ROOT / "completion.json"), indent=2), flush=True)


if __name__ == "__main__":
    main()
