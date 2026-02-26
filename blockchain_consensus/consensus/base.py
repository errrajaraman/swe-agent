"""
Abstract base class for consensus algorithms.

All consensus implementations must conform to this protocol so they can be
plugged into the simulation runner interchangeably.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from pydantic import BaseModel, Field

from blockchain_consensus.core.block import Block
from blockchain_consensus.core.chain import Blockchain
from blockchain_consensus.core.transaction import Transaction


class ConsensusResult(BaseModel):
    """Outcome of a single consensus round."""

    success: bool = Field(description="Whether the round reached consensus")
    block: Optional[Block] = Field(
        default=None, description="The block that was agreed upon"
    )
    proposer: Optional[str] = Field(
        default=None, description="Node that proposed / mined the block"
    )
    rounds: int = Field(
        default=1, description="Number of communication rounds needed"
    )
    message: str = Field(default="", description="Human-readable summary")


class ConsensusProtocol(ABC):
    """
    Interface every consensus algorithm must implement.

    The simulation runner calls ``run_round`` each time a new block needs to be
    produced, passing in the current blockchain, pending transactions, and the
    set of participating nodes.
    """

    name: str = "base"

    @abstractmethod
    def run_round(
        self,
        blockchain: Blockchain,
        transactions: List[Transaction],
        nodes: List[str],
    ) -> ConsensusResult:
        """
        Execute one consensus round to produce and finalize a new block.

        Args:
            blockchain: The current state of the chain.
            transactions: Transactions to include in the new block.
            nodes: List of participating node addresses.

        Returns:
            A ``ConsensusResult`` describing the outcome.
        """
        ...

    def __str__(self) -> str:
        return f"ConsensusProtocol({self.name})"
