[
  {
    "finding_id": "SAF-001",
    "title": "Cross-chain fee valuation uses manipulable instantaneous pool state",
    "description": "WooCrossFee.currentBalance() values configured WooPP reserves using the current Wooracle price and wooPP.poolSize(base), then uses that valuation to determine ingressFee() and outgressFee(). WooPPV3 poolSize() exposes the mutable tokenInfos[token].reserve, which is changed by public swaps. Consequently, an attacker can trade against the configured WooPP, alter its reserve state, and execute a cross-chain swap while the fee curve is evaluated from the manipulated balance. The piecewise fee curve can reduce fees when the calculated balance crosses the maxPercent threshold or increase fees when it moves in the opposite direction. In deployments where WooCrossFee uses a WooPPV2/WooracleV2 pair, WooPPV2 swaps additionally persist post-trade prices through WooracleV2.postPrice(). WooCrossFee also discards the feasibility flag returned by wooracle.price(base), so a stale or deviation-violating Wooracle price may still be used in the valuation. The supplied source does not establish deployment wiring or exact profitability, but it demonstrates the attacker-influenceable reserve/oracle state to cross-chain fee path.",
    "impact": "Cross-chain swaps may be charged reduced or zero fees, causing protocol fee-revenue loss. Other users may also be overcharged or have their fee outcome changed by short-lived reserve manipulation.",
    "vulnerable_code": [
      {
        "file": "contracts/CrossChain/WooCrossFee.sol",
        "contract": "WooCrossFee",
        "function": "currentBalance",
        "start_line": null,
        "end_line": null
      },
      {
        "file": "contracts/CrossChain/WooCrossFee.sol",
        "contract": "WooCrossFee",
        "function": "ingressFee",
        "start_line": null,
        "end_line": null
      },
      {
        "file": "contracts/CrossChain/WooCrossFee.sol",
        "contract": "WooCrossFee",
        "function": "outgressFee",
        "start_line": null,
        "end_line": null
      },
      {
        "file": "contracts/WooPPV3/WooPPV3.sol",
        "contract": "WooPPV3",
        "function": "poolSize",
        "start_line": null,
        "end_line": null
      },
      {
        "file": "contracts/WooPPV3/WooUsdOFTCrossRouter.sol",
        "contract": "WooUsdOFTCrossRouter",
        "function": "crossSwap",
        "start_line": null,
        "end_line": null
      }
    ],
    "mitigation": "Do not derive fee tiers from instantaneous poolSize() and spot-price values. Use a separately maintained, time-weighted or delayed reserve valuation and a manipulation-resistant independent price source. Require the oracle feasibility result before including a token in currentBalance(), enforce freshness and deviation checks, and bound the permitted fee or valuation change per transaction and over a time interval.",
    "severity": "Medium"
  },
  {
    "finding_id": "SAF-002",
    "title": "Rebate redemption can be favorably manipulated through WOOFi spot pricing",
    "description": "WooRebateManager.claimRebate() converts a user's fixed quote-token rebate into rewardToken through WooRouterV2.swap() with minToAmount set to zero. When the configured router uses WooPPV2, a public WOOFi trade can first alter the reward-token Wooracle price: WooPPV2._sellBase() calculates a lower post-trade price for a sufficiently large reward-token sale and persists it with WooracleV2.postPrice(). The subsequent quote-to-reward redemption uses WooPPV2._sellQuote(), which reads that manipulated spot price. A rebate holder can therefore move the reward-token price downward and redeem the same quote rebate for an inflated reward-token amount. The Chainlink bound and swap limits constrain the movement but do not provide a TWAP or redemption-specific independent execution-price check. The source does not provide deployment wiring or parameters proving a particular deployment is profitable, but it shows the concrete price-manipulation path into the redemption amount.",
    "impact": "The rebate manager may transfer more reward tokens than justified by the prevailing market value, reducing funds available for other rebate recipients.",
    "vulnerable_code": [
      {
        "file": "contracts/WooRebateManager.sol",
        "contract": "WooRebateManager",
        "function": "claimRebate",
        "start_line": null,
        "end_line": null
      },
      {
        "file": "contracts/WooPPV2.sol",
        "contract": "WooPPV2",
        "function": "_sellBase",
        "start_line": null,
        "end_line": null
      },
      {
        "file": "contracts/WooPPV2.sol",
        "contract": "WooPPV2",
        "function": "_sellQuote",
        "start_line": null,
        "end_line": null
      }
    ],
    "mitigation": "Redeem rebates directly in the quote token or price reward-token redemptions using a manipulation-resistant TWAP or independent oracle. If conversion through WOOFi remains necessary, require a user-supplied minimum reward amount derived from an independent reference price and reject stale or out-of-bound execution prices.",
    "severity": "Medium"
  },
  {
    "finding_id": "SAF-003",
    "title": "Vault reward conversion lacks an execution-price bound",
    "description": "WooVaultManager.distributeAllReward() swaps the accumulated quote-token reward balance into rewardToken through WooRouterV2 with minToAmount equal to zero, then distributes the returned amount among vaults. When the router is backed by WooPPV2, an attacker can trade the reward token before the distribution, causing WooPPV2._sellBase() to persist a changed Wooracle spot price. The administrator's quote-to-reward swap then executes using that manipulated price through WooPPV2._sellQuote(). Because the returned reward amount is distributed without an independent price or minimum-output check, the vaults can receive an unfavorable amount of reward tokens. The supplied source supports this path for the stated router/pool configuration; exact extraction and profitability depend on deployment parameters and transaction ordering.",
    "impact": "Vault reward distributions may receive fewer reward tokens than warranted by the quote-token balance, transferring value away from participating vaults and potentially allowing an attacker to benefit from surrounding price-moving trades.",
    "vulnerable_code": [
      {
        "file": "contracts/WooVaultManager.sol",
        "contract": "WooVaultManager",
        "function": "distributeAllReward",
        "start_line": null,
        "end_line": null
      },
      {
        "file": "contracts/WooPPV2.sol",
        "contract": "WooPPV2",
        "function": "_sellBase",
        "start_line": null,
        "end_line": null
      },
      {
        "file": "contracts/WooPPV2.sol",
        "contract": "WooPPV2",
        "function": "_sellQuote",
        "start_line": null,
        "end_line": null
      }
    ],
    "mitigation": "Add a minimum acceptable reward-token output or maximum execution price to distributeAllReward(), with the bound derived from a fresh independent oracle or TWAP. Prefer an oracle-priced conversion mechanism and reject execution when the WOOFi spot price deviates beyond the permitted threshold.",
    "severity": "Medium"
  }
]
