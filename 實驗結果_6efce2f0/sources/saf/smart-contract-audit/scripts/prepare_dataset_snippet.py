#!/usr/bin/env python3
"""Create a provenance-preserving, single-Solidity-file audit snippet."""

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path


def git_commit(root: Path) -> str | None:
    try:
        return subprocess.check_output(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-id", required=True)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--source-file", required=True, help="Solidity path relative to repo root")
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    root = args.repo_root.resolve()
    source_path = (root / args.source_file).resolve()
    if not source_path.is_relative_to(root):
        parser.error("source file must be inside repo root")
    if source_path.suffix.lower() != ".sol" or not source_path.is_file():
        parser.error("source file must be an existing .sol file")

    source = source_path.read_text(encoding="utf-8")
    relative_path = source_path.relative_to(root).as_posix()
    contracts = re.findall(r"\b(?:contract|library|interface)\s+([A-Za-z_$][\w$]*)", source)
    functions = re.findall(r"\bfunction\s+([A-Za-z_$][\w$]*)\s*\(", source)
    imports = re.findall(r"\bimport\s+(?:[^;]*?\s+from\s+)?['\"]([^'\"]+)['\"]\s*;", source)

    # The one-line marker makes the source path visible to the auditor. The
    # manifest records the resulting offset so reported line numbers map back.
    marker = f"// File: {relative_path}\n"
    snippet = marker + source
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "code_snippet.sol.txt").write_text(snippet, encoding="utf-8")

    manifest = {
        "repo_id": args.repo_id,
        "repo_root": str(root),
        "repo_commit": git_commit(root),
        "input_files": [relative_path],
        "source_sha256": hashlib.sha256(source.encode("utf-8")).hexdigest(),
        "source_line_count": len(source.splitlines()),
        "snippet_line_offset": 1,
        "snippet_sha256": hashlib.sha256(snippet.encode("utf-8")).hexdigest(),
        "snippet_char_count": len(snippet),
        "rough_token_estimate_chars_div_4": (len(snippet) + 3) // 4,
        "contracts": contracts,
        "functions": functions,
        "imports": imports,
        "preprocessing": "single source file; source body preserved verbatim; no ground-truth text added",
    }
    (output_dir / "snippet_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps({k: manifest[k] for k in (
        "repo_id", "repo_commit", "input_files", "source_line_count",
        "snippet_char_count", "rough_token_estimate_chars_div_4", "contracts",
    )}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
