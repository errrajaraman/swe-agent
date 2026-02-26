"""
Delegated Proof of Stake (DPoS) consensus algorithm.

Token holders vote for a fixed set of *delegates* (block producers) who take
turns producing blocks in a round-robin fashion. Delegates that misbehave can
be voted out.

Used by: EOS, Tron, Lisk.

Pros:
  - Very high throughput (fixed, small validator set).
  - Democratic governance via voting.
  - Energy-efficient.

Cons:
  - More centralized than PoW/PoS (few delegates).
  - Vulnerable to vote-buying / collusion.
  - Delegates hold significant power.
"""

import random
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from blockchain_consensus.consensus.base import ConsensusProtocol, ConsensusResult
from blockchain_consensus.core.chain import Blockchain
from blockchain_consensus.core.transaction import Transaction


class Delegate(BaseModel):
    """A delegate (block producer) in DPoS."""

    address: str = Field(description="Delegate address")
    votes: float = Field(default=0.0, description="Total votes received")
    blocks_produced: int = Field(default=0, description="Blocks produced so far")


class DelegatedProofOfStake(ConsensusProtocol):
    """
    Delegated Proof of Stake consensus.

    1. Token holders cast votes for delegate candidates.
    2. The top ``num_delegates`` candidates become active delegates.
    3. Active delegates take turns producing blocks in round-robin order.
    """

    name = "Delegated Proof of Stake (DPoS)"

    def __init__(
        self,
        votes: Dict[str, float],
        num_delegates: int = 3,
    ) -> None:
        """
        Args:
            votes: Mapping of candidate address -> total votes received.
            num_delegates: Number of active delegates to elect.
        """
        self.candidates: Dict[str, Delegate] = {
            addr: Delegate(address=addr, votes=v) for addr, v in votes.items()
        }
        self.num_delegates = num_delegates
        self.active_delegates: List[str] = []
        self._round_index: int = 0
        self._elect_delegates()

    def _elect_delegates(self) -> None:
        """Elect the top delegates by vote count."""
        sorted_candidates = sorted(
            self.candidates.values(), key=lambda d: d.votes, reverse=True
        )
        self.active_delegates = [
            d.address for d in sorted_candidates[: self.num_delegates]
        ]
        # Shuffle to randomize first-round order
        random.shuffle(self.active_delegates)

    def _current_delegate(self) -> Optional[str]:
        """Return the delegate whose turn it is."""
        if not self.active_delegates:
            return None
        return self.active_delegates[self._round_index % len(self.active_delegates)]

    def run_round(
        self,
        blockchain: Blockchain,
        transactions: List[Transaction],
        nodes: List[str],
    ) -> ConsensusResult:
        delegate = self._current_delegate()
        if delegate is None:
            return ConsensusResult(
                success=False, message="No active delegates elected."
            )

        block = blockchain.create_next_block(
            transactions=transactions, validator=delegate
        )
        block.hash = block.compute_hash()

        added = blockchain.add_block(block)

        if added and delegate in self.candidates:
            self.candidates[delegate].blocks_produced += 1

        self._round_index += 1

        delegate_info = self.candidates.get(delegate)
        votes_str = f"{delegate_info.votes:.1f}" if delegate_info else "?"

        return ConsensusResult(
            success=added,
            block=block,
            proposer=delegate,
            rounds=1,
            message=(
                f"Delegate {delegate[:8]}.. (votes={votes_str}) produced "
                f"Block #{block.index} [round-robin slot "
                f"{(self._round_index - 1) % len(self.active_delegates)}]."
            ),
        )
