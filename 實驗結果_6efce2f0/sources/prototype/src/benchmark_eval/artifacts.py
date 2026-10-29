"""Judge artifact loading and manifest identity checks."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from pydantic import ValidationError

from .contract import JudgeArtifact, Manifest, Scores
from .hashing import manifest_sha256
from .scoring import calculate_weighted_score, meets_threshold, validate_pair_score
from .validation import BenchmarkValidationError, load_json


def load_judge_artifact(source: str | Path | Mapping[str, Any]) -> JudgeArtifact:
    """Load and schema-validate a judge artifact."""

    data = load_json(source) if isinstance(source, (str, Path)) else source
    try:
        return JudgeArtifact.model_validate(data)
    except ValidationError as exc:
        details = "; ".join(
            f"field={'.'.join(str(part) for part in error['loc'])}: {error['msg']}"
            for error in exc.errors()
        )
        raise BenchmarkValidationError(f"invalid judge artifact: {details}") from exc


def verify_artifact_manifest_hash(
    manifest: str | Path | Mapping[str, Any] | Manifest,
    artifact: JudgeArtifact | str | Path | Mapping[str, Any],
) -> JudgeArtifact:
    """Verify that an artifact belongs to the supplied raw or validated manifest."""

    validated_artifact = (
        artifact
        if isinstance(artifact, JudgeArtifact)
        else load_judge_artifact(artifact)
    )
    expected_hash = manifest_sha256(manifest)
    if validated_artifact.manifest_sha256 != expected_hash:
        raise BenchmarkValidationError(
            "judge artifact manifest hash mismatch: "
            f"artifact={validated_artifact.manifest_sha256!r}, expected={expected_hash!r}"
        )
    return validated_artifact


def validate_artifact_completeness(
    manifest: Manifest,
    artifact: JudgeArtifact,
) -> JudgeArtifact:
    """Validate artifact repository identity and the complete pair matrix."""

    manifest_repositories = {repository.repo_id: repository for repository in manifest.repositories}
    artifact_repositories = {}
    for repository in artifact.repositories:
        if repository.repo_id in artifact_repositories:
            raise BenchmarkValidationError(
                f"duplicate artifact repo_id={repository.repo_id!r}"
            )
        artifact_repositories[repository.repo_id] = repository

    missing = sorted(set(manifest_repositories) - set(artifact_repositories))
    unknown = sorted(set(artifact_repositories) - set(manifest_repositories))
    if missing or unknown:
        raise BenchmarkValidationError(
            "artifact repository mismatch: "
            f"missing={missing!r}, unknown={unknown!r}"
        )

    weight_profile = artifact.judge_config.weight_profile
    calculate_weighted_score(Scores(R=0, L=0, I=0, M=0), weight_profile)
    meets_threshold(0.0, artifact.judge_config.threshold)
    for repo_id, manifest_repository in manifest_repositories.items():
        artifact_repository = artifact_repositories[repo_id]
        expected = {
            (prediction.finding_id, ground_truth.finding_id)
            for prediction in manifest_repository.predictions
            for ground_truth in manifest_repository.ground_truth
        }
        actual: set[tuple[str, str]] = set()
        for pair in artifact_repository.pairs:
            identity = (pair.prediction_id, pair.ground_truth_id)
            if identity in actual:
                raise BenchmarkValidationError(
                    "duplicate judge pair: "
                    f"repository={repo_id!r}, prediction_id={pair.prediction_id!r}, "
                    f"ground_truth_id={pair.ground_truth_id!r}"
                )
            if identity not in expected:
                raise BenchmarkValidationError(
                    "unknown judge pair: "
                    f"repository={repo_id!r}, prediction_id={pair.prediction_id!r}, "
                    f"ground_truth_id={pair.ground_truth_id!r}"
                )
            validate_pair_score(pair, weight_profile)
            actual.add(identity)
        if actual != expected:
            raise BenchmarkValidationError(
                f"incomplete judge pair matrix for repository={repo_id!r}: "
                f"missing={sorted(expected - actual)!r}"
            )
    return artifact
