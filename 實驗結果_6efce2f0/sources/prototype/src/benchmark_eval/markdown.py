"""Human-readable Markdown rendering for benchmark Evaluation reports."""

from __future__ import annotations

import os
from collections.abc import Mapping
from pathlib import Path
import tempfile
from typing import Any

from .contract import JudgeArtifact, Manifest


def render_evaluation_markdown(
    report: Mapping[str, Any],
    *,
    manifest: Manifest | Mapping[str, Any] | None = None,
    judge_artifact: JudgeArtifact | Mapping[str, Any] | None = None,
    title: str = "Benchmark Evaluation Report",
) -> str:
    """Render a deterministic, human-readable view of a benchmark report.

    ``report`` is the canonical source for all metrics and scores.  ``manifest``
    is optional and is used only to enrich finding IDs with titles and source
    locations. ``judge_artifact`` is optional and is used only for judge
    provenance such as the model and prompt version. Rendering never invokes a
    judge or recalculates Evaluation metrics.
    """

    findings = _manifest_findings(manifest)
    if report.get("prediction_views"):
        return _render_annotated_markdown(
            report,
            findings=findings,
            judge_artifact=judge_artifact,
            title=title,
        )
    corpus = _mapping(report.get("corpus_metrics"))
    judge_config = _mapping(report.get("judge_config"))
    weight_profile = _mapping(judge_config.get("weight_profile"))
    detector_metadata = _mapping(report.get("detector_metadata"))
    judge_metadata = _judge_metadata(judge_artifact)
    repositories = _sequence_of_mappings(report.get("repositories"))

    lines: list[str] = [
        f"# {_heading_text(title)}",
        "",
        "> Derived from canonical Evaluation artifacts. This report does not execute LLM requests.",
        "",
        "## Executive Summary",
        "",
    ]
    lines.extend(
        _table(
            ("Metric", "Value"),
            [
                ("Report version", report.get("report_version")),
                ("Benchmark version", report.get("benchmark_version")),
                ("Repositories", len(repositories)),
                ("Ground Truth findings", corpus.get("total_ground_truth_count")),
                ("Predictions", corpus.get("total_prediction_count")),
                ("Total matched predictions", _matched_prediction_count(repositories)),
                ("Total matched weight", _number(corpus.get("total_matched_weight"))),
                (
                    "Pooled soft precision",
                    _number(corpus.get("pooled_soft_precision")),
                ),
                ("Pooled soft recall", _number(corpus.get("pooled_soft_recall"))),
                ("Macro soft F1", _number(corpus.get("macro_soft_f1"))),
                ("Pooled soft F1", _number(corpus.get("pooled_soft_f1"))),
            ],
        )
    )

    lines.extend(["", "## Evaluation Configuration", ""])
    configuration_rows = [
        ("Matching strategy", report.get("matching_strategy")),
        ("Threshold", _number(judge_config.get("threshold"))),
        ("Weight profile", weight_profile.get("profile_id")),
        ("Judge model", judge_metadata.get("model")),
        ("Judge prompt version", judge_metadata.get("prompt_version")),
        ("Detector version", detector_metadata.get("detector_version")),
        ("Detector model", detector_metadata.get("llm_model")),
        ("Manifest SHA-256", report.get("manifest_sha256")),
    ]
    lines.extend(_table(("Field", "Value"), configuration_rows))

    lines.extend(["", "## Repository Summary", ""])
    summary_rows = []
    for repository in repositories:
        metrics = _mapping(repository.get("metrics"))
        summary_rows.append(
            (
                f"`{_inline(repository.get('repo_id'))}`",
                metrics.get("ground_truth_count"),
                metrics.get("prediction_count"),
                len(_sequence_of_mappings(repository.get("matched_pairs"))),
                _number(metrics.get("matched_weight")),
                _number(metrics.get("soft_precision")),
                _number(metrics.get("soft_recall")),
                _number(metrics.get("soft_f1")),
            )
        )
    lines.extend(
        _table(
            (
                "Repository",
                "Ground Truth",
                "Predictions",
                "Matched Predictions",
                "Matched weight",
                "Precision",
                "Recall",
                "Soft F1",
            ),
            summary_rows,
            empty_message="No repositories were evaluated.",
        )
    )

    lines.extend(["", "## Repository Details", ""])
    if not repositories:
        lines.append("No repository details are available.")
    for repository in repositories:
        lines.extend(_render_repository(repository, findings))

    lines.extend(
        [
            "",
            "## Artifacts",
            "",
            "- [manifest.json](manifest.json)",
            "- [judge_artifact.json](judge_artifact.json)",
            "- [report.json](report.json)",
            "",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def _render_annotated_markdown(
    report: Mapping[str, Any],
    *,
    findings: dict[str, dict[str, dict[str, Any]]],
    judge_artifact: JudgeArtifact | Mapping[str, Any] | None,
    title: str,
) -> str:
    """Render the three independent prediction views in an annotated report."""

    annotations = _mapping(report.get("prediction_annotations"))
    verification_summary = _mapping(report.get("verification_summary"))
    judge_config = _mapping(report.get("judge_config"))
    weight_profile = _mapping(judge_config.get("weight_profile"))
    detector_metadata = _mapping(report.get("detector_metadata"))
    judge_metadata = _judge_metadata(judge_artifact)
    prediction_views = _mapping(report.get("prediction_views"))
    view_titles = (
        ("verified-only", "Verified-only"),
        ("verified+needs_review", "Verified + Needs Review"),
        ("needs_review-only", "Needs Review-only"),
    )

    lines: list[str] = [
        f"# {_heading_text(title)}",
        "",
        "> Derived from canonical Evaluation artifacts. This report does not execute LLM requests.",
        "",
        "## Executive Summary",
        "",
    ]
    lines.extend(
        _table(
            ("Metric", "Value"),
            [
                ("Report version", report.get("report_version")),
                ("Benchmark version", report.get("benchmark_version")),
                ("Default prediction view", report.get("default_prediction_view")),
                (
                    "Available prediction views",
                    ", ".join(view_title for _view_key, view_title in view_titles),
                ),
                ("Verified predictions", annotations.get("verified")),
                ("Needs-review predictions", annotations.get("needs_review")),
                ("rejected by VERIFY", verification_summary.get("rejected")),
                ("out-of-scope", verification_summary.get("out-of-scope")),
            ],
        )
    )

    lines.extend(["", "## Evaluation Configuration", ""])
    lines.extend(
        _table(
            ("Field", "Value"),
            [
                ("Matching strategy", report.get("matching_strategy")),
                ("Threshold", _number(judge_config.get("threshold"))),
                ("Weight profile", weight_profile.get("profile_id")),
                ("Judge model", judge_metadata.get("model")),
                ("Judge prompt version", judge_metadata.get("prompt_version")),
                ("Detector version", detector_metadata.get("detector_version")),
                ("Detector model", detector_metadata.get("llm_model")),
                ("Manifest SHA-256", report.get("manifest_sha256")),
            ],
        )
    )

    lines.extend(["", "### View Comparison", ""])
    comparison_rows = []
    for view_key, view_title in view_titles:
        view = _mapping(prediction_views.get(view_key))
        corpus = _mapping(view.get("corpus_metrics"))
        comparison_rows.append(
            (
                view_title,
                corpus.get("total_prediction_count"),
                _number(corpus.get("pooled_soft_precision")),
                _number(corpus.get("pooled_soft_recall")),
                _number(corpus.get("macro_soft_f1")),
                _number(corpus.get("pooled_soft_f1")),
            )
        )
    lines.extend(
        _table(
            (
                "View",
                "Predictions",
                "Pooled Precision",
                "Pooled Recall",
                "Macro F1",
                "Pooled F1",
            ),
            comparison_rows,
        )
    )

    for view_key, view_title in view_titles:
        view = _mapping(prediction_views.get(view_key))
        corpus = _mapping(view.get("corpus_metrics"))
        repositories = _sequence_of_mappings(view.get("repositories"))
        lines.extend(["", f"## {view_title}", ""])
        lines.extend(
            _table(
                ("Metric", "Value"),
                [
                    ("Repositories", len(repositories)),
                    ("Ground Truth findings", corpus.get("total_ground_truth_count")),
                    ("Predictions", corpus.get("total_prediction_count")),
                    ("Total matched predictions", _matched_prediction_count(repositories)),
                    ("Total matched weight", _number(corpus.get("total_matched_weight"))),
                    ("Pooled soft precision", _number(corpus.get("pooled_soft_precision"))),
                    ("Pooled soft recall", _number(corpus.get("pooled_soft_recall"))),
                    ("Macro soft F1", _number(corpus.get("macro_soft_f1"))),
                    ("Pooled soft F1", _number(corpus.get("pooled_soft_f1"))),
                ],
            )
        )
        lines.extend(["", "### Repository Summary", ""])
        summary_rows = []
        for repository in repositories:
            metrics = _mapping(repository.get("metrics"))
            summary_rows.append(
                (
                    f"`{_inline(repository.get('repo_id'))}`",
                    metrics.get("ground_truth_count"),
                    metrics.get("prediction_count"),
                    len(_sequence_of_mappings(repository.get("matched_pairs"))),
                    _number(metrics.get("matched_weight")),
                    _number(metrics.get("soft_precision")),
                    _number(metrics.get("soft_recall")),
                    _number(metrics.get("soft_f1")),
                )
            )
        lines.extend(
            _table(
                (
                    "Repository",
                    "Ground Truth",
                    "Predictions",
                    "Matched Predictions",
                    "Matched weight",
                    "Precision",
                    "Recall",
                    "Soft F1",
                ),
                summary_rows,
                empty_message="No repositories were evaluated.",
            )
        )

    lines.extend(["", "## Repository Details", ""])
    for view_key, view_title in view_titles:
        view = _mapping(prediction_views.get(view_key))
        repositories = _sequence_of_mappings(view.get("repositories"))
        lines.extend([f"**{view_title}**", ""])
        if not repositories:
            lines.append("No repository details are available.")
        for repository in repositories:
            lines.extend(_render_repository(repository, findings))

    lines.extend(
        [
            "",
            "## Artifacts",
            "",
            "- [manifest.json](manifest.json)",
            "- [judge_artifact.json](judge_artifact.json)",
            "- [report.json](report.json)",
            "",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def write_evaluation_markdown(
    report: Mapping[str, Any],
    output: str | Path,
    *,
    manifest: Manifest | Mapping[str, Any] | None = None,
    judge_artifact: JudgeArtifact | Mapping[str, Any] | None = None,
    title: str = "Benchmark Evaluation Report",
) -> Path:
    """Render and atomically write a benchmark Markdown report."""

    path = Path(output)
    content = render_evaluation_markdown(
        report,
        manifest=manifest,
        judge_artifact=judge_artifact,
        title=title,
    )
    _write_text_atomic(content, path)
    return path


def _render_repository(
    repository: Mapping[str, Any],
    findings: dict[str, dict[str, dict[str, Any]]],
) -> list[str]:
    repo_id = str(repository.get("repo_id", ""))
    metrics = _mapping(repository.get("metrics"))
    lines = [
        f"### `{_inline(repo_id)}`",
        "",
    ]
    lines.extend(
        _table(
            ("Metric", "Value"),
            [
                ("Ground Truth findings", metrics.get("ground_truth_count")),
                ("Predictions", metrics.get("prediction_count")),
                ("Matched weight", _number(metrics.get("matched_weight"))),
                ("Soft precision", _number(metrics.get("soft_precision"))),
                ("Soft recall", _number(metrics.get("soft_recall"))),
                ("Soft F1", _number(metrics.get("soft_f1"))),
            ],
        )
    )

    matched_pairs = _sequence_of_mappings(repository.get("matched_pairs"))
    lines.extend(["", "#### Matched Findings", ""])
    matched_rows = []
    for pair in matched_pairs:
        ground_truth_id = str(pair.get("ground_truth_id", ""))
        prediction_id = str(pair.get("prediction_id", ""))
        scores = _mapping(pair.get("scores"))
        matched_rows.append(
            (
                _cell(
                    _finding_label(
                        ground_truth_id,
                        findings.get(repo_id, {})
                        .get("ground_truth", {})
                        .get(ground_truth_id),
                    )
                ),
                _cell(
                    _finding_label(
                        prediction_id,
                        findings.get(repo_id, {})
                        .get("predictions", {})
                        .get(prediction_id),
                    )
                ),
                _score(scores.get("R")),
                _score(scores.get("L")),
                _score(scores.get("I")),
                _score(scores.get("M")),
                _number(pair.get("weighted_score")),
            )
        )
    lines.extend(
        _table(
            ("Ground Truth", "Prediction", "R", "L", "I", "M", "Weighted"),
            matched_rows,
            empty_message="No matched findings.",
        )
    )

    for index, pair in enumerate(matched_pairs, start=1):
        lines.extend(_render_pair_details(repo_id, index, pair, findings))

    lines.extend(["", "#### Unmatched Ground Truth", ""])
    unmatched_ground_truths = [
        _cell(
            _finding_label(
                str(finding_id),
                findings.get(repo_id, {}).get("ground_truth", {}).get(str(finding_id)),
            )
        )
        for finding_id in repository.get("unmatched_ground_truths", [])
    ]
    lines.extend(_bullet_list(unmatched_ground_truths, "No unmatched Ground Truth findings."))

    lines.extend(["", "#### Unmatched Predictions", ""])
    unmatched_predictions = [
        _cell(
            _finding_label(
                str(finding_id),
                findings.get(repo_id, {}).get("predictions", {}).get(str(finding_id)),
            )
        )
        for finding_id in repository.get("unmatched_predictions", [])
    ]
    lines.extend(_bullet_list(unmatched_predictions, "No unmatched predictions."))
    lines.append("")
    return lines


def _render_pair_details(
    repo_id: str,
    index: int,
    pair: Mapping[str, Any],
    findings: dict[str, dict[str, dict[str, Any]]],
) -> list[str]:
    ground_truth_id = str(pair.get("ground_truth_id", ""))
    prediction_id = str(pair.get("prediction_id", ""))
    repository_findings = findings.get(repo_id, {})
    ground_truth = repository_findings.get("ground_truth", {}).get(ground_truth_id)
    prediction = repository_findings.get("predictions", {}).get(prediction_id)
    ground_truth_label = _finding_label(ground_truth_id, ground_truth)
    prediction_label = _finding_label(prediction_id, prediction)
    rationale = str(pair.get("rationale") or "No rationale provided.")

    lines = [
        "",
        "<details>",
        f"<summary>Pair {index}: {_inline(ground_truth_label)} ↔ {_inline(prediction_label)}</summary>",
        "",
        f"- **Ground Truth:** `{_inline(ground_truth_id)}`",
        f"- **Prediction:** `{_inline(prediction_id)}`",
        "",
    ]
    lines.extend(_render_locations("Ground Truth locations", ground_truth))
    lines.extend(_render_locations("Prediction locations", prediction))
    lines.extend(
        [
            "#### Judge rationale",
            "",
            _fenced(rationale, "text"),
            "",
            "</details>",
        ]
    )
    return lines


def _render_locations(title: str, finding: dict[str, Any] | None) -> list[str]:
    if not finding:
        return []
    locations = finding.get("vulnerable_code") or []
    if not locations:
        return []
    rows = []
    for location in locations:
        location_mapping = _mapping(location)
        rows.append(
            (
                _cell(location_mapping.get("file")),
                _cell(location_mapping.get("contract")),
                _cell(location_mapping.get("function")),
                _cell(
                    _line_range(
                        location_mapping.get("start_line"),
                        location_mapping.get("end_line"),
                    )
                ),
            )
        )
    return [f"#### {title}", ""] + _table(
        ("File", "Contract", "Function", "Lines"),
        rows,
    ) + [""]


def _manifest_findings(
    manifest: Manifest | Mapping[str, Any] | None,
) -> dict[str, dict[str, dict[str, Any]]]:
    if manifest is None:
        return {}
    raw_manifest = (
        manifest.model_dump(mode="python")
        if isinstance(manifest, Manifest)
        else manifest
    )
    result: dict[str, dict[str, dict[str, Any]]] = {}
    for repository in _sequence_of_mappings(raw_manifest.get("repositories")):
        repo_id = str(repository.get("repo_id", ""))
        result[repo_id] = {
            "ground_truth": _findings_by_id(repository.get("ground_truth")),
            "predictions": _findings_by_id(repository.get("predictions")),
        }
    return result


def _findings_by_id(value: Any) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for finding in _sequence_of_mappings(value):
        finding_id = finding.get("finding_id")
        if finding_id is not None:
            result[str(finding_id)] = finding
    return result


def _finding_label(finding_id: str, finding: dict[str, Any] | None) -> str:
    title = finding.get("title") if finding else None
    return f"{finding_id} — {title}" if title else finding_id


def _table(
    headers: tuple[str, ...],
    rows: list[tuple[Any, ...]],
    *,
    empty_message: str | None = None,
) -> list[str]:
    lines = [
        "| " + " | ".join(_cell(header) for header in headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    if not rows:
        message = empty_message or "No data."
        lines.append("| " + _cell(message) + " |" + " |" * (len(headers) - 1))
        return lines
    for row in rows:
        values = list(row) + ["—"] * max(0, len(headers) - len(row))
        lines.append("| " + " | ".join(_cell(value) for value in values[: len(headers)]) + " |")
    return lines


def _bullet_list(values: list[str], empty_message: str) -> list[str]:
    if not values:
        return [empty_message]
    return [f"- {value}" for value in values]


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _sequence_of_mappings(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _matched_prediction_count(repositories: list[Mapping[str, Any]]) -> int:
    """Count unique predictions participating in matched pairs."""

    return sum(
        len(
            {
                str(pair["prediction_id"])
                for pair in _sequence_of_mappings(repository.get("matched_pairs"))
                if pair.get("prediction_id") is not None
            }
        )
        for repository in repositories
    )


def _judge_metadata(
    judge_artifact: JudgeArtifact | Mapping[str, Any] | None,
) -> Mapping[str, Any]:
    if judge_artifact is None:
        return {}
    raw_artifact = (
        judge_artifact.model_dump(mode="python")
        if isinstance(judge_artifact, JudgeArtifact)
        else judge_artifact
    )
    return _mapping(raw_artifact.get("judge_metadata"))


def _number(value: Any) -> str:
    if value is None:
        return "—"
    try:
        return f"{float(value):.4f}"
    except (TypeError, ValueError):
        return _cell(value)


def _score(value: Any) -> str:
    if value is None:
        return "—"
    return f"{value}/4"


def _line_range(start: Any, end: Any) -> str:
    if start is None and end is None:
        return "—"
    if start == end or end is None:
        return str(start)
    return f"{start}–{end}"


def _cell(value: Any) -> str:
    if value is None or value == "":
        return "—"
    return str(value).replace("|", r"\|").replace("\n", "<br>")


def _inline(value: Any) -> str:
    return str(value).replace("`", r"\`").replace("\n", " ")


def _heading_text(value: Any) -> str:
    return str(value).replace("\n", " ").strip() or "Benchmark Evaluation Report"


def _fenced(value: str, language: str) -> str:
    longest = max(
        (len(run) for run in value.split() if run and set(run) == {"`"}),
        default=0,
    )
    fence = "`" * max(3, longest + 1)
    return f"{fence}{language}\n{value}\n{fence}"


def _write_text_atomic(content: str, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=output.parent,
            prefix=f".{output.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            temporary_path = Path(handle.name)
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        temporary_path.replace(output)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()


__all__ = ["render_evaluation_markdown", "write_evaluation_markdown"]
