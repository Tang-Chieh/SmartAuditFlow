# SmartAuditFlow Price-Manipulation Pilot — 3 Repositories

## Summary

Three representative dataset repositories were analyzed with the price-manipulation-focused SmartAuditFlow workflow, then evaluated by the project's LLM Judge against the selected, verified ground truths.

| Repository | SmartAuditFlow predictions | Ground-truth findings | Judge matches (threshold ≥ 0.50) | Repository soft F1 |
|---|---:|---:|---:|---:|
| `2023-06-real-wagmi` | 2 | 1 | 1 | 0.667 |
| `2023-04-blueberry` | 0 | 1 | 0 | 0.000 |
| `2024-03-woofi-swap` | 3 | 1 | 0 | 0.000 |
| **Total / macro** | **5** | **3** | **1 of 3** | **0.222 macro soft F1** |

The pooled soft F1 is **0.250**. One prediction matched a ground-truth finding at a weighted score of **1.00**. WOOFi Swap's closest prediction scored **0.45**, just below the evaluator's **0.50** acceptance threshold, so it was not counted as a match.

## Run configuration

- SmartAuditFlow: modified five-node workflow with price-manipulation-focused prompts and direct `PredictionCase` output.
- Model: `openai-codex/gpt-5.6-luna` through the local Codex OAuth gateway (`http://127.0.0.1:4000/v1`); no OpenAI API key was used.
- Audit task cap: 12 per repository. Each workflow completed all five nodes.
- Input: one prepared Solidity bundle per repository; ground truth was **not** included in SmartAuditFlow's input.
- Judge: the project's `benchmark-judge-v3`, model `openai-codex/gpt-5.6-luna`, temperature 0, batch size 10, concurrency 1.
- Scoring: `end-to-end-v2` weights — R 0.40, L 0.20, I 0.20, M 0.20; match threshold 0.50.
- Verified ground truth: one finding per repo (`H-3`, `H-4`, `H-1` respectively).

## Per-repository results

### `2023-06-real-wagmi`

SmartAuditFlow returned two predictions. `SAF-001` — “Spot-price manipulation affects Multipool deposit pricing and LP issuance” — matched ground truth `H-3` with **R/L/I/M = 4/4/4/4**, weighted score **1.00**. Judge rationale: it correctly identified attacker-manipulable Uniswap V3 `slot0` spot pricing in reserve valuation, deposit optimization, and LP issuance, and proposed TWAP/independent pricing and deviation checks. `SAF-002` was not matched; it described a separate Dispatcher fee-withdrawal exploit chain.

### `2023-04-blueberry`

SmartAuditFlow completed but returned **zero predictions**. Ground-truth finding `H-4` remained unmatched. Since there were no prediction/ground-truth pairs, the Judge made no model call for this repository.

### `2024-03-woofi-swap`

SmartAuditFlow returned three predictions; none reached the match threshold. The closest was `SAF-002` — “Rebate redemption can be favorably manipulated through WOOFi spot pricing” — with **R/L/I/M = 2/3/1/1**, weighted score **0.45**. It identified the relevant `_sellBase`/`_sellQuote` path, but did not fully capture the ground truth's split-swap compounding mechanism, missing independent Chainlink anchor, and flash-loan-assisted pool-drain impact. The other predictions scored **0.40** and **0.45** and also remained unmatched. Ground-truth finding `H-1` was therefore not counted as found.

## Evaluation interpretation

This is a small pilot on three selected repositories, not a measure of full-dataset performance. The result shows one exact Judge match, one repo with no generated candidate, and one near-threshold but semantically incomplete WOOFi candidate. “Completed” means the workflow ran to completion; it does **not** mean the analysis was correct or exhaustive. LLM Judge scores are model-based evaluation results, not independent security verification.

## Output artifacts

- `predictions/` — the three validated `PredictionCase` inputs used by the evaluator.
- `llm-judge/manifest.json` — assembled evaluation input.
- `llm-judge/judge_artifact.json` — per-pair Judge component scores and rationales.
- `llm-judge/report.json` — canonical report emitted by the benchmark evaluator.
- `2023-06-real-wagmi/workflow/`, `2023-04-blueberry/workflow/`, `2024-03-woofi-swap/workflow/` — each repo's raw SmartAuditFlow result, generated Markdown audit output, `PredictionCase`, and run manifest.

**Report format note:** the benchmark evaluator in this checkout writes its canonical evaluation report as JSON (`report.json`). This `report.md` is a human-readable rendering of that run's JSON report and Judge artifact; it does not replace or alter the evaluator's JSON output.
