"""Validation and normalization for benchmark manifests."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from pydantic import ValidationError

from .contract import Finding, Manifest, PredictionMode


class BenchmarkValidationError(ValueError):
    """Raised when benchmark input violates the evaluator contract."""


def load_json(source: str | Path) -> dict[str, Any]:
    """Load a JSON object from a file and report input errors clearly."""

    path = Path(source)
    try:
        with path.open(encoding="utf-8") as handle:
            value = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise BenchmarkValidationError(f"cannot load JSON {path}: {exc}") from exc

    if not isinstance(value, dict):
        raise BenchmarkValidationError(
            f"JSON root {path} must be an object, got {type(value).__name__}"
        )
    return value


def load_manifest(source: str | Path | Mapping[str, Any]) -> Manifest:
    """Load and validate a manifest from a path or already-loaded JSON mapping."""

    data = load_json(source) if isinstance(source, (str, Path)) else source
    return validate_manifest(data)


def validate_manifest(data: Mapping[str, Any] | Manifest) -> Manifest:
    """Validate a manifest schema and repository/finding identity rules."""

    if isinstance(data, Manifest):
        manifest = data
        raw_data: Mapping[str, Any] = manifest.model_dump(mode="python")
    else:
        raw_data = data
        try:
            manifest = Manifest.model_validate(data)
        except ValidationError as exc:
            raise BenchmarkValidationError(
                _format_validation_errors(exc, raw_data)
            ) from exc

    prediction_annotation_mode(manifest)

    repository_ids: set[str] = set()
    errors: list[str] = []
    raw_repositories = raw_data.get("repositories", [])
    for repository_index, repository in enumerate(manifest.repositories):
        repo_id = repository.repo_id
        repo_context = f"repository={repo_id!r}"
        if repo_id in repository_ids:
            errors.append(f"{repo_context}: duplicate repo_id")
        repository_ids.add(repo_id)

        _check_finding_ids(repository_index, repo_id, "ground_truth", repository.ground_truth, errors)
        _check_finding_ids(
            repository_index,
            repo_id,
            "predictions",
            repository.predictions,
            errors=errors,
        )

    if errors:
        raise BenchmarkValidationError("\n".join(errors))
    return manifest


def prediction_annotation_mode(manifest: Manifest) -> PredictionMode:
    """Return the manifest's all-legacy or all-annotated prediction mode."""

    verdicts = [
        finding.verdict
        for repository in manifest.repositories
        for finding in repository.predictions
    ]
    has_verdict = any(verdict is not None for verdict in verdicts)
    has_unclassified = any(verdict is None for verdict in verdicts)
    if has_verdict and has_unclassified:
        raise BenchmarkValidationError(
            "predictions must be uniformly legacy (without verdict) or "
            "annotated (every finding has verdict)"
        )
    inferred: PredictionMode = "annotated" if has_verdict else "legacy"
    if manifest.prediction_mode is None:
        return inferred
    if manifest.prediction_mode == "annotated" and has_unclassified:
        raise BenchmarkValidationError(
            "annotated manifest predictions must all have a verdict"
        )
    if manifest.prediction_mode == "legacy" and has_verdict:
        raise BenchmarkValidationError(
            "legacy manifest predictions must not have a verdict"
        )
    # An assembled annotated directory can legitimately select repositories
    # whose prediction lists are empty; retain the directory-level mode.
    return manifest.prediction_mode


def _check_finding_ids(
    repository_index: int,
    repo_id: str,
    collection_name: str,
    findings: list[Finding],
    errors: list[str],
) -> None:
    seen: set[str] = set()
    for finding_index, finding in enumerate(findings):
        finding_id = finding.finding_id
        finding_context = (
            f"repository={repo_id!r}, finding_id={finding_id!r}, "
            f"field=repositories[{repository_index}].{collection_name}[{finding_index}]"
        )
        if finding_id is not None:
            if finding_id in seen:
                errors.append(f"{finding_context}.finding_id: duplicate finding_id")
            seen.add(finding_id)


def _format_validation_errors(
    exc: ValidationError, raw_data: Mapping[str, Any]
) -> str:
    messages: list[str] = []
    raw_repositories = raw_data.get("repositories", [])
    for error in exc.errors():
        location = tuple(error.get("loc", ()))
        path = _format_location(location)
        repo_id, finding_id = _identity_for_location(raw_repositories, location)
        identity = f"repository={repo_id!r}, finding_id={finding_id!r}"
        messages.append(f"{identity}, field={path}: {error['msg']}")
    return "\n".join(messages)


def _format_location(location: tuple[Any, ...]) -> str:
    path = ""
    for part in location:
        if isinstance(part, int):
            path += f"[{part}]"
        elif path:
            path += f".{part}"
        else:
            path = str(part)
    return path


def _identity_for_location(
    raw_repositories: Any, location: tuple[Any, ...]
) -> tuple[str | None, str | None]:
    repo_id: str | None = None
    finding_id: str | None = None
    if not isinstance(raw_repositories, list) or not location:
        return repo_id, finding_id

    if location[0] != "repositories" or len(location) < 2:
        return repo_id, finding_id
    repository_index = location[1]
    if not isinstance(repository_index, int) or repository_index >= len(raw_repositories):
        return repo_id, finding_id
    repository = raw_repositories[repository_index]
    if not isinstance(repository, dict):
        return repo_id, finding_id
    repo_id = repository.get("repo_id")

    if len(location) >= 4 and location[2] in {"ground_truth", "predictions"}:
        finding_index = location[3]
        findings = repository.get(location[2])
        if isinstance(findings, list) and isinstance(finding_index, int):
            if finding_index < len(findings) and isinstance(findings[finding_index], dict):
                finding_id = findings[finding_index].get("finding_id")
    return repo_id, finding_id
