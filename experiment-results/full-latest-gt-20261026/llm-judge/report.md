# Benchmark Evaluation Report

> Derived from canonical Evaluation artifacts. This report does not execute LLM requests.

## Executive Summary

| Metric | Value |
| --- | --- |
| Report version | 0.2 |
| Benchmark version | v1 |
| Repositories | 23 |
| Ground Truth findings | 42 |
| Predictions | 23 |
| Total matched predictions | 12 |
| Total matched weight | 10.6500 |
| Pooled soft precision | 0.4630 |
| Pooled soft recall | 0.2536 |
| Macro soft F1 | 0.2584 |
| Pooled soft F1 | 0.3277 |

## Evaluation Configuration

| Field | Value |
| --- | --- |
| Matching strategy | greedy |
| Threshold | 0.5000 |
| Weight profile | end-to-end-v2 |
| Judge model | openai-codex/gpt-5.6-luna |
| Judge prompt version | benchmark-judge-v3 |
| Detector version | smartauditflow-price-manipulation-full-24-v1 |
| Detector model | openai-codex/gpt-5.6-luna |
| Manifest SHA-256 | d7d6571a054cd4a9b11d74c6efe44faa1d75bb68d29d0c9f6b7da949a4334d0a |

## Repository Summary

| Repository | Ground Truth | Predictions | Matched Predictions | Matched weight | Precision | Recall | Soft F1 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `2021-04-marginswap` | 1 | 1 | 1 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| `2021-07-spartan` | 3 | 2 | 1 | 0.6500 | 0.3250 | 0.2167 | 0.2600 |
| `2021-08-notional` | 2 | 2 | 1 | 0.5500 | 0.2750 | 0.2750 | 0.2750 |
| `2021-11-malt` | 3 | 2 | 2 | 2.0000 | 1.0000 | 0.6667 | 0.8000 |
| `2021-12-vader` | 4 | 4 | 3 | 2.9000 | 0.7250 | 0.7250 | 0.7250 |
| `2022-01-behodler` | 2 | 1 | 1 | 1.0000 | 1.0000 | 0.5000 | 0.6667 |
| `2022-01-sandclock` | 2 | 0 | 0 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| `2022-08-sentiment` | 2 | 0 | 0 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| `2022-09-notional` | 1 | 1 | 0 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| `2022-11-paraspace` | 4 | 0 | 0 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| `2022-11-telcoin` | 1 | 0 | 0 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| `2023-03-olympus` | 1 | 0 | 0 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| `2023-04-blueberry` | 1 | 3 | 0 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| `2023-05-ussd` | 2 | 1 | 1 | 1.0000 | 1.0000 | 0.5000 | 0.6667 |
| `2023-06-lybra` | 1 | 1 | 0 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| `2023-06-real-wagmi` | 1 | 1 | 1 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| `2023-06-tokemak` | 1 | 0 | 0 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| `2023-08-dopex` | 2 | 0 | 0 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| `2024-03-abracadabra-money` | 2 | 0 | 0 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| `2024-03-revert-lend` | 1 | 1 | 1 | 0.5500 | 0.5500 | 0.5500 | 0.5500 |
| `2024-03-woofi-swap` | 1 | 1 | 0 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| `2024-04-panoptic` | 1 | 2 | 0 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| `2025-12-panoptic` | 3 | 0 | 0 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |

## Repository Details

### `2021-04-marginswap`

| Metric | Value |
| --- | --- |
| Ground Truth findings | 1 |
| Predictions | 1 |
| Matched weight | 1.0000 |
| Soft precision | 1.0000 |
| Soft recall | 1.0000 |
| Soft F1 | 1.0000 |

#### Matched Findings

| Ground Truth | Prediction | R | L | I | M | Weighted |
| --- | --- | --- | --- | --- | --- | --- |
| H-03 — [H-03] Price feed can be manipulated | SAF-bundle-0001-001 — Liquidation valuation trusts manipulable AMM spot reserves | 4/4 | 4/4 | 4/4 | 4/4 | 1.0000 |

<details>
<summary>Pair 1: H-03 — [H-03] Price feed can be manipulated ↔ SAF-bundle-0001-001 — Liquidation valuation trusts manipulable AMM spot reserves</summary>

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
| contracts/PriceAware.sol | PriceAware | getPriceFromAMM | — |
| contracts/CrossMarginAccounts.sol | CrossMarginAccounts | belowMaintenanceThreshold | — |
| contracts/CrossMarginLiquidation.sol | CrossMarginLiquidation | liquidate | — |
| contracts/MarginRouter.sol | MarginRouter | authorizedSwapExactT4T | — |

#### Judge rationale

```text
R: Correctly identifies the root cause: forced pricing relies on a manipulable current Uniswap-style AMM spot quote derived from live reserves, allowing flash-loan reserve distortion.
L: Correctly localizes the vulnerable PriceAware.getCurrentPriceInPeg and getPriceFromAMM path, and also identifies relevant liquidation callers and downstream swap execution.
I: Correctly describes manipulated prices affecting liquidation eligibility, collateral/debt valuation, liquidation accounting, and potentially causing protocol losses, consistent with the ground-truth impact on borrowing and liquidations.
M: Correctly recommends replacing the raw spot quote with a manipulation-resistant TWAP or independent oracle and consistently using the validated price. The additional slippage protections are also relevant hardening.
```

</details>

#### Unmatched Ground Truth

No unmatched Ground Truth findings.

#### Unmatched Predictions

No unmatched predictions.

### `2021-07-spartan`

| Metric | Value |
| --- | --- |
| Ground Truth findings | 3 |
| Predictions | 2 |
| Matched weight | 0.6500 |
| Soft precision | 0.3250 |
| Soft recall | 0.2167 |
| Soft F1 | 0.2600 |

#### Matched Findings

| Ground Truth | Prediction | R | L | I | M | Weighted |
| --- | --- | --- | --- | --- | --- | --- |
| H-06 — [H-06] SynthVault rewards can be gamed | SAF-bundle-0001-001 — AMM spot-price manipulation inflates stored LP valuation weights | 2/4 | 2/4 | 3/4 | 4/4 | 0.6500 |

<details>
<summary>Pair 1: H-06 — [H-06] SynthVault rewards can be gamed ↔ SAF-bundle-0001-001 — AMM spot-price manipulation inflates stored LP valuation weights</summary>

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
| contracts/Utils.sol | Utils | getPoolShareWeight | — |
| contracts/Pool.sol | Pool | swapTo | — |
| contracts/Pool.sol | Pool | sync | — |
| contracts/DaoVault.sol | DaoVault | increaseWeight | — |
| contracts/Dao.sol | Dao | calcReward | — |

#### Judge rationale

```text
R: Correctly identifies the broad causal mechanism of manipulating an AMM spot valuation, persisting an inflated weight, and using it for rewards, but describes LP/DaoVault/BondVault weighting rather than SynthVault's synth-to-BASE conversion. L: Identifies an adjacent Utils spot-weight path and reward calculation, but not SynthVault._deposit() or Utils.calcSpotValueInBase()/calcSpotValueInBaseWithPool(). I: Correctly captures inflated persisted weight diverting reserve-funded rewards, with only scope/asset and vault differences; the governance-weight claim is additional and not the ground-truth impact. M: TWAP or an independent manipulation-resistant valuation, avoiding single-spot persisted weights, and delayed snapshots would prevent the ground-truth vulnerability.
```

</details>

#### Unmatched Ground Truth

- H-05 — [H-05] Synth realise is vulnerable to flash loan attacks
- M-14 — [M-14] BondVault `BASE` incentive can be gamed

#### Unmatched Predictions

- SAF-bundle-0001-002 — Swap entry points lack minimum-output protection against reserve manipulation

### `2021-08-notional`

| Metric | Value |
| --- | --- |
| Ground Truth findings | 2 |
| Predictions | 2 |
| Matched weight | 0.5500 |
| Soft precision | 0.2750 |
| Soft recall | 0.2750 |
| Soft F1 | 0.2750 |

#### Matched Findings

| Ground Truth | Prediction | R | L | I | M | Weighted |
| --- | --- | --- | --- | --- | --- | --- |
| H-10 — [H-10] Liquidity token value can be manipulated | SAF-bundle-0001-002 — Callback-composed nToken minting values liquidity positions from manipulable spot reserves | 2/4 | 3/4 | 0/4 | 4/4 | 0.5500 |

<details>
<summary>Pair 1: H-10 — [H-10] Liquidity token value can be manipulated ↔ SAF-bundle-0001-002 — Callback-composed nToken minting values liquidity positions from manipulable spot reserves</summary>

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
| contracts/external/actions/nTokenMintAction.sol | nTokenMintAction | calculateTokensToMint | — |
| contracts/internal/nTokenHandler.sol | nTokenHandler | getNTokenAssetPV | — |
| contracts/internal/valuation/AssetHandler.sol | AssetHandler | getLiquidityTokenValue | — |
| contracts/external/actions/ERC1155Action.sol | ERC1155Action | safeTransferFrom | — |
| contracts/external/actions/ERC1155Action.sol | ERC1155Action | _checkPostTransferEvent | — |

#### Judge rationale

```text
R: Correctly identifies that getLiquidityTokenValue derives value from manipulable current reserve ratios while the fCash component uses a lagged oracle, but omits the material asymmetric haircut mechanism and instead frames it as mint overvaluation. L: Correctly names AssetHandler.getLiquidityTokenValue and the valuation path, though it omits the more specific getHaircutCashClaims and _calcToken operations. I: Claims excess nToken minting and dilution rather than the ground-truth collateral reduction causing an otherwise adequately collateralized account to become liquidatable; this is not the same exploit outcome. M: Using a manipulation-resistant TWAP or independent reference for liquidity-token valuation, with deviation checks, would prevent the ground-truth reserve-manipulation vulnerability.
```

</details>

#### Unmatched Ground Truth

- M-07 — [M-07] Attackers can force liquidations by borrowing large amounts of an asset.

#### Unmatched Predictions

- SAF-bundle-0001-001 — nToken redemption executes against manipulable AMM state without output protection

### `2021-11-malt`

| Metric | Value |
| --- | --- |
| Ground Truth findings | 3 |
| Predictions | 2 |
| Matched weight | 2.0000 |
| Soft precision | 1.0000 |
| Soft recall | 0.6667 |
| Soft F1 | 0.8000 |

#### Matched Findings

| Ground Truth | Prediction | R | L | I | M | Weighted |
| --- | --- | --- | --- | --- | --- | --- |
| M-25 — [M-25] AMM Pool Can Be Drained Using a Flash Loan and Calling `stabilize` | SAF-bundle-0001-001 — AMM spot manipulation controls stabilization sizing and execution | 4/4 | 4/4 | 4/4 | 4/4 | 1.0000 |
| M-22 — [M-22] `_calculateMaltRequiredForExit` Uses Spot Price To Calculate Malt Quantity In `exitEarly` | SAF-bundle-0001-002 — Manipulable AMM spot price determines auction escape-hatch payouts | 4/4 | 4/4 | 4/4 | 4/4 | 1.0000 |

<details>
<summary>Pair 1: M-25 — [M-25] AMM Pool Can Be Drained Using a Flash Loan and Calling \`stabilize\` ↔ SAF-bundle-0001-001 — AMM spot manipulation controls stabilization sizing and execution</summary>

- **Ground Truth:** `M-25`
- **Prediction:** `SAF-bundle-0001-001`

#### Ground Truth locations

| File | Contract | Function | Lines |
| --- | --- | --- | --- |
| src/contracts/DexHandlers/UniswapHandler.sol | UniswapHandler | _calculateTradeSize(address,address,uint256) | 250–275 |

#### Prediction locations

| File | Contract | Function | Lines |
| --- | --- | --- | --- |
| contracts/DexHandlers/UniswapHandler.sol | UniswapHandler | _calculateTradeSize | — |
| contracts/DexHandlers/UniswapHandler.sol | UniswapHandler | buyMalt | — |
| contracts/DexHandlers/UniswapHandler.sol | UniswapHandler | sellMalt | — |
| contracts/StabilizerNode.sol | StabilizerNode | _distributeSupply | — |
| contracts/StabilizerNode.sol | StabilizerNode | _startAuction | — |
| contracts/Auction.sol | Auction | _triggerAuction | — |

#### Judge rationale

```text
R: Correctly identifies that live Uniswap reserves, rather than a manipulation-resistant price, determine stabilization trade sizing after the moving-average decision. L: Correctly localizes _calculateTradeSize and the related stabilization/distribution and swap paths. I: Correctly describes flash-loan reserve manipulation causing excessive minting/selling, distorted stabilization, and protocol value loss, including incorrectly sized auctions. M: TWAP/oracle pricing, deviation checks, trade caps, and bounded swap outputs would prevent the ground-truth reserve-manipulation vulnerability.
```

</details>

<details>
<summary>Pair 2: M-22 — [M-22] \`_calculateMaltRequiredForExit\` Uses Spot Price To Calculate Malt Quantity In \`exitEarly\` ↔ SAF-bundle-0001-002 — Manipulable AMM spot price determines auction escape-hatch payouts</summary>

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
| contracts/AuctionEscapeHatch.sol | AuctionEscapeHatch | _calculateMaltRequiredForExit | — |
| contracts/AuctionEscapeHatch.sol | AuctionEscapeHatch | exitEarly | — |
| contracts/AuctionEscapeHatch.sol | AuctionEscapeHatch | earlyExitReturn | — |
| contracts/DexHandlers/UniswapHandler.sol | UniswapHandler | maltMarketPrice | — |
| contracts/DexHandlers/UniswapHandler.sol | UniswapHandler | sellMalt | — |

#### Judge rationale

```text
R: Correctly identifies that maltMarketPrice() derives price from manipulable current Uniswap reserves and that this price controls early-exit settlement. L: Correctly localizes maltMarketPrice(), _calculateMaltRequiredForExit(), exitEarly(), and the related sale path; earlyExitReturn() is also a relevant dependent view. I: Correctly describes reserve manipulation causing incorrect early-exit payouts and minted Malt, enabling excessive collateral extraction, with the same zero-slippage-bound context. M: Replacing the spot price with a validated TWAP or independent oracle, with freshness/deviation checks and bounded execution, directly prevents the ground-truth vulnerability.
```

</details>

#### Unmatched Ground Truth

- M-30 — [M-30] Malt Protocol Uses Stale Results From `MaltDataLab` Which Can Be Abused By Users

#### Unmatched Predictions

No unmatched predictions.

### `2021-12-vader`

| Metric | Value |
| --- | --- |
| Ground Truth findings | 4 |
| Predictions | 4 |
| Matched weight | 2.9000 |
| Soft precision | 0.7250 |
| Soft recall | 0.7250 |
| Soft F1 | 0.7250 |

#### Matched Findings

| Ground Truth | Prediction | R | L | I | M | Weighted |
| --- | --- | --- | --- | --- | --- | --- |
| H-07 — [H-07] Synth minting and redemption use manipulable pool reserves to drain native assets. | SAF-bundle-0001-001 — Synth issuance and redemption use manipulable AMM spot reserves | 4/4 | 4/4 | 4/4 | 4/4 | 1.0000 |
| H-06 — [H-06] LPs of VaderPoolV2 can manipulate pool reserves to extract funds from the reserve. | SAF-bundle-0001-003 — LP impermanent-loss reimbursement is calculated from manipulable redemption values | 4/4 | 4/4 | 4/4 | 4/4 | 1.0000 |
| M-06 — [M-06] Manipulated pool reserves can make the oracle rely on a single pair. | SAF-bundle-0001-004 — LiquidityBasedTWAP uses attacker-influenced spot weights and lacks effective freshness validation | 4/4 | 4/4 | 3/4 | 3/4 | 0.9000 |

<details>
<summary>Pair 1: H-07 — [H-07] Synth minting and redemption use manipulable pool reserves to drain native assets. ↔ SAF-bundle-0001-001 — Synth issuance and redemption use manipulable AMM spot reserves</summary>

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
R: Correctly identifies that minting and burning use manipulable current pool reserves via VaderMath.calculateSwap. L: Correctly localizes VaderPoolV2.mintSynth and burnSynth, with the relevant reserve-based pricing path. I: Correctly describes reserve-price manipulation leading to over-issuance, over-redemption, and native-reserve depletion. M: Oracle/TWAP pricing, validation bounds, and redemption limits directly address the vulnerability; the extra balance check is also sound.
```

</details>

<details>
<summary>Pair 2: H-06 — [H-06] LPs of VaderPoolV2 can manipulate pool reserves to extract funds from the reserve. ↔ SAF-bundle-0001-003 — LP impermanent-loss reimbursement is calculated from manipulable redemption values</summary>

- **Ground Truth:** `H-06`
- **Prediction:** `SAF-bundle-0001-003`

#### Ground Truth locations

| File | Contract | Function | Lines |
| --- | --- | --- | --- |
| contracts/dex-v2/pool/BasePoolV2.sol | BasePoolV2 | _burn(uint256,address) | 203–246 |
| contracts/dex-v2/pool/VaderPoolV2.sol | VaderPoolV2 | burn(uint256,address) | 265–296 |
| contracts/dex/math/VaderMath.sol | VaderMath | calculateLoss(uint256,uint256,uint256,uint256) | 72–92 |
| contracts/dex-v2/router/VaderRouterV2.sol | VaderRouterV2 | removeLiquidity(address,address,uint256,uint256,uint256,address,uint256) | 173–221 |

#### Prediction locations

| File | Contract | Function | Lines |
| --- | --- | --- | --- |
| contracts/dex-v2/pool/BasePoolV2.sol | BasePoolV2 | _burn | — |
| contracts/dex-v2/pool/VaderPoolV2.sol | VaderPoolV2 | burn | — |
| contracts/dex/pool/BasePool.sol | BasePool | _burn | — |
| contracts/dex/pool/VaderPool.sol | VaderPool | burn | — |
| contracts/reserve/VaderReserve.sol | VaderReserve | reimburseImpermanentLoss | — |

#### Judge rationale

```text
R: Correctly identifies that redemption amounts derived from manipulable current reserves/balances are passed to calculateLoss, enabling inflated coveredLoss. L: Correctly localizes BasePoolV2._burn, VaderPoolV2.burn, VaderMath-related loss flow, and router/reserve reimbursement; the additional legacy-path references do not detract. I: Correctly describes reserve-funded VADER reimbursement being overstated through temporary AMM manipulation and potentially extracting reserve assets. M: TWAP/independent-oracle valuation, freshness/deviation controls, caps, and delayed validated observations effectively prevent the ground-truth flaw.
```

</details>

<details>
<summary>Pair 3: M-06 — [M-06] Manipulated pool reserves can make the oracle rely on a single pair. ↔ SAF-bundle-0001-004 — LiquidityBasedTWAP uses attacker-influenced spot weights and lacks effective freshness validation</summary>

- **Ground Truth:** `M-06`
- **Prediction:** `SAF-bundle-0001-004`

#### Ground Truth locations

| File | Contract | Function | Lines |
| --- | --- | --- | --- |
| contracts/lbt/LiquidityBasedTWAP.sol | LiquidityBasedTWAP | _updateUSDVPrice(IERC20,ExchangePair,uint256) | 353–383 |

#### Prediction locations

| File | Contract | Function | Lines |
| --- | --- | --- | --- |
| contracts/lbt/LiquidityBasedTWAP.sol | LiquidityBasedTWAP | _updateVaderPrice | — |
| contracts/lbt/LiquidityBasedTWAP.sol | LiquidityBasedTWAP | _updateUSDVPrice | — |
| contracts/lbt/LiquidityBasedTWAP.sol | LiquidityBasedTWAP | syncVaderPrice | — |
| contracts/lbt/LiquidityBasedTWAP.sol | LiquidityBasedTWAP | syncUSDVPrice | — |
| contracts/lbt/LiquidityBasedTWAP.sol | LiquidityBasedTWAP | getChainlinkPrice | — |
| contracts/tokens/USDV.sol | USDV | mint | — |
| contracts/tokens/USDV.sol | USDV | burn | — |

#### Judge rationale

```text
R: Correctly identifies that a single synchronization-time reserve snapshot determines pair liquidity weights, allowing manipulated reserves to dominate the aggregate oracle. L: Explicitly identifies LiquidityBasedTWAP._updateUSDVPrice and syncUSDVPrice, the ground-truth path; the additional VADER paths are not harmful. I: Correctly describes biased aggregate prices and notes the missing Chainlink freshness checks, but broadens the outcome to excess issuance/redemption and reimbursement without clearly stating the ground-truth condition that the dominated pair's faulty/deprecated feed must be relied upon; direct loss is not established. M: Time-weighted reserve-value observations, freshness/deviation checks, minimum-liquidity thresholds, and bounded/coherent updates are directionally effective against the snapshot-weight attack, though the proposal omits the specific invariant-and-fair-asset-price reserve calculation and is therefore not fully complete.
```

</details>

#### Unmatched Ground Truth

- H-04 — [H-04] Vader TWAP weights can be corrupted and price queries can be forced to revert.

#### Unmatched Predictions

- SAF-bundle-0001-002 — AMM reserve manipulation can reduce liquidity minted to depositors

### `2022-01-behodler`

| Metric | Value |
| --- | --- |
| Ground Truth findings | 2 |
| Predictions | 1 |
| Matched weight | 1.0000 |
| Soft precision | 1.0000 |
| Soft recall | 0.5000 |
| Soft F1 | 0.6667 |

#### Matched Findings

| Ground Truth | Prediction | R | L | I | M | Weighted |
| --- | --- | --- | --- | --- | --- | --- |
| H-05 — [H-05] Flash loan price manipulation in purchasePyroFlan() | SAF-bundle-0001-001 — Manipulable AMM spot balances control PyroFlan issuance | 4/4 | 4/4 | 4/4 | 4/4 | 1.0000 |

<details>
<summary>Pair 1: H-05 — [H-05] Flash loan price manipulation in purchasePyroFlan() ↔ SAF-bundle-0001-001 — Manipulable AMM spot balances control PyroFlan issuance</summary>

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
R: Correctly identifies attacker manipulation of instantaneous FLAN/stablecoin AMM balances, the resulting manipulation of priceBefore and tiltedPrice, and the insufficiency of the per-call acceptableHighestPrice cap. L: Correctly localizes the issue to FlanBackstop.purchasePyroFlan and its price-derived minting path. I: Correctly describes excess PyroFlan issuance, dilution, and potential attacker value extraction; the stated downstream extraction paths are consistent with the ground-truth consequence. M: Correctly proposes a TWAP or independent oracle and appropriately retains the price ceiling only as a secondary control.
```

</details>

#### Unmatched Ground Truth

- H-07 — [H-07] LP pricing formula is vulnerable to flashloan manipulation

#### Unmatched Predictions

No unmatched predictions.

### `2022-01-sandclock`

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

- H-03 — [H-03] Vaults with non-UST underlying asset vulnerable to flash loan attack on curve pool
- M-11 — [M-11] Changing a strategy can be bricked

#### Unmatched Predictions

No unmatched predictions.

### `2022-08-sentiment`

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

- M-10 — M-10: ERC4626Oracle Vulnerable To Price Manipulation
- H-1 — H-1: LToken pricePerShare can be manipulated by an early depositor

#### Unmatched Predictions

No unmatched predictions.

### `2022-09-notional`

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

- M-7 — [M-7] Gain From Balancer Vaults Can Be Stolen

#### Unmatched Predictions

- SAF-bundle-0001-001 — Normal vault deposits accept BPT amounts determined by manipulable pool state

### `2022-11-paraspace`

| Metric | Value |
| --- | --- |
| Ground Truth findings | 4 |
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

- H-05 — [H-05] Attacker can manipulate low TVL Uniswap V3 pool to borrow and swap to make Lending Pool in loss
- M-04 — [M-04] Fallback oracle is using spot price in Uniswap liquidity pool, which is very vulnerable to flashloan price manipulation
- M-05 — [M-05] Front-running admin setPrice call allows a single compromised oracle to set any price, allowing the oracle manipulator to drain all protocol funds
- M-22 — [M-22] Price can deviate by much more than maxDeviationRate

#### Unmatched Predictions

No unmatched predictions.

### `2022-11-telcoin`

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

- H-1 — H-1: Flashloan `TEL` tokens to stake and exit in the same block can fake a huge amount of stake with minimal material cost

#### Unmatched Predictions

No unmatched predictions.

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

- SAF-bundle-0001-001 — Zero minimum output permits manipulated LP redemptions during close
- SAF-bundle-0001-002 — Reward-token swaps accept arbitrarily poor AMM execution
- SAF-bundle-0001-003 — Caller-controlled zero LP-mint minimum permits manipulated leveraged deposits

### `2023-05-ussd`

| Metric | Value |
| --- | --- |
| Ground Truth findings | 2 |
| Predictions | 1 |
| Matched weight | 1.0000 |
| Soft precision | 1.0000 |
| Soft recall | 0.5000 |
| Soft F1 | 0.6667 |

#### Matched Findings

| Ground Truth | Prediction | R | L | I | M | Weighted |
| --- | --- | --- | --- | --- | --- | --- |
| H-5 — H-5: Price calculation susceptible to flashloan exploits | SAF-bundle-0001-001 — Rebalancer trusts manipulable Uniswap V3 spot price | 4/4 | 4/4 | 4/4 | 4/4 | 1.0000 |

<details>
<summary>Pair 1: H-5 — H-5: Price calculation susceptible to flashloan exploits ↔ SAF-bundle-0001-001 — Rebalancer trusts manipulable Uniswap V3 spot price</summary>

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
| contracts/USSDRebalancer.sol | USSDRebalancer | getSupplyProportion | — |
| contracts/USSD.sol | USSD | UniV3SwapInput | — |

#### Judge rationale

```text
R: Correctly identifies reliance on Uniswap V3 slot0().sqrtPriceX96 as a manipulable spot price without TWAP protection, including flash-loan/temporary pool-price manipulation. L: Correctly localizes the primary vulnerable path to USSDRebalancer.getOwnValuation() and rebalance(); the additional swap-related locations are relevant to the described propagation. I: Correctly states that an attacker can manipulate the valuation and induce attacker-influenced minting, burning, collateral sales, and swaps, matching the ground-truth consequence. M: Recommends replacing the spot price with a TWAP or independent oracle and adds sound validation and slippage protections; the proposed mitigation prevents the ground-truth vulnerability.
```

</details>

#### Unmatched Ground Truth

- H-9 — H-9: Uniswap v3 pool token balance proportion does not necessarily correspond to the price, and it is easy to manipulate.

#### Unmatched Predictions

No unmatched predictions.

### `2023-06-lybra`

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

- M-13 — [M-13] It is possible to manipulate WETH/LBR pair to claim reward of the users which shouldn't be claimed

#### Unmatched Predictions

- SAF-bundle-0001-001 — Curve spot price manipulation can distort protocol reward conversion

### `2023-06-real-wagmi`

| Metric | Value |
| --- | --- |
| Ground Truth findings | 1 |
| Predictions | 1 |
| Matched weight | 1.0000 |
| Soft precision | 1.0000 |
| Soft recall | 1.0000 |
| Soft F1 | 1.0000 |

#### Matched Findings

| Ground Truth | Prediction | R | L | I | M | Weighted |
| --- | --- | --- | --- | --- | --- | --- |
| H-3 — H-3: Usage of `slot0` is extremely easy to manipulate | SAF-bundle-0001-001 — Spot-price manipulation can misprice LP-token issuance | 4/4 | 4/4 | 4/4 | 4/4 | 1.0000 |

<details>
<summary>Pair 1: H-3 — H-3: Usage of \`slot0\` is extremely easy to manipulate ↔ SAF-bundle-0001-001 — Spot-price manipulation can misprice LP-token issuance</summary>

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
| contracts/Multipool.sol | Multipool | deposit | — |

#### Judge rationale

```text
R: Correctly identifies the root cause: attacker-manipulable Uniswap V3 spot `slot0` data is used to value positions, optimize deposits, and calculate LP issuance. L: Correctly localizes the path through `deposit()`, `getSlots()`, `_getReserves()`, and `LiquidityAmounts.getAmountsForLiquidity()`, including the relevant LP minting calculation. I: Correctly describes distorted reserve/share calculations, incorrect LP issuance, and dilution or value transfer affecting existing liquidity providers. M: Correctly recommends manipulation-resistant TWAP/oracle pricing, deviation and freshness checks, and consistent use of the protected reference across valuation, optimization, and minting.
```

</details>

#### Unmatched Ground Truth

No unmatched Ground Truth findings.

#### Unmatched Predictions

No unmatched predictions.

### `2023-06-tokemak`

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

- H-15 — H-15: Maverick oracle can be manipulated

#### Unmatched Predictions

No unmatched predictions.

### `2023-08-dopex`

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

- M-08 — [M-08] `reLPContract.reLP()` is susceptible to sandwich attack due to user control over `bond()`
- M-09 — [M-09] A malicious early depositor can manipulate the LP-Token price per share to take an unfair share of future user deposits

#### Unmatched Predictions

No unmatched predictions.

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
| Predictions | 1 |
| Matched weight | 0.5500 |
| Soft precision | 0.5500 |
| Soft recall | 0.5500 |
| Soft F1 | 0.5500 |

#### Matched Findings

| Ground Truth | Prediction | R | L | I | M | Weighted |
| --- | --- | --- | --- | --- | --- | --- |
| M-19 — [M-19] `V3Oracle` susceptible to price manipulation | SAF-bundle-0001-001 — Zero-duration TWAP mode permits spot-price manipulation of collateral valuation | 2/4 | 2/4 | 3/4 | 2/4 | 0.5500 |

<details>
<summary>Pair 1: M-19 — [M-19] \`V3Oracle\` susceptible to price manipulation ↔ SAF-bundle-0001-001 — Zero-duration TWAP mode permits spot-price manipulation of collateral valuation</summary>

- **Ground Truth:** `M-19`
- **Prediction:** `SAF-bundle-0001-001`

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
| src/V3Oracle.sol | V3Oracle | setTokenConfig | — |
| src/V3Oracle.sol | V3Oracle | _getReferencePoolPriceX96 | — |
| src/V3Oracle.sol | V3Oracle | _checkPoolPrice | — |
| src/V3Vault.sol | V3Vault | _checkLoanIsHealthy | — |

#### Judge rationale

```text
R: Identifies a related spot-price manipulation mechanism and correctly notes that permissive price verification can allow valuation distortion. However, it centers on the conditional zero-duration TWAP configuration and jointly manipulable reference pool, whereas the ground truth's core flaw is that position amounts are calculated from the current position-pool slot0 price despite oracle-derived valuation, especially harming tight-range positions.
L: Correctly references V3Oracle valuation, _checkPoolPrice(), and the vault health-check path, but does not localize the principal vulnerable operations in getPositionBreakdown(), _initializeState(), and _getAmounts(), where current slot0 pricing is used to calculate the position amounts.
I: Correctly describes inflated collateral valuation enabling excess borrowing and potentially leaving the vault undercollateralized after price recovery. The claim is conditionally framed and includes additional liquidation effects, but the primary borrowing impact is materially consistent with the ground truth.
M: The proposed minimum TWAP duration, independent oracle, and anti-self-reference controls are directionally useful, but they do not directly require amount0 and amount1 to be calculated from the oracle-derived price. Thus, the current-spot amount-calculation flaw could remain even with a nonzero TWAP.
```

</details>

#### Unmatched Ground Truth

No unmatched Ground Truth findings.

#### Unmatched Predictions

No unmatched predictions.

### `2024-03-woofi-swap`

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

- H-1 — H-1: Pool can be drained

#### Unmatched Predictions

- SAF-bundle-0001-001 — Stale Chainlink fallback prices are accepted for WooPP swaps

### `2024-04-panoptic`

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

- M-01 — [M-01] `PanopticFactory` uses spot price when deploying new pools, resulting in liquidity manipulation when minting

#### Unmatched Predictions

- SAF-bundle-0001-001 — Liquidation payouts and liquidator solvency use an unvalidated post-burn spot price
- SAF-bundle-0001-002 — Forced-exercise compensation is calculated from an unvalidated spot tick

### `2025-12-panoptic`

| Metric | Value |
| --- | --- |
| Ground Truth findings | 3 |
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

- M-11 — [M-11] An attacker can manipulate oracle easily
- M-03 — [M-03] TWAP misweights EMAs in RiskEngine, anchoring liquidation price to slow EMA and letting insolvent accounts dodge liquidation
- M-15 — [M-15] Commission share-burn distribution is JIT-capturable when `builderCode == 0` (default)

#### Unmatched Predictions

No unmatched predictions.


## Artifacts

- [manifest.json](manifest.json)
- [judge_artifact.json](judge_artifact.json)
- [report.json](report.json)
