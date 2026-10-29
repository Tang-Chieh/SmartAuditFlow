[
  {
    "finding_id": "SAF-001",
    "title": "Uniswap V2 LP price relies on manipulable spot reserves",
    "description": "UniV2LpOracle.getPrice() derives the LP-token price directly from the pair's current getReserves() values using a geometric-mean valuation. These reserves are instantaneous pool state and are not time-weighted, historically bounded, or checked against an independent valuation. Reserve-changing pair operations can therefore alter the value returned by the oracle before a consumer reads it. The supplied source does not include a downstream financial consumer, so the exact exploit transaction cannot be established; however, the attacker-influenceable reserve-to-price path is present in the oracle itself.",
    "impact": "If consumed for collateral valuation, borrowing, liquidation, minting, redemption, or settlement, an attacker may cause the protocol to use an inflated or understated LP-token value. This could enable excessive borrowing against LP collateral, incorrect liquidation decisions, or incorrect asset transfers and accounting.",
    "vulnerable_code": [
      {
        "file": "src/uniswap/UniV2LPOracle.sol",
        "contract": "UniV2LpOracle",
        "function": "getPrice",
        "start_line": null,
        "end_line": null
      }
    ],
    "mitigation": "Replace the direct getReserves() dependency with a sufficiently long Uniswap V2 cumulative-price or other historical TWAP-based valuation, and require a minimum observation period. Add maximum-deviation and freshness checks against a stored or independently sourced reference price, validate that the pair is an approved canonical pair, and apply conservative collateral or valuation parameters in downstream consumers.",
    "severity": "Medium"
  }
]
