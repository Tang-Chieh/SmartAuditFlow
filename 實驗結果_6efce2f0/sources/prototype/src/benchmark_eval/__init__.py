"""Public API for the benchmark evaluator workflow."""

from .artifacts import (
    load_judge_artifact,
    validate_artifact_completeness,
    verify_artifact_manifest_hash,
)
from .contract import (
    DetectorMetadata,
    Finding,
    GroundTruthCase,
    GroundTruthFinding,
    JudgeArtifact,
    WeightProfile,
    WeightProfileId,
    Manifest,
    PredictionCase,
    PredictionFinding,
    PredictionMode,
    PredictionVerdict,
)
from .hashing import canonical_json_bytes, manifest_sha256
from .judge_runner import (
    DEFAULT_MAX_CONCURRENCY,
    JudgeBatchResponse,
    JudgeArtifactGenerationError,
    build_batch_prompt,
    generate_judge_artifact,
    write_judge_artifact,
)
from .matching import MatchingResult, greedy_match, match_pairs
from .metrics import (
    CorpusMetrics,
    RepositoryMetrics,
    calculate_corpus_metrics,
    calculate_repository_metrics,
)
from .observability import DEFAULT_LOG_LEVEL, configure_logging
from .evaluator import EvaluationResult, evaluate_benchmark
from .config import DEFAULT_JUDGE_MODEL, EvaluationConfig
from .scoring import (
    DEFAULT_THRESHOLD,
    WEIGHT_PROFILES,
    calculate_weighted_score,
    get_weight_profile,
    meets_threshold,
    normalize_scores,
    recalculate_pair_score,
    validate_pair_score,
)
from .validation import (
    BenchmarkValidationError,
    load_json,
    load_manifest,
    validate_manifest,
)
from .inputs import IgnoredArtifactSummary, ManifestAssemblyResult, assemble_manifest
from .pipeline import evaluate_directory, evaluate_from_artifact, evaluate_manifest
from .markdown import render_evaluation_markdown, write_evaluation_markdown

__all__ = [
    "BenchmarkValidationError",
    "EvaluationResult",
    "EvaluationConfig",
    "DEFAULT_JUDGE_MODEL",
    "Finding",
    "GroundTruthFinding",
    "DetectorMetadata",
    "GroundTruthCase",
    "JudgeArtifact",
    "WeightProfile",
    "WeightProfileId",
    "JudgeBatchResponse",
    "JudgeArtifactGenerationError",
    "Manifest",
    "ManifestAssemblyResult",
    "IgnoredArtifactSummary",
    "PredictionCase",
    "PredictionFinding",
    "PredictionMode",
    "PredictionVerdict",
    "assemble_manifest",
    "evaluate_directory",
    "evaluate_from_artifact",
    "evaluate_manifest",
    "render_evaluation_markdown",
    "write_evaluation_markdown",
    "canonical_json_bytes",
    "build_batch_prompt",
    "calculate_weighted_score",
    "calculate_corpus_metrics",
    "calculate_repository_metrics",
    "CorpusMetrics",
    "DEFAULT_THRESHOLD",
    "WEIGHT_PROFILES",
    "DEFAULT_MAX_CONCURRENCY",
    "DEFAULT_LOG_LEVEL",
    "configure_logging",
    "load_judge_artifact",
    "evaluate_benchmark",
    "generate_judge_artifact",
    "get_weight_profile",
    "load_json",
    "load_manifest",
    "MatchingResult",
    "manifest_sha256",
    "greedy_match",
    "match_pairs",
    "meets_threshold",
    "normalize_scores",
    "recalculate_pair_score",
    "RepositoryMetrics",
    "validate_manifest",
    "validate_artifact_completeness",
    "validate_pair_score",
    "verify_artifact_manifest_hash",
    "write_judge_artifact",
]
