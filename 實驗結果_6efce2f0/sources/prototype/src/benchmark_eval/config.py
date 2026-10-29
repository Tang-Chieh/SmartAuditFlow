"""Configuration owned by the benchmark Evaluation module."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path

from src.openai_auth import DEFAULT_AUTH_MODE, AuthMode

from .contract import WeightProfile
from .judge_runner import (
    DEFAULT_BATCH_SIZE,
    DEFAULT_MAX_CONCURRENCY,
    DEFAULT_TEMPERATURE,
)
from .scoring import get_weight_profile
from .validation import BenchmarkValidationError


DEFAULT_JUDGE_MODEL = "gpt-5.6-luna"


@dataclass(frozen=True)
class EvaluationConfig:
    """Complete configuration for one benchmark Evaluation run."""

    judge_model: str
    weight_profile: WeightProfile
    batch_size: int = DEFAULT_BATCH_SIZE
    temperature: float = DEFAULT_TEMPERATURE
    max_concurrency: int = DEFAULT_MAX_CONCURRENCY
    auth_mode: AuthMode = DEFAULT_AUTH_MODE
    oauth_credential_file: Path | None = None

    def __post_init__(self) -> None:
        if not self.judge_model.strip():
            raise ValueError("judge_model must not be empty")
        if self.batch_size <= 0:
            raise ValueError("batch_size must be positive")
        if self.temperature < 0:
            raise ValueError("temperature must be non-negative")
        if self.max_concurrency <= 0:
            raise ValueError("max_concurrency must be positive")

    @classmethod
    def from_environment(
        cls,
        *,
        default_weight_profile: str = "end-to-end-v2",
    ) -> "EvaluationConfig":
        """Resolve the public defaults without loading dotenv files."""

        model = os.environ.get("OPENAI_JUDGE_MODEL") or DEFAULT_JUDGE_MODEL
        profile_name = os.environ.get(
            "SCAR_EVALUATION_WEIGHT_PROFILE", default_weight_profile
        )
        try:
            profile = get_weight_profile(profile_name)
        except (KeyError, ValueError) as exc:
            raise BenchmarkValidationError(
                f"unknown Evaluation weight profile: {profile_name!r}"
            ) from exc
        auth_mode = os.environ.get("SCAR_OPENAI_AUTH_MODE", DEFAULT_AUTH_MODE)
        if auth_mode not in ("oauth", "api-key"):
            raise BenchmarkValidationError(
                f"unsupported SCAR_OPENAI_AUTH_MODE: {auth_mode!r}"
            )
        credential_file = os.environ.get("SCAR_OPENAI_OAUTH_CREDENTIAL_FILE")
        return cls(
            judge_model=model,
            weight_profile=profile,
            auth_mode=auth_mode,  # type: ignore[arg-type]
            oauth_credential_file=Path(credential_file) if credential_file else None,
        )


__all__ = ["DEFAULT_JUDGE_MODEL", "EvaluationConfig"]
