"""Canonical JSON serialization and manifest hashes."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from .contract import CANONICAL_JSON_RULE, Manifest
from .validation import BenchmarkValidationError, load_json, validate_manifest


def canonical_json_bytes(value: Any) -> bytes:
    """Serialize JSON data using the canonical rule frozen in Phase 0."""

    try:
        serialized = json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise BenchmarkValidationError(
            f"value cannot be canonicalized with {CANONICAL_JSON_RULE}: {exc}"
        ) from exc
    return serialized.encode("utf-8")


def manifest_sha256(
    source: str | Path | Mapping[str, Any] | Manifest,
) -> str:
    """Hash a validated manifest's normalized canonical JSON representation."""

    data = _normalized_manifest_data(source)
    return hashlib.sha256(canonical_json_bytes(data)).hexdigest()


def _normalized_manifest_data(
    source: str | Path | Mapping[str, Any] | Manifest,
) -> dict[str, Any]:
    if isinstance(source, (str, Path)):
        source = load_json(source)
    manifest = validate_manifest(source)
    return manifest.model_dump(mode="json", exclude_none=True)
