#!/usr/bin/env python3
"""Run price-focused SmartAuditFlow on latest pilot-v1 repos, resumably."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


WORKSPACE = Path(__file__).resolve().parents[3]
SAF_ROOT = WORKSPACE / "SmartAuditFlow-codex-smoke/smart-contract-audit"
DATASET_ROOT = WORKSPACE / "SmartAuditFlow-codex-smoke/dataset-inputs"
GROUND_TRUTH_SOURCE = (
    WORKSPACE
    / "SmartAuditFlow-codex-smoke/experiment-results/full-latest-gt-20261022/ground_truth"
)
TOKEN_FILE = WORKSPACE / "subscription-gateway-pilot/runtime-home/.omp/auth-gateway.token"
MODEL = "openai-codex/gpt-5.6-luna"
DETECTOR_VERSION = "smartauditflow-price-manipulation-full-24-v1"
SINGLE_BUNDLE_MAX_ESTIMATE = 240_000
MAX_TASKS = 12
GROUND_TRUTH_SOURCE_LABEL = (
    "fffuuuming/prototype@SCAR, fetched 2026-10-22; branch was 7 commits ahead of "
    "8a3132c7ed3f94acddb718d951dfe2d2ceab5986. Updated-file blob SHAs are recorded "
    "in run_status.json."
)
GROUND_TRUTH_BLOB_SHAS = {
    "2021-07-spartan.json": "43fcf092217508b7d7f4b600539dc8188be5469d",
    "2022-01-sandclock.json": "8c097b69ef805c2501fd8c65b23c5db4bba0dd44",
    "2022-11-paraspace.json": "92b08d3d7e40ba6eb3f8d82047231c53e807221c",
    "2025-12-panoptic.json": "7c80f9ec30959201c06a10ddb4b2a7e5e3f6ebb9",
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(temp, path)


def select_bundles(repo_id: str) -> tuple[list[tuple[str, Path]], str]:
    one_root = DATASET_ROOT / "pilot-v1-one-file-per-repo" / repo_id
    one_manifest = load_json(one_root / "manifest.json")
    estimate = int(one_manifest.get("estimated_total_bundle_tokens", 0))
    if estimate <= SINGLE_BUNDLE_MAX_ESTIMATE:
        entries = one_manifest.get("bundles", [])
        return (
            [(entry["bundle_id"], one_root / entry["path"]) for entry in entries],
            "one-bundle-per-repo",
        )

    split_root = DATASET_ROOT / "pilot-v1" / repo_id
    split_manifest = load_json(split_root / "manifest.json")
    entries = split_manifest.get("bundles", [])
    return (
        [(entry["bundle_id"], split_root / entry["path"]) for entry in entries],
        "50k-estimated-token-bundles",
    )


def normalize_predictions(raw: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str]]:
    result = raw.get("Predictions", [])
    if not isinstance(result, list):
        return [], ["Predictions was not a JSON array"]
    return [item for item in result if isinstance(item, dict)], list(raw.get("OutputWarnings", []))


def aggregate_repo(repo_id: str, run_root: Path, bundles: list[tuple[str, Path]]) -> dict[str, Any]:
    predictions: list[dict[str, Any]] = []
    rejected_warnings: list[dict[str, Any]] = []
    exact_seen: set[str] = set()
    duplicate_count = 0
    for bundle_id, _ in bundles:
        raw_path = run_root / repo_id / bundle_id / "workflow/smartauditflow_raw_result.json"
        raw = load_json(raw_path)
        items, warnings = normalize_predictions(raw)
        rejected_warnings.extend({"bundle_id": bundle_id, "warning": w} for w in warnings)
        for item in items:
            # Bundle-local SAF IDs repeat across independent workflow executions.
            # Replace with a stable repo/bundle-scoped ID before validation.
            identity = {k: v for k, v in item.items() if k != "finding_id"}
            fingerprint = json.dumps(identity, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
            if fingerprint in exact_seen:
                duplicate_count += 1
                continue
            exact_seen.add(fingerprint)
            item = dict(item)
            item["finding_id"] = f"SAF-{bundle_id}-{len(predictions) + 1:03d}"
            predictions.append(item)

    return {
        "repo_id": repo_id,
        "detector_metadata": {
            "detector_version": DETECTOR_VERSION,
            "llm_model": MODEL,
        },
        "predictions": predictions,
        "_validation": {
            "accepted_prediction_count": len(predictions),
            "output_warning_count": len(rejected_warnings),
            "output_warnings": rejected_warnings,
            "exact_duplicate_predictions_removed": duplicate_count,
            "bundle_count": len(bundles),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--max-tasks", type=int, default=MAX_TASKS)
    parser.add_argument(
        "--exclude-repo",
        action="append",
        default=[],
        help="Ground-truth repo ID to exclude; may be supplied more than once.",
    )
    args = parser.parse_args()
    if args.max_tasks < 1 or args.max_tasks > 12:
        parser.error("--max-tasks must be between 1 and 12 (the workflow's planner limit)")
    output_root = args.output_root.resolve()
    if not TOKEN_FILE.is_file():
        parser.error(f"local gateway token file is missing: {TOKEN_FILE}")

    all_latest_gt = sorted(GROUND_TRUTH_SOURCE.glob("*.json"), key=lambda p: p.stem.casefold())
    if len(all_latest_gt) != 24:
        parser.error(f"expected 24 latest ground-truth files, found {len(all_latest_gt)}")
    excluded_repos = {repo_id.casefold() for repo_id in args.exclude_repo}
    latest_gt = [path for path in all_latest_gt if path.stem.casefold() not in excluded_repos]
    if not latest_gt:
        parser.error("all ground-truth repositories were excluded")
    gt_out = output_root / "ground_truth"
    gt_out.mkdir(parents=True, exist_ok=True)
    for source in latest_gt:
        target = gt_out / source.name
        if not target.exists():
            target.write_bytes(source.read_bytes())
        if hashlib.sha1(target.read_bytes()).hexdigest() != hashlib.sha1(source.read_bytes()).hexdigest():
            parser.error(f"ground-truth snapshot differs from source: {source.name}")

    (output_root / "raw").mkdir(parents=True, exist_ok=True)
    (output_root / "predictions").mkdir(parents=True, exist_ok=True)
    status_path = output_root / "run_status.json"
    status = {
        "status": "running",
        "model": MODEL,
        "detector_version": DETECTOR_VERSION,
        "ground_truth_source": GROUND_TRUTH_SOURCE_LABEL,
        "ground_truth_updated_file_blob_shas": GROUND_TRUTH_BLOB_SHAS,
        "ground_truth_count": len(latest_gt),
        "excluded_repositories": sorted(excluded_repos),
        "max_tasks_per_bundle": args.max_tasks,
        "single_bundle_estimated_token_limit": SINGLE_BUNDLE_MAX_ESTIMATE,
        "token_estimator_note": "dataset manifest uses ceil(chars/4), not the model tokenizer",
        "repos": {},
    }

    run_script = SAF_ROOT / "scripts/run_dataset_smoke.py"
    for gt_path in latest_gt:
        repo_id = gt_path.stem
        bundles, input_mode = select_bundles(repo_id)
        if not bundles:
            status["repos"][repo_id] = {"status": "failed", "error": "no input bundles"}
            write_json(status_path, status)
            continue
        repo_status = status["repos"].setdefault(
            repo_id,
            {"status": "running", "input_mode": input_mode, "bundles": {}},
        )
        repo_failed = False
        for bundle_id, snippet_path in bundles:
            raw_result_path = output_root / "raw" / repo_id / bundle_id / "workflow/smartauditflow_raw_result.json"
            prior_single_run = output_root / repo_id / "workflow"
            if not raw_result_path.is_file() and len(bundles) == 1:
                prior_raw = prior_single_run / "smartauditflow_raw_result.json"
                if prior_raw.is_file():
                    raw_result_path.parent.mkdir(parents=True, exist_ok=True)
                    import shutil
                    shutil.copytree(prior_single_run, raw_result_path.parent, dirs_exist_ok=True)
            if raw_result_path.is_file():
                try:
                    existing = load_json(raw_result_path)
                    if existing.get("ExecutionSummary", {}).get("failed_tasks", 0) == 0:
                        repo_status["bundles"][bundle_id] = {"status": "completed", "resumed": True}
                        continue
                except Exception:
                    pass
            workflow_dir = output_root / "raw" / repo_id / bundle_id / "workflow"
            cmd = [
                sys.executable,
                str(run_script),
                "--snippet", str(snippet_path),
                "--output-dir", str(workflow_dir),
                "--token-file", str(TOKEN_FILE),
                "--model", MODEL,
                "--max-tasks", str(args.max_tasks),
                "--repo-id", repo_id,
                "--detector-version", DETECTOR_VERSION,
            ]
            env = os.environ.copy()
            env["PYTHONDONTWRITEBYTECODE"] = "1"
            print(f"\n===== {repo_id} / {bundle_id} ({input_mode}) =====", flush=True)
            completed = subprocess.run(cmd, cwd=SAF_ROOT, env=env, check=False)
            if completed.returncode != 0 or not raw_result_path.is_file():
                repo_status["bundles"][bundle_id] = {
                    "status": "failed",
                    "returncode": completed.returncode,
                    "snippet": str(snippet_path),
                }
                repo_failed = True
                write_json(status_path, status)
                print(f"FAILED: {repo_id}/{bundle_id}; stopping for resumable recovery", flush=True)
                return completed.returncode or 1
            raw = load_json(raw_result_path)
            repo_status["bundles"][bundle_id] = {
                "status": "completed",
                "task_count": raw.get("ExecutionSummary", {}).get("total_tasks", 0),
                "completed_tasks": raw.get("ExecutionSummary", {}).get("completed_tasks", 0),
                "failed_tasks": raw.get("ExecutionSummary", {}).get("failed_tasks", 0),
                "prediction_count": len(raw.get("Predictions", [])),
                "output_warning_count": len(raw.get("OutputWarnings", [])),
            }
            write_json(status_path, status)

        if not repo_failed:
            merged = aggregate_repo(repo_id, output_root / "raw", bundles)
            validation = merged.pop("_validation")
            write_json(output_root / "predictions" / f"{repo_id}.json", merged)
            repo_status.update(
                {
                    "status": "completed",
                    "bundle_count": len(bundles),
                    "prediction_count": validation["accepted_prediction_count"],
                    "output_warning_count": validation["output_warning_count"],
                    "exact_duplicate_predictions_removed": validation["exact_duplicate_predictions_removed"],
                    "output_warnings": validation["output_warnings"],
                }
            )
            write_json(status_path, status)

    status["status"] = "completed" if all(v.get("status") == "completed" for v in status["repos"].values()) else "partial"
    write_json(status_path, status)
    print(json.dumps({"status": status["status"], "repo_count": len(status["repos"]), "output_root": str(output_root)}, indent=2))
    return 0 if status["status"] == "completed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
