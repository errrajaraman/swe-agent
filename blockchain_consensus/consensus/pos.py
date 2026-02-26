"""
Proof of Stake (PoS) consensus algorithm.

Validators are chosen to propose new blocks based on the amount of
cryptocurrency they have "staked" (locked up as collateral). The probability
of being selected is proportional to a validator's stake.

Used by: Ethereum 2.0, Cardano, Solana.

Pros:
  - Energy-efficient (no mining).
  - Encourages long-term holding of the network token.
  - Slashing penalties deter malicious behaviour.

Cons:
  - "Rich get richer" concern.
  - Nothing-at-stake problem (mitigated by slashing).
  - Requires careful economic design.
"""

import random
from typing import Dict, List

from pydantic import BaseModel, Field

from blockchain_consensus.consensus.base import ConsensusProtocol, ConsensusResult
from blockchain_consensus.core.block import Block
from blockchain_consensus.core.chain import Blockchain
from blockchain_consensus.core.transaction import Transaction


class StakeInfo(BaseModel):
    """Tracks stake and age for a single validator."""

    address: str = Field(description="Validator address")
    stake: float = Field(description="Amount staked", ge=0)
    age: int = Field(
        default=0,
        description="Number of rounds since last block production (coin age)",
    )


class ProofOfStake(ConsensusProtocol):
    """
    Proof of Stake consensus.

    Validator selection is weighted by ``stake * (1 + age_factor * age)`` to
    model coin-age weighting. After a validator produces a block its age
    resets.
    """

    name = "Proof of Stake (PoS)"

    def __init__(
        self,
        stakes: Dict[str, float],
        age_factor: float = 0.1,
    ) -> None:
        """
        Args:
            stakes: Mapping of validator address -> staked amount.
            age_factor: Multiplier for coin-age influence on selection weight.
        """
        self.validators: Dict[str, StakeInfo] = {
            addr: StakeInfo(address=addr, stake=amount)
            for addr, amount in stakes.items()
        }
        self.age_factor = age_factor

    def _select_validator(self) -> str:
        """Select a validator weighted by effective stake (stake * age bonus)."""
        weights: List[float] = []
        addresses: List[str] = []
        for info in self.validators.values():
            effective = info.stake * (1.0 + self.age_factor * info.age)
            weights.append(effective)
            addresses.append(info.address)

        total = sum(weights)
        if total == 0:
            return random.choice(addresses)

        chosen = random.choices(addresses, weights=weights, k=1)[0]
        return chosen

    def run_round(
        self,
        blockchain: Blockchain,
        transactions: List[Transaction],
        nodes: List[str],
    ) -> ConsensusResult:
        if not self.validators:
            return ConsensusResult(
                success=False, message="No validators registered."
            )

        # Select proposer
        proposer = self._select_validator()
        info = self.validators[proposer]

        block = blockchain.create_next_block(
            transactions=transactions, validator=proposer
        )
        block.hash = block.compute_hash()

        added = blockchain.add_block(block)

        if added:
            # Reset age for the proposer, increment for everyone else
            for addr, v in self.validators.items():
                if addr == proposer:
                    v.age = 0
                else:
                    v.age += 1

        return ConsensusResult(
            success=added,
            block=block,
            proposer=proposer,
            rounds=1,
            message=(
                f"Validator {proposer[:8]}.. selected (stake={info.stake:.1f}, "
                f"age={info.age}). Block #{block.index} added."
            ),
        )
