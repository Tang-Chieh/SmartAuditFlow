[
  {
    "finding_id": "SAF-001",
    "title": "Spot-price manipulation affects Multipool deposit pricing and LP issuance",
    "description": "Multipool.deposit() uses attacker-influenceable instantaneous Uniswap V3 spot state to price existing liquidity and determine LP issuance. deposit() calls getSlots(), which reads each trusted underlying pool's slot0().sqrtPriceX96. Those values are passed to _getReserves(), where LiquidityAmounts.getAmountsForLiquidity() derives reserve0 and reserve1 from the current spot price. _optimizeAmounts() then uses those reserves to select the token deposit ratio, and deposit() calculates lpAmount from the same spot-derived reserves before _deposit() calculates underlying liquidity using the manipulated spot price again. The path has no TWAP or independent oracle valuation, spot-to-reference deviation check, or minimum LP-output control. An attacker who temporarily moves a trusted underlying pool price can therefore cause a deposit to execute using a transient reserve composition and LP exchange rate before restoring the price.",
    "impact": "A victim or attacker can be forced to provide an economically unfavorable token mix and receive LP tokens based on a transient price. Depending on the configured position ranges, liquidity, and manipulation direction, the distorted LP issuance can transfer value between the depositor and existing LP holders or cause the depositor to receive fewer LP tokens than expected.",
    "vulnerable_code": [
      {
        "file": "contracts/Multipool.sol",
        "contract": "Multipool",
        "function": "deposit",
        "start_line": null,
        "end_line": null
      },
      {
        "file": "contracts/Multipool.sol",
        "contract": "Multipool",
        "function": "getSlots",
        "start_line": null,
        "end_line": null
      },
      {
        "file": "contracts/Multipool.sol",
        "contract": "Multipool",
        "function": "_getReserves",
        "start_line": null,
        "end_line": null
      }
    ],
    "mitigation": "Use a sufficiently long Uniswap V3 TWAP or an independent oracle to value existing positions and determine the deposit ratio and LP issuance. Add a spot-versus-reference deviation check with freshness and liquidity safeguards, and add a caller-supplied minLpAmount that is checked before minting. The protected valuation should be applied consistently to reserve calculation, deposit optimization, and LP issuance.",
    "severity": "Medium"
  },
  {
    "finding_id": "SAF-002",
    "title": "Spot-price manipulation can overstate LP redemption required for Dispatcher fee claims",
    "description": "Dispatcher.withdraw() converts accrued token fees into a Multipool LP amount using spot-dependent reserves. The function calls Multipool.snapshot(), which obtains current underlying Uniswap V3 slot0() prices through getSlots() and uses them in _getReserves(). When the withdrawal amount is less than the user's tracked shares, Dispatcher.withdraw() calculates fee0 and fee1 and passes them to _estimateWithdrawalLp(). That function computes the LP amount as ((amount0 * totalSupply) / reserve0 + (amount1 * totalSupply) / reserve1) / 2. An attacker with accrued fees can temporarily move an underlying pool price so that the relevant spot-derived reserve is distorted, causing the fee entitlement to convert into an excessive LP amount. Dispatcher then reduces user.shares by that amount and calls _withdrawFee(), which burns the calculated LP amount through Multipool.withdraw() and pays the resulting assets to the caller. The withdrawal minimums are also derived from the same manipulated reserves and therefore do not provide an independent price control.",
    "impact": "The caller can receive more pooled assets than the recorded token-denominated fee entitlement warrants while consuming an inflated amount of Dispatcher shares. The resulting excess redemption is borne by the remaining Dispatcher users through reduced pooled assets or altered share accounting. The exact gain depends on the position ranges, fee balances, liquidity, and manipulation direction.",
    "vulnerable_code": [
      {
        "file": "contracts/Dispatcher.sol",
        "contract": "Dispatcher",
        "function": "withdraw",
        "start_line": null,
        "end_line": null
      },
      {
        "file": "contracts/Dispatcher.sol",
        "contract": "Dispatcher",
        "function": "_estimateWithdrawalLp",
        "start_line": null,
        "end_line": null
      },
      {
        "file": "contracts/Dispatcher.sol",
        "contract": "Dispatcher",
        "function": "_withdrawFee",
        "start_line": null,
        "end_line": null
      },
      {
        "file": "contracts/Multipool.sol",
        "contract": "Multipool",
        "function": "snapshot",
        "start_line": null,
        "end_line": null
      },
      {
        "file": "contracts/Multipool.sol",
        "contract": "Multipool",
        "function": "_getReserves",
        "start_line": null,
        "end_line": null
      }
    ],
    "mitigation": "Avoid converting accrued token fees into LP shares using current spot-derived reserves. Pay accrued fees directly where possible. If conversion is required, use a sufficiently long TWAP or independent oracle with freshness and maximum-deviation checks, and derive withdrawal minimums from the same protected valuation rather than from attacker-influenceable slot0-based reserves.",
    "severity": "High"
  }
]
