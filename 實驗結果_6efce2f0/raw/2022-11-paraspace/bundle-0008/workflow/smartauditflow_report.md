[
  {
    "finding_id": "SAF-001",
    "title": "Manipulable Uniswap V2 spot price used as fallback asset oracle",
    "description": "ParaSpaceFallbackOracle.getAssetPrice derives ERC20 asset prices from the instantaneous reserves of a single Uniswap V2 WETH/asset pair using getReserves() and getAmountOut(). Uniswap V2 reserves are mutable through swaps, and the implementation does not use a TWAP, historical observations, minimum-liquidity requirement, deviation bound, freshness check, or independent reference price. ParaSpaceOracle.getAssetPrice invokes this fallback whenever the configured primary source is unset or returns zero, allowing an attacker-manipulated AMM price to flow into the protocol price oracle. The supplied pool interfaces indicate that oracle prices can influence collateral valuation, borrowing capacity, health factors, and liquidation decisions. Exploitability is conditional on the fallback being configured for an affected asset, the asset having a usable WETH pair, the primary source activating the fallback path, and the asset being used in financially sensitive protocol logic.",
    "impact": "An attacker may temporarily inflate or deflate the reported asset price by trading against the configured Uniswap V2 pair. If the manipulated price is consumed during borrowing or collateral assessment, the attacker could obtain excessive credit against overvalued collateral, avoid liquidation, trigger improper liquidations, or cause incorrect health-factor and collateral calculations. In the worst case, inflated valuations could create undercollateralized debt and protocol bad debt.",
    "vulnerable_code": [
      {
        "file": "contracts/misc/ParaSpaceFallbackOracle.sol",
        "contract": "ParaSpaceFallbackOracle",
        "function": "getAssetPrice",
        "start_line": null,
        "end_line": null
      },
      {
        "file": "contracts/misc/ParaSpaceOracle.sol",
        "contract": "ParaSpaceOracle",
        "function": "getAssetPrice",
        "start_line": null,
        "end_line": null
      }
    ],
    "mitigation": "Replace the instantaneous reserve quote with a manipulation-resistant source, preferably a trusted independent oracle or a sufficiently long Uniswap TWAP based on cumulative observations. If an AMM fallback is retained, require a minimum observation interval and liquidity threshold, validate freshness, compare the result against an independent reference price, enforce a maximum deviation, and restrict fallback support to explicitly approved assets and markets. Consider failing closed or pausing price-dependent operations when the primary oracle is unavailable rather than automatically accepting an unvalidated spot price.",
    "severity": "High"
  }
]
