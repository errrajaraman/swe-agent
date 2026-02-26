"""
Proof of Work (PoW) consensus algorithm.

Miners compete to solve a computationally expensive puzzle (finding a nonce
that produces a hash with a required number of leading zeros). The first miner
to solve it broadcasts the block and collects the reward.

Used by: Bitcoin, Litecoin (historically Ethereum).

Pros:
  - Battle-tested, highly secure.
  - Sybil-resistant via computational cost.

Cons:
  - Extremely energy-intensive.
  - Slow block times due to difficulty adjustment.
  - Favors nodes with specialized hardware (ASICs).
"""

import random
import time
from typing import List

from blockchain_consensus.consensus.base import ConsensusProtocol, ConsensusResult
from blockchain_consensus.core.block import Block
from blockchain_consensus.core.chain import Blockchain
from blockchain_consensus.core.transaction import Transaction


class ProofOfWork(ConsensusProtocol):
    """
    Proof of Work consensus.

    Each participating miner attempts to find a valid nonce. The simulation
    picks a random winner to model the probabilistic nature of mining without
    burning real CPU cycles at high difficulty.
    """

    name = "Proof of Work (PoW)"

    def __init__(self, difficulty: int = 3) -> None:
        """
        Args:
            difficulty: Number of leading zeros required in the block hash.
        """
        self.difficulty = difficulty

    def run_round(
        self,
        blockchain: Blockchain,
        transactions: List[Transaction],
        nodes: List[str],
    ) -> ConsensusResult:
        if not nodes:
            return ConsensusResult(
                success=False, message="No miners available."
            )

        # Simulate mining competition: pick a random winner
        miner = random.choice(nodes)

        block = blockchain.create_next_block(
            transactions=transactions, validator=miner
        )

        # Actual mining (finding the nonce)
        start = time.time()
        block.mine(self.difficulty)
        elapsed = time.time() - start

        added = blockchain.add_block(block)

        return ConsensusResult(
            success=added,
            block=block,
            proposer=miner,
            rounds=1,
            message=(
                f"Miner {miner[:8]}.. found nonce={block.nonce} in {elapsed:.4f}s "
                f"(difficulty={self.difficulty}). Block #{block.index} added."
            ),
        )
