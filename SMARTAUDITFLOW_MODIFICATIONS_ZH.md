# SmartAuditFlow 改動與三 Repo 實驗整理

## 摘要

本文件整理 SmartAuditFlow 為了使用 Codex OAuth gateway、讀入專題 dataset、聚焦 price manipulation，並輸出可交給專案 LLM Judge 的 `PredictionCase` 所做的改動。程式修改已先提交到個人 fork 的功能 branch；這次文件補充會獨立提交，方便 review。三 repo pilot 是歷史測試結果，不代表最新完整 dataset 實驗。

## 1. 原本 SmartAuditFlow 的流程

SmartAuditFlow 原本透過 `WorkflowEngine` 依序執行五個節點，輸入主要是一段 Solidity `code_snippet`，另可附上 static-analysis 文字：

1. **Initial Analysis**：對程式碼做一般性初步分析。
2. **Audit Plan**：從初步分析產生 audit tasks。
3. **Parameter Extractor**：以關鍵字規則整理任務、指定優先級；這個節點本身不呼叫 LLM。
4. **Iteration**：逐一讓模型執行 audit tasks，整理 task results。
5. **Format Converter**：整合 task results，產生最終 findings/report。

原始 prompt 是一般性 smart-contract audit，涵蓋 reentrancy、整數問題、權限、gas、標準相容性等多種面向。原始最後輸出以 `Issue`、`Severity`、`Description`、`Impact`、`Location` 等 SmartAuditFlow 自有欄位為主，不是 benchmark evaluator 所需的 `Finding` 形狀。原有格式轉換程式在解析失敗時也可能從 task prose 合成 finding；本次改成不把解析失敗偽裝成漏洞 finding。

## 2. Codex OAuth gateway：改動與請求路徑

沒有將 SmartAuditFlow 改成官方 Codex API client；SmartAuditFlow 仍使用 OpenAI Python SDK。改動是新增一個明確的 `codex-gateway` provider，將 OpenAI-compatible 請求送到本機 gateway，由 gateway 使用已登入的 Codex OAuth session 轉送：

```text
SmartAuditFlow
  → OpenAI Python SDK / chat.completions
  → http://127.0.0.1:4000/v1（本機 OpenAI-compatible gateway）
  → auth broker 使用既有 Codex OAuth session
  → openai-codex/gpt-5.6-luna
```

主要改動位置：

- `smart-contract-audit/src/workflow/models.py`：新增 `_init_codex_gateway()`，從環境變數讀本機 gateway bearer token、檢查 URL 必須是 loopback，再建立 OpenAI-compatible client；`codex-gateway` 是明確選取的 provider，不會悄悄 fallback 到其他模型。模型名稱由 `CODEX_GATEWAY_MODEL` 指定。
- `smart-contract-audit/src/workflow/engine.py`：加入 `codex-gateway` provider 的可用性檢查。
- `smart-contract-audit/src/api/models_api.py`、`smart-contract-audit/src/static/index.html`：讓 UI 的 model status、model test 和模型選單辨識本機 gateway。
- `smart-contract-audit/scripts/run_dataset_smoke.py`：從本機 token file 讀 bearer token，在此子程序移除其他供應商的 API-key 環境變數，設定 `CODEX_GATEWAY_BASE_URL`、`CODEX_GATEWAY_MODEL`，再選擇 `codex-gateway` 執行 workflow。

`CODEX_GATEWAY_API_KEY` 這個名稱指的是本機 gateway bearer token；它不是 OpenAI API key，也不是程式自行保存的 Codex OAuth access token。runner 的 manifest 記錄模型和 gateway URL，但不保存 token 值。

## 3. Dataset 如何轉成 SmartAuditFlow 輸入

輸入準備工具在 `smart-contract-audit/scripts/prepare_ground_truth_dataset.py`。它用 ground-truth JSON **檔名**取得 repo ID，不讀取或複製 ground-truth 內容；再依 dataset metadata 找到本機 repo 與指定工作目錄，核對實際 Git HEAD 是否等於 dataset 的 resolved commit。

它不是把 repo 的所有檔案直接串成可編譯的單一 `.sol`。它只整理 Solidity source，依相對路徑排序後，包成一份或多份 **純文字 bundle**：

- 保留每個檔案的程式碼、import、pragma 和原始路徑。
- 每個檔案用 `BEGIN SOURCE FILE` / `END SOURCE FILE` marker 隔開。
- manifest 記錄 commit、檔案 hash、納入/排除原因，以及 bundle 行號到原始 source 的對應資訊。
- 依路徑規則排除 `.git`、build/generated、test、mock、fixture、vendor 等內容，以及 Foundry `*.t.sol`。
- token 上限使用 `ceil(characters / 4)` 粗估，不是 GPT tokenizer 的精確數字；單一過大的 source file 不會被切開。

這批整理資料總計 **24 個 repo、1,487 個納入的 Solidity source files、393 個排除檔案**；各 repo 都有 bundle 和 manifest。測試用的三份輸入為：

| Repo | 納入 Solidity 檔案 | 粗估 tokens |
|---|---:|---:|
| `2023-06-real-wagmi` | 18 | 23,208 |
| `2023-04-blueberry` | 80 | 64,947 |
| `2024-03-woofi-swap` | 81 | 141,212 |

runner 讀取 bundle 文字後傳入原 workflow 的 `code_snippet` 參數。這次 `static_tool` 是空字串，沒有實際執行 Slither 或其他 static analysis；被排除的 vendor/import 依賴也不會自動補入，所以這個輸入政策不代表完整編譯或完整依賴上下文。

## 4. Price-manipulation prompt：每個階段具體改動

在 `smart-contract-audit/src/workflow/nodes.py` 加入共用的 `PRICE_MANIPULATION_SCOPE`，並把它嵌入四個會呼叫模型的階段。這不只是加一句 Scope：原先的一般稽核任務清單、輸入說明、證據要求和輸出要求也一併改成與 price manipulation 有關。以下 before 是原始程式的代表性原文，after 是修改後的代表性 prompt；省略處以 `…` 表示。

> 僅稽核財務敏感 smart-contract logic 中的 price-manipulation；追蹤 attacker-influenceable AMM/DEX 狀態（reserves、token balances、liquidity、spot price、`slot0` / `getReserves`）、flash-loan 或 swap 造成的暫時狀態變化，如何影響 LP token、vault share、collateral 估值及 borrowing、minting、redemption、withdrawal、liquidation、reward 等操作；並檢查 TWAP、獨立 oracle、freshness/deviation、liquidity/slippage 和 state-update ordering 防護。

共用 scope 也明確要求：要指出從攻擊者可影響狀態到財務結果的具體資料/控制路徑；證據不足時不可把推測寫成 finding；不得補造未提供的測試、static-analysis、外部 knowledge-base 結果；不產生與 price manipulation 無關的通用漏洞 finding。

### 4.1 Initial Analysis

**Before（原始 prompt 節錄）**：要求廣泛檢視用途、架構、標準、權限和一般安全問題。

```text
Please provide a detailed initial analysis including:
1. Contract Overview and Purpose
2. Architecture Analysis
3. Initial Security Observations
4. Potential Areas of Concern
5. Code Quality Assessment
```

**After（修改後 prompt 節錄）**：要求建立 price/oracle 狀態到財務操作的證據地圖。

```text
Audit scope: [PRICE_MANIPULATION_SCOPE]
Return a concise, evidence-led map of:
(1) functions that read price/reserve/balance/liquidity/oracle/pool state;
(2) financial operations that consume those values;
(3) the data/control path between them; and
(4) safeguards visibly present or absent.
```

也明確說明 `static_tool` 可能為空，不可假裝工具有執行；引用檔案與符號，區分事實與假設。

### 4.2 Audit Plan

**Before（原始 prompt 節錄）**：把一般漏洞、business logic、gas、標準相容性和測試都列為稽核範圍。

```text
Create a detailed audit plan covering:
Security Vulnerability Assessment (reentrancy, overflow, access control, …)
Business Logic Validation
Gas Optimization Analysis
Standards Compliance
Specific Test Scenarios
```

**After（修改後 prompt 節錄）**：只產生 price manipulation 的驗證任務，最多 12 項。

```text
Produce up to 12 numbered, non-duplicative tasks.
Prioritize tracing attacker-controlled reserve/spot-price changes into a
financial action; checking LP/vault/collateral valuation; flash-loan or
same-transaction manipulation; and TWAP/oracle freshness, deviation,
liquidity, and update-order protections.
Each task names candidate contract/function and evidence needed to confirm
or reject the hypothesis. Do not add general audit or gas tasks.
```

### 4.3 Parameter Extractor

這一階段**沒有 LLM prompt**，是程式的 deterministic keyword 規則。

**Before（原始 high-priority 關鍵字）**：

```python
['reentrancy', 'overflow', 'underflow', 'access control', 'external call']
```

**After（修改後 high-priority 關鍵字）**：

```python
['price', 'oracle', 'reserve', 'spot', 'twap', 'flash loan',
 'collateral', 'liquidity', 'valuation']
```

medium priority 也改為 `deviation`、`freshness`、`slippage`、`lp token`、`vault share`、`reward` 等相關詞。它只排序 plan task 的優先級，不自行判斷漏洞成立。

### 4.4 Iteration

**Before（原始 prompt 節錄）**：每個 task 依通用漏洞格式分析問題、severity、技術細節、impact 和建議。

```text
Provide detailed findings for this specific task including:
1. Issue Analysis
2. Severity Assessment
3. Technical Details
4. Impact Assessment
5. Recommendations
```

**After（修改後 prompt 節錄）**：每個 task 都要求追蹤具體價格操縱路徑並說明證據狀態。

```text
Scope and exclusions: [PRICE_MANIPULATION_SCOPE]
Trace the exact source/value flow and state transition relevant to this task.
State whether code demonstrates an exploitable path, is protected, or lacks
evidence. A positive result cites source path, contract, function, and known
lines; explain prerequisites, transaction sequence, affected operation, and
impact. Recommend mitigation only for a demonstrated issue.
```

如果 static-analysis 輸入為空，Iteration 只能根據提供的 Solidity source 下結論。

### 4.5 Format Converter / Finalize

**Before（原始 prompt 節錄）**：輸出 SmartAuditFlow 自有欄位，並要求描述是否來自 code、static analysis 或 knowledge base。

```json
{
  "Issue": "...",
  "Severity": "High / Medium / Low",
  "Description": "...",
  "Impact": "...",
  "Location": "..."
}
```

**After（修改後 prompt 節錄）**：改為要求 evaluator 使用的 finding 欄位，並限制證據來源。

```json
{
  "finding_id": "SAF-001",
  "title": "...",
  "description": "Evidence-based root cause and exploit path",
  "impact": "Concrete consequence",
  "vulnerable_code": [{
    "file": "path/from/source/marker.sol",
    "contract": "ContractName",
    "function": "functionName",
    "start_line": null,
    "end_line": null
  }],
  "mitigation": "Actionable recommendation grounded in the root cause",
  "severity": "High / Medium / Low"
}
```

prompt 要求無充分證據時輸出 `[]`，不得捏造 location，也不得聲稱未提供的 static analysis 或 knowledge-base 結果。程式端的 schema/location validation 會再拒收不合規 finding 並寫入 `OutputWarnings`（詳見第 5 節）。

## 5. Output 如何符合 LLM Judge input

專案 evaluator 的基本形狀是 `PredictionCase`：

```json
{
  "repo_id": "example-repo",
  "detector_metadata": {
    "detector_version": "smartauditflow-price-manipulation-v1",
    "llm_model": "openai-codex/gpt-5.6-luna"
  },
  "predictions": [
    {
      "finding_id": "SAF-001",
      "title": "AMM spot price can be manipulated during redemption",
      "description": "Evidence-based root cause and exploit path.",
      "impact": "Concrete consequence to assets or protocol operations.",
      "vulnerable_code": [
        {
          "file": "src/Pool.sol",
          "contract": "Pool",
          "function": "redeem",
          "start_line": null,
          "end_line": null
        }
      ],
      "mitigation": "Use manipulation-resistant pricing with freshness and deviation checks."
    }
  ]
}
```

具體改動：

1. **模型最後輸出 findings 本身**：Format Converter 不再只輸出 `Issue`、`Location` 等舊欄位，而是要求 `finding_id`、`title`、`description`、`impact`、`vulnerable_code`、`mitigation`，可另帶 `severity`。`vulnerable_code` 的路徑、contract、function 必須可辨認；`start_line` / `end_line` 成對出現，確定不了則兩者皆 `null`。
2. **新增程式端檢查**：`_validate_prediction_findings()` 檢查必填文字、非空 `vulnerable_code`、source path 是否出現在 bundle markers、行號格式/範圍和 severity 值。格式錯誤或必要欄位缺漏的 finding 會被拒收並記入 `OutputWarnings`，不會自動補造 mitigation 或位置。這是結構檢查，不能單獨證明漏洞或保證 function 名稱語意正確。
3. **維持舊介面相容**：保留原有 consumers 使用的 `Findings`，另外新增 benchmark 使用的 `Predictions`、`PredictionSchema`。格式轉換失敗回傳空 findings 加 warning，不再偽裝成 High severity 漏洞。
4. **補 runtime envelope**：`run_dataset_smoke.py` 在拿到 workflow 結果後，以 CLI 的 repo ID 和 detector/model metadata 包住 `Predictions`，寫出 `prediction_case.json`；另寫 raw JSON、SmartAuditFlow Markdown 報告和 `run_manifest.json`。token 值不寫入這些產物。
5. **串 benchmark Judge**：把三個 JSON 放在同一個 predictions directory，使用相同 `repo_id` 從指定 ground-truth directory 組裝 manifest。Judge 才在這一步看到 ground truth，逐一比較 prediction/ground-truth pair，評分 R/L/I/M；最後 benchmark evaluator 根據 `end-to-end-v2` 權重（R 0.40、L/I/M 各 0.20）及 0.50 門檻產生結果。

本次透過 gateway 跑 Judge 時，使用相容層把 Pydantic JSON schema 加到 Judge instructions，再呼叫 gateway 的 Responses 路徑並在本機解析 JSON；Judge prompt、評分維度和 evaluator 邏輯沒有因此替換成另一套評分器。

## 6. 完整重現流程

```text
24 個 dataset repo + metadata + ground_truth 檔名
       │ 只用 ground_truth 檔名選 repo，不把 ground truth 交給掃描器
       ▼
核對 source commit → 篩 Solidity 檔案 → 加 file markers → 建立 bundle/manifest
       ▼
啟動本機 auth broker + Codex OAuth gateway
       ▼
選定三個 bundle 作為 code_snippet，static_tool 留空
       ▼
Initial Analysis → Audit Plan → Parameter Extractor → Iteration → Format Converter
       ▼
Raw result + PredictionCase（含 repo_id、detector metadata）
       ▼
PredictionCase schema validation → manifest assembly + verified ground truth
       ▼
LLM Judge（R/L/I/M）→ deterministic threshold/matching/evaluation
       ▼
judge_artifact.json + report.json + 人類可讀摘要 report.md
```

本次實際使用三個 repo、每 repo 最多 12 個 audit tasks，模型皆為 `openai-codex/gpt-5.6-luna`。SmartAuditFlow 三個 workflow 都完成五個節點：

| Repo | workflow predictions | Judge 結果 |
|---|---:|---|
| `2023-06-real-wagmi` | 2 | `SAF-001` 命中 `H-3`，R/L/I/M 為 4/4/4/4，weighted score 1.00。 |
| `2023-04-blueberry` | 0 | `H-4` 未命中。 |
| `2024-03-woofi-swap` | 3 | `H-1` 未達門檻；最高候選 weighted score 0.45，低於 0.50。 |

總計 5 predictions、3 個 ground-truth findings；macro soft F1 為 0.222，pooled soft F1 為 0.250。這只是三個 repo 的 pilot 結果，不足以代表完整 dataset 表現；Judge 結果也不是人工安全審計結論。

## 相關產物與注意事項

- 三 repo 的完整結果與評估摘要：`experiment-results/price-focused-3repos_20261014/`。
- 實驗摘要：`experiment-results/price-focused-3repos_20261014/report.md`。
- benchmark canonical report：`experiment-results/price-focused-3repos_20261014/llm-judge/report.json`。目前 evaluator 的 `write_report()` 寫 JSON；同目錄的 `report.md` 是依 JSON/Judge artifact 整理的人類可讀摘要，不是 evaluator 原生 Markdown writer。
- 執行測試會更新 Python `.pyc` / cache 檔；這些不是功能改動，不應納入文件或程式碼 commit。
