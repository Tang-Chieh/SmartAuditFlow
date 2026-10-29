[
  {
    "finding_id": "SAF-001",
    "title": "Raw AMM tick influences premium and solvency accounting",
    "description": "Several financially sensitive PanopticPool paths obtain the live Uniswap tick through getCurrentTick() and pass it into premium calculations. In particular, getAccumulatedFeesAndPositionsData() and _validateSolvency() use the raw current tick when calling _calculateAccumulatedPremia(), which forwards it to SFPM.getAccountPremium(). For Uniswap V3, FeesCalc.calculateAMMSwapFees() uses the supplied tick to select the fee-growth-inside branch based on whether the tick is below, above, or within the position range. An attacker who temporarily moves the underlying AMM price can therefore influence premium attribution and the premium values subsequently used in collateral and solvency calculations. The current-tick/TWAP consistency check is applied in dispatchFrom(), but it is not a universal check for all raw-tick consumers, including premium valuation and settlement paths.",
    "impact": "A temporary AMM price displacement may cause incorrect premium accounting and distort collateral or solvency results. Depending on active positions and liquidity, this could enable favorable premium settlement, premature or delayed liquidation behavior, or protocol and liquidity-provider losses.",
    "vulnerable_code": [
      {
        "file": "contracts/PanopticPool.sol",
        "contract": "PanopticPool",
        "function": "getAccumulatedFeesAndPositionsData",
        "start_line": null,
        "end_line": null
      },
      {
        "file": "contracts/PanopticPool.sol",
        "contract": "PanopticPool",
        "function": "_validateSolvency",
        "start_line": null,
        "end_line": null
      },
      {
        "file": "contracts/SemiFungiblePositionManager.sol",
        "contract": "SemiFungiblePositionManager",
        "function": "getAccountPremium",
        "start_line": null,
        "end_line": null
      },
      {
        "file": "contracts/libraries/FeesCalc.sol",
        "contract": "FeesCalc",
        "function": "calculateAMMSwapFees",
        "start_line": null,
        "end_line": null
      }
    ],
    "mitigation": "Separate execution pricing from valuation pricing. Use a protocol-approved EMA, median, or historical TWAP for premium, collateral, solvency, settlement, and payout calculations, or require every raw current-tick consumer to validate the live tick against an independently calculated oracle value using an operation-specific deviation bound. For AMM operations, validate the price before and after execution while using the validated oracle price for accounting. Consider reverting premium and collateral-affecting operations when the current tick is materially inconsistent with the oracle.",
    "severity": "Medium"
  },
  {
    "finding_id": "SAF-002",
    "title": "Permissionless spot-fed oracle can be gradually poisoned",
    "description": "PanopticPool.pokeOracle() is permissionless and advances the internal OraclePack using the current Uniswap AMM tick. OraclePackLibrary.computeInternalMedian() accepts a new observation once the 64-second epoch changes, and clampTick() only limits the observation relative to the previous stored observation by MAX_CLAMP_DELTA. The observation remains derived from the instantaneous, attacker-influenceable AMM price rather than a historical TWAP or independently verified reference. An attacker who maintains an artificial AMM price can call pokeOracle() across successive epochs, gradually replacing entries in the eight-observation median queue and moving the spot, fast, slow, and eons EMAs. The resulting oracle state is consumed by getTWAP(), getSolvencyTicks(), liquidation bonus calculations, forced-exercise pricing, and collateral conversion.",
    "impact": "Sustained AMM manipulation can bias the internal median and EMA oracle, potentially causing solvent accounts to appear insolvent, allowing undercollateralized accounts to pass risk checks, or altering liquidation bonuses, forced-exercise compensation, and cross-token collateral conversions. The clamp and epoch gating limit the speed of manipulation but do not eliminate the cumulative poisoning path.",
    "vulnerable_code": [
      {
        "file": "contracts/PanopticPool.sol",
        "contract": "PanopticPool",
        "function": "pokeOracle",
        "start_line": null,
        "end_line": null
      },
      {
        "file": "contracts/RiskEngine.sol",
        "contract": "RiskEngine",
        "function": "computeInternalMedian",
        "start_line": null,
        "end_line": null
      },
      {
        "file": "contracts/types/OraclePack.sol",
        "contract": "OraclePackLibrary",
        "function": "computeInternalMedian",
        "start_line": null,
        "end_line": null
      },
      {
        "file": "contracts/types/OraclePack.sol",
        "contract": "OraclePackLibrary",
        "function": "clampTick",
        "start_line": null,
        "end_line": null
      }
    ],
    "mitigation": "Source accepted oracle observations from a historical Uniswap observation-based TWAP or median window covering a meaningful portion of each epoch instead of directly using slot0/currentTick. Add an independent reference-price or cumulative-deviation check, require a minimum observation interval based on actual elapsed time, and consider requiring agreement between the internal oracle and an independent historical price before liquidation, forced exercise, or other value-transferring operations. Retain the per-update clamp and multi-tick checks as supplementary controls.",
    "severity": "Medium"
  }
]
