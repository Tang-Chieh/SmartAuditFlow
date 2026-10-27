# SmartAuditFlow dataset inputs — pilot-v1

This folder contains deterministic plain-text Solidity bundles for the 24 repos whose IDs appear in `prototype-hound/dataset/downstream-stage1/pilot-v1/ground_truth/`. The script reads ground-truth **filenames only** to select repo IDs; it never reads or copies ground-truth contents.

## What is included

- 1487 Solidity source files in 24 bundles.
- All source commits were checked against the dataset `metadata.json` resolved commit.
- Source bodies, import lines, pragma lines, and file boundaries are preserved. Bundles are text prompts, not compilable flattened `.sol` files.
- Files are packed in deterministic relative-path order up to 750,000 rough tokens per bundle (`ceil(chars / 4)`). This estimate is not the GPT-5.6 Luna tokenizer.
- Excluded Solidity files: 393; each path and reason is recorded per repo in `manifest.json`.
- Oversized bundles: 0. Individual files are never split.

## Exclusion policy

Generated/build directories (`.git`, `node_modules`, `out`, `cache`, `artifacts`, `build`, `dist`, `coverage`, `broadcast`, `typechain-types`) and obvious test/mock/fixture/vendor directory components are excluded by path; Foundry `*.t.sol` files are excluded. These are mechanical path rules, not manual code review. Imported source dependencies that fall under excluded paths are not inlined; review `imports` and excluded-file manifests before claiming complete dependency context.

## Files

- `dataset_manifest.json`: scope, totals, per-repo summary.
- `<repo-id>/manifest.json`: exact source commit, included/excluded files, bundle files, and line mapping.
- `<repo-id>/bundles/bundle-NNNN.txt`: input text; each source segment has `BEGIN/END SOURCE FILE` markers.

No SmartAuditFlow workflow or LLM Judge was run during preparation.
