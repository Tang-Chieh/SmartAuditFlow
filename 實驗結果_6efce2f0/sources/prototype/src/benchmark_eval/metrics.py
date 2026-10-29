"""Repository and corpus metrics derived from matching results."""

from __future__ import annotations

import math
from collections.abc import Iterable
from dataclasses import dataclass

from .matching import MatchingResult
from .validation import BenchmarkValidationError


@dataclass(frozen=True)
class RepositoryMetrics:
    """Soft metrics for one repository."""

    repo_id: str
    ground_truth_count: int
    prediction_count: int
    matched_weight: float
    soft_precision: float
    soft_recall: float
    soft_f1: float


@dataclass(frozen=True)
class CorpusMetrics:
    """Macro and pooled soft metrics for a corpus."""

    repositories: tuple[RepositoryMetrics, ...]
    macro_soft_f1: float
    pooled_soft_precision: float
    pooled_soft_recall: float
    pooled_soft_f1: float
    total_matched_weight: float
    total_ground_truth_count: int
    total_prediction_count: int


def calculate_repository_metrics(
    repo_id: str, matching: MatchingResult
) -> RepositoryMetrics:
    """Calculate repository metrics solely from a matching result."""

    if not repo_id:
        raise BenchmarkValidationError("repo_id must be a non-empty string")

    matched_prediction_ids: set[str] = set()
    matched_ground_truth_ids: set[str] = set()
    matched_weight = 0.0
    for pair in matching.matched_pairs:
        if pair.prediction_id in matched_prediction_ids:
            raise BenchmarkValidationError(
                f"matching result reuses prediction_id={pair.prediction_id!r}"
            )
        if pair.ground_truth_id in matched_ground_truth_ids:
            raise BenchmarkValidationError(
                f"matching result reuses ground_truth_id={pair.ground_truth_id!r}"
            )
        matched_prediction_ids.add(pair.prediction_id)
        matched_ground_truth_ids.add(pair.ground_truth_id)
        if not math.isfinite(pair.weighted_score) or not 0 <= pair.weighted_score <= 1:
            raise BenchmarkValidationError(
                "matched pair weighted_score must be between 0 and 1"
            )
        matched_weight += pair.weighted_score

    _validate_unmatched_ids(matching.unmatched_prediction_ids, matched_prediction_ids, "prediction")
    _validate_unmatched_ids(
        matching.unmatched_ground_truth_ids, matched_ground_truth_ids, "ground_truth"
    )

    prediction_count = len(matched_prediction_ids) + len(
        matching.unmatched_prediction_ids
    )
    ground_truth_count = len(matched_ground_truth_ids) + len(
        matching.unmatched_ground_truth_ids
    )
    soft_precision = _safe_ratio(matched_weight, prediction_count, ground_truth_count == 0)
    soft_recall = _safe_ratio(matched_weight, ground_truth_count, prediction_count == 0)
    soft_f1 = _soft_f1(matched_weight, ground_truth_count, prediction_count)

    return RepositoryMetrics(
        repo_id=repo_id,
        ground_truth_count=ground_truth_count,
        prediction_count=prediction_count,
        matched_weight=matched_weight,
        soft_precision=soft_precision,
        soft_recall=soft_recall,
        soft_f1=soft_f1,
    )


def calculate_corpus_metrics(
    repositories: Iterable[RepositoryMetrics],
) -> CorpusMetrics:
    """Calculate macro repository SoftF1 and pooled corpus SoftF1."""

    repository_metrics = tuple(repositories)
    total_matched_weight = sum(item.matched_weight for item in repository_metrics)
    total_ground_truth_count = sum(
        item.ground_truth_count for item in repository_metrics
    )
    total_prediction_count = sum(item.prediction_count for item in repository_metrics)

    macro_soft_f1 = (
        sum(item.soft_f1 for item in repository_metrics) / len(repository_metrics)
        if repository_metrics
        else 0.0
    )
    pooled_soft_f1 = _soft_f1(
        total_matched_weight,
        total_ground_truth_count,
        total_prediction_count,
    )
    pooled_soft_precision = _safe_ratio(
        total_matched_weight,
        total_prediction_count,
        total_ground_truth_count == 0,
    )
    pooled_soft_recall = _safe_ratio(
        total_matched_weight,
        total_ground_truth_count,
        total_prediction_count == 0,
    )
    return CorpusMetrics(
        repositories=repository_metrics,
        macro_soft_f1=macro_soft_f1,
        pooled_soft_precision=pooled_soft_precision,
        pooled_soft_recall=pooled_soft_recall,
        pooled_soft_f1=pooled_soft_f1,
        total_matched_weight=total_matched_weight,
        total_ground_truth_count=total_ground_truth_count,
        total_prediction_count=total_prediction_count,
    )


def _safe_ratio(numerator: float, denominator: int, empty_other_side: bool) -> float:
    if denominator:
        return numerator / denominator
    return 1.0 if empty_other_side else 0.0


def _soft_f1(matched_weight: float, ground_truth_count: int, prediction_count: int) -> float:
    denominator = ground_truth_count + prediction_count
    return 1.0 if denominator == 0 else 2 * matched_weight / denominator


def _validate_unmatched_ids(
    ids: list[str], matched_ids: set[str], side: str
) -> None:
    if len(ids) != len(set(ids)):
        raise BenchmarkValidationError(f"matching result duplicates {side}_id")
    overlap = matched_ids.intersection(ids)
    if overlap:
        raise BenchmarkValidationError(
            f"matching result marks {side}_id as both matched and unmatched: {sorted(overlap)!r}"
        )
