[
  {
    "finding_id": "SAF-001",
    "title": "Stale-market oracle falls back to attacker-influenceable spot rate",
    "description": "The market oracle is intended to mitigate short-term manipulation by blending the stored oracle rate with the latest implied rate. However, in Market._updateRateOracle, once blockTime - previousTradeTime exceeds the governance-configured rateOracleTimeWindow, the function returns lastImpliedRate directly. lastImpliedRate can be changed by permissionless lend or borrow trades through TradingAction._executeLendBorrowTrade and Market.calculateTrade. Consequently, after a sufficiently inactive period, an attacker can move the AMM implied rate and cause that rate to become the effective oracle used by CashGroup.calculateOracleRate and downstream valuation, free-collateral, nToken, residual-purchase, and liquidation logic.",
    "impact": "A manipulated implied rate may distort fCash present values, nToken collateral values, free-collateral determinations, liquidation eligibility, liquidation pricing, residual-purchase pricing, and settlement-related calculations. This could cause premature or unfavorable liquidations, incorrect collateral requirements, or other financial losses for accounts exposed to the affected market, particularly in thinly traded or inactive markets.",
    "vulnerable_code": [
      {
        "file": "contracts/internal/markets/Market.sol",
        "contract": "Market",
        "function": "_updateRateOracle",
        "start_line": null,
        "end_line": null
      }
    ],
    "mitigation": "Do not make the latest AMM-derived lastImpliedRate the sole oracle value after the oracle window expires. Replace the fallback with a rolling historical TWAP, an independently sourced reference rate, or a conservative bounded update that limits the maximum deviation from the prior oracle rate. Consider suspending valuation or liquidation when market liquidity is insufficient or the implied-rate deviation exceeds a governance-configured threshold, and add tests covering large trades after prolonged market inactivity.",
    "severity": "Medium"
  }
]
