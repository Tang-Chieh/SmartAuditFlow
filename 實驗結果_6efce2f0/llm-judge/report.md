# Benchmark Evaluation Report

> Derived from canonical Evaluation artifacts. This report does not execute LLM requests.

## Executive Summary

| Metric | Value |
| --- | --- |
| Report version | 0.2 |
| Benchmark version | v1 |
| Repositories | 23 |
| Ground Truth findings | 42 |
| Predictions | 52 |
| Total matched predictions | 19 |
| Total matched weight | 18.4500 |
| Pooled soft precision | 0.3548 |
| Pooled soft recall | 0.4393 |
| Macro soft F1 | 0.2980 |
| Pooled soft F1 | 0.3926 |

## Evaluation Configuration

| Field | Value |
| --- | --- |
| Matching strategy | greedy |
| Threshold | 0.5000 |
| Weight profile | end-to-end-v2 |
| Judge model | openai-codex/gpt-5.6-luna |
| Judge prompt version | benchmark-judge-v3 |
| Detector version | smartauditflow-merged-pr1-6efce2f0-20261029 |
| Detector model | openai-codex/gpt-5.6-luna |
| Manifest SHA-256 | eaac45b93d24eda1b5612e15c2cead8299b998bda8227a4d52265a3efd7d9efb |

## Repository Summary

| Repository | Ground Truth | Predictions | Matched Predictions | Matched weight | Precision | Recall | Soft F1 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `2021-04-marginswap` | 1 | 3 | 1 | 1.0000 | 0.3333 | 1.0000 | 0.5000 |
| `2021-07-spartan` | 3 | 5 | 3 | 2.9500 | 0.5900 | 0.9833 | 0.7375 |
| `2021-08-notional` | 2 | 2 | 1 | 0.9500 | 0.4750 | 0.4750 | 0.4750 |
| `2021-11-malt` | 3 | 5 | 3 | 3.0000 | 0.6000 | 1.0000 | 0.7500 |
| `2021-12-vader` | 4 | 4 | 2 | 1.8000 | 0.4500 | 0.4500 | 0.4500 |
| `2022-01-behodler` | 2 | 4 | 2 | 2.0000 | 0.5000 | 1.0000 | 0.6667 |
| `2022-01-sandclock` | 2 | 2 | 1 | 1.0000 | 0.5000 | 0.5000 | 0.5000 |
| `2022-08-sentiment` | 2 | 1 | 0 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| `2022-09-notional` | 1 | 2 | 0 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| `2022-11-paraspace` | 4 | 2 | 1 | 1.0000 | 0.5000 | 0.2500 | 0.3333 |
| `2022-11-telcoin` | 1 | 1 | 0 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| `2023-03-olympus` | 1 | 0 | 0 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| `2023-04-blueberry` | 1 | 3 | 0 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| `2023-05-ussd` | 2 | 2 | 1 | 1.0000 | 0.5000 | 0.5000 | 0.5000 |
| `2023-06-lybra` | 1 | 0 | 0 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| `2023-06-real-wagmi` | 1 | 3 | 1 | 1.0000 | 0.3333 | 1.0000 | 0.5000 |
| `2023-06-tokemak` | 1 | 1 | 0 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| `2023-08-dopex` | 2 | 2 | 1 | 0.7500 | 0.3750 | 0.3750 | 0.3750 |
| `2024-03-abracadabra-money` | 2 | 0 | 0 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| `2024-03-revert-lend` | 1 | 2 | 1 | 1.0000 | 0.5000 | 1.0000 | 0.6667 |
| `2024-03-woofi-swap` | 1 | 2 | 0 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| `2024-04-panoptic` | 1 | 4 | 0 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| `2025-12-panoptic` | 3 | 2 | 1 | 1.0000 | 0.5000 | 0.3333 | 0.4000 |

## Repository Details

### `2021-04-marginswap`

| Metric | Value |
| --- | --- |
| Ground Truth findings | 1 |
| Predictions | 3 |
| Matched weight | 1.0000 |
| Soft precision | 0.3333 |
| Soft recall | 1.0000 |
| Soft F1 | 0.5000 |

#### Matched Findings

| Ground Truth | Prediction | R | L | I | M | Weighted |
| --- | --- | --- | --- | --- | --- | --- |
| H-03 — [H-03] Price feed can be manipulated | SAF-bundle-0001-001 — AMM spot-price manipulation can trigger wrongful margin liquidations | 4/4 | 4/4 | 4/4 | 4/4 | 1.0000 |

<details>
<summary>Pair 1: H-03 — [H-03] Price feed can be manipulated ↔ SAF-bundle-0001-001 — AMM spot-price manipulation can trigger wrongful margin liquidations</summary>

- **Ground Truth:** `H-03`
- **Prediction:** `SAF-bundle-0001-001`

#### Ground Truth locations

| File | Contract | Function | Lines |
| --- | --- | --- | --- |
| contracts/PriceAware.sol | PriceAware | getCurrentPriceInPeg(address,uint256,bool) | 60–87 |
| contracts/PriceAware.sol | PriceAware | getPriceFromAMM(address,uint256) | 111–137 |

#### Prediction locations

| File | Contract | Function | Lines |
| --- | --- | --- | --- |
| contracts/PriceAware.sol | PriceAware | getCurrentPriceInPeg | — |
| contracts/PriceAware.sol | PriceAware | viewCurrentPriceInPeg | — |
| contracts/PriceAware.sol | PriceAware | getPriceFromAMM | — |
| contracts/CrossMarginAccounts.sol | CrossMarginAccounts | belowMaintenanceThreshold | — |
| contracts/CrossMarginLiquidation.sol | CrossMarginLiquidation | liquidate | — |
| contracts/IsolatedMarginAccounts.sol | IsolatedMarginAccounts | belowMaintenanceThreshold | — |
| contracts/IsolatedMarginLiquidation.sol | IsolatedMarginLiquidation | liquidate | — |

#### Judge rationale

```text
R: Correctly identifies manipulation of current Uniswap-style AMM reserves and use of the resulting spot quote when forceCurBlock is true. L: Correctly localizes PriceAware.getCurrentPriceInPeg and getPriceFromAMM, with relevant liquidation callers. I: Correctly describes manipulated prices causing wrongful liquidation, distorted collateral valuation, and associated losses. M: Recommends replacing spot pricing with TWAP or other manipulation-resistant oracle pricing and adds sound protective controls; the extra slippage mitigations are also relevant but not required.
```

</details>

#### Unmatched Ground Truth

No unmatched Ground Truth findings.

#### Unmatched Predictions

- SAF-bundle-0001-002 — AMM-derived valuations can bypass cross-margin borrowing and withdrawal collateral checks
- SAF-bundle-0001-003 — AMM-derived prices can permit undercollateralized isolated-margin borrowing

### `2021-07-spartan`

| Metric | Value |
| --- | --- |
| Ground Truth findings | 3 |
| Predictions | 5 |
| Matched weight | 2.9500 |
| Soft precision | 0.5900 |
| Soft recall | 0.9833 |
| Soft F1 | 0.7375 |

#### Matched Findings

| Ground Truth | Prediction | R | L | I | M | Weighted |
| --- | --- | --- | --- | --- | --- | --- |
| H-06 — [H-06] SynthVault rewards can be gamed | SAF-bundle-0001-001 — Manipulable spot price permanently inflates SynthVault reward weight | 4/4 | 4/4 | 4/4 | 4/4 | 1.0000 |
| M-14 — [M-14] BondVault `BASE` incentive can be gamed | SAF-bundle-0001-002 — Manipulable pool reserves control bond LP allocation | 4/4 | 4/4 | 4/4 | 4/4 | 1.0000 |
| H-05 — [H-05] Synth realise is vulnerable to flash loan attacks | SAF-bundle-0001-004 — Spot-price manipulation can trigger excessive synth collateral burning | 4/4 | 4/4 | 3/4 | 4/4 | 0.9500 |

<details>
<summary>Pair 1: H-06 — [H-06] SynthVault rewards can be gamed ↔ SAF-bundle-0001-001 — Manipulable spot price permanently inflates SynthVault reward weight</summary>

- **Ground Truth:** `H-06`
- **Prediction:** `SAF-bundle-0001-001`

#### Ground Truth locations

| File | Contract | Function | Lines |
| --- | --- | --- | --- |
| contracts/synthVault.sol | SynthVault | _deposit(address,address,uint256) | 102–116 |
| contracts/Utils.sol | Utils | calcSpotValueInBase(address,uint256) | 160–163 |
| contracts/Utils.sol | Utils | calcSpotValueInBaseWithPool(address,uint256) | 186–190 |

#### Prediction locations

| File | Contract | Function | Lines |
| --- | --- | --- | --- |
| contracts/Utils.sol | Utils | calcSpotValueInBaseWithPool | — |
| contracts/synthVault.sol | SynthVault | _deposit | — |
| contracts/synthVault.sol | SynthVault | calcReward | — |

#### Judge rationale

```text
R: Correctly identifies instantaneous AMM spot valuation being persisted as SynthVault weight and retained after price restoration. L: Correctly names Utils.calcSpotValueInBaseWithPool, SynthVault._deposit, and downstream reward calculation. I: Correctly describes disproportionate BASE-funded rewards and dilution of honest depositors from inflated stored weight. M: TWAP/oracle valuation and preventing permanent entitlement from a transaction-time spot price address the flaw.
```

</details>

<details>
<summary>Pair 2: M-14 — [M-14] BondVault \`BASE\` incentive can be gamed ↔ SAF-bundle-0001-002 — Manipulable pool reserves control bond LP allocation</summary>

- **Ground Truth:** `M-14`
- **Prediction:** `SAF-bundle-0001-002`

#### Ground Truth locations

| File | Contract | Function | Lines |
| --- | --- | --- | --- |
| contracts/Dao.sol | Dao | bond(address,uint256) | 239–253 |
| contracts/Utils.sol | Utils | calcSwapValueInBase(address,uint) | 170–173 |
| contracts/Utils.sol | Utils | calcSwapValueInBaseWithPool(address,uint) | 198–202 |

#### Prediction locations

| File | Contract | Function | Lines |
| --- | --- | --- | --- |
| contracts/Utils.sol | Utils | calcSwapValueInBaseWithPool | — |
| contracts/Dao.sol | Dao | handleTransferIn | — |
| contracts/Dao.sol | Dao | bond | — |

#### Judge rationale

```text
R: Correctly identifies manipulation of current pool reserves used by calcSwapValueInBase to determine the protocol-funded BASE/SPARTA bond allocation before liquidity is added. L: Correctly names calcSwapValueInBaseWithPool, Dao.handleTransferIn, and Dao.bond, covering the vulnerable data flow. I: Correctly describes an attacker obtaining an oversized LP/BASE claim and imposing losses through manipulated allocation. M: TWAP or independent pricing with deviation, allocation, liquidity, and LP-output limits would prevent the ground-truth manipulation.
```

</details>

<details>
<summary>Pair 3: H-05 — [H-05] Synth realise is vulnerable to flash loan attacks ↔ SAF-bundle-0001-004 — Spot-price manipulation can trigger excessive synth collateral burning</summary>

- **Ground Truth:** `H-05`
- **Prediction:** `SAF-bundle-0001-004`

#### Ground Truth locations

| File | Contract | Function | Lines |
| --- | --- | --- | --- |
| contracts/Synth.sol | Synth | realise(address) | 187–199 |
| contracts/Utils.sol | Utils | calcLiquidityHoldings(uint,address,address) | 114–125 |
| contracts/Utils.sol | Utils | calcActualSynthUnits(uint,address) | 210–216 |

#### Prediction locations

| File | Contract | Function | Lines |
| --- | --- | --- | --- |
| contracts/Utils.sol | Utils | calcActualSynthUnits | — |
| contracts/Synth.sol | Synth | realise | — |

#### Judge rationale

```text
R: Correctly identifies instantaneous reserve-ratio valuation of synth debt, manipulation before realise, and the resulting premium-driven LP burn. L: Correctly names Utils.calcActualSynthUnits and Synth.realise, covering the central vulnerable path; omission of calcLiquidityHoldings is minor. I: Correctly describes excessive burning of synth-held LP collateral and the resulting increased claim for remaining LP holders, but does not explicitly state the attacker’s subsequent redemption and value extraction from other LP holders. M: TWAP or an independently validated oracle directly fixes the root cause; cooldown/deviation checks and burn caps are also technically sound additional protections.
```

</details>

#### Unmatched Ground Truth

No unmatched Ground Truth findings.

#### Unmatched Predictions

- SAF-bundle-0001-003 — Permissionless sync converts unsolicited token transfers into pricing reserves
- SAF-bundle-0001-005 — Mutable pool valuation controls stored DAO and bond reward weight

### `2021-08-notional`

| Metric | Value |
| --- | --- |
| Ground Truth findings | 2 |
| Predictions | 2 |
| Matched weight | 0.9500 |
| Soft precision | 0.4750 |
| Soft recall | 0.4750 |
| Soft F1 | 0.4750 |

#### Matched Findings

| Ground Truth | Prediction | R | L | I | M | Weighted |
| --- | --- | --- | --- | --- | --- | --- |
| H-10 — [H-10] Liquidity token value can be manipulated | SAF-bundle-0001-002 — Spot market reserve composition can manipulate liquidity-token and nToken valuation | 4/4 | 4/4 | 3/4 | 4/4 | 0.9500 |

<details>
<summary>Pair 1: H-10 — [H-10] Liquidity token value can be manipulated ↔ SAF-bundle-0001-002 — Spot market reserve composition can manipulate liquidity-token and nToken valuation</summary>

- **Ground Truth:** `H-10`
- **Prediction:** `SAF-bundle-0001-002`

#### Ground Truth locations

| File | Contract | Function | Lines |
| --- | --- | --- | --- |
| contracts/internal/valuation/AssetHandler.sol | AssetHandler | getHaircutCashClaims(PortfolioAsset,MarketParameters,CashGroupParameters) | 120–138 |
| contracts/internal/valuation/AssetHandler.sol | AssetHandler | _calcToken(int256,int256,int256,int256) | 141–148 |
| contracts/internal/valuation/AssetHandler.sol | AssetHandler | getLiquidityTokenValue(uint256,CashGroupParameters,MarketParameters,PortfolioAsset[],uint256,bool) | 151–216 |

#### Prediction locations

| File | Contract | Function | Lines |
| --- | --- | --- | --- |
| contracts/internal/markets/Market.sol | Market | calculateTrade | — |
| contracts/internal/valuation/AssetHandler.sol | AssetHandler | getLiquidityTokenValue | — |
| contracts/internal/valuation/AssetHandler.sol | AssetHandler | getCashClaims | — |
| contracts/internal/valuation/AssetHandler.sol | AssetHandler | getHaircutCashClaims | — |
| contracts/internal/nTokenHandler.sol | nTokenHandler | getNTokenAssetPV | — |

#### Judge rationale

```text
R: Correctly identifies mutable totalfCash/totalAssetCash reserve composition, combined with lagged oracle-rate discounting, as the manipulation mechanism. L: Correctly identifies calculateTrade and the AssetHandler getLiquidityTokenValue/getCashClaims/getHaircutCashClaims path; the additional nToken valuation location is not contradictory. I: Correctly covers manipulation of liquidity-token collateral, free-collateral and liquidation eligibility, including over/undervaluation; it is broader and does not specifically emphasize the direct LP risk-adjusted-value decrease caused by the extra fCash haircut, so minor imprecision remains. M: Time-weighted or historical/oracle-consistent reserve valuation and conservative valuation methods would prevent reliance on immediately manipulable reserves; the proposed additional safeguards are not required but do not detract.
```

</details>

#### Unmatched Ground Truth

- M-07 — [M-07] Attackers can force liquidations by borrowing large amounts of an asset.

#### Unmatched Predictions

- SAF-bundle-0001-001 — NToken redemption lacks execution-price slippage protection

### `2021-11-malt`

| Metric | Value |
| --- | --- |
| Ground Truth findings | 3 |
| Predictions | 5 |
| Matched weight | 3.0000 |
| Soft precision | 0.6000 |
| Soft recall | 1.0000 |
| Soft F1 | 0.7500 |

#### Matched Findings

| Ground Truth | Prediction | R | L | I | M | Weighted |
| --- | --- | --- | --- | --- | --- | --- |
| M-22 — [M-22] `_calculateMaltRequiredForExit` Uses Spot Price To Calculate Malt Quantity In `exitEarly` | SAF-bundle-0001-002 — Spot AMM price controls auction escape-hatch collateral payouts | 4/4 | 4/4 | 4/4 | 4/4 | 1.0000 |
| M-25 — [M-25] AMM Pool Can Be Drained Using a Flash Loan and Calling `stabilize` | SAF-bundle-0001-003 — Spot reserves determine protocol stabilization trade sizes | 4/4 | 4/4 | 4/4 | 4/4 | 1.0000 |
| M-30 — [M-30] Malt Protocol Uses Stale Results From `MaltDataLab` Which Can Be Abused By Users | SAF-bundle-0001-005 — Spot AMM reserves can be recorded into the Malt price oracle | 4/4 | 4/4 | 4/4 | 4/4 | 1.0000 |

<details>
<summary>Pair 1: M-22 — [M-22] \`_calculateMaltRequiredForExit\` Uses Spot Price To Calculate Malt Quantity In \`exitEarly\` ↔ SAF-bundle-0001-002 — Spot AMM price controls auction escape-hatch collateral payouts</summary>

- **Ground Truth:** `M-22`
- **Prediction:** `SAF-bundle-0001-002`

#### Ground Truth locations

| File | Contract | Function | Lines |
| --- | --- | --- | --- |
| src/contracts/DexHandlers/UniswapHandler.sol | UniswapHandler | maltMarketPrice() | 80–109 |
| src/contracts/AuctionEscapeHatch.sol | AuctionEscapeHatch | _calculateMaltRequiredForExit(uint256,uint256) | 168–213 |
| src/contracts/AuctionEscapeHatch.sol | AuctionEscapeHatch | exitEarly(uint256,uint256,uint256) | 65–92 |

#### Prediction locations

| File | Contract | Function | Lines |
| --- | --- | --- | --- |
| contracts/DexHandlers/UniswapHandler.sol | UniswapHandler | maltMarketPrice | — |
| contracts/AuctionEscapeHatch.sol | AuctionEscapeHatch | _calculateMaltRequiredForExit | — |
| contracts/AuctionEscapeHatch.sol | AuctionEscapeHatch | exitEarly | — |

#### Judge rationale

```text
R: Correctly identifies the instantaneous Uniswap reserve price as manipulable and used to determine the early-exit Malt amount. L: Correctly names maltMarketPrice(), _calculateMaltRequiredForExit(), and exitEarly(), matching the vulnerable data flow. I: Correctly describes reserve manipulation causing an incorrect mint/sale and excessive collateral payout to the early-exit caller. M: Replacing the spot price with a TWAP or validated oracle, with appropriate execution protections, would prevent the ground-truth vulnerability.
```

</details>

<details>
<summary>Pair 2: M-25 — [M-25] AMM Pool Can Be Drained Using a Flash Loan and Calling \`stabilize\` ↔ SAF-bundle-0001-003 — Spot reserves determine protocol stabilization trade sizes</summary>

- **Ground Truth:** `M-25`
- **Prediction:** `SAF-bundle-0001-003`

#### Ground Truth locations

| File | Contract | Function | Lines |
| --- | --- | --- | --- |
| src/contracts/DexHandlers/UniswapHandler.sol | UniswapHandler | _calculateTradeSize(address,address,uint256) | 250–275 |

#### Prediction locations

| File | Contract | Function | Lines |
| --- | --- | --- | --- |
| contracts/DexHandlers/UniswapHandler.sol | UniswapHandler | _calculateTradeSize | — |
| contracts/DexHandlers/UniswapHandler.sol | UniswapHandler | calculateMintingTradeSize | — |
| contracts/DexHandlers/UniswapHandler.sol | UniswapHandler | calculateBurningTradeSize | — |
| contracts/DexHandlers/UniswapHandler.sol | UniswapHandler | buyMalt | — |
| contracts/DexHandlers/UniswapHandler.sol | UniswapHandler | sellMalt | — |

#### Judge rationale

```text
R: Correctly identifies instantaneous Uniswap reserve-derived sizing as the causal flaw and connects it to manipulated stabilization operations. L: Explicitly identifies UniswapHandler._calculateTradeSize() and the relevant sizing/trade functions, matching the ground-truth vulnerable path. I: Correctly states that flash-loan reserve manipulation can cause excessive Malt minting and unfavorable protocol-owned stabilization trades, including the ground-truth pool-damaging outcome. M: Replacing spot sizing with a manipulation-resistant TWAP or validated price, plus bounds and execution limits, directly prevents the vulnerability.
```

</details>

<details>
<summary>Pair 3: M-30 — [M-30] Malt Protocol Uses Stale Results From \`MaltDataLab\` Which Can Be Abused By Users ↔ SAF-bundle-0001-005 — Spot AMM reserves can be recorded into the Malt price oracle</summary>

- **Ground Truth:** `M-30`
- **Prediction:** `SAF-bundle-0001-005`

#### Ground Truth locations

| File | Contract | Function | Lines |
| --- | --- | --- | --- |
| src/contracts/MaltDataLab.sol | MaltDataLab | trackMaltPrice() | 133–151 |
| src/contracts/MaltDataLab.sol | MaltDataLab | trackPoolReserves() | 153–170 |
| src/contracts/MaltDataLab.sol | MaltDataLab | trackPool() | 172–197 |
| src/contracts/MovingAverage.sol | MovingAverage | update(uint256) | 142–246 |

#### Prediction locations

| File | Contract | Function | Lines |
| --- | --- | --- | --- |
| contracts/MaltDataLab.sol | MaltDataLab | trackMaltPrice | — |
| contracts/MovingAverage.sol | MovingAverage | update | — |

#### Judge rationale

```text
R: Correctly identifies instantaneous AMM reserves being recorded as Malt price observations in a moving average and the resulting contamination when reserves are manipulated around updater calls. L: Correctly locates MaltDataLab.trackMaltPrice() and MovingAverage.update(), matching the ground-truth path. I: Correctly explains that manipulated samples can drive auctions, stabilization, supply distribution, transfer restrictions, and financial losses. M: Replacing spot snapshots with a genuine TWAP or independent validated oracle, together with freshness/deviation/history controls, directly prevents the ground-truth vulnerability.
```

</details>

#### Unmatched Ground Truth

No unmatched Ground Truth findings.

#### Unmatched Predictions

- SAF-bundle-0001-001 — Permissionless reserve-ratio oracle updates enable auction manipulation
- SAF-bundle-0001-004 — Manipulable spot quote controls user Malt contribution during reinvestment

### `2021-12-vader`

| Metric | Value |
| --- | --- |
| Ground Truth findings | 4 |
| Predictions | 4 |
| Matched weight | 1.8000 |
| Soft precision | 0.4500 |
| Soft recall | 0.4500 |
| Soft F1 | 0.4500 |

#### Matched Findings

| Ground Truth | Prediction | R | L | I | M | Weighted |
| --- | --- | --- | --- | --- | --- | --- |
| H-07 — [H-07] Synth minting and redemption use manipulable pool reserves to drain native assets. | SAF-bundle-0001-001 — Spot reserve manipulation enables mispriced synthetic issuance and redemption | 4/4 | 4/4 | 4/4 | 4/4 | 1.0000 |
| H-04 — [H-04] Vader TWAP weights can be corrupted and price queries can be forced to revert. | SAF-bundle-0001-002 — LiquidityBasedTWAP uses attacker-controlled spot reserves as historical weights | 3/4 | 3/4 | 3/4 | 4/4 | 0.8000 |

<details>
<summary>Pair 1: H-07 — [H-07] Synth minting and redemption use manipulable pool reserves to drain native assets. ↔ SAF-bundle-0001-001 — Spot reserve manipulation enables mispriced synthetic issuance and redemption</summary>

- **Ground Truth:** `H-07`
- **Prediction:** `SAF-bundle-0001-001`

#### Ground Truth locations

| File | Contract | Function | Lines |
| --- | --- | --- | --- |
| contracts/dex-v2/pool/VaderPoolV2.sol | VaderPoolV2 | mintSynth(IERC20,uint256,address,address) | 153–194 |
| contracts/dex-v2/pool/VaderPoolV2.sol | VaderPoolV2 | burnSynth(IERC20,uint256,address) | 206–246 |

#### Prediction locations

| File | Contract | Function | Lines |
| --- | --- | --- | --- |
| contracts/dex-v2/pool/VaderPoolV2.sol | VaderPoolV2 | mintSynth | — |
| contracts/dex-v2/pool/VaderPoolV2.sol | VaderPoolV2 | burnSynth | — |
| contracts/dex-v2/pool/BasePoolV2.sol | BasePoolV2 | swap | — |

#### Judge rationale

```text
R: Correctly identifies that mintSynth and burnSynth use instantaneous, manipulable pool reserves through VaderMath.calculateSwap. L: Correctly localizes both VaderPoolV2.mintSynth and burnSynth, with BasePoolV2.swap as the reserve-manipulation path. I: Correctly describes favorable rate manipulation causing excessive synth issuance or native-asset redemption, reserve depletion, and value extraction. M: Oracle/TWAP pricing, deviation checks, and related protections directly address reserve-based manipulation across both operations.
```

</details>

<details>
<summary>Pair 2: H-04 — [H-04] Vader TWAP weights can be corrupted and price queries can be forced to revert. ↔ SAF-bundle-0001-002 — LiquidityBasedTWAP uses attacker-controlled spot reserves as historical weights</summary>

- **Ground Truth:** `H-04`
- **Prediction:** `SAF-bundle-0001-002`

#### Ground Truth locations

| File | Contract | Function | Lines |
| --- | --- | --- | --- |
| contracts/lbt/LiquidityBasedTWAP.sol | LiquidityBasedTWAP | syncVaderPrice() | 113–148 |

#### Prediction locations

| File | Contract | Function | Lines |
| --- | --- | --- | --- |
| contracts/lbt/LiquidityBasedTWAP.sol | LiquidityBasedTWAP | syncVaderPrice | — |
| contracts/lbt/LiquidityBasedTWAP.sol | LiquidityBasedTWAP | syncUSDVPrice | — |
| contracts/lbt/LiquidityBasedTWAP.sol | LiquidityBasedTWAP | _updateVaderPrice | — |
| contracts/lbt/LiquidityBasedTWAP.sol | LiquidityBasedTWAP | _updateUSDVPrice | — |

#### Judge rationale

```text
R: Correctly identifies that synchronization rebuilds the aggregate from only pairs updated in the call and excludes pairs whose update period has not elapsed; the additional spot-reserve manipulation claim is broader than the ground truth. L: Includes LiquidityBasedTWAP.syncVaderPrice, the vulnerable function, though it adds other synchronization/update paths. I: Correctly identifies distorted aggregate oracle prices affecting USDV minting and reimbursement and notes malformed outputs from incomplete inclusion, but does not explicitly state zero-aggregate division and forced reverts. M: Correctly requires retaining prior pair weights and recomputing totals from all stored weights, which fixes the ground-truth flaw.
```

</details>

#### Unmatched Ground Truth

- H-06 — [H-06] LPs of VaderPoolV2 can manipulate pool reserves to extract funds from the reserve.
- M-06 — [M-06] Manipulated pool reserves can make the oracle rely on a single pair.

#### Unmatched Predictions

- SAF-bundle-0001-003 — AMM-derived LBT prices can manipulate USDV conversion rates
- SAF-bundle-0001-004 — Nominal swap inputs can corrupt price-bearing reserves for non-standard tokens

### `2022-01-behodler`

| Metric | Value |
| --- | --- |
| Ground Truth findings | 2 |
| Predictions | 4 |
| Matched weight | 2.0000 |
| Soft precision | 0.5000 |
| Soft recall | 1.0000 |
| Soft F1 | 0.6667 |

#### Matched Findings

| Ground Truth | Prediction | R | L | I | M | Weighted |
| --- | --- | --- | --- | --- | --- | --- |
| H-05 — [H-05] Flash loan price manipulation in purchasePyroFlan() | SAF-bundle-0001-001 — Spot-price manipulation can inflate PyroFlan issuance | 4/4 | 4/4 | 4/4 | 4/4 | 1.0000 |
| H-07 — [H-07] LP pricing formula is vulnerable to flashloan manipulation | SAF-bundle-0001-002 — LP EYE balance donations can inflate Fate valuation | 4/4 | 4/4 | 4/4 | 4/4 | 1.0000 |

<details>
<summary>Pair 1: H-05 — [H-05] Flash loan price manipulation in purchasePyroFlan() ↔ SAF-bundle-0001-001 — Spot-price manipulation can inflate PyroFlan issuance</summary>

- **Ground Truth:** `H-05`
- **Prediction:** `SAF-bundle-0001-001`

#### Ground Truth locations

| File | Contract | Function | Lines |
| --- | --- | --- | --- |
| contracts/FlanBackstop.sol | FlanBackstop | purchasePyroFlan(address,uint256) | 75–114 |

#### Prediction locations

| File | Contract | Function | Lines |
| --- | --- | --- | --- |
| contracts/FlanBackstop.sol | FlanBackstop | purchasePyroFlan | — |

#### Judge rationale

```text
R: Correctly identifies instantaneous FLAN/stablecoin LP-balance pricing, manipulation of priceBefore/tiltedPrice, and the insufficiency of the per-call ceiling against repeated attacks. L: Correctly localizes FlanBackstop.purchasePyroFlan and its pricing-to-mint path. I: Correctly describes inflated PyroFlan issuance and attacker value extraction while remaining under the per-call limit. M: TWAP, independent pricing, and output/premium controls would prevent the ground-truth manipulation; the additional safeguards do not detract.
```

</details>

<details>
<summary>Pair 2: H-07 — [H-07] LP pricing formula is vulnerable to flashloan manipulation ↔ SAF-bundle-0001-002 — LP EYE balance donations can inflate Fate valuation</summary>

- **Ground Truth:** `H-07`
- **Prediction:** `SAF-bundle-0001-002`

#### Ground Truth locations

| File | Contract | Function | Lines |
| --- | --- | --- | --- |
| contracts/DAO/LimboDAO.sol | LimboDAO | setEYEBasedAssetStake(uint256,uint256,uint256,address) | 356–366 |
| contracts/DAO/LimboDAO.sol | LimboDAO | burnAsset(address,uint256) | 392–397 |

#### Prediction locations

| File | Contract | Function | Lines |
| --- | --- | --- | --- |
| contracts/Limbo.sol | Limbo | setEYEBasedAssetStake | — |
| contracts/Limbo.sol | Limbo | burnAsset | — |

#### Judge rationale

```text
R: Correctly identifies valuation as raw EYE balance divided by LP total supply and recognizes that manipulable balance changes inflate the implied LP value, including unsolicited donations as a concrete manipulation vector. L: Names both ground-truth functions, setEYEBasedAssetStake and burnAsset, with the relevant Fate-calculation flow; the Limbo versus LimboDAO naming is minor. I: Correctly describes disproportionate Fate, governance influence, and potential conversion to Flan. M: Replacing raw balances with recognized/canonical reserves and adding delayed or time-weighted valuation directly prevents the underlying manipulation across both functions.
```

</details>

#### Unmatched Ground Truth

No unmatched Ground Truth findings.

#### Unmatched Predictions

- SAF-bundle-0001-003 — Raw external-pair balances can cause excess Flan minting during stabilization
- SAF-bundle-0001-004 — Spot AMM pricing can cause unfavorable protocol buybacks

### `2022-01-sandclock`

| Metric | Value |
| --- | --- |
| Ground Truth findings | 2 |
| Predictions | 2 |
| Matched weight | 1.0000 |
| Soft precision | 0.5000 |
| Soft recall | 0.5000 |
| Soft F1 | 0.5000 |

#### Matched Findings

| Ground Truth | Prediction | R | L | I | M | Weighted |
| --- | --- | --- | --- | --- | --- | --- |
| H-03 — [H-03] Vaults with non-UST underlying asset vulnerable to flash loan attack on curve pool | SAF-bundle-0001-002 — Curve spot-price valuation and zero-slippage swaps in NonUSTStrategy | 4/4 | 4/4 | 4/4 | 4/4 | 1.0000 |

<details>
<summary>Pair 1: H-03 — [H-03] Vaults with non-UST underlying asset vulnerable to flash loan attack on curve pool ↔ SAF-bundle-0001-002 — Curve spot-price valuation and zero-slippage swaps in NonUSTStrategy</summary>

- **Ground Truth:** `H-03`
- **Prediction:** `SAF-bundle-0001-002`

#### Ground Truth locations

| File | Contract | Function | Lines |
| --- | --- | --- | --- |
| sandclock/contracts/strategy/NonUSTStrategy.sol | NonUSTStrategy | investedAssets() | 120–136 |

#### Prediction locations

| File | Contract | Function | Lines |
| --- | --- | --- | --- |
| contracts/strategy/NonUSTStrategy.sol | NonUSTStrategy | investedAssets | — |
| contracts/strategy/NonUSTStrategy.sol | NonUSTStrategy | _swapUnderlyingToUst | — |
| contracts/strategy/NonUSTStrategy.sol | NonUSTStrategy | _swapUstToUnderlying | — |
| contracts/Vault.sol | Vault | totalUnderlying | — |

#### Judge rationale

```text
R: Correctly identifies instantaneous Curve get_dy_underlying() valuation as manipulable and its flow into vault accounting; the additional swap observations do not contradict the core finding. L: Correctly localizes NonUSTStrategy.investedAssets() and the downstream Vault.totalUnderlying/share and withdrawal paths. I: Correctly describes flash-manipulated valuation causing excessive or insufficient shares and incorrect withdrawals at depositors' expense. M: Recommends a manipulation-resistant oracle or sufficiently long TWAP, deviation/staleness checks, and suitable execution slippage protections; the oracle/TWAP mitigation directly fixes the ground-truth flaw.
```

</details>

#### Unmatched Ground Truth

- M-11 — [M-11] Changing a strategy can be bricked

#### Unmatched Predictions

- SAF-bundle-0001-001 — Share-price inflation through unsolicited underlying-token transfers

### `2022-08-sentiment`

| Metric | Value |
| --- | --- |
| Ground Truth findings | 2 |
| Predictions | 1 |
| Matched weight | 0.0000 |
| Soft precision | 0.0000 |
| Soft recall | 0.0000 |
| Soft F1 | 0.0000 |

#### Matched Findings

| Ground Truth | Prediction | R | L | I | M | Weighted |
| --- | --- | --- | --- | --- | --- | --- |
| No matched findings. | | | | | | |

#### Unmatched Ground Truth

- M-10 — M-10: ERC4626Oracle Vulnerable To Price Manipulation
- H-1 — H-1: LToken pricePerShare can be manipulated by an early depositor

#### Unmatched Predictions

- SAF-bundle-0001-001 — Uniswap V2 LP price relies on manipulable spot reserves

### `2022-09-notional`

| Metric | Value |
| --- | --- |
| Ground Truth findings | 1 |
| Predictions | 2 |
| Matched weight | 0.0000 |
| Soft precision | 0.0000 |
| Soft recall | 0.0000 |
| Soft F1 | 0.0000 |

#### Matched Findings

| Ground Truth | Prediction | R | L | I | M | Weighted |
| --- | --- | --- | --- | --- | --- | --- |
| No matched findings. | | | | | | |

#### Unmatched Ground Truth

- M-7 — [M-7] Gain From Balancer Vaults Can Be Stolen

#### Unmatched Predictions

- SAF-bundle-0001-001 — Boosted vault valuation relies on attacker-influenceable current pool balances
- SAF-bundle-0001-002 — MetaStable strategy valuation can rely entirely on Balancer BPT TWAP

### `2022-11-paraspace`

| Metric | Value |
| --- | --- |
| Ground Truth findings | 4 |
| Predictions | 2 |
| Matched weight | 1.0000 |
| Soft precision | 0.5000 |
| Soft recall | 0.2500 |
| Soft F1 | 0.3333 |

#### Matched Findings

| Ground Truth | Prediction | R | L | I | M | Weighted |
| --- | --- | --- | --- | --- | --- | --- |
| M-04 — [M-04] Fallback oracle is using spot price in Uniswap liquidity pool, which is very vulnerable to flashloan price manipulation | SAF-bundle-0008-002 — Manipulable Uniswap V2 spot price used as fallback asset oracle | 4/4 | 4/4 | 4/4 | 4/4 | 1.0000 |

<details>
<summary>Pair 1: M-04 — [M-04] Fallback oracle is using spot price in Uniswap liquidity pool, which is very vulnerable to flashloan price manipulation ↔ SAF-bundle-0008-002 — Manipulable Uniswap V2 spot price used as fallback asset oracle</summary>

- **Ground Truth:** `M-04`
- **Prediction:** `SAF-bundle-0008-002`

#### Ground Truth locations

| File | Contract | Function | Lines |
| --- | --- | --- | --- |
| paraspace-core/contracts/misc/ParaSpaceOracle.sol | ParaSpaceOracle | getAssetPrice(address) | 115–136 |
| paraspace-core/contracts/misc/ParaSpaceFallbackOracle.sol | ParaSpaceFallbackOracle | getAssetPrice(address) | 34–60 |

#### Prediction locations

| File | Contract | Function | Lines |
| --- | --- | --- | --- |
| contracts/misc/ParaSpaceFallbackOracle.sol | ParaSpaceFallbackOracle | getAssetPrice | — |
| contracts/misc/ParaSpaceOracle.sol | ParaSpaceOracle | getAssetPrice | — |

#### Judge rationale

```text
R: Correctly identifies the mutable Uniswap V2 reserve spot quote and fallback activation when the primary oracle is unavailable, enabling flash-loan price manipulation. L: Correctly localizes both ParaSpaceFallbackOracle.getAssetPrice and the delegating ParaSpaceOracle.getAssetPrice path. I: Correctly describes manipulated valuation affecting borrowing, collateral and liquidation decisions, including undercollateralized debt and bad debt. M: Recommends manipulation-resistant pricing and, importantly, failing closed when the primary oracle is unavailable; these measures prevent the ground-truth vulnerability.
```

</details>

#### Unmatched Ground Truth

- H-05 — [H-05] Attacker can manipulate low TVL Uniswap V3 pool to borrow and swap to make Lending Pool in loss
- M-05 — [M-05] Front-running admin setPrice call allows a single compromised oracle to set any price, allowing the oracle manipulator to drain all protocol funds
- M-22 — [M-22] Price can deviate by much more than maxDeviationRate

#### Unmatched Predictions

- SAF-bundle-0001-001 — Block Timestamp Manipulation Can Lower Dutch Auction Execution Price

### `2022-11-telcoin`

| Metric | Value |
| --- | --- |
| Ground Truth findings | 1 |
| Predictions | 1 |
| Matched weight | 0.0000 |
| Soft precision | 0.0000 |
| Soft recall | 0.0000 |
| Soft F1 | 0.0000 |

#### Matched Findings

| Ground Truth | Prediction | R | L | I | M | Weighted |
| --- | --- | --- | --- | --- | --- | --- |
| No matched findings. | | | | | | |

#### Unmatched Ground Truth

- H-1 — H-1: Flashloan `TEL` tokens to stake and exit in the same block can fake a huge amount of stake with minimal material cost

#### Unmatched Predictions

- SAF-bundle-0001-001 — Missing minimum-output protection on secondary buyback swaps

### `2023-03-olympus`

| Metric | Value |
| --- | --- |
| Ground Truth findings | 1 |
| Predictions | 0 |
| Matched weight | 0.0000 |
| Soft precision | 0.0000 |
| Soft recall | 0.0000 |
| Soft F1 | 0.0000 |

#### Matched Findings

| Ground Truth | Prediction | R | L | I | M | Weighted |
| --- | --- | --- | --- | --- | --- | --- |
| No matched findings. | | | | | | |

#### Unmatched Ground Truth

- H-1 — H-1: Adversary can sandwich oracle updates to exploit vault

#### Unmatched Predictions

No unmatched predictions.

### `2023-04-blueberry`

| Metric | Value |
| --- | --- |
| Ground Truth findings | 1 |
| Predictions | 3 |
| Matched weight | 0.0000 |
| Soft precision | 0.0000 |
| Soft recall | 0.0000 |
| Soft F1 | 0.0000 |

#### Matched Findings

| Ground Truth | Prediction | R | L | I | M | Weighted |
| --- | --- | --- | --- | --- | --- | --- |
| No matched findings. | | | | | | |

#### Unmatched Ground Truth

- H-4 — H-4: Potential flash loan attack vulnerability in `getPrice` function of CurveOracle

#### Unmatched Predictions

- SAF-bundle-0001-001 — Close operations accept attacker-manipulated exchange rates
- SAF-bundle-0001-002 — Balancer position entry lacks minimum BPT output protection
- SAF-bundle-0001-003 — Uniswap V2 LP valuation relies on mutable spot reserves

### `2023-05-ussd`

| Metric | Value |
| --- | --- |
| Ground Truth findings | 2 |
| Predictions | 2 |
| Matched weight | 1.0000 |
| Soft precision | 0.5000 |
| Soft recall | 0.5000 |
| Soft F1 | 0.5000 |

#### Matched Findings

| Ground Truth | Prediction | R | L | I | M | Weighted |
| --- | --- | --- | --- | --- | --- | --- |
| H-5 — H-5: Price calculation susceptible to flashloan exploits | SAF-bundle-0001-001 — Rebalancer relies on manipulable Uniswap V3 spot price | 4/4 | 4/4 | 4/4 | 4/4 | 1.0000 |

<details>
<summary>Pair 1: H-5 — H-5: Price calculation susceptible to flashloan exploits ↔ SAF-bundle-0001-001 — Rebalancer relies on manipulable Uniswap V3 spot price</summary>

- **Ground Truth:** `H-5`
- **Prediction:** `SAF-bundle-0001-001`

#### Ground Truth locations

| File | Contract | Function | Lines |
| --- | --- | --- | --- |
| ussd-contracts/contracts/USSDRebalancer.sol | USSDRebalancer | getOwnValuation() | 71–80 |
| ussd-contracts/contracts/USSDRebalancer.sol | USSDRebalancer | rebalance() | 92–107 |

#### Prediction locations

| File | Contract | Function | Lines |
| --- | --- | --- | --- |
| contracts/USSDRebalancer.sol | USSDRebalancer | getOwnValuation | — |
| contracts/USSDRebalancer.sol | USSDRebalancer | rebalance | — |
| contracts/USSD.sol | USSD | UniV3SwapInput | — |

#### Judge rationale

```text
R: Correctly identifies the instantaneous Uniswap V3 slot0 price as manipulable instead of a TWAP, including flash-loan/trading manipulation. L: Correctly localizes getOwnValuation() and rebalance(), with relevant downstream swap execution detail. I: Correctly describes attacker-controlled rebalance decisions and protocol value loss from trades at manipulated prices. M: Recommends replacing slot0 with a TWAP or independent oracle and protecting branch selection/trade sizing; this directly fixes the ground-truth flaw, with additional valid hardening.
```

</details>

#### Unmatched Ground Truth

- H-9 — H-9: Uniswap v3 pool token balance proportion does not necessarily correspond to the price, and it is easy to manipulate.

#### Unmatched Predictions

- SAF-bundle-0001-002 — Permissionless SimOracle price updates can overvalue collateral and overmint USSD

### `2023-06-lybra`

| Metric | Value |
| --- | --- |
| Ground Truth findings | 1 |
| Predictions | 0 |
| Matched weight | 0.0000 |
| Soft precision | 0.0000 |
| Soft recall | 0.0000 |
| Soft F1 | 0.0000 |

#### Matched Findings

| Ground Truth | Prediction | R | L | I | M | Weighted |
| --- | --- | --- | --- | --- | --- | --- |
| No matched findings. | | | | | | |

#### Unmatched Ground Truth

- M-13 — [M-13] It is possible to manipulate WETH/LBR pair to claim reward of the users which shouldn't be claimed

#### Unmatched Predictions

No unmatched predictions.

### `2023-06-real-wagmi`

| Metric | Value |
| --- | --- |
| Ground Truth findings | 1 |
| Predictions | 3 |
| Matched weight | 1.0000 |
| Soft precision | 0.3333 |
| Soft recall | 1.0000 |
| Soft F1 | 0.5000 |

#### Matched Findings

| Ground Truth | Prediction | R | L | I | M | Weighted |
| --- | --- | --- | --- | --- | --- | --- |
| H-3 — H-3: Usage of `slot0` is extremely easy to manipulate | SAF-bundle-0001-001 — Spot-price manipulation affects reserve valuation and LP accounting | 4/4 | 4/4 | 4/4 | 4/4 | 1.0000 |

<details>
<summary>Pair 1: H-3 — H-3: Usage of \`slot0\` is extremely easy to manipulate ↔ SAF-bundle-0001-001 — Spot-price manipulation affects reserve valuation and LP accounting</summary>

- **Ground Truth:** `H-3`
- **Prediction:** `SAF-bundle-0001-001`

#### Ground Truth locations

| File | Contract | Function | Lines |
| --- | --- | --- | --- |
| concentrator/contracts/Multipool.sol | Multipool | deposit(uint256,uint256,uint256,uint256) | 433–486 |
| concentrator/contracts/Multipool.sol | Multipool | getSlots() | 589–602 |
| concentrator/contracts/Multipool.sol | Multipool | _getReserves(Slot0Data[]) | 693–768 |

#### Prediction locations

| File | Contract | Function | Lines |
| --- | --- | --- | --- |
| contracts/Multipool.sol | Multipool | _getReserves | — |
| contracts/Multipool.sol | Multipool | getSlots | — |
| contracts/Multipool.sol | Multipool | deposit | — |
| contracts/Dispatcher.sol | Dispatcher | _estimateWithdrawalLp | — |
| contracts/Dispatcher.sol | Dispatcher | deposit | — |
| contracts/Dispatcher.sol | Dispatcher | withdraw | — |

#### Judge rationale

```text
R: Correctly identifies manipulation of instantaneous Uniswap V3 slot0/sqrt-price data, propagation through _getReserves(), and use in deposit LP issuance. Extra claims about fee settlement do not contradict the core cause. L: Correctly localizes _getReserves(), getSlots(), and deposit(), matching the vulnerable path. I: Correctly describes incorrect LP minting, unfavorable deposit composition, and redistribution/dilution affecting existing holders. M: TWAP or validated spot-vs-TWAP deviation checks directly address the raw slot0 vulnerability; the additional bounds are also sound.
```

</details>

#### Unmatched Ground Truth

No unmatched Ground Truth findings.

#### Unmatched Predictions

- SAF-bundle-0001-002 — Strategy ranges are initialized from manipulable spot ticks
- SAF-bundle-0001-003 — One-sided TWAP validation can accept an unfavorable rebalance swap

### `2023-06-tokemak`

| Metric | Value |
| --- | --- |
| Ground Truth findings | 1 |
| Predictions | 1 |
| Matched weight | 0.0000 |
| Soft precision | 0.0000 |
| Soft recall | 0.0000 |
| Soft F1 | 0.0000 |

#### Matched Findings

| Ground Truth | Prediction | R | L | I | M | Weighted |
| --- | --- | --- | --- | --- | --- | --- |
| No matched findings. | | | | | | |

#### Unmatched Ground Truth

- H-15 — H-15: Maverick oracle can be manipulated

#### Unmatched Predictions

- SAF-bundle-0001-001 — Uniswap V2 LP valuation relies on instantaneous reserve state

### `2023-08-dopex`

| Metric | Value |
| --- | --- |
| Ground Truth findings | 2 |
| Predictions | 2 |
| Matched weight | 0.7500 |
| Soft precision | 0.3750 |
| Soft recall | 0.3750 |
| Soft F1 | 0.3750 |

#### Matched Findings

| Ground Truth | Prediction | R | L | I | M | Weighted |
| --- | --- | --- | --- | --- | --- | --- |
| M-08 — [M-08] `reLPContract.reLP()` is susceptible to sandwich attack due to user control over `bond()` | SAF-bundle-0001-002 — ReLP relies on manipulable V2 reserves and performs unbounded final liquidity addition | 3/4 | 3/4 | 2/4 | 4/4 | 0.7500 |

<details>
<summary>Pair 1: M-08 — [M-08] \`reLPContract.reLP()\` is susceptible to sandwich attack due to user control over \`bond()\` ↔ SAF-bundle-0001-002 — ReLP relies on manipulable V2 reserves and performs unbounded final liquidity addition</summary>

- **Ground Truth:** `M-08`
- **Prediction:** `SAF-bundle-0001-002`

#### Ground Truth locations

| File | Contract | Function | Lines |
| --- | --- | --- | --- |
| contracts/core/RdpxV2Core.sol | RdpxV2Core | bond(uint256,uint256,address) | 894–930 |
| contracts/reLP/ReLPContract.sol | ReLPContract | reLP(uint256) | 202–295 |

#### Prediction locations

| File | Contract | Function | Lines |
| --- | --- | --- | --- |
| contracts/reLP/ReLPContract.sol | ReLPContract | reLP | — |

#### Judge rationale

```text
R: Correctly identifies manipulation of the V2 pool around reLP(), including its public triggering through bond() and permissive liquidity addition; it does not clearly emphasize that the caller-controlled bond amount controls the transaction-local reLP operation. L: Correctly identifies ReLPContract.reLP() and describes its bond()/bondWithDelegate() caller path, but does not localize the RdpxV2Core.bond() function as a separate vulnerable component. I: Captures unfavorable protocol liquidity/value outcomes from manipulation, but omits the ground-truth primary consequence that an attacker can profitably steal value through a sandwich and instead emphasizes possible reverts/disruption. M: Separating reLP from the public bonding path directly implements the ground-truth mitigation; the additional oracle, bounds, and value checks are also directionally sound.
```

</details>

#### Unmatched Ground Truth

- M-09 — [M-09] A malicious early depositor can manipulate the LP-Token price per share to take an unfair share of future user deposits

#### Unmatched Predictions

- SAF-bundle-0001-001 — Uniswap V3 AMO operations lack enforced manipulation-resistant price bounds

### `2024-03-abracadabra-money`

| Metric | Value |
| --- | --- |
| Ground Truth findings | 2 |
| Predictions | 0 |
| Matched weight | 0.0000 |
| Soft precision | 0.0000 |
| Soft recall | 0.0000 |
| Soft F1 | 0.0000 |

#### Matched Findings

| Ground Truth | Prediction | R | L | I | M | Weighted |
| --- | --- | --- | --- | --- | --- | --- |
| No matched findings. | | | | | | |

#### Unmatched Ground Truth

- H-04 — [H-04] Oracle price can be manipulated
- H-01 — [H-01] Anyone making use of the MagicLP's TWAP to determine token prices will be exploitable.

#### Unmatched Predictions

No unmatched predictions.

### `2024-03-revert-lend`

| Metric | Value |
| --- | --- |
| Ground Truth findings | 1 |
| Predictions | 2 |
| Matched weight | 1.0000 |
| Soft precision | 0.5000 |
| Soft recall | 1.0000 |
| Soft F1 | 0.6667 |

#### Matched Findings

| Ground Truth | Prediction | R | L | I | M | Weighted |
| --- | --- | --- | --- | --- | --- | --- |
| M-19 — [M-19] `V3Oracle` susceptible to price manipulation | SAF-bundle-0001-002 — LP collateral composition is calculated from manipulable spot price | 4/4 | 4/4 | 4/4 | 4/4 | 1.0000 |

<details>
<summary>Pair 1: M-19 — [M-19] \`V3Oracle\` susceptible to price manipulation ↔ SAF-bundle-0001-002 — LP collateral composition is calculated from manipulable spot price</summary>

- **Ground Truth:** `M-19`
- **Prediction:** `SAF-bundle-0001-002`

#### Ground Truth locations

| File | Contract | Function | Lines |
| --- | --- | --- | --- |
| src/V3Oracle.sol | V3Oracle | getValue(uint256,address) | 95–131 |
| src/V3Oracle.sol | V3Oracle | getPositionBreakdown(uint256) | 162–181 |
| src/V3Oracle.sol | V3Oracle | _initializeState(uint256) | 395–423 |
| src/V3Oracle.sol | V3Oracle | _getAmounts(PositionState) | 426–442 |

#### Prediction locations

| File | Contract | Function | Lines |
| --- | --- | --- | --- |
| src/V3Oracle.sol | V3Oracle | _initializeState | — |
| src/V3Oracle.sol | V3Oracle | _getAmounts | — |
| src/V3Oracle.sol | V3Oracle | getValue | — |
| src/V3Oracle.sol | V3Oracle | _checkPoolPrice | — |
| src/V3Vault.sol | V3Vault | _checkLoanIsHealthy | — |

#### Judge rationale

```text
R: Correctly identifies that LP token amounts are computed from manipulable current position-pool slot0 data while token values use oracle prices, with the pool-price check potentially accepting the distorted composition under its configured threshold. L: Precisely localizes _initializeState, _getAmounts, getValue, _checkPoolPrice, and the vault health-check path. I: Correctly describes manipulation of tight-range collateral valuation leading to excess borrowing, bad debt, and altered liquidation outcomes, with relevant configuration and position-range conditions. M: Replacing instantaneous slot0-based amount calculation with a validated TWAP/oracle-derived price, plus independent consistency validation or conservative anti-overvaluation handling, addresses the underlying vulnerability.
```

</details>

#### Unmatched Ground Truth

No unmatched Ground Truth findings.

#### Unmatched Predictions

- SAF-bundle-0001-001 — Zero-second TWAP configuration enables spot-price manipulation of collateral valuation

### `2024-03-woofi-swap`

| Metric | Value |
| --- | --- |
| Ground Truth findings | 1 |
| Predictions | 2 |
| Matched weight | 0.0000 |
| Soft precision | 0.0000 |
| Soft recall | 0.0000 |
| Soft F1 | 0.0000 |

#### Matched Findings

| Ground Truth | Prediction | R | L | I | M | Weighted |
| --- | --- | --- | --- | --- | --- | --- |
| No matched findings. | | | | | | |

#### Unmatched Ground Truth

- H-1 — H-1: Pool can be drained

#### Unmatched Predictions

- SAF-bundle-0001-001 — Infeasible Wooracle prices influence cross-chain fee calculations
- SAF-bundle-0001-002 — Reward conversions execute without minimum-output protection

### `2024-04-panoptic`

| Metric | Value |
| --- | --- |
| Ground Truth findings | 1 |
| Predictions | 4 |
| Matched weight | 0.0000 |
| Soft precision | 0.0000 |
| Soft recall | 0.0000 |
| Soft F1 | 0.0000 |

#### Matched Findings

| Ground Truth | Prediction | R | L | I | M | Weighted |
| --- | --- | --- | --- | --- | --- | --- |
| No matched findings. | | | | | | |

#### Unmatched Ground Truth

- M-01 — [M-01] `PanopticFactory` uses spot price when deploying new pools, resulting in liquidity manipulation when minting

#### Unmatched Predictions

- SAF-bundle-0001-001 — TWAP filter returns the upper adjacent order statistic
- SAF-bundle-0001-002 — Solvency validation can rely solely on the short-window fast oracle
- SAF-bundle-0001-003 — Forced exercise uses inconsistent and manipulable spot/TWAP prices
- SAF-bundle-0001-004 — Spot tick influences pending premium accounting in security-sensitive paths

### `2025-12-panoptic`

| Metric | Value |
| --- | --- |
| Ground Truth findings | 3 |
| Predictions | 2 |
| Matched weight | 1.0000 |
| Soft precision | 0.5000 |
| Soft recall | 0.3333 |
| Soft F1 | 0.4000 |

#### Matched Findings

| Ground Truth | Prediction | R | L | I | M | Weighted |
| --- | --- | --- | --- | --- | --- | --- |
| M-11 — [M-11] An attacker can manipulate oracle easily | SAF-bundle-0001-002 — Permissionless spot-fed oracle can be gradually poisoned | 4/4 | 4/4 | 4/4 | 4/4 | 1.0000 |

<details>
<summary>Pair 1: M-11 — [M-11] An attacker can manipulate oracle easily ↔ SAF-bundle-0001-002 — Permissionless spot-fed oracle can be gradually poisoned</summary>

- **Ground Truth:** `M-11`
- **Prediction:** `SAF-bundle-0001-002`

#### Ground Truth locations

| File | Contract | Function | Lines |
| --- | --- | --- | --- |
| contracts/types/OraclePack.sol | OraclePackLibrary | computeInternalMedian(OraclePack,int24,uint96,int24) | 536–567 |
| contracts/PanopticPool.sol | PanopticPool | pokeOracle() | 552–558 |

#### Prediction locations

| File | Contract | Function | Lines |
| --- | --- | --- | --- |
| contracts/PanopticPool.sol | PanopticPool | pokeOracle | — |
| contracts/RiskEngine.sol | RiskEngine | computeInternalMedian | — |
| contracts/types/OraclePack.sol | OraclePackLibrary | computeInternalMedian | — |
| contracts/types/OraclePack.sol | OraclePackLibrary | clampTick | — |

#### Judge rationale

```text
R: Correctly identifies the permissionless spot-tick input, epoch-gated observation insertion, clamping limits, and progressive poisoning of the internal median/EMA oracle. L: Correctly localizes both PanopticPool.pokeOracle and OraclePackLibrary.computeInternalMedian/clampTick, including the relevant data flow. I: Correctly describes manipulation of oracle-derived solvency, liquidation, forced-exercise, and collateral outcomes, including cumulative manipulation despite clamp and epoch controls. M: Replacing instantaneous tick observations with historical TWAP/median data and adding independent price/deviation checks would prevent the ground-truth poisoning path; the supplementary controls are also technically relevant.
```

</details>

#### Unmatched Ground Truth

- M-03 — [M-03] TWAP misweights EMAs in RiskEngine, anchoring liquidation price to slow EMA and letting insolvent accounts dodge liquidation
- M-15 — [M-15] Commission share-burn distribution is JIT-capturable when `builderCode == 0` (default)

#### Unmatched Predictions

- SAF-bundle-0001-001 — Raw AMM tick influences premium and solvency accounting


## Artifacts

- [manifest.json](manifest.json)
- [judge_artifact.json](judge_artifact.json)
- [report.json](report.json)
