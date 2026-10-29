"""Public directory-level benchmark Evaluation workflow."""

from __future__ import annotations

from dataclasses import replace
import logging
from pathlib import Path
from typing import Any, Iterable, Mapping

from .config import EvaluationConfig
from .contract import Manifest
from .evaluator import EvaluationResult, evaluate_benchmark
from .inputs import assemble_manifest
from .judge_runner import JudgeArtifactGenerationError, generate_judge_artifact
from .markdown import write_evaluation_markdown
from .reporting import write_json_atomic, write_report
from .artifacts import validate_artifact_completeness, verify_artifact_manifest_hash
from .validation import BenchmarkValidationError, load_manifest


logger = logging.getLogger("benchmark_eval")


def evaluate_directory(
    *,
    ground_truth_dir: str | Path,
    predictions_dir: str | Path,
    output_dir: str | Path,
    repo_ids: Iterable[str] | None = None,
    finding_selections: Iterable[tuple[str, str]] | None = None,
    config: EvaluationConfig | None = None,
    client: Any | None = None,
    verification_summary: Mapping[str, Any] | None = None,
) -> EvaluationResult:
    """Evaluate canonical case directories and write a fresh result directory.

    ``predictions_dir`` determines the repository universe. Python callers may
    use ``repo_ids`` to select complete repositories or
    ``finding_selections`` to select explicit repository/finding pairs; these
    filters are mutually exclusive. The input directories are never modified.
    An output directory may already contain input files, but its generated
    Evaluation artifacts must not already exist.
    """

    active_config = config or EvaluationConfig.from_environment()
    destination = Path(output_dir)
    if destination.exists() and not destination.is_dir():
        raise BenchmarkValidationError(
            f"Evaluation output directory already exists: {destination}"
        )
    _ensure_output_files_absent(destination)
    assembly = assemble_manifest(
        ground_truth_dir,
        predictions_dir,
        repo_ids,
        finding_selections,
    )
    logger.info(
        "evaluation started: repositories=%d, model=%s, auth=%s",
        len(assembly.manifest.repositories),
        active_config.judge_model,
        active_config.auth_mode,
    )
    destination.mkdir(parents=True, exist_ok=True)
    manifest_path = destination / "manifest.json"
    judge_path = destination / "judge_artifact.json"
    report_path = destination / "report.json"
    write_json_atomic(
        assembly.manifest.model_dump(mode="json", exclude_none=True),
        manifest_path,
    )
    try:
        artifact = generate_judge_artifact(
            manifest_path,
            model=active_config.judge_model,
            weight_profile=active_config.weight_profile,
            batch_size=active_config.batch_size,
            temperature=active_config.temperature,
            client=client,
            max_concurrency=active_config.max_concurrency,
            auth_mode=active_config.auth_mode,
            oauth_credential_file=active_config.oauth_credential_file,
        )
    except JudgeArtifactGenerationError as exc:
        write_json_atomic(
            exc.diagnostic_artifact,
            destination / "judge_artifact_fail.json",
        )
        if verification_summary is not None:
            write_json_atomic(
                dict(verification_summary),
                destination / "verification_summary.json",
            )
        raise
    write_json_atomic(artifact.model_dump(mode="json"), judge_path)
    result = evaluate_benchmark(
        manifest_path,
        judge_path,
        verification_summary=verification_summary,
    )
    write_report(result, report_path)
    write_evaluation_markdown(
        result.report,
        destination / "report.md",
        manifest=assembly.manifest,
        judge_artifact=artifact,
    )
    logger.info(
        "evaluation completed: repositories=%d, output=%s",
        len(assembly.manifest.repositories),
        destination,
    )
    return replace(
        result,
        selected_case_count=len(assembly.manifest.repositories),
        ignored_case_count=len(assembly.ignored.case_ids),
    )


def evaluate_from_artifact(
    *,
    output_dir: str | Path,
    verification_summary: Mapping[str, Any] | None = None,
) -> EvaluationResult:
    """Regenerate reports from the canonical artifacts in an output directory.

    This seam performs only deterministic validation, scoring, and rendering;
    it never creates an OpenAI client or sends a Judge request. The output
    directory must already contain ``manifest.json`` and
    ``judge_artifact.json``.
    """

    destination = Path(output_dir)
    if not destination.is_dir():
        raise BenchmarkValidationError(
            f"Evaluation output directory does not exist: {destination}"
        )
    manifest_path = destination / "manifest.json"
    judge_path = destination / "judge_artifact.json"
    for path in (manifest_path, judge_path):
        if not path.is_file():
            raise BenchmarkValidationError(
                f"required report-only input is missing: {path}"
            )

    validated_manifest = load_manifest(manifest_path)
    artifact = verify_artifact_manifest_hash(validated_manifest, judge_path)
    validate_artifact_completeness(validated_manifest, artifact)

    result = evaluate_benchmark(
        validated_manifest,
        artifact,
        verification_summary=verification_summary,
    )
    write_report(result, destination / "report.json")
    write_evaluation_markdown(
        result.report,
        destination / "report.md",
        manifest=validated_manifest,
        judge_artifact=artifact,
    )
    return replace(
        result,
        selected_case_count=len(validated_manifest.repositories),
    )


def evaluate_manifest(
    manifest: Manifest,
    *,
    output_dir: str | Path,
    config: EvaluationConfig,
    client: Any | None = None,
    verification_summary: Mapping[str, Any] | None = None,
) -> EvaluationResult:
    """Evaluate an already assembled in-memory manifest.

    This advanced seam never loads an existing manifest from disk as a
    selection file.
    """

    destination = Path(output_dir)
    if destination.exists() and not destination.is_dir():
        raise BenchmarkValidationError(
            f"Evaluation output directory already exists: {destination}"
        )
    _ensure_output_files_absent(destination)
    destination.mkdir(parents=True, exist_ok=True)
    manifest_path = destination / "manifest.json"
    judge_path = destination / "judge_artifact.json"
    report_path = destination / "report.json"
    write_json_atomic(manifest.model_dump(mode="json", exclude_none=True), manifest_path)
    artifact = generate_judge_artifact(
        manifest_path,
        model=config.judge_model,
        weight_profile=config.weight_profile,
        batch_size=config.batch_size,
        temperature=config.temperature,
        client=client,
        max_concurrency=config.max_concurrency,
        auth_mode=config.auth_mode,
        oauth_credential_file=config.oauth_credential_file,
    )
    write_json_atomic(artifact.model_dump(mode="json"), judge_path)
    result = evaluate_benchmark(
        manifest_path,
        judge_path,
        verification_summary=verification_summary,
    )
    write_report(result, report_path)
    write_evaluation_markdown(
        result.report,
        destination / "report.md",
        manifest=manifest,
        judge_artifact=artifact,
    )
    return replace(result, selected_case_count=len(manifest.repositories))


def _ensure_output_files_absent(destination: Path) -> None:
    existing = [
        destination / name
        for name in (
            "manifest.json",
            "judge_artifact.json",
            "report.json",
            "report.md",
        )
        if (destination / name).exists()
    ]
    if existing:
        raise BenchmarkValidationError(
            "Evaluation output already contains generated artifacts: "
            + ", ".join(str(path) for path in existing)
        )


__all__ = [
    "EvaluationConfig",
    "evaluate_directory",
    "evaluate_from_artifact",
    "evaluate_manifest",
]
