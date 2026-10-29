# PR #1 Merge 後完整實驗結果

本目錄保存 [PR #1](https://github.com/Tang-Chieh/SmartAuditFlow/pull/1) merge 後重新執行的 SmartAuditFlow 與 LLM Judge 結果，不是較早的 shared-scope-only 實驗。

## 固定版本與設定

| 項目 | 設定 |
| --- | --- |
| SmartAuditFlow | `6efce2f0e92efe2e26397a6e832f1b533a27480d`（PR #1 merge commit） |
| 官方 Judge / Evaluator / Markdown renderer | `fffuuuming/prototype` 的 `e46fc2702a1c6506f9a56af00990f8218648f697`（開始實驗時取得的最新 SCAR） |
| Detector 與 Judge model | `openai-codex/gpt-5.6-luna` |
| 模型連線 | 本機 OpenAI-compatible gateway，轉送至使用者已授權的 Codex OAuth；不是付費 API fallback |
| Dataset | 23 repos，排除 `margintrading`；42 筆 ground truth |
| 輸入 | 既有 `dataset-inputs/`；小於等於 240k estimated tokens 使用單一 bundle，超過則用既有約 50k estimated-token bundles |
| Token estimate | `ceil(chars/4)`，不是精確 tokenizer 計數 |
| Workflow | Initial Analysis → Audit Plan → Parameter Extractor → Iteration → Format Converter |
| 任務上限 | 每個 bundle 最多 12 個；不修改 merge commit 的 prompt 或分析邏輯 |
| Judge 設定 | `end-to-end-v2`，threshold 0.5，greedy matching，temperature 0，batch size 10，concurrency 1 |

完整 source snapshots 在 `sources/`，prompt、輸入與 ground truth hashes 在 [provenance.json](provenance.json)。Ground truth 僅供 evaluator 使用，沒有傳入 SmartAuditFlow prompts。

## 結果

| 指標 | 結果 |
| --- | ---: |
| 完成 repos | 23 / 23 |
| 最終採用輪次的成功任務 | 408 / 408 |
| 最終採用輪次的 OutputWarnings | 0 |
| Predictions | 52 |
| Matched Predictions（通過 matching threshold） | 19 |
| Total matched weight | 18.45 |
| Pooled soft precision | 0.3548 |
| Pooled soft recall | 0.4393 |
| Pooled soft F1 | 0.3926 |
| Macro soft F1 | 0.2980 |

請優先閱讀 **[官方 report.md](llm-judge/report.md)**。這份檔案由上述固定版本的官方 `evaluate_directory()` 流程自動產生，不是人工整理的 report。Judge 的原始評分與 rationale 在 [judge_artifact.json](llm-judge/judge_artifact.json)。Matched Predictions 是 benchmark matching 結果，不是獨立 exploit 驗證。

## 重試與限制

- 五個 bundle 曾重試：`2021-08-notional`、`2022-01-behodler`、`2022-09-notional`、`2023-06-real-wagmi`、`2023-06-tokemak`。
- 原因為單次模型呼叫逾時，或 gateway 回覆 `usage_limit_reached`。配額恢復後，以原模型與原程式接續，沒有切換模型或帳戶。
- 每個 bundle 最多三次嘗試，採用首次滿足完整執行檢查的輪次；沒有根據 finding 數或 Judge 分數選取輪次。
- `408/408` 與 `0 warnings` 只描述最終採用輪次，不表示此前從未失敗。失敗輪次保存在 `raw/.../attempt-*/`，採用輪次另存為 `raw/.../workflow/`。
- 跨 bundle 只移除完全相同的 predictions，沒有使用 LLM 做語意去重。

## 檔案索引

```text
實驗結果_6efce2f0/
├── README.md
├── provenance.json          # 固定 commits、prompt 與輸入 hashes
├── run_experiment.py        # 當時實際執行的 archival runner
├── run_status.json          # 各 repo/bundle 的執行、重試、驗證紀錄
├── completion.json
├── ground_truth/            # 本次 evaluator 使用的標籤快照
├── predictions/             # 送進 evaluator 的 PredictionCase
├── raw/                     # 每次嘗試的 log、原始輸出與採用輪次
├── sources/                 # 精確固定的 SmartAuditFlow / evaluator source snapshots
└── llm-judge/
    ├── manifest.json
    ├── judge_artifact.json
    ├── report.json
    └── report.md
```

## 如何檢查與重現

不需任何登入即可閱讀 `llm-judge/report.md` 與 JSON artifacts。只重新計算 metrics／產生 Markdown 不需呼叫 LLM；使用 `sources/prototype/src/benchmark_eval/` 的 `evaluate_benchmark()`、`write_report()` 與 `write_evaluation_markdown()`，輸入現有 manifest 和 Judge artifact 即可。這不等於重新執行模型評分。

`run_experiment.py` 保留了當時執行環境的相對路徑，**不是放到此新目錄後就可直接執行的 standalone CLI**。要重跑全部 live workflow，可先在 repository root 把本目錄複製成一個新的 run directory，以符合原 runner 的位置假設：

```bash
mkdir -p experiment-results
cp -R 實驗結果_6efce2f0 experiment-results/merged-pr1-reproduction
```

接著在新副本中移除舊的 `raw/`、`predictions/`、`llm-judge/`、`run_status.json`、`completion.json`（請勿刪除本封存目錄），準備 Python dependencies，並以自己授權的 gateway 啟動 `127.0.0.1:4000`。原 runner 預期本機 bearer token 位於 repository 的 sibling directory `subscription-gateway-pilot/runtime-home/.omp/auth-gateway.token`，依個人環境調整 runner 的 `TOKEN` 路徑；不要把 token 寫入 repo。

```bash
PYTHONDONTWRITEBYTECODE=1 python -u \
  experiment-results/merged-pr1-reproduction/run_experiment.py
```

Runner 使用 repository 既有 `dataset-inputs/`，並引用 `experiment-results/full-latest-gt-20261022/run_full_dataset.py` 的輸入選擇／合併 helpers，以及同目錄 `run_llm_judge.py` 的 gateway transport adapter。Judge 的 rubric、matching、metrics 和 Markdown renderer 均來自本目錄的固定官方 evaluator snapshot。Live rerun 會消耗模型額度，且模型結果不保證逐字相同。

本目錄不包含 OAuth credentials、gateway bearer tokens、`.env` 或 credential databases。JSON 中的絕對路徑僅記錄原本機執行位置，不是下載者電腦上的路徑。
