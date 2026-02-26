"""
Block model for the blockchain.

Each block contains a list of transactions and is linked to the previous block
via cryptographic hashing, forming the chain.
"""

import hashlib
import time
from typing import List, Optional

from pydantic import BaseModel, Field

from blockchain_consensus.core.transaction import Transaction


class Block(BaseModel):
    """A single block in the blockchain."""

    index: int = Field(description="Position of the block in the chain")
    timestamp: float = Field(
        default_factory=time.time,
        description="Unix timestamp when the block was created",
    )
    transactions: List[Transaction] = Field(
        default_factory=list, description="List of transactions in this block"
    )
    previous_hash: str = Field(
        description="Hash of the previous block in the chain"
    )
    nonce: int = Field(default=0, description="Nonce used for Proof of Work mining")
    validator: Optional[str] = Field(
        default=None,
        description="Address of the validator/miner who created this block",
    )
    hash: Optional[str] = Field(
        default=None, description="SHA-256 hash of this block"
    )

    def compute_hash(self) -> str:
        """Compute the SHA-256 hash of the block contents."""
        tx_data = "".join(tx.tx_id or tx.compute_hash() for tx in self.transactions)
        data = (
            f"{self.index}{self.timestamp}{tx_data}"
            f"{self.previous_hash}{self.nonce}{self.validator}"
        )
        return hashlib.sha256(data.encode()).hexdigest()

    def mine(self, difficulty: int) -> str:
        """
        Mine the block by finding a nonce that produces a hash
        with a given number of leading zeros (for PoW).

        Args:
            difficulty: Number of leading zeros required in the hash.

        Returns:
            The valid hash string.
        """
        target = "0" * difficulty
        while True:
            candidate_hash = self.compute_hash()
            if candidate_hash.startswith(target):
                self.hash = candidate_hash
                return candidate_hash
            self.nonce += 1

    def __str__(self) -> str:
        short_hash = (self.hash or "unmined")[:12]
        return (
            f"Block(#{self.index}, txs={len(self.transactions)}, "
            f"hash={short_hash}..)"
        )

    @classmethod
    def genesis(cls) -> "Block":
        """Create the genesis (first) block of the chain."""
        block = cls(
            index=0,
            timestamp=0.0,
            transactions=[],
            previous_hash="0" * 64,
            validator="genesis",
        )
        block.hash = block.compute_hash()
        return block
