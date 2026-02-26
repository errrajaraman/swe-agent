"""
Blockchain chain management.

Manages the ordered sequence of blocks and provides validation utilities.
"""

from typing import List, Optional

from pydantic import BaseModel, Field

from blockchain_consensus.core.block import Block
from blockchain_consensus.core.transaction import Transaction


class Blockchain(BaseModel):
    """
    A blockchain: an ordered, immutable sequence of blocks.

    Provides methods for adding blocks, validating the chain,
    and managing a pending transaction pool.
    """

    chain: List[Block] = Field(default_factory=list, description="The list of blocks")
    pending_transactions: List[Transaction] = Field(
        default_factory=list, description="Transactions waiting to be included in a block"
    )
    difficulty: int = Field(
        default=2, description="Mining difficulty (leading zeros required in hash)"
    )

    def model_post_init(self, __context: object) -> None:
        """Initialize the chain with a genesis block if empty."""
        if not self.chain:
            self.chain.append(Block.genesis())

    @property
    def latest_block(self) -> Block:
        """Return the most recent block in the chain."""
        return self.chain[-1]

    @property
    def height(self) -> int:
        """Return the current height (length) of the chain."""
        return len(self.chain)

    def add_transaction(self, transaction: Transaction) -> None:
        """Add a transaction to the pending pool."""
        self.pending_transactions.append(transaction)

    def add_block(self, block: Block) -> bool:
        """
        Add a validated block to the chain.

        Args:
            block: The block to add.

        Returns:
            True if the block was added successfully, False otherwise.
        """
        if block.previous_hash != self.latest_block.hash:
            return False
        if block.hash is None:
            return False
        if block.hash != block.compute_hash():
            return False
        self.chain.append(block)
        return True

    def create_next_block(
        self,
        transactions: Optional[List[Transaction]] = None,
        validator: Optional[str] = None,
    ) -> Block:
        """
        Create the next block using pending transactions (or supplied ones).

        Args:
            transactions: Explicit list of transactions; uses pending pool if None.
            validator: Address of the block creator.

        Returns:
            A new (unmined) Block ready for consensus processing.
        """
        txs = transactions if transactions is not None else list(self.pending_transactions)
        block = Block(
            index=self.height,
            transactions=txs,
            previous_hash=self.latest_block.hash or "",
            validator=validator,
        )
        if transactions is None:
            self.pending_transactions.clear()
        return block

    def is_valid(self) -> bool:
        """
        Validate the entire blockchain.

        Checks:
        - Hash integrity of each block.
        - Linkage between consecutive blocks.

        Returns:
            True if the chain is valid, False otherwise.
        """
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]

            if current.hash != current.compute_hash():
                return False
            if current.previous_hash != previous.hash:
                return False

        return True

    def __str__(self) -> str:
        return f"Blockchain(height={self.height}, pending_txs={len(self.pending_transactions)})"
