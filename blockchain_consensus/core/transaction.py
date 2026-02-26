"""
Transaction model for the blockchain.

Represents a transfer of value between participants in the network.
"""

import hashlib
import time
from typing import Optional

from pydantic import BaseModel, Field


class Transaction(BaseModel):
    """A single transaction in the blockchain network."""

    sender: str = Field(description="Address of the sender")
    recipient: str = Field(description="Address of the recipient")
    amount: float = Field(description="Amount being transferred", gt=0)
    timestamp: float = Field(
        default_factory=time.time,
        description="Unix timestamp when the transaction was created",
    )
    tx_id: Optional[str] = Field(
        default=None, description="Unique transaction identifier (hash)"
    )

    def model_post_init(self, __context: object) -> None:
        """Compute the transaction ID after initialization."""
        if self.tx_id is None:
            self.tx_id = self.compute_hash()

    def compute_hash(self) -> str:
        """Compute a SHA-256 hash of the transaction data."""
        data = f"{self.sender}{self.recipient}{self.amount}{self.timestamp}"
        return hashlib.sha256(data.encode()).hexdigest()

    def __str__(self) -> str:
        return (
            f"Tx({self.sender[:8]}.. -> {self.recipient[:8]}.. : {self.amount:.2f})"
        )
