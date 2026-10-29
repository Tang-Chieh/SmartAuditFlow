#!/usr/bin/env python3
"""Prepare deterministic, provenance-preserving Solidity text bundles for SmartAuditFlow.

This is an input-preparation tool only. It never reads ground-truth JSON contents,
never runs an LLM, and never modifies the source repositories.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


GENERATED_DIRS = {
    ".git", "node_modules", "out", "cache", "artifacts", "build", "dist",
    "coverage", "broadcast", "typechain-types",
}
OUT_OF_SCOPE_DIRS = {
    "test", "tests", "testing", "__tests__", "mock", "mocks", "__mocks__",
    "fixture", "fixtures", "vendor", "vendors", "third_party", "third-party",
}
IMPORT_RE = re.compile(
    r"^\s*import\s+(?:[^;]*?\s+from\s+)?['\"]([^'\"]+)['\"]\s*;",
    re.MULTILINE,
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_head(path: Path) -> str:
    return subprocess.check_output(
        ["git", "-C", str(path), "rev-parse", "HEAD"],
        stderr=subprocess.DEVNULL,
        text=True,
    ).strip()


def should_exclude(relative_path: Path) -> str | None:
    parts = [part.casefold() for part in relative_path.parts]
    generated = next((part for part in parts if part in GENERATED_DIRS), None)
    if generated:
        return f"generated_or_build_directory:{generated}"
    out_of_scope = next((part for part in parts if part in OUT_OF_SCOPE_DIRS), None)
    if out_of_scope:
        return f"out_of_scope_directory:{out_of_scope}"
    if relative_path.name.casefold().endswith(".t.sol"):
        return "foundry_test_file_suffix:.t.sol"
    return None


def wrapped_source(relative_path: str, text: str) -> str:
    begin = f"// ===== BEGIN SOURCE FILE: {relative_path} =====\n"
    body = text
    if body and not body.endswith(("\n", "\r")):
        body += "\n"
    end = f"// ===== END SOURCE FILE: {relative_path} =====\n"
    return begin + body + end


def estimated_tokens(text: str) -> int:
    """Conservative bookkeeping estimate only; not a model tokenizer."""
    return math.ceil(len(text) / 4)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ground-truth-dir", type=Path, required=True)
    parser.add_argument("--repo-metadata-root", type=Path, required=True)
    parser.add_argument("--candidate-repos-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--max-estimated-tokens", type=int, default=50_000)
    args = parser.parse_args()

    ground_truth_dir = args.ground_truth_dir.resolve()
    metadata_root = args.repo_metadata_root.resolve()
    candidate_root = args.candidate_repos_root.resolve()
    output_dir = args.output_dir.resolve()

    if not ground_truth_dir.is_dir() or not metadata_root.is_dir() or not candidate_root.is_dir():
        parser.error("ground-truth, metadata, and candidate-repo paths must all exist")
    if args.max_estimated_tokens <= 0:
        parser.error("--max-estimated-tokens must be positive")
    if output_dir.exists() and any(output_dir.iterdir()):
        parser.error(f"output directory is non-empty; refusing to overwrite: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)

    candidate_by_id = {path.name.casefold(): path for path in candidate_root.iterdir() if path.is_dir()}
    ground_truth_files = sorted(ground_truth_dir.glob("*.json"), key=lambda path: path.stem.casefold())
    if not ground_truth_files:
        parser.error("no ground-truth JSON filenames found; expected filenames to identify repo IDs")

    dataset_summary: dict[str, Any] = {
        "schema_version": "smartauditflow-input-bundles-v1",
        "repo_scope_source": "ground_truth filenames only; ground-truth contents were not read",
        "input_kind": "plain text Solidity bundles; not intended to compile as a single Solidity file",
        "bundle_target_estimated_tokens": args.max_estimated_tokens,
        "token_estimator": "ceil(character_count / 4); rough estimate, not GPT-5.6 Luna tokenizer output",
        "source_policy": {
            "included": "UTF-8 .sol files below metadata.source.working_directory, packed in sorted relative-path order",
            "preserved": ["source bodies", "import lines", "pragma lines", "file boundaries", "original source hashes"],
            "excluded_directory_components": sorted(GENERATED_DIRS | OUT_OF_SCOPE_DIRS),
            "excluded_file_rule": "*.t.sol",
            "line_mapping": "bundle manifest records bundle and original source line ranges",
        },
        "repositories": [],
    }

    for gt_path in ground_truth_files:
        repo_id = gt_path.stem
        metadata_path = metadata_root / repo_id / "metadata.json"
        if not metadata_path.is_file():
            parser.error(f"missing dataset metadata for ground-truth repo {repo_id}: {metadata_path}")
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        source = metadata.get("source", {})
        expected_commit = source.get("resolved_commit")
        working_directory = source.get("working_directory", "")
        candidate = candidate_by_id.get(repo_id.casefold())
        if candidate is None:
            parser.error(f"no candidate source repo found for {repo_id}")
        source_root = (candidate / working_directory).resolve()
        if not source_root.is_dir():
            parser.error(f"working directory for {repo_id} does not exist: {source_root}")
        try:
            actual_commit = git_head(source_root)
        except (OSError, subprocess.CalledProcessError):
            parser.error(f"cannot verify Git HEAD for {repo_id}: {source_root}")
        if expected_commit and actual_commit != expected_commit:
            parser.error(
                f"source commit mismatch for {repo_id}: expected {expected_commit}, got {actual_commit}"
            )

        repo_output = output_dir / repo_id
        bundle_dir = repo_output / "bundles"
        bundle_dir.mkdir(parents=True, exist_ok=True)
        included_files: list[dict[str, Any]] = []
        excluded_files: list[dict[str, str]] = []

        for file_path in sorted(source_root.rglob("*.sol"), key=lambda p: p.relative_to(source_root).as_posix().casefold()):
            if not file_path.is_file():
                continue
            relative = file_path.relative_to(source_root)
            reason = should_exclude(relative)
            if reason:
                excluded_files.append({"file": relative.as_posix(), "reason": reason})
                continue
            try:
                with file_path.open("r", encoding="utf-8", newline="") as handle:
                    text = handle.read()
            except UnicodeDecodeError:
                excluded_files.append({"file": relative.as_posix(), "reason": "not_valid_utf8"})
                continue
            raw = text.encode("utf-8")
            wrapped = wrapped_source(relative.as_posix(), text)
            imports = IMPORT_RE.findall(text)
            included_files.append({
                "file": relative.as_posix(),
                "sha256": sha256(raw),
                "source_bytes_utf8": len(raw),
                "source_line_count": len(text.splitlines()),
                "estimated_tokens_with_markers": estimated_tokens(wrapped),
                "imports": imports,
                "_wrapped": wrapped,
            })

        bundles: list[dict[str, Any]] = []
        current_parts: list[str] = []
        current_entries: list[dict[str, Any]] = []
        current_estimate = 0

        def flush_bundle() -> None:
            nonlocal current_parts, current_entries, current_estimate
            if not current_entries:
                return
            bundle_id = f"bundle-{len(bundles) + 1:04d}"
            bundle_text = "".join(current_parts)
            bundle_path = bundle_dir / f"{bundle_id}.txt"
            bundle_path.write_text(bundle_text, encoding="utf-8", newline="")
            bundles.append({
                "bundle_id": bundle_id,
                "path": f"bundles/{bundle_path.name}",
                "estimated_tokens": estimated_tokens(bundle_text),
                "estimated_over_target": estimated_tokens(bundle_text) > args.max_estimated_tokens,
                "files": current_entries,
            })
            current_parts = []
            current_entries = []
            current_estimate = 0

        for file_record in included_files:
            wrapped = file_record.pop("_wrapped")
            file_estimate = estimated_tokens(wrapped)
            if current_entries and current_estimate + file_estimate > args.max_estimated_tokens:
                flush_bundle()

            prefix = "".join(current_parts)
            marker_line = prefix.count("\n") + 1
            source_start_line = marker_line + 1
            source_line_count = file_record["source_line_count"]
            source_end_line = source_start_line + source_line_count - 1
            entry_record = {key: value for key, value in file_record.items() if key != "estimated_tokens_with_markers"}
            entry_record.update({
                "bundle_marker_line": marker_line,
                "bundle_source_start_line": source_start_line,
                "bundle_source_end_line": source_end_line,
            })
            current_parts.append(wrapped)
            current_entries.append(entry_record)
            current_estimate += file_estimate

            # Keep an exceptionally large source file intact and isolate it.
            if file_estimate > args.max_estimated_tokens:
                flush_bundle()

        flush_bundle()

        repo_manifest = {
            "schema_version": "smartauditflow-repo-input-v1",
            "repo_id": repo_id,
            "source_repo_dir": candidate.name,
            "working_directory": working_directory or ".",
            "source_root_relative_to_repo": working_directory or ".",
            "expected_resolved_commit": expected_commit,
            "actual_git_head": actual_commit,
            "commit_verified": not expected_commit or expected_commit == actual_commit,
            "ground_truth_content_used": False,
            "included_solidity_file_count": sum(len(bundle["files"]) for bundle in bundles),
            "excluded_solidity_file_count": len(excluded_files),
            "bundle_count": len(bundles),
            "estimated_total_bundle_tokens": sum(bundle["estimated_tokens"] for bundle in bundles),
            "bundles": bundles,
            "excluded_files": excluded_files,
        }
        write_json(repo_output / "manifest.json", repo_manifest)
        dataset_summary["repositories"].append({
            "repo_id": repo_id,
            "source_commit": actual_commit,
            "included_solidity_file_count": repo_manifest["included_solidity_file_count"],
            "excluded_solidity_file_count": len(excluded_files),
            "bundle_count": len(bundles),
            "estimated_total_bundle_tokens": repo_manifest["estimated_total_bundle_tokens"],
            "oversized_bundle_count": sum(bundle["estimated_over_target"] for bundle in bundles),
        })

    dataset_summary["repo_count"] = len(dataset_summary["repositories"])
    dataset_summary["included_solidity_file_count"] = sum(
        repo["included_solidity_file_count"] for repo in dataset_summary["repositories"]
    )
    dataset_summary["excluded_solidity_file_count"] = sum(
        repo["excluded_solidity_file_count"] for repo in dataset_summary["repositories"]
    )
    dataset_summary["bundle_count"] = sum(repo["bundle_count"] for repo in dataset_summary["repositories"])
    dataset_summary["estimated_total_bundle_tokens"] = sum(
        repo["estimated_total_bundle_tokens"] for repo in dataset_summary["repositories"]
    )
    dataset_summary["oversized_bundle_count"] = sum(
        repo["oversized_bundle_count"] for repo in dataset_summary["repositories"]
    )
    write_json(output_dir / "dataset_manifest.json", dataset_summary)

    readme = f"""# SmartAuditFlow dataset inputs — pilot-v1\n\nThis folder contains deterministic plain-text Solidity bundles for the {dataset_summary['repo_count']} repos whose IDs appear in `prototype-hound/dataset/downstream-stage1/pilot-v1/ground_truth/`. The script reads ground-truth **filenames only** to select repo IDs; it never reads or copies ground-truth contents.\n\n## What is included\n\n- {dataset_summary['included_solidity_file_count']} Solidity source files in {dataset_summary['bundle_count']} bundles.\n- All source commits were checked against the dataset `metadata.json` resolved commit.\n- Source bodies, import lines, pragma lines, and file boundaries are preserved. Bundles are text prompts, not compilable flattened `.sol` files.\n- Files are packed in deterministic relative-path order up to {args.max_estimated_tokens:,} rough tokens per bundle (`ceil(chars / 4)`). This estimate is not the GPT-5.6 Luna tokenizer.\n- Excluded Solidity files: {dataset_summary['excluded_solidity_file_count']}; each path and reason is recorded per repo in `manifest.json`.\n- Oversized bundles: {dataset_summary['oversized_bundle_count']}. Individual files are never split.\n\n## Exclusion policy\n\nGenerated/build directories (`.git`, `node_modules`, `out`, `cache`, `artifacts`, `build`, `dist`, `coverage`, `broadcast`, `typechain-types`) and obvious test/mock/fixture/vendor directory components are excluded by path; Foundry `*.t.sol` files are excluded. These are mechanical path rules, not manual code review. Imported source dependencies that fall under excluded paths are not inlined; review `imports` and excluded-file manifests before claiming complete dependency context.\n\n## Files\n\n- `dataset_manifest.json`: scope, totals, per-repo summary.\n- `<repo-id>/manifest.json`: exact source commit, included/excluded files, bundle files, and line mapping.\n- `<repo-id>/bundles/bundle-NNNN.txt`: input text; each source segment has `BEGIN/END SOURCE FILE` markers.\n\nNo SmartAuditFlow workflow or LLM Judge was run during preparation.\n"""
    (output_dir / "README.md").write_text(readme, encoding="utf-8")
    print(json.dumps({key: dataset_summary[key] for key in (
        "repo_count", "included_solidity_file_count", "excluded_solidity_file_count",
        "bundle_count", "estimated_total_bundle_tokens", "oversized_bundle_count",
    )}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
