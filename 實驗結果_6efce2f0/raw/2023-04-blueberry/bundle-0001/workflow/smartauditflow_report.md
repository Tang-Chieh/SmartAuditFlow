[
  {
    "finding_id": "SAF-001",
    "title": "Close operations accept attacker-manipulated exchange rates",
    "description": "The Curve, Convex, and Aura farming close paths perform financially sensitive conversions without meaningful minimum-output protection. CurveSpell.closePositionFarm() and ConvexSpell.closePositionFarm() call remove_liquidity_one_coin(..., 0), accepting any amount of debt tokens returned by the Curve pool. CurveSpell.closePositionFarm(), ConvexSpell.closePositionFarm(), and AuraSpell.closePositionFarm() also call swapExactTokensForTokens() with amountOutMin set to zero and an effectively unbounded deadline. AuraSpell additionally exits Balancer liquidity with a minAmountsOut array initialized entirely to zero. The ClosePosParam.sellSlippage parameter and ProtocolConfig.maxSlippageOfClose() are not applied in these paths. An attacker can influence the relevant Curve, Balancer, or router pool state before execution, causing the position assets or rewards to be exchanged at an unfavorable rate while the external calls still succeed.",
    "impact": "Position owners may receive materially fewer debt tokens from LP withdrawals and reward swaps, reducing refunds and repayment proceeds. Full closures may revert because the degraded proceeds are insufficient to repay the requested debt, leaving positions open and exposed to liquidation. Partial closures may succeed at an unfavorable rate and leave the owner with reduced value or residual debt. The transaction is atomic, so a failed close does not permanently consume collateral, but successful zero-minimum-output conversions can realize direct value loss.",
    "vulnerable_code": [
      {
        "file": "contracts/spell/CurveSpell.sol",
        "contract": "CurveSpell",
        "function": "closePositionFarm",
        "start_line": null,
        "end_line": null
      },
      {
        "file": "contracts/spell/ConvexSpell.sol",
        "contract": "ConvexSpell",
        "function": "closePositionFarm",
        "start_line": null,
        "end_line": null
      },
      {
        "file": "contracts/spell/AuraSpell.sol",
        "contract": "AuraSpell",
        "function": "closePositionFarm",
        "start_line": null,
        "end_line": null
      }
    ],
    "mitigation": "Add explicit user-supplied minimum outputs for every conversion leg. Pass a nonzero min_dy to Curve remove_liquidity_one_coin(), populate Balancer minAmountsOut with validated minimums, and pass per-swap amountOutMin values to reward-token swaps. Validate sellSlippage against bank.config().maxSlippageOfClose() and ensure it actually derives or constrains those minimums. Validate that each route starts with the expected input token and ends with the position debt token, restrict routers to approved implementations where appropriate, and replace type(uint256).max deadlines with caller-provided bounded deadlines. Expected outputs should be based on a trusted or manipulation-resistant quote and/or explicitly supplied by the user.",
    "severity": "High"
  },
  {
    "finding_id": "SAF-002",
    "title": "Balancer position entry lacks minimum BPT output protection",
    "description": "AuraSpell.openPositionFarm() joins a Balancer pool using a JoinPoolRequest with empty userData and no minimum BPT output enforcement. The function calculates poolAmountOut from current Balancer balances and total LP supply, but uses that value only to decide whether to call joinPool(); it is not passed as a minimum output or checked against the actual BPT balance increase. An attacker can alter the Balancer pool state before execution, causing the same borrowed assets to mint fewer BPT tokens while the spell continues and wraps the reduced LP balance as collateral.",
    "impact": "The user may receive less LP collateral for the borrowed assets, resulting in worse leverage and position economics. The operation may later fail its LTV or maximum-position checks, or it may succeed with reduced collateral and increased liquidation risk relative to the user's expectation.",
    "vulnerable_code": [
      {
        "file": "contracts/spell/AuraSpell.sol",
        "contract": "AuraSpell",
        "function": "openPositionFarm",
        "start_line": null,
        "end_line": null
      }
    ],
    "mitigation": "Encode the appropriate Balancer join kind and include a caller-specified minBptOut, or record the BPT balance before and after joinPool() and revert if the increase is below the required minimum. Derive the minimum from a user-approved slippage limit and a trusted or manipulation-resistant quote. Do not rely only on the later LTV or position-size checks, because those checks do not recover value lost during the join.",
    "severity": "Medium"
  },
  {
    "finding_id": "SAF-003",
    "title": "Uniswap V2 LP valuation relies on mutable spot reserves",
    "description": "UniswapV2Oracle.getPrice() calculates LP-token value directly from the current reserves returned by pool.getReserves(). No TWAP, historical observation, independent deviation check, or other manipulation-resistance mechanism is applied to those reserves. The resulting LP price can flow through CoreOracle into BlueBerryBank.getPositionValue(), getPositionRisk(), isLiquidatable(), and the post-execution solvency check in execute(). It is also used by BasicSpell._validateMaxPosSize(). The exploitation path depends on the configured external Uniswap V2 pair allowing an attacker to influence the reserve values observed by the oracle; that external reserve-update behavior is not implemented in the supplied source, but the supplied code clearly trusts the mutable spot values for security-critical collateral decisions.",
    "impact": "If the configured pair state can be sufficiently distorted, LP collateral may be overvalued, allowing an undercollateralized position to pass borrowing or post-execution checks. After the manipulated state normalizes, the position may become liquidatable and the protocol may incur unrecovered debt. Liquidation and position-size calculations may also be temporarily incorrect.",
    "vulnerable_code": [
      {
        "file": "contracts/oracle/UniswapV2Oracle.sol",
        "contract": "UniswapV2Oracle",
        "function": "getPrice",
        "start_line": null,
        "end_line": null
      },
      {
        "file": "contracts/BlueBerryBank.sol",
        "contract": "BlueBerryBank",
        "function": "getPositionValue",
        "start_line": null,
        "end_line": null
      },
      {
        "file": "contracts/BlueBerryBank.sol",
        "contract": "BlueBerryBank",
        "function": "getPositionRisk",
        "start_line": null,
        "end_line": null
      }
    ],
    "mitigation": "Replace reliance on current getReserves() values with a manipulation-resistant LP valuation. Use sufficiently long TWAP or historical observations, independently sourced underlying prices, conservative valuation haircuts, and configured deviation checks against an independent reference. Restrict routes to adequately liquid approved pairs, add reserve and liquidity sanity checks, and reject or pause valuation when the LP price changes beyond configured bounds.",
    "severity": "Medium"
  }
]
