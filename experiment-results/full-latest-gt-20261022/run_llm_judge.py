#!/usr/bin/env python3
"""Run the prototype benchmark LLM Judge via the local Codex OAuth gateway."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any


WORKSPACE = Path(__file__).resolve().parents[3]
PROJECT_ROOT = WORKSPACE / "prototype-scar"
TOKEN_FILE = WORKSPACE / "subscription-gateway-pilot/runtime-home/.omp/auth-gateway.token"
MODEL = "openai-codex/gpt-5.6-luna"
BASE_URL = "http://127.0.0.1:4000/v1"


class ResponsesParseCompatibility:
    """Pass the Judge's Pydantic schema through prompt instructions for this gateway."""

    def __init__(self, client: Any, retry_instructions: str | None = None):
        self.client = client
        self.retry_instructions = retry_instructions

    def parse(self, **request: Any) -> Any:
        model = request.pop("text_format")
        schema = model.model_json_schema()
        request["instructions"] = (
            str(request.get("instructions", ""))
            + ("\n" + self.retry_instructions if self.retry_instructions else "")
            + "\nFollow this JSON schema exactly (no extra keys, all required):\n"
            + json.dumps(schema, ensure_ascii=False)
            + "\nReturn ONLY valid JSON. No markdown. No prose."
        )
        response = self.client.responses.create(**request)
        parsed = model.model_validate_json(response.output_text)
        return SimpleNamespace(
            status=response.status,
            output_parsed=parsed,
            id=response.id,
            model=response.model,
            usage=response.usage,
        )


class JudgeClient:
    def __init__(self, client: Any, retry_instructions: str | None = None):
        self.responses = ResponsesParseCompatibility(client, retry_instructions)


def render_markdown(report: dict[str, Any], artifact: dict[str, Any], run_status: dict[str, Any]) -> str:
    corpus = report.get("corpus_metrics", {})
    lines = [
        "# SmartAuditFlow — Latest Ground Truth Full Evaluation",
        "",
        "## Summary",
        "",
        f"- Ground Truth source: `fffuuuming/prototype` branch `SCAR` at `{run_status.get('ground_truth_source', 'unknown')}`.",
        f"- Repositories evaluated: {len(report.get('repositories', []))} / {run_status.get('ground_truth_count', 'unknown')}",
        f"- SmartAuditFlow model: `{run_status.get('model', MODEL)}` via local Codex OAuth gateway.",
        f"- Full workflow: {', '.join(run_status.get('workflow_nodes', ['initial-analysis', 'audit-plan', 'parameter-extractor', 'iteration', 'format-converter']))}.",
        f"- Maximum planned audit tasks per input bundle: {run_status.get('max_tasks_per_bundle', 'unknown')}.",
        f"- Ground Truth findings: {corpus.get('total_ground_truth_count', 'n/a')}; predictions: {corpus.get('total_prediction_count', 'n/a')}.",
        f"- Macro soft F1: {corpus.get('macro_soft_f1', 0):.3f}; pooled soft F1: {corpus.get('pooled_soft_f1', 0):.3f}; total matched weight: {corpus.get('total_matched_weight', 0):.3f}.",
        "",
        "## Evaluation configuration",
        "",
        f"- Judge model: `{MODEL}`; batch size 10; temperature 0; concurrency 1.",
        f"- Matching strategy: `{report.get('matching_strategy', 'unknown')}`.",
        f"- Threshold: {report.get('judge_config', {}).get('threshold', 'n/a')}; weights: `{json.dumps(report.get('judge_config', {}).get('weight_profile', {}), ensure_ascii=False)}`.",
        f"- Targeted retries for incomplete ordinal batches: {sum(1 for event in run_status.get('judge_retry_events', []) if event.get('recovered'))} recovered batch(es); full event log is in `judge_run_summary.json`.",
        "- Ground Truth was used only by the evaluator, not included in SmartAuditFlow prompts.",
        "- Source bundles use the repository-prepared Solidity input and retain source-path markers. The 240k token estimate cutoff uses the dataset's `ceil(chars/4)` estimate; larger inputs are split into 50k-estimated-token bundles because the gateway reports 272k context for this model.",
        "- When a repo is split across bundles, predictions are combined into one `PredictionCase`; exact duplicate predictions are removed and bundle-local finding IDs are made unique. Cross-bundle semantic duplicates are not automatically merged.",
        "",
        "## Per-repository metrics",
        "",
        "| Repo | Ground Truth | Predictions | Matched weight | Precision | Recall | Soft F1 |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for entry in report.get("repositories", []):
        metrics = entry.get("metrics", {})
        lines.append(
            f"| `{entry.get('repo_id')}` | {metrics.get('ground_truth_count', 0)} | {metrics.get('prediction_count', 0)} | {metrics.get('matched_weight', 0):.3f} | {metrics.get('soft_precision', 0):.3f} | {metrics.get('soft_recall', 0):.3f} | {metrics.get('soft_f1', 0):.3f} |"
        )
    lines.extend(["", "## Judge matches and misses", ""])
    for entry in report.get("repositories", []):
        repo_id = entry.get("repo_id")
        lines.extend([f"### `{repo_id}`", ""])
        matches = entry.get("matched_pairs", [])
        if matches:
            for pair in matches:
                scores = pair.get("scores", {})
                lines.append(
                    f"- Matched prediction `{pair.get('prediction_id')}` ↔ Ground Truth `{pair.get('ground_truth_id')}`; R/L/I/M = {scores.get('R')}/{scores.get('L')}/{scores.get('I')}/{scores.get('M')}; weighted score {pair.get('weighted_score', 0):.3f}."
                )
                if pair.get("rationale"):
                    lines.append(f"  - Judge rationale: {pair['rationale']}")
        else:
            lines.append("- No accepted prediction–Ground Truth match.")
        unmatched_gt = entry.get("unmatched_ground_truths", [])
        unmatched_pred = entry.get("unmatched_predictions", [])
        lines.append(f"- Unmatched Ground Truth IDs: {', '.join(f'`{x}`' for x in unmatched_gt) if unmatched_gt else 'none'}.")
        lines.append(f"- Unmatched prediction IDs: {', '.join(f'`{x}`' for x in unmatched_pred) if unmatched_pred else 'none'}.")
        lines.append("")
    failed = [repo for repo, data in run_status.get("repos", {}).items() if data.get("status") != "completed"]
    warning_total = sum(data.get("output_warning_count", 0) for data in run_status.get("repos", {}).values())
    lines.extend(
        [
            "## Output validation and limitations",
            "",
            f"- SmartAuditFlow OutputWarnings recorded across completed repo runs: {warning_total}.",
            f"- Incomplete/failed repositories: {', '.join(f'`{r}`' for r in failed) if failed else 'none'}.",
            "- The Judge provides model-based benchmark matching, not independent exploit validation. A high score means semantic similarity under the configured rubric, not proof of exploitability.",
            "- Raw workflow outputs, per-bundle run manifests, and OutputWarnings are retained under `raw/`; aggregated evaluator inputs are under `predictions/`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--experiment-root", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    root = args.experiment_root.resolve()
    status_path = root / "run_status.json"
    if not status_path.is_file():
        parser.error("run_status.json is missing; run SmartAuditFlow first")
    status = json.loads(status_path.read_text(encoding="utf-8"))
    if status.get("status") != "completed":
        parser.error(f"SmartAuditFlow run is not complete: {status.get('status')}")
    if not TOKEN_FILE.is_file():
        parser.error(f"local gateway token file is missing: {TOKEN_FILE}")
    artifacts = root / "llm-judge"
    artifacts.mkdir(parents=True, exist_ok=True)
    # The manifest is deterministic input preparation and may be safely
    # regenerated after a failed Judge startup; protect actual Judge outputs.
    for name in ("judge_artifact.json", "report.json", "report.matrix.json", "judge_run_summary.json", "report.md"):
        if (artifacts / name).exists():
            parser.error(f"refusing to overwrite existing Judge artifact: {artifacts / name}")

    sys.path.insert(0, str(PROJECT_ROOT))
    from openai import OpenAI
    from src.benchmark_eval.inputs import assemble_manifest
    from src.benchmark_eval.evaluator import evaluate_benchmark
    from src.benchmark_eval.judge_runner import generate_judge_artifact
    from src.benchmark_eval.reporting import write_json_atomic, write_pair_matrix, write_report
    from src.benchmark_eval.scoring import get_weight_profile
    from src.benchmark_eval import judge_runner as judge_runner_module
    from src.benchmark_eval.validation import BenchmarkValidationError

    # The gateway may return schema-valid output while omitting a pair ordinal.
    # Retry only that affected batch, explicitly listing the missing ordinals;
    # prompts, rubric, scoring, and evaluator code remain unchanged.
    retry_events: list[dict[str, Any]] = []
    original_run_judge_job = judge_runner_module._run_judge_job

    def run_judge_job_with_missing_pair_retry(job: Any, active_client: Any, model: str, temperature: float) -> Any:
        for attempt in range(3):
            if attempt == 0:
                retry_client = active_client
            else:
                retry_client = JudgeClient(
                    active_client.responses.client,
                    retry_instructions=(
                        "Your previous response omitted or duplicated required pair ordinals. "
                        "Return exactly one pair for every ordinal index in this batch, with no omissions or extras. "
                        f"Required ordinal indexes: {list(range(len(job.predictions)))}."
                    ),
                )
            response = original_run_judge_job(job, retry_client, model, temperature)
            parsed = response.output_parsed
            ordinals = [pair.ordinal_index for pair in parsed.pairs]
            expected = list(range(len(job.predictions)))
            missing = sorted(set(expected) - set(ordinals))
            unknown = sorted(set(ordinals) - set(expected))
            duplicates = sorted({index for index in ordinals if ordinals.count(index) > 1})
            if not (missing or unknown or duplicates):
                if attempt:
                    retry_events.append(
                        {
                            "repo_id": job.repo_id,
                            "ground_truth_id": job.ground_truth.finding_id,
                            "retry_attempts": attempt,
                            "recovered": True,
                        }
                    )
                return response
            retry_events.append(
                {
                    "repo_id": job.repo_id,
                    "ground_truth_id": job.ground_truth.finding_id,
                    "retry_attempt": attempt + 1,
                    "missing_ordinals": missing,
                    "unknown_ordinals": unknown,
                    "duplicate_ordinals": duplicates,
                    "recovered": False,
                }
            )
        raise BenchmarkValidationError(
            "judge batch still has incomplete pair ordinals after two targeted retries: "
            f"repository={job.repo_id!r}, ground_truth_id={job.ground_truth.finding_id!r}"
        )

    judge_runner_module._run_judge_job = run_judge_job_with_missing_pair_retry

    manifest_result = assemble_manifest(root / "ground_truth", root / "predictions")
    manifest_path = artifacts / "manifest.json"
    write_json_atomic(manifest_result.manifest.model_dump(mode="json"), manifest_path)

    token = TOKEN_FILE.read_text(encoding="utf-8").strip()
    client = OpenAI(api_key=token, base_url=BASE_URL, timeout=240, max_retries=0)
    artifact = generate_judge_artifact(
        manifest_result.manifest,
        model=MODEL,
        weight_profile=get_weight_profile("end-to-end-v2"),
        batch_size=10,
        temperature=0.0,
        client=JudgeClient(client),
        max_concurrency=1,
    )
    artifact_path = artifacts / "judge_artifact.json"
    write_json_atomic(artifact.model_dump(mode="json"), artifact_path)
    evaluation = evaluate_benchmark(manifest_path, artifact_path)
    write_report(evaluation, artifacts / "report.json")
    write_pair_matrix(evaluation, artifacts / "report.matrix.json")

    calls = artifact.judge_metadata.get("calls", [])
    usage = [call.get("usage", {}) for call in calls]
    summary = {
        "ground_truth_source": status.get("ground_truth_source"),
        "model": MODEL,
        "gateway": BASE_URL,
        "temperature": 0.0,
        "batch_size": 10,
        "max_concurrency": 1,
        "judge_call_count": len(calls),
        "pair_score_count": sum(len(repo.pairs) for repo in artifact.repositories),
        "targeted_pair_ordinal_retry_events": retry_events,
        "total_input_tokens": sum(item.get("input_tokens", 0) for item in usage),
        "total_output_tokens": sum(item.get("output_tokens", 0) for item in usage),
        "total_tokens": sum(item.get("total_tokens", 0) for item in usage),
        "corpus_metrics": evaluation.report.get("corpus_metrics", {}),
        "report": str(artifacts / "report.json"),
        "judge_artifact": str(artifact_path),
        "pair_matrix": str(artifacts / "report.matrix.json"),
    }
    write_json_atomic(summary, artifacts / "judge_run_summary.json")
    (artifacts / "report.md").write_text(
        render_markdown(
            evaluation.report,
            artifact.model_dump(mode="json"),
            {**status, "judge_retry_events": retry_events},
        ),
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
