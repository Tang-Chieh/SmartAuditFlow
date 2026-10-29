"""Pydantic models for the benchmark evaluator JSON contract."""

from __future__ import annotations

import math
from typing import Annotated, Literal, Mapping

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StrictFloat,
    StrictInt,
    StrictStr,
    model_validator,
)


NonEmptyStr = Annotated[StrictStr, Field(min_length=1)]
Score = Annotated[StrictInt, Field(ge=0, le=4)]
WeightProfileId = Literal["legacy", "downstream-v2", "end-to-end-v2"]
PredictionVerdict = Literal["verified", "needs_review"]
PredictionMode = Literal["legacy", "annotated"]


class ContractModel(BaseModel):
    """Base model that preserves unknown JSON fields for forward compatibility."""

    model_config = ConfigDict(extra="allow")


class VulnerableCode(ContractModel):
    file: NonEmptyStr
    contract: NonEmptyStr
    function: NonEmptyStr
    start_line: Annotated[StrictInt, Field(ge=1)] | None = None
    end_line: Annotated[StrictInt, Field(ge=1)] | None = None

    @model_validator(mode="before")
    @classmethod
    def reject_legacy_lines(cls, value: object) -> object:
        if isinstance(value, Mapping) and "lines" in value:
            raise ValueError(
                "lines is not supported; use inclusive start_line and end_line"
            )
        return value

    @model_validator(mode="after")
    def validate_line_range(self) -> VulnerableCode:
        if (self.start_line is None) != (self.end_line is None):
            raise ValueError("start_line and end_line must be provided together")
        if (
            self.start_line is not None
            and self.end_line is not None
            and self.end_line < self.start_line
        ):
            raise ValueError("end_line must be greater than or equal to start_line")
        return self


class Finding(ContractModel):
    """Shared finding shape for both ground truth and predictions."""

    title: NonEmptyStr
    description: NonEmptyStr
    impact: NonEmptyStr
    vulnerable_code: list[VulnerableCode]
    mitigation: NonEmptyStr
    finding_id: NonEmptyStr
    poc: StrictStr | None = None
    severity: StrictStr | None = None


class GroundTruthFinding(Finding):
    """Evaluation target plus its eligibility status.

    The status is consumed by manifest assembly and intentionally excluded from
    the LLM judge payload.
    """

    review_status: Literal["draft_for_manual_review", "gold_verified"] = (
        "draft_for_manual_review"
    )


class PredictionFinding(Finding):
    """Prediction with an optional auditor verification annotation.

    ``None`` is the legacy input shape.  The evaluator enforces that one
    prediction directory is either entirely legacy or entirely annotated.
    ``rejected`` is intentionally not a valid prediction verdict: rejected
    auditor findings must stay out of benchmark predictions.
    """

    verdict: PredictionVerdict | None = None


class DetectorMetadata(ContractModel):
    """Identity of the detector that produced a prediction collection."""

    detector_version: NonEmptyStr
    llm_model: NonEmptyStr


class GroundTruthCase(ContractModel):
    """Ground-truth input for one repository evaluation case."""

    repo_id: NonEmptyStr
    ground_truth: list[GroundTruthFinding]


class PredictionCase(ContractModel):
    """Detector output for one repository evaluation case."""

    repo_id: NonEmptyStr
    detector_metadata: DetectorMetadata
    predictions: list[PredictionFinding]


class Repository(ContractModel):
    repo_id: NonEmptyStr
    ground_truth: list[GroundTruthFinding]
    predictions: list[PredictionFinding]


class Manifest(ContractModel):
    benchmark_version: NonEmptyStr
    repositories: list[Repository]
    detector_metadata: DetectorMetadata | None = None
    # Set by directory assembly when the source directory has been classified.
    # Older hand-authored manifests omit this field and are classified from
    # their prediction findings during validation.
    prediction_mode: PredictionMode | None = None


class WeightProfile(BaseModel):
    """Immutable, named scoring policy for one evaluation context."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    profile_id: WeightProfileId
    R: Annotated[StrictFloat, Field(ge=0, le=1)]
    L: Annotated[StrictFloat, Field(ge=0, le=1)]
    I: Annotated[StrictFloat, Field(ge=0, le=1)]
    M: Annotated[StrictFloat, Field(ge=0, le=1)]

    @model_validator(mode="after")
    def validate_sum(self) -> WeightProfile:
        if not math.isclose(
            sum((self.R, self.L, self.I, self.M)),
            1.0,
            rel_tol=0.0,
            abs_tol=1e-9,
        ):
            raise ValueError("weight profile components must sum to 1.0")
        return self


class JudgeConfig(ContractModel):
    model_config = ConfigDict(extra="forbid")

    threshold: Annotated[StrictFloat, Field(ge=0, le=1)]
    weight_profile: WeightProfile


class Scores(ContractModel):
    R: Score
    L: Score
    I: Score
    M: Score


class PairScore(ContractModel):
    prediction_id: NonEmptyStr
    ground_truth_id: NonEmptyStr
    scores: Scores
    weighted_score: StrictFloat
    rationale: StrictStr


class JudgeRepository(ContractModel):
    repo_id: NonEmptyStr
    pairs: list[PairScore]


class JudgeArtifact(ContractModel):
    artifact_version: Literal["0.3"]
    manifest_sha256: NonEmptyStr
    judge_config: JudgeConfig
    judge_metadata: dict[str, object]
    repositories: list[JudgeRepository]


# Canonical serialization used by the hashing phase:
# json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
CANONICAL_JSON_RULE = (
    "json.dumps(value, ensure_ascii=False, sort_keys=True, "
    "separators=(\",\", \":\"))"
)
