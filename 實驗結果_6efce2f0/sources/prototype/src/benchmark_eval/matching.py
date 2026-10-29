"""Deterministic matching strategies for judged finding pairs."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from numbers import Real

from .contract import PairScore, WeightProfile
from .scoring import DEFAULT_THRESHOLD, meets_threshold, validate_pair_score
from .validation import BenchmarkValidationError


@dataclass
class MatchingResult:
    """The accepted pairs and the unmatched IDs for one repository."""

    matched_pairs: list[PairScore]
    unmatched_prediction_ids: list[str]
    unmatched_ground_truth_ids: list[str]
    matching_order: list[tuple[str, str]]


def greedy_match(
    pair_scores: Iterable[PairScore],
    prediction_ids: Sequence[str],
    ground_truth_ids: Sequence[str],
    weight_profile: WeightProfile,
    threshold: Real = DEFAULT_THRESHOLD,
) -> MatchingResult:
    """Match the highest-scoring eligible pair while preserving one-to-one use."""

    predictions = _unique_ids(prediction_ids, "prediction")
    ground_truths = _unique_ids(ground_truth_ids, "ground_truth")
    pairs = _validate_complete_matrix(pair_scores, predictions, ground_truths)

    scored_pairs = []
    for pair in pairs:
        scored_pair = validate_pair_score(pair, weight_profile)
        if meets_threshold(scored_pair.weighted_score, threshold):
            scored_pairs.append(scored_pair)
    scored_pairs.sort(
        key=lambda pair: (
            -pair.weighted_score,
            pair.prediction_id,
            pair.ground_truth_id,
        )
    )

    used_predictions: set[str] = set()
    used_ground_truths: set[str] = set()
    matched_pairs: list[PairScore] = []
    matching_order: list[tuple[str, str]] = []
    for pair in scored_pairs:
        if pair.prediction_id in used_predictions:
            continue
        if pair.ground_truth_id in used_ground_truths:
            continue
        used_predictions.add(pair.prediction_id)
        used_ground_truths.add(pair.ground_truth_id)
        matched_pairs.append(pair)
        matching_order.append((pair.prediction_id, pair.ground_truth_id))

    return MatchingResult(
        matched_pairs=matched_pairs,
        unmatched_prediction_ids=[
            finding_id
            for finding_id in predictions
            if finding_id not in used_predictions
        ],
        unmatched_ground_truth_ids=[
            finding_id
            for finding_id in ground_truths
            if finding_id not in used_ground_truths
        ],
        matching_order=matching_order,
    )


def match_pairs(
    pair_scores: Iterable[PairScore],
    prediction_ids: Sequence[str],
    ground_truth_ids: Sequence[str],
    weight_profile: WeightProfile,
    threshold: Real = DEFAULT_THRESHOLD,
) -> MatchingResult:
    """Public strategy entry point; currently backed by deterministic greedy matching."""

    return greedy_match(
        pair_scores, prediction_ids, ground_truth_ids, weight_profile, threshold
    )


def _unique_ids(ids: Sequence[str], side: str) -> list[str]:
    values = list(ids)
    if any(not isinstance(value, str) or not value for value in values):
        raise BenchmarkValidationError(f"{side}_ids must contain non-empty strings")
    if len(values) != len(set(values)):
        raise BenchmarkValidationError(f"duplicate {side}_id in matching input")
    return values


def _validate_complete_matrix(
    pair_scores: Iterable[PairScore],
    prediction_ids: Sequence[str],
    ground_truth_ids: Sequence[str],
) -> list[PairScore]:
    pairs = list(pair_scores)
    expected = {
        (prediction_id, ground_truth_id)
        for prediction_id in prediction_ids
        for ground_truth_id in ground_truth_ids
    }
    actual: set[tuple[str, str]] = set()
    for pair in pairs:
        identity = (pair.prediction_id, pair.ground_truth_id)
        if identity in actual:
            raise BenchmarkValidationError(
                "duplicate judge pair: "
                f"prediction_id={pair.prediction_id!r}, "
                f"ground_truth_id={pair.ground_truth_id!r}"
            )
        if identity not in expected:
            raise BenchmarkValidationError(
                "unknown judge pair: "
                f"prediction_id={pair.prediction_id!r}, "
                f"ground_truth_id={pair.ground_truth_id!r}"
            )
        actual.add(identity)

    missing = sorted(expected - actual)
    if missing:
        raise BenchmarkValidationError(f"incomplete judge pair matrix: missing={missing!r}")
    return pairs
