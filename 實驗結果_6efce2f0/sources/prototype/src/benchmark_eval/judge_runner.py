"""OpenAI judge runner for generating complete benchmark pair artifacts."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
from contextlib import nullcontext
import json
import logging
import math
from pathlib import Path
from dataclasses import dataclass
from typing import Annotated, Any, Mapping, Protocol

from pydantic import BaseModel, ConfigDict, Field, StrictInt, StrictStr, ValidationError

from .artifacts import validate_artifact_completeness
from .contract import (
    Finding,
    JudgeArtifact,
    JudgeConfig,
    JudgeRepository,
    Manifest,
    PairScore,
    Score,
    Scores,
    WeightProfile,
)
from .hashing import manifest_sha256
from .scoring import DEFAULT_THRESHOLD, calculate_weighted_score
from .reporting import write_json_atomic
from .validation import BenchmarkValidationError, load_manifest, validate_manifest
from src.openai_auth import (
    DEFAULT_AUTH_MODE,
    AuthMode,
    OpenAIClientProvider,
)


logger = logging.getLogger("benchmark_eval")


ARTIFACT_VERSION = "0.3"
PROMPT_VERSION = "benchmark-judge-v3"
DEFAULT_BATCH_SIZE = 10
DEFAULT_TEMPERATURE = 0.0
DEFAULT_MAX_CONCURRENCY = 4

SYSTEM_PROMPT = """You are a smart-contract security benchmark judge.

Compare each prediction independently against the single ground-truth finding. Do not rank predictions or select only the best candidate.

For each prediction-ground-truth pair, first evaluate each component independently and form a concise rationale covering R, L, I, and M. For each component, identify the specific correct claims, omissions, errors, or contradictions relevant to that component. Then assign the corresponding integer score according to the rubric below.

The rationale should make the basis of each component score clear, for example using concise labels such as "R:", "L:", "I:", and "M:". Do not use correctness in one component as evidence for another.

Score these four components independently:

* R: root-cause correctness
* L: vulnerable-code localization
* I: impact correctness
* M: mitigation correctness

## R — Root-cause correctness

Evaluate whether the prediction identifies the same underlying security flaw or mechanism as the ground truth.

* 0: No meaningful root-cause claim, or the claimed mechanism is unrelated to or contradicts the ground truth.
* 1: Mentions only a broadly related vulnerability category, symptom, or affected area, but does not identify the actual causal flaw.
* 2: Identifies part of the correct mechanism, but omits or misstates one or more material causal elements.
* 3: Identifies the correct core security flaw or mechanism, with only minor omissions or imprecision that do not materially change the cause.
* 4: Identifies the same underlying security flaw or mechanism as the ground truth and is causally equivalent, with no material contradiction.

Do not require the prediction to describe the full exploit or propagation chain in order to receive a high R score if it correctly identifies the root cause itself.

## L — Vulnerable-code localization

Evaluate whether the prediction identifies the same vulnerable code path, function, or relevant operation as the ground truth.

* 0: No meaningful localization, or the identified code is unrelated to the vulnerability.
* 1: Identifies only a broad contract, module, subsystem, or general code area.
* 2: Identifies a relevant or adjacent contract/function, but misses the actual vulnerable function, operation, or an important part of the vulnerable path.
* 3: Identifies the correct vulnerable function or code path, with only minor imprecision in the exact operation or a minor omission of a secondary relevant location.
* 4: Identifies the same vulnerable code path or function as the ground truth and correctly localizes the relevant vulnerable operation or data-flow point.

Equivalent caller/callee references are acceptable when the vulnerability spans multiple functions. Exact line numbers are not required.

## I — Impact correctness

Evaluate whether the prediction describes the same attacker capability or security consequence as the ground truth.

* 0: No meaningful impact claim, or the claimed consequence is unrelated to or contradicts the ground truth.
* 1: States only a generic consequence such as "loss of funds", "can be exploited", or "incorrect behavior" without identifying the actual security consequence.
* 2: Identifies the general consequence, but materially omits or misstates the attacker capability, affected asset, required condition, scope, or resulting security violation.
* 3: Correctly identifies the primary security consequence, with only minor scope, condition, or asset imprecision.
* 4: Describes the same attacker capability or security consequence as the ground truth, with materially equivalent exploit outcome under the same relevant vulnerable state and code path.

As a semantic check, consider whether the described vulnerability would support substantially the same exploit outcome as the ground truth under the relevant state and code path.

A severity label alone is not an impact description.

## M — Mitigation correctness

Evaluate whether the proposed mitigation would actually prevent or remove the ground-truth vulnerability.

* 0: No meaningful mitigation is provided, or the mitigation is unrelated, ineffective, or would not address the vulnerability.
* 1: Suggests only generic hardening or a weakly related best practice that does not adequately address the underlying flaw.
* 2: The mitigation is directionally relevant, but materially incomplete, bypassable, or addresses only a symptom rather than the underlying vulnerability.
* 3: The mitigation correctly addresses the underlying flaw in principle, with only minor implementation or coverage omissions.
* 4: Applying the proposed mitigation would also fix the ground-truth vulnerability. The mitigation is technically sound and sufficiently complete to prevent the same underlying flaw across the affected path.

The prediction does not need to use the same wording or exact mitigation as the ground truth. An alternative mitigation is fully acceptable if it effectively prevents the same vulnerability.

Return exactly one result for every supplied prediction, preserving each supplied ordinal_index. Do not return prediction IDs or ground-truth IDs; the server owns those identities.
"""


class _ResponseScores(BaseModel):
    model_config = ConfigDict(extra="forbid")

    R: Score
    L: Score
    I: Score
    M: Score


class _ResponsePair(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ordinal_index: Annotated[StrictInt, Field(ge=0)]
    scores: _ResponseScores
    rationale: StrictStr


class JudgeBatchResponse(BaseModel):
    """Strict Structured Outputs schema for one ground-truth row batch."""

    model_config = ConfigDict(extra="forbid")

    pairs: list[_ResponsePair]


class JudgeArtifactGenerationError(BenchmarkValidationError):
    """Raised when a Judge run completes but cannot form a valid artifact."""

    def __init__(self, message: str, diagnostic_artifact: dict[str, Any]) -> None:
        super().__init__(message)
        self.diagnostic_artifact = diagnostic_artifact


def build_batch_prompt(ground_truth: Finding, predictions: list[Finding]) -> str:
    """Build the versioned user prompt for one row-wise prediction batch."""

    payload = {
        "prompt_version": PROMPT_VERSION,
        "ground_truth": _finding_payload(ground_truth),
        "predictions": [
            {"ordinal_index": index, **_finding_payload(prediction)}
            for index, prediction in enumerate(predictions)
        ],
    }
    return (
        "Score every prediction against the ground truth using the system rubric. "
        "Return exactly one result per ordinal_index, including every index exactly once. "
        "Do not invent or return prediction IDs or ground-truth IDs.\n\n"
        + json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2)
    )


def generate_judge_artifact(
    manifest: str | Path | Mapping[str, Any] | Manifest,
    *,
    model: str,
    weight_profile: WeightProfile,
    batch_size: int = DEFAULT_BATCH_SIZE,
    temperature: float = DEFAULT_TEMPERATURE,
    client: Any | None = None,
    max_concurrency: int = DEFAULT_MAX_CONCURRENCY,
    auth_mode: AuthMode = DEFAULT_AUTH_MODE,
    oauth_credential_file: str | Path | None = None,
    judge_backend: "JudgeBackend | None" = None,
) -> JudgeArtifact:
    """Judge all row-wise batches and return a validated complete artifact."""

    validated_manifest = (
        validate_manifest(manifest)
        if isinstance(manifest, Manifest)
        else load_manifest(manifest)
    )
    _validate_options(model, batch_size, temperature, max_concurrency, auth_mode)
    if auth_mode == "oauth" and temperature != DEFAULT_TEMPERATURE:
        raise BenchmarkValidationError(
            "OAuth judge mode requires temperature=0 because the ChatGPT OAuth "
            "Responses path does not accept temperature"
        )

    jobs: list[_JudgeJob] = []
    for repository in validated_manifest.repositories:
        for ground_truth in repository.ground_truth:
            for start in range(0, len(repository.predictions), batch_size):
                jobs.append(
                    _JudgeJob(
                        repo_id=repository.repo_id,
                        ground_truth=ground_truth,
                        predictions=repository.predictions[start : start + batch_size],
                    )
                    )

    prediction_count = sum(
        len(repository.predictions) for repository in validated_manifest.repositories
    )
    logger.info(
        "judge plan: repositories=%d, predictions=%d, jobs=%d, "
        "batch_size=%d, concurrency=%d",
        len(validated_manifest.repositories),
        prediction_count,
        len(jobs),
        batch_size,
        max_concurrency,
    )

    active_backend = judge_backend
    if active_backend is None and jobs:
        if client is not None:
            active_backend = _SdkJudgeBackend(client=client, auth_mode="api-key")
        else:
            active_backend = _SdkJudgeBackend(
                provider=OpenAIClientProvider(
                    auth_mode=auth_mode,
                    oauth_credential_file=(
                        str(oauth_credential_file)
                        if oauth_credential_file is not None
                        else None
                    ),
                ),
                auth_mode=auth_mode,
            )

    with ThreadPoolExecutor(max_workers=min(max_concurrency, len(jobs) or 1)) as executor:
        futures = {
            executor.submit(
                _run_judge_job,
                job,
                active_backend,
                model,
                temperature,
            ): index
            for index, job in enumerate(jobs)
        }
        responses: list[Any | None] = [None] * len(jobs)
        failures: list[tuple[int, Exception]] = []
        completed = 0
        progress_interval = max(1, min(50, len(jobs)))
        for future in as_completed(futures):
            index = futures[future]
            try:
                responses[index] = future.result()
            except Exception as exc:
                failures.append((index, exc))
            completed += 1
            if completed % progress_interval == 0 or completed == len(jobs):
                logger.info(
                    "judge progress: completed=%d/%d",
                    completed,
                    len(jobs),
                )
    pairs_by_repo: dict[str, list[PairScore]] = {
        repository.repo_id: [] for repository in validated_manifest.repositories
    }
    calls: list[dict[str, Any]] = []
    diagnostic_jobs: list[dict[str, Any]] = []
    validation_failures: list[dict[str, Any]] = []
    request_failures = dict(failures)
    for index, (job, response) in enumerate(zip(jobs, responses, strict=True)):
        if response is None:
            failure = request_failures[index]
            error = (
                str(failure)
                if isinstance(failure, Exception)
                else repr(failure)
            )
            diagnostic_jobs.append(
                _diagnostic_job_payload(job, response=None, error=error)
            )
            validation_failures.append(
                {
                    "job_index": index,
                    "repo_id": job.repo_id,
                    "ground_truth_id": job.ground_truth.finding_id,
                    "stage": "request",
                    "error": error,
                }
            )
            continue
        diagnostic_payload = _diagnostic_job_payload(job, response=response)
        diagnostic_jobs.append(diagnostic_payload)
        calls.append(_call_metadata(job, response))
        try:
            batch_pairs = _validate_judge_response(job, response, weight_profile)
        except BenchmarkValidationError as exc:
            pairs_by_repo[job.repo_id].extend(
                _partial_batch_pairs(job, response, weight_profile)
            )
            validation_failures.append(
                {
                    "job_index": index,
                    "repo_id": job.repo_id,
                    "ground_truth_id": job.ground_truth.finding_id,
                    "stage": "validation",
                    "error": str(exc),
                }
            )
            continue
        pairs_by_repo[job.repo_id].extend(batch_pairs)

    if validation_failures:
        diagnostic = _diagnostic_artifact(
            validated_manifest,
            model=model,
            batch_size=batch_size,
            temperature=temperature,
            max_concurrency=max_concurrency,
            auth_mode=auth_mode,
            weight_profile=weight_profile,
            calls=calls,
            partial_pairs=pairs_by_repo,
            jobs=diagnostic_jobs,
            failures=validation_failures,
        )
        first_failure = validation_failures[0]["error"]
        raise JudgeArtifactGenerationError(first_failure, diagnostic)

    artifact_repositories = [
        JudgeRepository(repo_id=repository.repo_id, pairs=pairs_by_repo[repository.repo_id])
        for repository in validated_manifest.repositories
    ]

    artifact = JudgeArtifact(
        artifact_version=ARTIFACT_VERSION,
        manifest_sha256=manifest_sha256(validated_manifest),
        judge_config=JudgeConfig(
            threshold=DEFAULT_THRESHOLD,
            weight_profile=weight_profile,
        ),
        judge_metadata={
            "api": "responses",
            "model": model,
            "temperature": temperature,
            "prompt_version": PROMPT_VERSION,
            "batch_size": batch_size,
            "max_concurrency": max_concurrency,
            "auth_mode": "injected" if client is not None else auth_mode,
            "calls": calls,
        },
        repositories=artifact_repositories,
    )
    return validate_artifact_completeness(validated_manifest, artifact)


def write_judge_artifact(artifact: JudgeArtifact, output: str | Path) -> Path:
    """Atomically write a complete judge artifact and return its path."""

    return write_json_atomic(artifact.model_dump(mode="json"), output)


def _call_metadata(job: _JudgeJob, response: Any) -> dict[str, Any]:
    return {
        "repo_id": job.repo_id,
        "ground_truth_id": job.ground_truth.finding_id,
        "prediction_ids": [item.finding_id for item in job.predictions],
        "response_id": getattr(response, "id", None),
        "returned_model": getattr(response, "model", None),
        "usage": _usage_payload(getattr(response, "usage", None)),
    }


def _response_payload(response: Any) -> dict[str, Any]:
    parsed = getattr(response, "output_parsed", None)
    if isinstance(parsed, BaseModel):
        parsed_payload: Any = parsed.model_dump(mode="json")
    elif isinstance(parsed, Mapping):
        parsed_payload = dict(parsed)
    else:
        parsed_payload = parsed
    return {
        "status": getattr(response, "status", None),
        "id": getattr(response, "id", None),
        "model": getattr(response, "model", None),
        "usage": _usage_payload(getattr(response, "usage", None)),
        "output_parsed": parsed_payload,
    }


def _diagnostic_job_payload(
    job: _JudgeJob,
    *,
    response: Any | None,
    error: str | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "repo_id": job.repo_id,
        "ground_truth_id": job.ground_truth.finding_id,
        "prediction_ids": [item.finding_id for item in job.predictions],
        "expected_ordinal_indexes": list(range(len(job.predictions))),
    }
    if response is not None:
        payload["response"] = _response_payload(response)
    if error is not None:
        payload["error"] = error
    return payload


def _diagnostic_artifact(
    manifest: Manifest,
    *,
    model: str,
    batch_size: int,
    temperature: float,
    max_concurrency: int,
    auth_mode: AuthMode,
    weight_profile: WeightProfile,
    calls: list[dict[str, Any]],
    partial_pairs: dict[str, list[PairScore]],
    jobs: list[dict[str, Any]],
    failures: list[Any],
) -> dict[str, Any]:
    return {
        "status": "validation_failed",
        "artifact_version": ARTIFACT_VERSION,
        "manifest_sha256": manifest_sha256(manifest),
        "judge_config": {
            "threshold": DEFAULT_THRESHOLD,
            "weight_profile": weight_profile.model_dump(mode="json"),
        },
        "judge_metadata": {
            "api": "responses",
            "model": model,
            "temperature": temperature,
            "prompt_version": PROMPT_VERSION,
            "batch_size": batch_size,
            "max_concurrency": max_concurrency,
            "auth_mode": auth_mode,
            "calls": calls,
        },
        "repositories": [
            {
                "repo_id": repository.repo_id,
                "pairs": [
                    pair.model_dump(mode="json")
                    for pair in partial_pairs.get(repository.repo_id, [])
                ],
            }
            for repository in manifest.repositories
        ],
        "jobs": jobs,
        "failures": [
            item if isinstance(item, dict) else {"error": str(item)}
            for item in failures
        ],
    }


def _partial_batch_pairs(
    job: _JudgeJob,
    response: Any,
    weight_profile: WeightProfile,
) -> list[PairScore]:
    """Extract unambiguous pairs for a diagnostic artifact.

    This helper never makes a failed run successful. It only preserves pairs
    whose ordinal is present exactly once and maps to a supplied prediction,
    so a human can inspect or repair the remaining batch later.
    """

    if getattr(response, "status", None) != "completed":
        return []
    parsed = getattr(response, "output_parsed", None)
    try:
        validated_response = JudgeBatchResponse.model_validate(parsed)
    except ValidationError:
        return []

    expected = set(range(len(job.predictions)))
    by_index: dict[int, _ResponsePair] = {}
    duplicates: set[int] = set()
    for pair in validated_response.pairs:
        if pair.ordinal_index in by_index:
            duplicates.add(pair.ordinal_index)
        else:
            by_index[pair.ordinal_index] = pair

    result: list[PairScore] = []
    for ordinal_index in sorted(expected & set(by_index) - duplicates):
        response_pair = by_index[ordinal_index]
        prediction = job.predictions[ordinal_index]
        result.append(
            PairScore(
                prediction_id=prediction.finding_id,
                ground_truth_id=job.ground_truth.finding_id,
                scores=Scores.model_validate(response_pair.scores.model_dump()),
                weighted_score=calculate_weighted_score(
                    Scores.model_validate(response_pair.scores.model_dump()),
                    weight_profile,
                ),
                rationale=response_pair.rationale,
            )
        )
    return result


@dataclass(frozen=True)
class _JudgeJob:
    repo_id: str
    ground_truth: Finding
    predictions: list[Finding]


class JudgeBackend(Protocol):
    """Small seam between benchmark validation and a model transport."""

    def request_batch(
        self,
        job: _JudgeJob,
        *,
        model: str,
        temperature: float,
    ) -> Any:
        """Return a response with status, parsed output, model, and usage."""


@dataclass(frozen=True)
class _StreamJudgeResponse:
    status: str
    id: str | None
    model: str | None
    usage: Any
    output_parsed: JudgeBatchResponse


@dataclass
class _SdkJudgeBackend:
    """Use the existing parse path or the OAuth streaming path."""

    client: Any | None = None
    provider: OpenAIClientProvider | None = None
    auth_mode: AuthMode = DEFAULT_AUTH_MODE

    def request_batch(
        self,
        job: _JudgeJob,
        *,
        model: str,
        temperature: float,
    ) -> Any:
        client = self.client or (self.provider.get_client() if self.provider else None)
        if client is None:
            raise BenchmarkValidationError("judge backend has no OpenAI client")
        user_prompt = build_batch_prompt(job.ground_truth, job.predictions)
        if self.auth_mode == "oauth":
            return _request_oauth_batch(
                client,
                model=model,
                user_prompt=user_prompt,
                repo_id=job.repo_id,
                ground_truth_id=job.ground_truth.finding_id,
            )
        return _request_batch(
            client,
            model=model,
            temperature=temperature,
            user_prompt=user_prompt,
            repo_id=job.repo_id,
            ground_truth_id=job.ground_truth.finding_id,
        )


def _run_judge_job(
    job: _JudgeJob,
    backend: JudgeBackend,
    model: str,
    temperature: float,
) -> Any:
    logger.debug(
        "judge batch started: repo=%s, ground_truth=%s, predictions=%d",
        job.repo_id,
        job.ground_truth.finding_id,
        len(job.predictions),
    )
    response = backend.request_batch(
        job,
        model=model,
        temperature=temperature,
    )
    logger.debug(
        "judge batch completed: repo=%s, ground_truth=%s, predictions=%d",
        job.repo_id,
        job.ground_truth.finding_id,
        len(job.predictions),
    )
    return response


def _validate_judge_response(
    job: _JudgeJob,
    response: Any,
    weight_profile: WeightProfile,
) -> list[PairScore]:
    if response.status != "completed":
        raise BenchmarkValidationError(
            "judge response was not completed: "
            f"repository={job.repo_id!r}, "
            f"ground_truth_id={job.ground_truth.finding_id!r}, "
            f"status={response.status!r}"
        )
    parsed = response.output_parsed
    if parsed is None:
        raise BenchmarkValidationError(
            "judge response did not contain parsed structured output: "
            f"repository={job.repo_id!r}, "
            f"ground_truth_id={job.ground_truth.finding_id!r}"
        )
    try:
        validated_response = JudgeBatchResponse.model_validate(parsed)
    except ValidationError as exc:
        raise BenchmarkValidationError(
            "invalid structured judge response: "
            f"repository={job.repo_id!r}, "
            f"ground_truth_id={job.ground_truth.finding_id!r}: {exc}"
        ) from exc
    return _validate_batch_response(
        job.repo_id,
        job.ground_truth,
        job.predictions,
        validated_response,
        weight_profile,
    )


def _request_batch(
    client: Any,
    *,
    model: str,
    temperature: float,
    user_prompt: str,
    repo_id: str,
    ground_truth_id: str,
) -> Any:
    try:
        request: dict[str, Any] = {
            "model": model,
            "instructions": SYSTEM_PROMPT,
            "input": user_prompt,
            "text_format": JudgeBatchResponse,
        }
        if _supports_temperature(model):
            request["temperature"] = temperature
        return client.responses.parse(**request)
    except Exception as exc:
        from openai import OpenAIError

        if not isinstance(exc, (OpenAIError, ValidationError)):
            raise
        raise BenchmarkValidationError(
            "judge request failed: "
            f"repository={repo_id!r}, ground_truth_id={ground_truth_id!r}: {exc}"
        ) from exc


def _request_oauth_batch(
    client: Any,
    *,
    model: str,
    user_prompt: str,
    repo_id: str,
    ground_truth_id: str,
) -> _StreamJudgeResponse:
    """Run the ChatGPT plan flow with its streaming request requirements."""

    request: dict[str, Any] = {
        "model": model,
        "instructions": SYSTEM_PROMPT,
        "input": [{"role": "user", "content": user_prompt}],
        "store": False,
        "stream": True,
        "text": {
            "format": {
                "type": "json_schema",
                "name": "judge_batch_response",
                "schema": JudgeBatchResponse.model_json_schema(),
                "strict": True,
            }
        },
    }
    try:
        stream = client.responses.create(**request)
        text_parts: list[str] = []
        completed_response: Any | None = None
        stream_context = stream if hasattr(stream, "__enter__") else nullcontext(stream)
        with stream_context as events:
            for event in events:
                event_type = getattr(event, "type", None)
                if event_type == "response.output_text.delta":
                    delta = getattr(event, "delta", "")
                    if isinstance(delta, str):
                        text_parts.append(delta)
                elif event_type == "response.failed":
                    error = getattr(getattr(event, "response", None), "error", None)
                    code = getattr(error, "code", None) or "unknown_error"
                    raise BenchmarkValidationError(
                        "OAuth judge response failed: "
                        f"repository={repo_id!r}, ground_truth_id={ground_truth_id!r}, "
                        f"code={code!r}"
                    )
                elif event_type == "response.completed":
                    completed_response = getattr(event, "response", None)
        if completed_response is None:
            raise BenchmarkValidationError(
                "OAuth judge stream ended without response.completed: "
                f"repository={repo_id!r}, ground_truth_id={ground_truth_id!r}"
            )
        response_text = "".join(text_parts)
        if not response_text:
            response_text = getattr(completed_response, "output_text", "") or ""
        parsed = JudgeBatchResponse.model_validate(json.loads(response_text))
        return _StreamJudgeResponse(
            status="completed",
            id=getattr(completed_response, "id", None),
            model=getattr(completed_response, "model", model),
            usage=getattr(completed_response, "usage", None),
            output_parsed=parsed,
        )
    except BenchmarkValidationError:
        raise
    except Exception as exc:
        raise BenchmarkValidationError(
            "OAuth judge request failed: "
            f"repository={repo_id!r}, ground_truth_id={ground_truth_id!r}: {exc}"
        ) from exc


def _supports_temperature(model: str) -> bool:
    """Return whether the OpenAI Responses API accepts temperature for this model family."""

    normalized = model.lower()
    return not normalized.startswith(("gpt-5", "o1", "o3", "o4"))


def _usage_payload(usage: Any) -> dict[str, int | None]:
    """Normalize SDK usage while allowing OAuth streams without usage data."""

    return {
        name: (
            value
            if type(value) is int and value >= 0
            else None
        )
        for name in ("input_tokens", "output_tokens", "total_tokens")
        for value in [getattr(usage, name, None)]
    }


def _validate_batch_response(
    repo_id: str,
    ground_truth: Finding,
    predictions: list[Finding],
    response: JudgeBatchResponse,
    weight_profile: WeightProfile,
) -> list[PairScore]:
    expected = set(range(len(predictions)))
    by_index: dict[int, _ResponsePair] = {}
    duplicates: set[int] = set()
    for pair in response.pairs:
        if pair.ordinal_index in by_index:
            duplicates.add(pair.ordinal_index)
        by_index[pair.ordinal_index] = pair

    actual = set(by_index)
    missing = sorted(expected - actual)
    unknown = sorted(actual - expected)
    if missing or unknown or duplicates:
        raise BenchmarkValidationError(
            "invalid judge batch ordinal indexes: "
            f"repository={repo_id!r}, ground_truth_id={ground_truth.finding_id!r}, "
            f"missing={missing!r}, unknown={unknown!r}, duplicates={sorted(duplicates)!r}"
        )

    result: list[PairScore] = []
    for ordinal_index, prediction in enumerate(predictions):
        response_pair = by_index[ordinal_index]
        scores = Scores.model_validate(response_pair.scores.model_dump())
        result.append(
            PairScore(
                prediction_id=prediction.finding_id,
                ground_truth_id=ground_truth.finding_id,
                scores=scores,
                weighted_score=calculate_weighted_score(scores, weight_profile),
                rationale=response_pair.rationale,
            )
        )
    return result


def _finding_payload(finding: Finding) -> dict[str, Any]:
    return {
        "title": finding.title,
        "description": finding.description,
        "impact": finding.impact,
        "vulnerable_code": [
            item.model_dump(mode="json", exclude_none=True)
            for item in finding.vulnerable_code
        ],
        "mitigation": finding.mitigation,
    }


def _validate_options(
    model: str,
    batch_size: int,
    temperature: float,
    max_concurrency: int,
    auth_mode: AuthMode,
) -> None:
    if not isinstance(model, str) or not model.strip():
        raise BenchmarkValidationError("model must be a non-empty string")
    if isinstance(batch_size, bool) or not isinstance(batch_size, int) or batch_size <= 0:
        raise BenchmarkValidationError("batch_size must be a positive integer")
    if isinstance(temperature, bool) or not isinstance(temperature, (int, float)):
        raise BenchmarkValidationError("temperature must be a finite number")
    if not math.isfinite(float(temperature)):
        raise BenchmarkValidationError("temperature must be a finite number")
    if isinstance(max_concurrency, bool) or not isinstance(max_concurrency, int) or max_concurrency <= 0:
        raise BenchmarkValidationError("max_concurrency must be a positive integer")
    if auth_mode not in ("oauth", "api-key"):
        raise BenchmarkValidationError(f"unsupported judge auth mode: {auth_mode!r}")
