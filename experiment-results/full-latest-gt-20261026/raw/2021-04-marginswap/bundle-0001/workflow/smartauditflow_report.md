[
  {
    "finding_id": "SAF-001",
    "title": "Liquidation valuation trusts manipulable AMM spot reserves",
    "description": "Cross-margin liquidation evaluates account collateral and debt using `belowMaintenanceThreshold()`, which calls `holdingsInPeg(account, true)` and `loanInPeg(account, true)`. These functions reach `PriceAware.getCurrentPriceInPeg(..., true)`. Both branches of the forced-price path use the current AMM quote: the stale-cache branch calls `getPriceFromAMM()`, while the recent-cache branch calls `viewCurrentPriceInPeg()`. Both functions invoke `UniswapStyleLib.getAmountsOut()`, which reads live `IUniswapV2Pair.getReserves()` values. The cached `tokenPer1k` value is therefore bypassed for the liquidation decision, and cache bounds only control whether the value is persisted; an out-of-range quote is still returned to the caller. An attacker who moves the configured AMM reserves can consequently alter the collateral/debt comparison and the subsequent `holdingsValue`, `borrowValue`, and maintainer-cut calculations. Once selected, the account is processed and deleted by `deleteAccount()`. The liquidation swaps also use AMM-derived amounts with `amountOutMin` set to zero or `amountInMax` set to `type(uint256).max`, so settlement has no meaningful slippage protection. The same spot-pricing pattern is present in the isolated-margin liquidation path when its configured price controller uses the supplied `PriceAware` implementation, although that deployment wiring is not shown.",
    "impact": "Temporary reserve manipulation can change liquidation eligibility and liquidation accounting, potentially causing incorrect liquidation of candidate accounts, incorrect residual payments and maintainer fees, and protocol losses when collateral is exchanged at an attacker-influenced AMM price. The account state is deleted after processing, and unfavorable liquidation execution can contribute to liquidation shortfalls.",
    "vulnerable_code": [
      {
        "file": "contracts/PriceAware.sol",
        "contract": "PriceAware",
        "function": "getCurrentPriceInPeg",
        "start_line": null,
        "end_line": null
      },
      {
        "file": "contracts/PriceAware.sol",
        "contract": "PriceAware",
        "function": "getPriceFromAMM",
        "start_line": null,
        "end_line": null
      },
      {
        "file": "contracts/CrossMarginAccounts.sol",
        "contract": "CrossMarginAccounts",
        "function": "belowMaintenanceThreshold",
        "start_line": null,
        "end_line": null
      },
      {
        "file": "contracts/CrossMarginLiquidation.sol",
        "contract": "CrossMarginLiquidation",
        "function": "liquidate",
        "start_line": null,
        "end_line": null
      },
      {
        "file": "contracts/MarginRouter.sol",
        "contract": "MarginRouter",
        "function": "authorizedSwapExactT4T",
        "start_line": null,
        "end_line": null
      }
    ],
    "mitigation": "Use a manipulation-resistant TWAP or independent oracle for liquidation eligibility, collateral/debt accounting, and settlement. Do not return a raw AMM spot quote from the forced liquidation-pricing path; validate freshness, deviation, and minimum liquidity before accepting any AMM observation, and use the validated price consistently throughout one liquidation. If a quote is outside configured bounds, reject it or retain the previous validated price rather than returning the raw value. Add explicit minimum-output and maximum-input slippage limits to liquidation swaps.",
    "severity": "High"
  }
]
