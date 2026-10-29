"""Deterministic component scoring for judged finding pairs."""

from __future__ import annotations

import math
from collections.abc import Mapping
from types import MappingProxyType
from numbers import Real
from typing import Any

from pydantic import ValidationError

from .contract import PairScore, Scores, WeightProfile, WeightProfileId
from .validation import BenchmarkValidationError


DEFAULT_THRESHOLD = 0.50
_COMPONENTS = ("R", "L", "I", "M")

WEIGHT_PROFILES: Mapping[WeightProfileId, WeightProfile] = MappingProxyType(
    {
        "legacy": WeightProfile(profile_id="legacy", R=0.35, L=0.30, I=0.20, M=0.15),
        "downstream-v2": WeightProfile(
            profile_id="downstream-v2", R=0.40, L=0.10, I=0.25, M=0.25
        ),
        "end-to-end-v2": WeightProfile(
            profile_id="end-to-end-v2", R=0.40, L=0.20, I=0.20, M=0.20
        ),
    }
)


def get_weight_profile(profile_id: str) -> WeightProfile:
    """Return a canonical named profile; no implicit profile is selected."""

    try:
        return WEIGHT_PROFILES[profile_id]  # type: ignore[index]
    except KeyError as exc:
        supported = ", ".join(WEIGHT_PROFILES)
        raise ValueError(
            f"unknown weight profile {profile_id!r}; expected one of: {supported}"
        ) from exc


def normalize_scores(scores: Scores | Mapping[str, Any]) -> dict[str, float]:
    """Validate component scores and normalize each integer score to ``0..1``."""

    validated = _validate_scores(scores)
    return {component: getattr(validated, component) / 4 for component in _COMPONENTS}


def calculate_weighted_score(
    scores: Scores | Mapping[str, Any],
    weight_profile: WeightProfile,
) -> float:
    """Calculate the normalized weighted score from R/L/I/M components."""

    normalized = normalize_scores(scores)
    validated_weights = _validate_weight_profile(weight_profile)
    return sum(
        normalized[component] * validated_weights[component] for component in _COMPONENTS
    )


def recalculate_pair_score(
    pair: PairScore,
    weight_profile: WeightProfile,
) -> PairScore:
    """Return a pair with its weighted score recalculated from raw components."""

    return pair.model_copy(
        update={"weighted_score": calculate_weighted_score(pair.scores, weight_profile)}
    )


def validate_pair_score(
    pair: PairScore,
    weight_profile: WeightProfile,
) -> PairScore:
    """Fail loudly when an artifact's stored weighted score is stale or incorrect."""

    expected = calculate_weighted_score(pair.scores, weight_profile)
    if not math.isclose(pair.weighted_score, expected, rel_tol=0.0, abs_tol=1e-9):
        raise BenchmarkValidationError(
            "weighted score mismatch for "
            f"prediction_id={pair.prediction_id!r}, "
            f"ground_truth_id={pair.ground_truth_id!r}: "
            f"artifact={pair.weighted_score!r}, expected={expected!r}"
        )
    return pair


def meets_threshold(score: Real, threshold: Real = DEFAULT_THRESHOLD) -> bool:
    """Return whether a normalized score is eligible for matching."""

    validated_score = _validate_unit_interval(score, "score")
    validated_threshold = _validate_unit_interval(threshold, "threshold")
    return validated_score >= validated_threshold


def _validate_scores(scores: Scores | Mapping[str, Any]) -> Scores:
    if isinstance(scores, Scores):
        return scores
    if not isinstance(scores, Mapping):
        raise BenchmarkValidationError(
            f"scores must be a Scores model or mapping, got {type(scores).__name__}"
        )
    try:
        return Scores.model_validate(scores)
    except ValidationError as exc:
        details = "; ".join(
            f"field={'.'.join(str(part) for part in error['loc'])}: {error['msg']}"
            for error in exc.errors()
        )
        raise BenchmarkValidationError(f"invalid scores: {details}") from exc


def _validate_weight_profile(weight_profile: WeightProfile) -> dict[str, float]:
    if not isinstance(weight_profile, WeightProfile):
        raise BenchmarkValidationError(
            "weight_profile must be a WeightProfile; an implicit or mapping-based "
            "weight configuration is not supported"
        )

    validated: dict[str, float] = {}
    for component in _COMPONENTS:
        value = getattr(weight_profile, component)
        numeric_value = float(value)
        if not math.isfinite(numeric_value) or numeric_value < 0:
            raise BenchmarkValidationError(
                f"weight {component!r} must be finite and non-negative"
            )
        validated[component] = numeric_value

    if not math.isclose(sum(validated.values()), 1.0, rel_tol=0.0, abs_tol=1e-9):
        raise BenchmarkValidationError("weight profile components must sum to 1.0")
    return validated


def _validate_unit_interval(value: Real, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise BenchmarkValidationError(f"{name} must be a finite number")
    numeric_value = float(value)
    if not math.isfinite(numeric_value) or not 0 <= numeric_value <= 1:
        raise BenchmarkValidationError(f"{name} must be between 0 and 1")
    return numeric_value
