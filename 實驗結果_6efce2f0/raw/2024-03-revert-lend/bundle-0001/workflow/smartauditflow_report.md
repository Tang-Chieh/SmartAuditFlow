[
  {
    "finding_id": "SAF-001",
    "title": "Zero-second TWAP configuration enables spot-price manipulation of collateral valuation",
    "description": "V3Oracle.setTokenConfig() accepts twapSeconds == 0 for all non-reference token modes, including Mode.TWAP, Mode.CHAINLINK_TWAP_VERIFY, and Mode.TWAP_CHAINLINK_VERIFY. When the configured period is zero, _getReferencePoolPriceX96() reads the current Uniswap V3 pool slot0() price instead of a historical observation. The resulting spot-derived price is used by V3Oracle.getValue() to calculate the LP position value, which V3Vault._checkLoanIsHealthy() uses to determine collateralValue and loan health. This directly affects V3Vault.borrow(), where a passing health check results in transfer of the vault asset to the borrower, and V3Vault.liquidate(), where the same values determine liquidation eligibility and liquidation economics. The final _checkPoolPrice() comparison does not provide independent protection because it also reads the position pool's current spot price with a zero-second period. The issue is conditional on deployment or governance selecting a TWAP-dependent mode with twapSeconds == 0, but the source does not prevent that unsafe configuration.",
    "impact": "An attacker who can manipulate the configured reference pool, and where necessary the collateral position pool consistently, may cause collateral to be overvalued and borrow more vault assets than the position supports. After prices normalize, the vault may hold undercollateralized debt and incur losses shared by reserves or lenders. Manipulated values can also make loans appear healthy, delay liquidation, or distort liquidationValue, liquidatorCost, reserveCost, and the collateral transferred to liquidators.",
    "vulnerable_code": [
      {
        "file": "src/V3Oracle.sol",
        "contract": "V3Oracle",
        "function": "setTokenConfig",
        "start_line": null,
        "end_line": null
      },
      {
        "file": "src/V3Oracle.sol",
        "contract": "V3Oracle",
        "function": "_getReferencePoolPriceX96",
        "start_line": null,
        "end_line": null
      },
      {
        "file": "src/V3Oracle.sol",
        "contract": "V3Oracle",
        "function": "_getReferenceTokenPriceX96",
        "start_line": null,
        "end_line": null
      },
      {
        "file": "src/V3Oracle.sol",
        "contract": "V3Oracle",
        "function": "getValue",
        "start_line": null,
        "end_line": null
      },
      {
        "file": "src/V3Vault.sol",
        "contract": "V3Vault",
        "function": "_checkLoanIsHealthy",
        "start_line": null,
        "end_line": null
      },
      {
        "file": "src/V3Vault.sol",
        "contract": "V3Vault",
        "function": "borrow",
        "start_line": null,
        "end_line": null
      }
    ],
    "mitigation": "Reject zero and insufficiently short TWAP periods for every mode that uses TWAP pricing. Enforce a protocol-level minimum such as MIN_ORACLE_TWAP_SECONDS and validate the existing stored period in setOracleMode() before allowing a token to enter a TWAP-dependent mode. Prefer Chainlink-backed pricing with an independently sourced, sufficiently long Uniswap TWAP as verification. Do not use the current slot0() price as the sole collateral price source, and avoid using the same manipulable spot state for both valuation and consistency validation. Existing deployments should be reviewed for TWAP-dependent configurations with twapSeconds == 0.",
    "severity": "High"
  },
  {
    "finding_id": "SAF-002",
    "title": "LP collateral composition is calculated from manipulable spot price",
    "description": "V3Oracle._initializeState() obtains the collateral position pool's current sqrtPriceX96 and tick from pool.slot0(). V3Oracle._getAmounts() then passes that spot-derived price to LiquidityAmounts.getAmountsForLiquidity() to calculate the position's amount0 and amount1. V3Oracle.getValue() prices those spot-dependent token amounts and returns fullValue and feeValue to V3Vault._checkLoanIsHealthy(). Consequently, even when the token price source is Chainlink or a nonzero TWAP, a temporary manipulation of the position pool spot can change the token composition used in collateral valuation. The oracle's consistency check compares the derived price against the same position pool's current spot price and accepts deviations below the configured maxPoolPriceDifference, so it is not an independent historical validation of the spot-derived composition.",
    "impact": "A sufficiently economical spot manipulation can alter the reported value of an LP position and therefore affect borrowing eligibility, maximum borrowable debt, liquidation eligibility, and the amount of collateral allocated during liquidation. A resulting overvaluation may permit additional borrowing and create bad debt after the pool returns to its normal price. The magnitude depends on the position range, pool liquidity, configured deviation threshold, collateral factors, and deployment configuration.",
    "vulnerable_code": [
      {
        "file": "src/V3Oracle.sol",
        "contract": "V3Oracle",
        "function": "_initializeState",
        "start_line": null,
        "end_line": null
      },
      {
        "file": "src/V3Oracle.sol",
        "contract": "V3Oracle",
        "function": "_getAmounts",
        "start_line": null,
        "end_line": null
      },
      {
        "file": "src/V3Oracle.sol",
        "contract": "V3Oracle",
        "function": "getValue",
        "start_line": null,
        "end_line": null
      },
      {
        "file": "src/V3Oracle.sol",
        "contract": "V3Oracle",
        "function": "_checkPoolPrice",
        "start_line": null,
        "end_line": null
      },
      {
        "file": "src/V3Vault.sol",
        "contract": "V3Vault",
        "function": "_checkLoanIsHealthy",
        "start_line": null,
        "end_line": null
      }
    ],
    "mitigation": "Calculate LP token amounts using a sufficiently long, validated TWAP tick rather than the instantaneous slot0() price, or apply a conservative valuation that cannot overstate collateral during temporary spot movements. Use an independent oracle or historical observation for the position-pool consistency check instead of passing zero to _getReferencePoolPriceX96(). Consider blocking new borrowing when spot and TWAP composition or price differ beyond a conservative threshold, while retaining a separate robust path for liquidation.",
    "severity": "Medium"
  }
]
