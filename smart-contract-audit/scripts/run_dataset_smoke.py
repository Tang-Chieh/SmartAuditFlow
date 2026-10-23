#!/usr/bin/env python3
"""Run SmartAuditFlow's five-node engine through the local Codex gateway."""

import argparse
import json
import os
import sys
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snippet", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--token-file", type=Path, required=True)
    parser.add_argument("--model", default="openai-codex/gpt-5.6-luna")
    parser.add_argument("--max-tasks", type=int, default=1)
    parser.add_argument("--repo-id", help="Dataset repo ID; when supplied, also write a benchmark PredictionCase")
    parser.add_argument("--detector-version", default="smartauditflow-price-manipulation-v1")
    args = parser.parse_args()

    if args.max_tasks < 1:
        parser.error("--max-tasks must be at least 1")
    if not args.token_file.is_file():
        parser.error("gateway token file does not exist")
    if not args.snippet.is_file():
        parser.error("snippet file does not exist")

    # Do not inherit paid-provider credentials or load the upstream tracked
    # .env. Only the local bearer token is used for the selected gateway.
    for key in (
        "OPENAI_API_KEY", "OPENAI_BASE_URL", "GEMINI_API_KEY", "DEEPSEEK_API_KEY",
        "ANTHROPIC_API_KEY", "GOOGLE_API_KEY",
    ):
        os.environ.pop(key, None)
    os.environ["CODEX_GATEWAY_API_KEY"] = args.token_file.read_text(encoding="utf-8").strip()
    os.environ["CODEX_GATEWAY_BASE_URL"] = "http://127.0.0.1:4000/v1"
    os.environ["CODEX_GATEWAY_MODEL"] = args.model

    app_root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(app_root))
    from src.storage.memory import storage
    from src.workflow.engine import WorkflowEngine
    from src.workflow.nodes import AuditPlanNode

    # Keep the actual five-node workflow intact but bound the audit loop to one
    # task for a smoke run. This is a runtime test limit, not a source change to
    # the production workflow's task extraction policy.
    original_extract = AuditPlanNode._extract_tasks
    AuditPlanNode._extract_tasks = lambda self, plan: original_extract(self, plan)[:args.max_tasks]

    snippet = args.snippet.read_text(encoding="utf-8")
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    session_id = storage.create_session(snippet, "", "codex-gateway")
    engine = WorkflowEngine(session_id, "codex-gateway")
    result = engine.execute_workflow_sync(snippet)

    prediction_case = None
    if args.repo_id:
        prediction_case = {
            "repo_id": args.repo_id,
            "detector_metadata": {
                "detector_version": args.detector_version,
                "llm_model": args.model,
            },
            "predictions": result.get("Predictions", []),
        }
        result["PredictionCase"] = prediction_case

    (output_dir / "smartauditflow_raw_result.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (output_dir / "smartauditflow_report.md").write_text(
        str(result.get("FullReport", "")) + "\n", encoding="utf-8"
    )
    if prediction_case is not None:
        (output_dir / "prediction_case.json").write_text(
            json.dumps(prediction_case, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    run_info = {
        "status": "completed",
        "session_id": session_id,
        "model_provider": "codex-gateway",
        "model_id": args.model,
        "gateway_base_url": "http://127.0.0.1:4000/v1",
        "workflow_nodes": ["initial-analysis", "audit-plan", "parameter-extractor", "iteration", "format-converter"],
        "max_audit_tasks": args.max_tasks,
        "result_findings": result.get("FindingNumber", len(result.get("Findings", []))),
        "prediction_case_written": prediction_case is not None,
        "credential_value_saved": False,
    }
    (output_dir / "run_manifest.json").write_text(
        json.dumps(run_info, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(run_info, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
