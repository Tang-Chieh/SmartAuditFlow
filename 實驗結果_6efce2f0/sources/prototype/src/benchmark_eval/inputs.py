"""Loading and deterministic assembly of per-case benchmark inputs."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from pydantic import ValidationError

from .contract import (
    DetectorMetadata,
    GroundTruthCase,
    Manifest,
    PredictionMode,
    PredictionCase,
    Repository,
)
from .validation import BenchmarkValidationError, load_json, validate_manifest


@dataclass(frozen=True)
class IgnoredArtifactSummary:
    """Input cases outside the selected prediction repository set."""

    ground_truth_files: tuple[str, ...] = ()
    prediction_files: tuple[str, ...] = ()
    ground_truth_repo_ids: tuple[str, ...] = ()
    prediction_repo_ids: tuple[str, ...] = ()

    @property
    def file_count(self) -> int:
        return len(self.ground_truth_files) + len(self.prediction_files)

    @property
    def case_ids(self) -> tuple[str, ...]:
        return tuple(
            sorted(set(self.ground_truth_repo_ids) | set(self.prediction_repo_ids))
        )


@dataclass(frozen=True)
class ManifestAssemblyResult:
    """Validated manifest plus detector provenance and ignored input summary."""

    manifest: Manifest
    detector_metadata: DetectorMetadata | None
    ignored: IgnoredArtifactSummary
    prediction_mode: PredictionMode


def assemble_manifest(
    ground_truth_dir: str | Path,
    predictions_dir: str | Path,
    repo_ids: Iterable[str] | None = None,
    finding_selections: Iterable[tuple[str, str]] | None = None,
) -> ManifestAssemblyResult:
    """Assemble a manifest from canonical case directories.

    The prediction directory is authoritative for the repository set. Extra
    ground-truth cases are ignored; missing ground-truth cases are rejected.
    ``repo_ids`` optionally selects complete repositories for Python callers.
    ``finding_selections`` explicitly selects ``(repo_id, finding_id)`` pairs
    and cannot be combined with ``repo_ids``. No existing manifest is read as
    a selection file.
    """

    ground_truth_entries = _load_case_entries(
        ground_truth_dir, GroundTruthCase, "ground truth"
    )
    prediction_entries = _load_case_entries(
        predictions_dir, PredictionCase, "prediction"
    )
    ground_truth_cases = _index_cases(ground_truth_entries, "ground truth")
    prediction_cases = _index_cases(prediction_entries, "prediction")
    prediction_mode = _prediction_directory_mode(prediction_entries)

    requested_ids = _normalize_repo_ids(repo_ids)
    normalized_selections = _normalize_finding_selections(finding_selections)
    if requested_ids is not None and normalized_selections is not None:
        raise BenchmarkValidationError(
            "repo_ids and finding_selections cannot be used together"
        )
    if normalized_selections is None:
        if requested_ids is None:
            selected_ids = sorted(prediction_cases)
        else:
            unknown_ids = sorted(set(requested_ids) - set(prediction_cases))
            if unknown_ids:
                raise BenchmarkValidationError(
                    "requested prediction cases were not found: "
                    + ", ".join(unknown_ids)
                )
            selected_ids = sorted(set(requested_ids))
    else:
        requested_ids = sorted({repo_id for repo_id, _ in normalized_selections})
        unknown_ids = sorted(set(requested_ids) - set(prediction_cases))
        if unknown_ids:
            raise BenchmarkValidationError(
                "requested prediction cases were not found: "
                + ", ".join(unknown_ids)
            )
        selected_ids = requested_ids
    if not selected_ids:
        raise BenchmarkValidationError(
            f"no prediction cases found under {predictions_dir}"
        )
    missing_ground_truth = sorted(set(selected_ids) - set(ground_truth_cases))
    if missing_ground_truth:
        raise BenchmarkValidationError(
            "prediction cases are missing matching ground truth cases: "
            + ", ".join(missing_ground_truth)
        )
    ignored = IgnoredArtifactSummary(
        ground_truth_files=tuple(
            entry.path.name
            for entry in ground_truth_entries
            if entry.case.repo_id not in set(selected_ids)
        ),
        prediction_files=tuple(
            entry.path.name
            for entry in prediction_entries
            if entry.case.repo_id not in set(selected_ids)
        ),
        ground_truth_repo_ids=tuple(
            sorted(set(ground_truth_cases) - set(selected_ids))
        ),
        prediction_repo_ids=tuple(
            sorted(set(prediction_cases) - set(selected_ids))
        ),
    )
    selected_finding_ids: dict[str, set[str]] | None = None
    if normalized_selections is not None:
        selected_finding_ids = {}
        for repo_id, finding_id in normalized_selections:
            selected_finding_ids.setdefault(repo_id, set()).add(finding_id)

    selected_ground_truth_cases = []
    for repo_id in selected_ids:
        ground_truth_case = ground_truth_cases[repo_id].case
        selected_findings = ground_truth_case.ground_truth
        if selected_finding_ids is not None:
            requested_finding_ids = selected_finding_ids[repo_id]
            selected_findings = [
                finding
                for finding in selected_findings
                if finding.finding_id in requested_finding_ids
            ]
            found_finding_ids = {finding.finding_id for finding in selected_findings}
            missing_finding_ids = sorted(requested_finding_ids - found_finding_ids)
            if missing_finding_ids:
                raise BenchmarkValidationError(
                    "ground_truth_id not found: "
                    f"repository={repo_id!r}, "
                    f"ground_truth_ids={missing_finding_ids!r}"
                )
        selected_ground_truth_cases.append(
            ground_truth_case.model_copy(update={"ground_truth": selected_findings})
        )

    _require_gold_verified(selected_ground_truth_cases)

    detector_metadata = _consistent_detector_metadata(
        [prediction_cases[repo_id] for repo_id in selected_ids]
    )
    repositories = [
        Repository(
            repo_id=repo_id,
            ground_truth=selected_ground_truth_cases[index].ground_truth,
            predictions=prediction_cases[repo_id].case.predictions,
        )
        for index, repo_id in enumerate(sorted(selected_ids))
    ]
    manifest = validate_manifest(
        Manifest(
            benchmark_version="v1",
            detector_metadata=detector_metadata,
            prediction_mode=prediction_mode,
            repositories=repositories,
        )
    )
    return ManifestAssemblyResult(
        manifest=manifest,
        detector_metadata=detector_metadata,
        ignored=ignored,
        prediction_mode=prediction_mode,
    )


def _normalize_finding_selections(
    selections: Iterable[tuple[str, str]] | None,
) -> tuple[tuple[str, str], ...] | None:
    if selections is None:
        return None
    normalized = tuple(
        dict.fromkeys(
            (repo_id.strip(), finding_id.strip())
            for repo_id, finding_id in selections
        )
    )
    if not normalized or any(not repo_id or not finding_id for repo_id, finding_id in normalized):
        raise BenchmarkValidationError(
            "finding_selections must contain non-empty repository and finding IDs"
        )
    return normalized


def _normalize_repo_ids(repo_ids: Iterable[str] | None) -> tuple[str, ...] | None:
    if repo_ids is None:
        return None
    normalized = tuple(dict.fromkeys(repo_id.strip() for repo_id in repo_ids))
    if not normalized or any(not repo_id for repo_id in normalized):
        raise BenchmarkValidationError("repo_ids must contain non-empty repository IDs")
    return normalized


@dataclass(frozen=True)
class _CaseEntry:
    path: Path
    case: GroundTruthCase | PredictionCase


def _load_case_entries(
    directory: str | Path,
    case_type: type[GroundTruthCase] | type[PredictionCase],
    label: str,
) -> list[_CaseEntry]:
    path = Path(directory)
    if not path.is_dir():
        raise BenchmarkValidationError(f"{label} directory does not exist: {path}")

    entries: list[_CaseEntry] = []
    for artifact_path in sorted(path.glob("*.json"), key=lambda item: item.name):
        data = load_json(artifact_path)
        try:
            case = case_type.model_validate(data)
        except ValidationError as exc:
            details = "; ".join(
                f"field={'.'.join(str(part) for part in error['loc'])}: {error['msg']}"
                for error in exc.errors()
            )
            raise BenchmarkValidationError(
                f"invalid {label} artifact {artifact_path}: {details}"
            ) from exc
        entries.append(_CaseEntry(artifact_path, case))
    return entries


def _index_cases(entries: list[_CaseEntry], label: str) -> dict[str, _CaseEntry]:
    indexed: dict[str, _CaseEntry] = {}
    for entry in entries:
        repo_id = entry.case.repo_id
        if repo_id in indexed:
            raise BenchmarkValidationError(
                f"duplicate {label} repo_id={repo_id!r}: "
                f"{indexed[repo_id].path} and {entry.path}"
            )
        indexed[repo_id] = entry
    return indexed


def _require_gold_verified(cases: Iterable[GroundTruthCase]) -> None:
    """Reject selected evaluation targets that have not passed human review."""

    drafts = [
        f"{case.repo_id}/{finding.finding_id}"
        for case in cases
        for finding in case.ground_truth
        if finding.review_status != "gold_verified"
    ]
    if drafts:
        raise BenchmarkValidationError(
            "selected ground-truth findings must be gold_verified: "
            + ", ".join(sorted(drafts))
        )


def _consistent_detector_metadata(
    entries: list[_CaseEntry],
) -> DetectorMetadata | None:
    metadata = [entry.case.detector_metadata for entry in entries]
    if not metadata:
        return None
    first = metadata[0]
    inconsistent = [
        entry.path
        for entry in entries
        if (
            entry.case.detector_metadata.detector_version != first.detector_version
            or entry.case.detector_metadata.llm_model != first.llm_model
        )
    ]
    if inconsistent:
        raise BenchmarkValidationError(
            "prediction detector metadata is inconsistent: "
            f"expected={first.model_dump(mode='json', exclude_none=True)!r}, "
            f"files={[str(path) for path in inconsistent]!r}"
        )
    return first


def _prediction_directory_mode(entries: list[_CaseEntry]) -> PredictionMode:
    """Classify every prediction file before repository filtering is applied."""

    verdicts = [
        finding.verdict
        for entry in entries
        for finding in entry.case.predictions
    ]
    has_verdict = any(verdict is not None for verdict in verdicts)
    has_unclassified = any(verdict is None for verdict in verdicts)
    if has_verdict and has_unclassified:
        raise BenchmarkValidationError(
            "prediction directory must be uniformly legacy (without verdict) "
            "or annotated (every finding has verdict)"
        )
    return "annotated" if has_verdict else "legacy"
