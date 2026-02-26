"""
Network node model.

Represents a participant in the blockchain network with its own copy of the
chain and a wallet balance.
"""

import hashlib
import time
from typing import Optional

from pydantic import BaseModel, Field

from blockchain_consensus.core.chain import Blockchain


class NetworkNode(BaseModel):
    """A single node in the simulated blockchain network."""

    address: str = Field(description="Unique address of this node")
    balance: float = Field(default=100.0, description="Wallet balance")
    stake: float = Field(default=0.0, description="Amount currently staked")
    is_active: bool = Field(default=True, description="Whether the node is online")
    blocks_produced: int = Field(default=0, description="Number of blocks this node has produced")
    blockchain: Optional[Blockchain] = Field(
        default=None, description="Local copy of the blockchain"
    )

    @classmethod
    def create(cls, name: str, balance: float = 100.0, stake: float = 0.0) -> "NetworkNode":
        """
        Factory that creates a node with a deterministic address derived from its name.

        Args:
            name: Human-readable name for the node.
            balance: Initial wallet balance.
            stake: Initial amount staked.

        Returns:
            A new ``NetworkNode``.
        """
        address = hashlib.sha256(f"{name}-{time.time()}".encode()).hexdigest()
        return cls(address=address, balance=balance, stake=stake)

    def __str__(self) -> str:
        return (
            f"Node({self.address[:8]}.., balance={self.balance:.1f}, "
            f"stake={self.stake:.1f}, blocks={self.blocks_produced})"
        )
