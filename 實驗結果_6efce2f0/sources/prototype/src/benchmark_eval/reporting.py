"""Stable JSON report writers for benchmark evaluations."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any

from .evaluator import EvaluationResult


def write_report(result: EvaluationResult, output: str | Path) -> Path:
    """Write the compact report and return its path."""

    # Preserve the report's intentional object order, especially repo_id as
    # the first key in each repository entry.
    return _write_json(result.report, output, sort_keys=False)


def write_pair_matrix(result: EvaluationResult, output: str | Path) -> Path:
    """Write the optional complete n×m pair matrix."""

    return _write_json(result.pair_matrix, output)


def _write_json(value: Any, output: str | Path, *, sort_keys: bool = True) -> Path:
    return write_json_atomic(value, output, sort_keys=sort_keys)


def write_json_atomic(
    value: Any, output: str | Path, *, sort_keys: bool = True
) -> Path:
    """Serialize JSON to a target without exposing a partial file."""

    path = Path(output)
    serialized = json.dumps(
        value, ensure_ascii=False, sort_keys=sort_keys, indent=2
    ) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)

    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            temporary_path = Path(handle.name)
            handle.write(serialized)
            handle.flush()
            os.fsync(handle.fileno())
        temporary_path.replace(path)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()
    return path
