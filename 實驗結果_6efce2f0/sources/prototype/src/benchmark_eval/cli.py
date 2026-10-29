"""CLI for evaluating canonical GroundTruthCase and PredictionCase directories."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys

from . import (
    DEFAULT_JUDGE_MODEL,
    EvaluationConfig,
    configure_logging,
    evaluate_directory,
    evaluate_from_artifact,
    get_weight_profile,
    load_json,
)
from .validation import BenchmarkValidationError


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_GROUND_TRUTH_DIR = (
    REPOSITORY_ROOT / "dataset" / "downstream-stage1" / "pilot-v1" / "ground_truth"
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Evaluate canonical GroundTruthCase and PredictionCase directories."
    )
    parser.add_argument(
        "--ground-truth-dir",
        type=Path,
        default=DEFAULT_GROUND_TRUTH_DIR,
    )
    parser.add_argument("--predictions-dir", type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument(
        "--report-only",
        action="store_true",
        help=(
            "Render deterministic reports from an existing manifest and Judge "
            "artifact without sending Judge requests."
        ),
    )
    parser.add_argument(
        "--verification-summary",
        type=Path,
        help="Optional verification summary JSON used by --report-only.",
    )
    parser.add_argument(
        "--repo-id",
        action="append",
        dest="repo_ids",
        metavar="REPO_ID",
        help="evaluate all findings in this repository; repeat as needed",
    )
    parser.add_argument(
        "--finding",
        action="append",
        type=_parse_finding_selection,
        dest="finding_selections",
        metavar="REPO_ID:FINDING_ID",
        help="evaluate only this repository/finding pair; repeat as needed",
    )
    parser.add_argument(
        "--judge-model",
        default=None,
        help=f"judge model override (default: {DEFAULT_JUDGE_MODEL})",
    )
    parser.add_argument(
        "--weight-profile",
        choices=("legacy", "downstream-v2", "end-to-end-v2"),
        default="end-to-end-v2",
    )
    parser.add_argument("--batch-size", type=int, default=10)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-concurrency", type=int, default=4)
    parser.add_argument("--auth-mode", choices=("oauth", "api-key"), default="oauth")
    parser.add_argument("--oauth-credential-file", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        configure_logging()
    except ValueError as exc:
        parser.error(str(exc))
    if args.report_only:
        if args.repo_ids is not None or args.finding_selections is not None:
            parser.error("--repo-id and --finding cannot be used with --report-only")
        try:
            verification_summary = (
                load_json(args.verification_summary)
                if args.verification_summary is not None
                else None
            )
            result = evaluate_from_artifact(
                output_dir=args.output_dir,
                verification_summary=verification_summary,
            )
        except (BenchmarkValidationError, OSError, ValueError, RuntimeError) as exc:
            print(f"benchmark Evaluation failed: {exc}", file=sys.stderr)
            return 2
        print(f"evaluated repositories: {result.selected_case_count}")
        print(f"output: {args.output_dir}")
        return 0

    if args.predictions_dir is None:
        parser.error("--predictions-dir is required unless --report-only is used")
    if args.repo_ids is not None and args.finding_selections is not None:
        parser.error("--repo-id and --finding cannot be used together")
    judge_model = (
        args.judge_model
        or os.environ.get("OPENAI_JUDGE_MODEL")
        or DEFAULT_JUDGE_MODEL
    )
    try:
        config = EvaluationConfig(
            judge_model=judge_model,
            weight_profile=get_weight_profile(args.weight_profile),
            batch_size=args.batch_size,
            temperature=args.temperature,
            max_concurrency=args.max_concurrency,
            auth_mode=args.auth_mode,
            oauth_credential_file=args.oauth_credential_file,
        )
        result = evaluate_directory(
            ground_truth_dir=args.ground_truth_dir,
            predictions_dir=args.predictions_dir,
            output_dir=args.output_dir,
            repo_ids=args.repo_ids,
            finding_selections=args.finding_selections,
            config=config,
        )
    except (BenchmarkValidationError, OSError, ValueError, RuntimeError) as exc:
        print(f"benchmark Evaluation failed: {exc}", file=sys.stderr)
        return 2
    print(f"evaluated repositories: {result.selected_case_count}")
    print(f"output: {args.output_dir}")
    return 0


def _parse_finding_selection(value: str) -> tuple[str, str]:
    repo_id, separator, finding_id = value.partition(":")
    repo_id = repo_id.strip()
    finding_id = finding_id.strip()
    if not separator or not repo_id or not finding_id:
        raise argparse.ArgumentTypeError(
            "finding must use REPO_ID:FINDING_ID with both values non-empty"
        )
    return repo_id, finding_id


if __name__ == "__main__":
    raise SystemExit(main())
