"""Deterministic benchmark evaluation orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from .artifacts import (
    validate_artifact_completeness,
    verify_artifact_manifest_hash,
)
from .contract import Manifest
from .hashing import manifest_sha256
from .matching import match_pairs
from .metrics import calculate_corpus_metrics, calculate_repository_metrics
from .validation import load_manifest, prediction_annotation_mode


@dataclass(frozen=True)
class EvaluationResult:
    """Report data and the optional large pair matrix kept separately."""

    report: dict[str, Any]
    pair_matrix: dict[str, list[dict[str, Any]]]
    selected_case_count: int | None = None
    ignored_case_count: int = 0


@dataclass(frozen=True)
class _ViewEvaluation:
    corpus_metrics: dict[str, Any]
    repositories: list[dict[str, Any]]


def evaluate_benchmark(
    manifest: str | Path | Mapping[str, Any],
    judge_artifact: str | Path | Mapping[str, Any],
    verification_summary: Mapping[str, Any] | None = None,
) -> EvaluationResult:
    """Evaluate a manifest using a verified, complete judge artifact.

    Legacy manifests produce the unchanged 0.2 report shape. Annotated
    predictions produce a 0.3 report with independently evaluated prediction
    views; the judge artifact is still generated once for the complete input.
    """

    validated_manifest = load_manifest(manifest)
    artifact = verify_artifact_manifest_hash(validated_manifest, judge_artifact)
    validate_artifact_completeness(validated_manifest, artifact)

    pair_matrix = {
        repository.repo_id: [
            _model_data(pair)
            for pair in next(
                item
                for item in artifact.repositories
                if item.repo_id == repository.repo_id
            ).pairs
        ]
        for repository in validated_manifest.repositories
    }

    mode = prediction_annotation_mode(validated_manifest)
    if mode == "legacy":
        evaluation = _evaluate_view(validated_manifest, artifact, None)
        report = {"report_version": "0.2"}
        report.update(
            _common_report_fields(
                validated_manifest,
                artifact,
                verification_summary=verification_summary,
            )
        )
        report.update(
            {
                "corpus_metrics": evaluation.corpus_metrics,
                "repositories": evaluation.repositories,
            }
        )
    else:
        view_statuses: tuple[tuple[str, frozenset[str]], ...] = (
            ("verified-only", frozenset({"verified"})),
            ("verified+needs_review", frozenset({"verified", "needs_review"})),
            ("needs_review-only", frozenset({"needs_review"})),
        )
        views = {
            name: _evaluate_view(validated_manifest, artifact, statuses)
            for name, statuses in view_statuses
        }
        report = {"report_version": "0.3"}
        report.update(
            _common_report_fields(
                validated_manifest,
                artifact,
                verification_summary=verification_summary,
            )
        )
        report.update(
            {
                "default_prediction_view": "verified-only",
                "prediction_annotations": {
                    "verified": _count_predictions(validated_manifest, "verified"),
                    "needs_review": _count_predictions(
                        validated_manifest, "needs_review"
                    ),
                },
                "prediction_views": {
                    name: {
                        "corpus_metrics": evaluation.corpus_metrics,
                        "repositories": evaluation.repositories,
                    }
                    for name, evaluation in views.items()
                },
            }
        )

    return EvaluationResult(
        report=report,
        pair_matrix=pair_matrix,
    )


def _evaluate_view(
    manifest: Manifest,
    artifact: Any,
    allowed_verdicts: frozenset[str] | None,
) -> _ViewEvaluation:
    """Match one prediction subset from the complete judge pair matrix."""

    repositories: list[dict[str, Any]] = []
    repository_metrics = []
    artifact_by_repo = {repository.repo_id: repository for repository in artifact.repositories}
    for manifest_repository in manifest.repositories:
        predictions = [
            prediction
            for prediction in manifest_repository.predictions
            if allowed_verdicts is None or prediction.verdict in allowed_verdicts
        ]
        prediction_ids = [item.finding_id for item in predictions]
        ground_truth_ids = [item.finding_id for item in manifest_repository.ground_truth]
        artifact_repository = artifact_by_repo[manifest_repository.repo_id]
        selected_pairs = [
            pair
            for pair in artifact_repository.pairs
            if pair.prediction_id in prediction_ids
        ]
        matching = match_pairs(
            selected_pairs,
            prediction_ids,
            ground_truth_ids,
            threshold=artifact.judge_config.threshold,
            weight_profile=artifact.judge_config.weight_profile,
        )
        metrics = calculate_repository_metrics(manifest_repository.repo_id, matching)
        repository_metrics.append(metrics)
        repositories.append(
            {
                "repo_id": metrics.repo_id,
                "metrics": _model_data(metrics),
                "matched_pairs": [_model_data(pair) for pair in matching.matched_pairs],
                "matching_order": [
                    {
                        "prediction_id": prediction_id,
                        "ground_truth_id": ground_truth_id,
                    }
                    for prediction_id, ground_truth_id in matching.matching_order
                ],
                "unmatched_predictions": matching.unmatched_prediction_ids,
                "unmatched_ground_truths": matching.unmatched_ground_truth_ids,
            }
        )

    corpus = calculate_corpus_metrics(repository_metrics)
    corpus_data = _model_data(corpus)
    # Repository-level metrics already live under report.repositories[].metrics.
    corpus_data.pop("repositories", None)
    return _ViewEvaluation(corpus_metrics=corpus_data, repositories=repositories)


def _common_report_fields(
    manifest: Manifest,
    artifact: Any,
    *,
    verification_summary: Mapping[str, Any] | None,
) -> dict[str, Any]:
    report: dict[str, Any] = {
        "benchmark_version": manifest.benchmark_version,
        "manifest_sha256": manifest_sha256(manifest),
        "judge_config": {
            "threshold": artifact.judge_config.threshold,
            "weight_profile": artifact.judge_config.weight_profile.model_dump(
                mode="json"
            ),
        },
        "matching_strategy": "greedy",
    }
    if manifest.detector_metadata is not None:
        report["detector_metadata"] = manifest.detector_metadata.model_dump(
            mode="json"
        )
    if verification_summary is not None:
        report["verification_summary"] = dict(verification_summary)
    return report


def _count_predictions(manifest: Manifest, verdict: str) -> int:
    return sum(
        prediction.verdict == verdict
        for repository in manifest.repositories
        for prediction in repository.predictions
    )


def _model_data(value: Any) -> dict[str, Any]:
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    if hasattr(value, "__dict__"):
        data = dict(value.__dict__)
        if "repositories" in data:
            data["repositories"] = [_model_data(item) for item in data["repositories"]]
        return data
    raise TypeError(f"unsupported report value: {type(value).__name__}")
