# Benchmark Evaluation

`src/benchmark_eval/` 提供統一的 canonical Evaluation interface。它接收
detector output 與已驗證的 Ground Truth，執行 LLM Judge、計算 deterministic
metrics，並產生標準化的 Evaluation artifacts。

## Quick start：先完成 OAuth login

本指南使用 OAuth 作為 LLM Judge 的 authentication。從 repository root 執行：

```bash
uv run python scripts/login_openai_oauth.py
```

這個 script 會開啟 ChatGPT OAuth authorization flow，將取得的 credential
保存到 local credential file，讓 evaluator 後續可以取得或 refresh judge 所需的
access token。

完成 login 後，執行 repository 內建的 smoke test：

```bash
uv run python -m src.benchmark_eval \
  --ground-truth-dir examples/benchmark_eval/price-manipulation-smoke/ground_truth \
  --predictions-dir examples/benchmark_eval/price-manipulation-smoke/predictions \
  --output-dir output/benchmark-eval-smoke \
  --auth-mode oauth
```

這個 command 會真的呼叫 LLM Judge，因此會消耗 configured quota。預設設定為：

- judge model：`gpt-5.6-luna`
- authentication：OAuth
- weight profile：`end-to-end-v2`
- temperature：`0`
- batch size：`10`
- max concurrency：`4`

如需使用其他 judge model，可以設定 `OPENAI_JUDGE_MODEL`；如需指定其他
credential file，可以傳入 `--oauth-credential-file`。

`--ground-truth-dir` 是 optional；如果省略，default 為：

```text
dataset/downstream-stage1/pilot-v1/ground_truth
```

這個 default 是 repository 內正式的 `pilot-v1` Ground Truth dataset。若要
使用其他 dataset，可以明確傳入 `--ground-truth-dir` 覆寫。`--predictions-dir`
與 `--output-dir` 沒有 default，仍然必須明確指定，因為 predictions 通常來自
某一次 detector run。

上面的 smoke test 刻意明確指定 `examples/.../ground_truth`，因為它使用
`example-repo`，需要和同一個 example directory 下的 predictions 配對。

## 如何理解統一 interface

`benchmark_eval` 不負責產生 detector findings。Detector 或 pipeline wrapper
應先將自己的 output 轉成 canonical input contract，再交給
`benchmark_eval` 統一處理：

```text
Detector output ──> PredictionCase ──┐
                                     ├── repo_id 配對
Ground Truth ────> GroundTruthCase ──┘
                                           │
                                           ▼
                                   benchmark_eval
                                           │
                    ┌──────────────────────┼──────────────────────┐
                    ▼                      ▼                      ▼
                LLM Judge          deterministic metrics    Evaluation artifacts
```

這個 boundary 的重點是：上游只負責準備 canonical inputs；matching、LLM
judging、metrics 與 artifact generation 都由這個統一 interface 負責。

## Input contract

最基本的 input directory 結構如下：

```text
ground_truth/
└── <repo_id>.json

predictions/
└── <repo_id>.json
```

### `PredictionCase`

每個 prediction file 必須包含 `repo_id`、detector provenance，以及
`predictions`：

```json
{
  "repo_id": "example-repo",
  "detector_metadata": {
    "detector_version": "example-detector-v1",
    "llm_model": "example-detector"
  },
  "predictions": [
    {
      "finding_id": "P-EXAMPLE-001",
      "title": "AMM spot price can be manipulated during redemption",
      "description": "The redemption path trusts the current AMM spot price.",
      "vulnerable_code": [
        {
          "file": "src/Pool.sol",
          "contract": "Pool",
          "function": "redeem",
          "start_line": 42,
          "end_line": 48
        }
      ],
      "verdict": "verified"
    }
  ]
}
```

`verdict` 是 optional。若 predictions directory 的 findings 都有此欄位，
`benchmark_eval` 會建立 annotated Evaluation；允許的值是 `verified` 與
`needs_review`。若整個 directory 都沒有此欄位，則維持 legacy Evaluation。
同一個 directory 不允許混用兩種 shape。`rejected` findings 不應寫入
`predictions`。

### `GroundTruthCase`

每個 ground-truth file 必須包含相同的 `repo_id` 與 `ground_truth` findings。
被選入 Evaluation 的每個 finding 都必須先通過 human review，並標記為
`review_status: "gold_verified"`：

```json
{
  "repo_id": "example-repo",
  "ground_truth": [
    {
      "finding_id": "H-EXAMPLE-001",
      "title": "Spot price controls redemption",
      "review_status": "gold_verified"
    }
  ]
}
```

### Input matching rules

- `repo_id` 是 `PredictionCase` 與 `GroundTruthCase` 的 join key。
- 未傳入 `--finding` 時，prediction directory 中的 repositories 與 Ground Truth
  findings 都會納入 Evaluation。
- `--repo-id REPO_ID` 可重複指定，只評估列出的 repositories 中的全部 findings。
- `--finding REPO_ID:FINDING_ID` 可重複指定，只評估列出的 repository/finding
  組合；同一個 repository 可指定多筆 findings。
- `--repo-id` 與 `--finding` 不可在同一個 run 混用。需同時使用兩種篩選時，
  請拆成不同 runs。
- Python caller 也可使用 `evaluate_directory(repo_ids=...)` 篩選完整 repositories。
- 每個選取的 prediction 都必須有 matching ground truth；缺少時會被拒絕。
- Extra ground-truth cases 可以存在，但不會被選入 Evaluation。
- Selected ground-truth findings 若不是 `gold_verified`，會被拒絕。
- 同一次 Evaluation 中的 prediction files 必須有一致的 detector metadata。

例如，同一次只重新評估 `2021-11-malt / M-25`、`2021-11-malt / M-30` 與
`2021-12-vader / H-04`：

```bash
uv run python -m src.benchmark_eval \
  --ground-truth-dir dataset/downstream-stage1/pilot-v1/ground_truth \
  --predictions-dir output/price-manipulation-auditor-3cc6f60/predictions \
  --output-dir output/price-manipulation-repair/three-findings \
  --finding 2021-11-malt:M-25 \
  --finding 2021-11-malt:M-30 \
  --finding 2021-12-vader:H-04 \
  --judge-model gpt-5.6-luna \
  --batch-size 1 \
  --max-concurrency 1 \
  --auth-mode oauth
```

這會產生只包含上述三筆 ground truths 的 subset manifest 與 Judge artifact；
second run 的 `manifest_sha256` 只對應這個 subset，不能直接取代 first run 的
artifact。

完整可執行的 input example 位於：

```text
examples/benchmark_eval/price-manipulation-smoke/
├── ground_truth/example-repo.json
└── predictions/example-repo.json
```

## Evaluation outputs

Smoke test 的 artifacts 會寫入被 Git ignore 的 `output/` directory：

```text
output/benchmark-eval-smoke/
├── manifest.json
├── judge_artifact.json
├── report.json
└── report.md
```

如果 LLM Judge response 完成但未通過 batch validation，pipeline 仍會保留
`manifest.json`，並另外寫入：

```text
output/benchmark-eval-smoke/
├── manifest.json
├── judge_artifact_fail.json
└── verification_summary.json  # 若 caller 提供 verification summary
```

`judge_artifact_fail.json` 會保存每個 Judge job 的 structured response、預期的
`ordinal_index`、validation error 與目前可安全重建的 partial pairs。它不是
自動接受的 canonical artifact；人工確認或修補後，仍必須通過 artifact
completeness validation。

- `manifest.json`：validated input 與 detector metadata
- `judge_artifact.json`：LLM Judge 的 canonical results
- `report.json`：metrics 與最終 Evaluation summary。Legacy input 產生
  `report_version=0.2`，以 top-level `corpus_metrics` 與 `repositories` 表示。
  Annotated input 產生 `report_version=0.3`，metrics 位於
  `prediction_views.verified-only`、`prediction_views.verified+needs_review`、
  `prediction_views.needs_review-only`；不會放置 top-level corpus metrics 或
  repositories，避免 consumer 把某一個 view 誤當成唯一結果。
- 若由 price-manipulation auditor 提供既有 `verification-results.json` 的
  summary，`report.json` 會額外包含 `verification_summary`，記錄
  `verified`、`needs_review`、`rejected` 與 `out-of-scope` 的數量；此 metadata
  不會改變 manifest 或 LLM Judge 的 matching input。
- `report.md`：由 `report.json`、`manifest.json` 與 `judge_artifact.json` 產生的
  deterministic、human-readable report。Rendering 不會再次發送 judge request
  或重新計算 metrics；內容包含 corpus 與 repository summaries、Evaluation 與
  judge configuration、matched finding scores、judge rationales、unmatched
  findings，以及 canonical JSON artifacts 的 links。

### 使用既有 Judge artifact 產生 report

`--report-only` 從 `--output-dir` 讀取既有的 `manifest.json` 和
`judge_artifact.json`，驗證後重新產生同一目錄中的 `report.json` 和
`report.md`。報告檔若已存在會被覆寫；輸入檔不會被修改。這個 mode 不會建立
LLM client 或發送 Judge request：

```bash
uv run python -m src.benchmark_eval \
  --report-only \
  --output-dir output/benchmark-eval-smoke
```

`--output-dir` 必須已存在且同時包含 `manifest.json` 與
`judge_artifact.json`。驗證會檢查 artifact 的 `manifest_sha256` 是否對應該
manifest、repository 和 pairwise score 是否符合完整的 prediction/ground-truth
配對矩陣，以及配對與分數是否有效。若缺少輸入或驗證失敗，report 不會被更新。

### 人工修復失敗的 Judge artifact

Judge generation 失敗時只會寫出 `judge_artifact_fail.json` 診斷資料，不會寫出
canonical `judge_artifact.json`。人工修復時，先保留 first run 的
`manifest.json`，再把失敗診斷整理成 canonical artifact：

1. 若失敗 artifact 只有格式錯誤且資料完整，修正格式、移除診斷用欄位，整理成
   `judge_artifact.json`。
2. 若部分 ground truths 缺少 pairwise scores，可用重複的 `--finding` 在另一個
   output directory 重跑這些 findings。
3. 從 second run artifact 取出目標 findings 的完整 pair records（含 scores 和
   rationale），補入 first run 診斷資料。對同一目標 finding，若已有 partial pairs，
   以 second run 的完整 pair records 取代；保留 first run 的 manifest hash、
   judge configuration 與其他 findings 的 pairs，並整理成 canonical
   `judge_artifact.json`。不要用 subset artifact 的 manifest hash 取代 first run
   的 hash。
4. 將整理好的 `judge_artifact.json` 放回 first run output directory，再對該目錄執行
   `--report-only`。它會檢查原始 manifest 所需的所有配對都齊全且有效後，重產報告。

Pair record 的 key 是 `(repo_id, prediction_id, ground_truth_id)`。合併時需避免
重複或遺漏配對；若修復後 artifact 不符合 first run manifest 的完整矩陣，
`--report-only` 會拒絕產生報告。

## Python API

如果 caller 已經準備好 canonical input，可以直接使用
`evaluate_directory`：

```python
from src.benchmark_eval import evaluate_directory

result = evaluate_directory(
    ground_truth_dir="ground_truth",
    predictions_dir="predictions",
    output_dir="output/evaluation",
    finding_selections=[("example-repo", "H-EXAMPLE-001")],
)
```

省略 `config` 或傳入 `config=None` 時，會使用 `benchmark_eval` defaults。
Detector-specific wrapper 應負責準備 `PredictionCase` 與
`GroundTruthCase`，不要自行重複實作 judge configuration 或 Evaluation
execution。

## Workflow logs

CLI workflows 會將簡潔的 lifecycle logs 寫到 `stderr`，正常 command summary
則寫到 `stdout`：

```text
[benchmark_eval] evaluation started: repositories=1, model=gpt-5.6-luna, auth=oauth
[benchmark_eval] judge plan: repositories=1, predictions=1, jobs=1, batch_size=10, concurrency=4
[benchmark_eval] judge progress: completed=1/1
[benchmark_eval] evaluation completed: repositories=1, output=...
```

設定 `SCAR_LOG_LEVEL=DEBUG` 可以查看 per-batch details 與 OAuth expiration
checks；refresh events 會以 `INFO` 記錄。Token values、authorization headers
與 prompts 永遠不會寫入 logs。
