#!/usr/bin/env python3
"""Convert SmartAuditFlow final findings to the evaluator PredictionCase shape."""

import argparse
import json
import re
from pathlib import Path


MISSING_MITIGATION = "Not provided in SmartAuditFlow output."


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-result", type=Path, required=True)
    parser.add_argument("--snippet-manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--detector-version", default="smartauditflow-codex-gateway-smoke-v1")
    parser.add_argument("--llm-model", default="openai-codex/gpt-5.6-luna")
    args = parser.parse_args()

    raw = json.loads(args.raw_result.read_text(encoding="utf-8"))
    manifest = json.loads(args.snippet_manifest.read_text(encoding="utf-8"))
    source_path = manifest["input_files"][0]
    source_root = Path(manifest["repo_root"])
    contract_names = manifest.get("contracts", [])
    function_names = manifest.get("functions", [])

    raw_findings = raw.get("Findings", raw.get("findings", [])) or []
    predictions = []
    for index, item in enumerate(raw_findings, 1):
        if not isinstance(item, dict):
            continue
        title = str(item.get("Issue") or item.get("title") or "Untitled SmartAuditFlow finding").strip()
        description = str(item.get("Description") or item.get("description") or "Not provided in SmartAuditFlow output.").strip()
        impact = str(item.get("Impact") or item.get("impact") or "Not provided in SmartAuditFlow output.").strip()
        location = str(item.get("Location") or item.get("location") or "")
        vulnerable_code = []

        # Only map locations actually stated by SmartAuditFlow. Do not use the
        # benchmark's ground truth to fill or repair a predicted location.
        explicit_function = re.search(
            r"\bfunction\s+([A-Za-z_$][\w$]*)\s*\(", location, flags=re.IGNORECASE
        )
        if not explicit_function:
            explicit_function = re.search(
                r"\b(?:in|at)\s+([A-Za-z_$][\w$]*)\s*\(", location, flags=re.IGNORECASE
            )
        matched_function = explicit_function.group(1) if explicit_function else None
        if matched_function not in function_names:
            matched_function = None
        if not matched_function:
            # Fall back to the earliest explicitly mentioned source symbol;
            # affected downstream functions listed later in the location text
            # must not replace the finding's primary code location.
            candidates = [
                (match.start(), name)
                for name in function_names
                for match in re.finditer(rf"(?<![\w$]){re.escape(name)}(?![\w$])", location)
            ]
            matched_function = min(candidates)[1] if candidates else None
        matched_contract = next(
            (name for name in contract_names if re.search(rf"(?<![\w$]){re.escape(name)}(?![\w$])", location)),
            None,
        )
        if matched_contract is None and len(contract_names) == 1:
            matched_contract = contract_names[0]
        if matched_function and matched_contract:
            line_match = re.search(
                r"(?:lines?\s*)?(\d+)\s*(?:-|–|to)\s*(\d+)|(?:line\s*)(\d+)",
                location,
                flags=re.IGNORECASE,
            )
            start_line = end_line = None
            if line_match:
                if line_match.group(1):
                    start_line, end_line = int(line_match.group(1)), int(line_match.group(2))
                else:
                    start_line = end_line = int(line_match.group(3))
                # SmartAuditFlow sees the snippet's one-line file marker; map
                # its line numbers back to the original file where possible.
                offset = int(manifest.get("snippet_line_offset", 0))
                start_line, end_line = start_line - offset, end_line - offset
                total = int(manifest.get("source_line_count", 0))
                if start_line < 1 or end_line < start_line or end_line > total:
                    start_line = end_line = None
            vulnerable_code.append({
                "file": source_path,
                "contract": matched_contract,
                "function": matched_function,
                "start_line": start_line,
                "end_line": end_line,
            })

        prediction = {
            "finding_id": str(item.get("finding_id") or f"SAF-{index:03d}"),
            "title": title,
            "description": description,
            "impact": impact,
            "vulnerable_code": vulnerable_code,
            "mitigation": str(item.get("Mitigation") or item.get("mitigation") or MISSING_MITIGATION),
        }
        if item.get("Severity") or item.get("severity"):
            prediction["severity"] = str(item.get("Severity") or item.get("severity"))
        predictions.append(prediction)

    case = {
        "repo_id": manifest["repo_id"],
        "detector_metadata": {
            "detector_version": args.detector_version,
            "llm_model": args.llm_model,
        },
        "predictions": predictions,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(case, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "repo_id": case["repo_id"], "prediction_count": len(predictions)}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
