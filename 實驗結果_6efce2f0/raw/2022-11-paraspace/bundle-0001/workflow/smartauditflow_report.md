[
  {
    "finding_id": "SAF-001",
    "title": "Block Timestamp Manipulation Can Lower Dutch Auction Execution Price",
    "description": "The Dutch auction strategy derives the current auction price directly from block.timestamp: currentAuctionPrice = startPrice - (((startPrice - endPrice) * (block.timestamp - startTime)) / (endTime - startTime)). This value determines whether a taker bid is accepted through takerBid.price >= currentAuctionPrice. A block proposer or coordinated participant with limited ability to influence the block timestamp may advance the timestamp within consensus constraints, causing the calculated auction price to decrease and allowing a lower bid to execute earlier than it would under the intended wall-clock time. The maker's auction parameters are signature-protected, but the timestamp used in the calculation is not signed and is externally supplied by block production.",
    "impact": "A seller may receive a lower execution price than expected for the actual elapsed time, particularly in short-duration auctions or auctions with a large price decline. The impact is bounded by the underlying chain's timestamp constraints and does not provide arbitrary price control.",
    "vulnerable_code": [
      {
        "file": "contracts/dependencies/looksrare/contracts/executionStrategies/StrategyDutchAuction.sol",
        "contract": "StrategyDutchAuction",
        "function": "canExecuteTakerBid",
        "start_line": null,
        "end_line": null
      }
    ],
    "mitigation": "Reduce reliance on fine-grained block timestamps for price progression. Consider using coarser price-update intervals, enforcing auction durations substantially larger than the expected timestamp deviation, and adding a signed seller-defined minimum execution price that is enforced independently of block.timestamp. If exact deterministic progression is required, consider a block-based or otherwise verifiable auction mechanism appropriate for the deployment chain.",
    "severity": "Medium"
  }
]
