[
  {
    "finding_id": "SAF-001",
    "title": "Spot-price manipulation affects reserve valuation and LP accounting",
    "description": "Multipool._getReserves() values concentrated-liquidity positions using the instantaneous sqrtPriceX96 and tick obtained from each underlying Uniswap V3 pool through getSlots() and slot0(). These spot-derived reserves are used by Multipool.deposit() to optimize deposit ratios and calculate LP tokens minted, and by Multipool.snapshot() and Dispatcher deposit/withdraw flows to convert accrued token fees into LP-share withdrawals. The current tick also determines the branch used by _getFeeGrowthInside(), affecting pending-fee calculations. An attacker can temporarily manipulate an underlying pool price, cause a deposit or Dispatcher fee settlement during the manipulated state, and then restore the price, resulting in incorrect LP issuance, fee settlement, or share accounting.",
    "impact": "Users may receive too many or too few LP tokens, provide an unfavorable token composition, or have an incorrect number of tracked shares removed for fee claims. Value may be redistributed between the interacting user and existing LP holders. Reserve and claim estimates can also become materially incorrect during manipulation.",
    "vulnerable_code": [
      {
        "file": "contracts/Multipool.sol",
        "contract": "Multipool",
        "function": "_getReserves",
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
        "function": "deposit",
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
        "function": "deposit",
        "start_line": null,
        "end_line": null
      },
      {
        "file": "contracts/Dispatcher.sol",
        "contract": "Dispatcher",
        "function": "withdraw",
        "start_line": null,
        "end_line": null
      }
    ],
    "mitigation": "Use a sufficiently long TWAP or another manipulation-resistant oracle for position valuation, pending-fee determination, deposit optimization, LP minting, and Dispatcher fee/share conversion. Alternatively, compare spot prices against validated TWAP prices and revert when deviation exceeds a protocol-defined bound. Prefer paying accrued token0 and token1 fees directly rather than converting them into LP shares using spot-derived reserve ratios. Add an explicit user-provided minimum LP-output or equivalent execution bound for deposits.",
    "severity": "High"
  },
  {
    "finding_id": "SAF-002",
    "title": "Strategy ranges are initialized from manipulable spot ticks",
    "description": "Multipool._initializeStrategy() reads each underlying pool's instantaneous slot0 tick and uses it in _getTicksForPosition() to determine the lower and upper ticks of every strategy position. The same unvalidated spot sqrt price is then used by _calcLiquidityAmountToDeposit() when opening liquidity. During the first owner deposit or an operator-authorized rebalance, an attacker can temporarily move an underlying pool price, causing the Multipool to establish ranges around the manipulated tick. Once the price returns, the positions may be out of range or have an unfavorable token composition.",
    "impact": "Existing LP holders may suffer reduced fee generation, misallocated liquidity, unfavorable asset exposure, and losses or additional costs when the strategy is later corrected. A rebalance can successfully execute while establishing liquidity at an attacker-influenced price.",
    "vulnerable_code": [
      {
        "file": "contracts/Multipool.sol",
        "contract": "Multipool",
        "function": "_initializeStrategy",
        "start_line": null,
        "end_line": null
      },
      {
        "file": "contracts/Multipool.sol",
        "contract": "Multipool",
        "function": "_getTicksForPosition",
        "start_line": null,
        "end_line": null
      },
      {
        "file": "contracts/Multipool.sol",
        "contract": "Multipool",
        "function": "_calcLiquidityAmountToDeposit",
        "start_line": null,
        "end_line": null
      },
      {
        "file": "contracts/Multipool.sol",
        "contract": "Multipool",
        "function": "rebalanceAll",
        "start_line": null,
        "end_line": null
      }
    ],
    "mitigation": "Derive position centers and ranges from a sufficiently long TWAP for each underlying strategy pool, or require the current spot tick and sqrt price to remain within a strict deviation from the corresponding TWAP before initialization. Apply the validation independently to every pool used by the strategy, and use validated pricing for both range selection and liquidity calculation. Add rebalance bounds for acceptable position centers and resulting token composition.",
    "severity": "Medium"
  },
  {
    "finding_id": "SAF-003",
    "title": "One-sided TWAP validation can accept an unfavorable rebalance swap",
    "description": "Multipool.getAmountOut() calculates the expected swap output from the arithmetic mean tick of the hard-coded fee-500 underlying pool over twapDuration. In rebalanceAll(), the execution is rejected only when actual output is below the oracle-derived output and the shortfall exceeds maxTwapDeviation. If an attacker manipulates the underlying pool sufficiently to make the TWAP quote artificially low for the swap direction, an unfavorable actual output can still satisfy amountOut >= swappedOut, causing the slippage check to be skipped. The rebalance is operator-restricted, but an attacker may manipulate or anticipate the underlying market during an operator-triggered rebalance.",
    "impact": "The Multipool may execute a materially unfavorable token swap while its TWAP protection accepts the transaction. The resulting loss reduces the assets backing LP tokens and is borne by Multipool LP holders. The practical impact depends on the underlying pool's liquidity, twapDuration, swap size, and whether the approved swap target applies independent minimum-output protection.",
    "vulnerable_code": [
      {
        "file": "contracts/Multipool.sol",
        "contract": "Multipool",
        "function": "getAmountOut",
        "start_line": null,
        "end_line": null
      },
      {
        "file": "contracts/Multipool.sol",
        "contract": "Multipool",
        "function": "rebalanceAll",
        "start_line": null,
        "end_line": null
      }
    ],
    "mitigation": "Require an explicit operator-supplied minimum output and pass the same bound to the approved swap target. Treat the TWAP as an additional sanity check rather than the sole execution limit. Use conservative two-sided price bounds, a longer minimum TWAP duration, and preferably multiple validated pools or an independent oracle. Prevent twapDuration from being configured to zero or an excessively short interval.",
    "severity": "Medium"
  }
]
