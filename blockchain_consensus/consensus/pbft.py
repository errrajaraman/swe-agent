"""
Practical Byzantine Fault Tolerance (PBFT) consensus algorithm.

A leader-based protocol that tolerates up to f = floor((n-1)/3) Byzantine
(arbitrarily faulty) nodes among n total nodes. Consensus is reached through
three phases:

  1. Pre-Prepare: The leader proposes a block.
  2. Prepare: Nodes validate and broadcast PREPARE messages.
  3. Commit: Once 2f+1 PREPARE messages are received, nodes broadcast COMMIT.

If 2f+1 COMMIT messages are collected the block is finalized.

Used by: Hyperledger Fabric (v0.6), Zilliqa, Tendermint (variant).

Pros:
  - Immediate finality (no forks).
  - Works well for permissioned / consortium blockchains.
  - Tolerates Byzantine failures.

Cons:
  - O(n^2) message complexity; doesn't scale to thousands of nodes.
  - Requires known, fixed validator set.
  - Leader can be a bottleneck.
"""

import random
from enum import Enum
from typing import Dict, List, Set

from pydantic import BaseModel, Field

from blockchain_consensus.consensus.base import ConsensusProtocol, ConsensusResult
from blockchain_consensus.core.block import Block
from blockchain_consensus.core.chain import Blockchain
from blockchain_consensus.core.transaction import Transaction


class MessageType(str, Enum):
    """PBFT message types."""

    PRE_PREPARE = "PRE_PREPARE"
    PREPARE = "PREPARE"
    COMMIT = "COMMIT"


class PBFTMessage(BaseModel):
    """A single PBFT protocol message."""

    msg_type: MessageType = Field(description="Type of the PBFT message")
    sender: str = Field(description="Node that sent this message")
    block_hash: str = Field(description="Hash of the proposed block")
    view: int = Field(default=0, description="Current view number")


class PBFTNode(BaseModel):
    """State tracked per node during a PBFT round."""

    address: str
    is_byzantine: bool = Field(
        default=False, description="If True, this node may act maliciously"
    )
    prepares_received: Set[str] = Field(default_factory=set)
    commits_received: Set[str] = Field(default_factory=set)
    prepared: bool = False
    committed: bool = False


class PracticalBFT(ConsensusProtocol):
    """
    Practical Byzantine Fault Tolerance consensus.

    Simulates the three-phase protocol among a known validator set. A
    configurable number of nodes may be marked as Byzantine.
    """

    name = "Practical Byzantine Fault Tolerance (PBFT)"

    def __init__(
        self,
        nodes: List[str],
        byzantine_nodes: int = 0,
    ) -> None:
        """
        Args:
            nodes: List of all validator node addresses.
            byzantine_nodes: Number of nodes that will act as Byzantine faults.
        """
        if byzantine_nodes > (len(nodes) - 1) // 3:
            raise ValueError(
                f"PBFT tolerates at most f=floor((n-1)/3) Byzantine nodes. "
                f"n={len(nodes)}, max f={(len(nodes) - 1) // 3}, got {byzantine_nodes}."
            )

        self.node_list = nodes
        self.byzantine_count = byzantine_nodes
        self._view = 0

        # Mark random nodes as Byzantine
        byzantine_set = set(random.sample(nodes, byzantine_nodes))
        self.pbft_nodes: Dict[str, PBFTNode] = {
            addr: PBFTNode(address=addr, is_byzantine=(addr in byzantine_set))
            for addr in nodes
        }

    @property
    def _quorum(self) -> int:
        """Minimum messages required: 2f + 1."""
        f = self.byzantine_count
        return 2 * f + 1

    def _reset_round(self) -> None:
        """Reset per-round state for all nodes."""
        for node in self.pbft_nodes.values():
            node.prepares_received = set()
            node.commits_received = set()
            node.prepared = False
            node.committed = False

    def _phase_pre_prepare(self, leader: str, block: Block) -> List[PBFTMessage]:
        """Leader broadcasts PRE_PREPARE."""
        block_hash = block.compute_hash()
        return [
            PBFTMessage(
                msg_type=MessageType.PRE_PREPARE,
                sender=leader,
                block_hash=block_hash,
                view=self._view,
            )
        ]

    def _phase_prepare(self, block_hash: str) -> List[PBFTMessage]:
        """Each honest node broadcasts PREPARE after receiving PRE_PREPARE."""
        messages: List[PBFTMessage] = []
        for node in self.pbft_nodes.values():
            if node.is_byzantine:
                # Byzantine nodes may not send PREPARE (or send garbage)
                continue
            msg = PBFTMessage(
                msg_type=MessageType.PREPARE,
                sender=node.address,
                block_hash=block_hash,
                view=self._view,
            )
            messages.append(msg)
        return messages

    def _phase_commit(self, block_hash: str) -> List[PBFTMessage]:
        """Nodes that collected enough PREPAREs broadcast COMMIT."""
        messages: List[PBFTMessage] = []
        for node in self.pbft_nodes.values():
            if node.is_byzantine:
                continue
            if len(node.prepares_received) >= self._quorum:
                node.prepared = True
                msg = PBFTMessage(
                    msg_type=MessageType.COMMIT,
                    sender=node.address,
                    block_hash=block_hash,
                    view=self._view,
                )
                messages.append(msg)
        return messages

    def run_round(
        self,
        blockchain: Blockchain,
        transactions: List[Transaction],
        nodes: List[str],
    ) -> ConsensusResult:
        self._reset_round()

        n = len(self.node_list)
        f = self.byzantine_count

        # Rotate leader based on view
        leader = self.node_list[self._view % n]

        block = blockchain.create_next_block(
            transactions=transactions, validator=leader
        )
        block.hash = block.compute_hash()
        block_hash = block.hash

        # --- Phase 1: PRE_PREPARE ---
        pre_prepare_msgs = self._phase_pre_prepare(leader, block)

        # --- Phase 2: PREPARE ---
        prepare_msgs = self._phase_prepare(block_hash)

        # Distribute PREPARE messages to all nodes
        for msg in prepare_msgs:
            for node in self.pbft_nodes.values():
                node.prepares_received.add(msg.sender)

        # --- Phase 3: COMMIT ---
        commit_msgs = self._phase_commit(block_hash)

        # Distribute COMMIT messages
        for msg in commit_msgs:
            for node in self.pbft_nodes.values():
                node.commits_received.add(msg.sender)

        # Check if enough nodes committed
        committed_count = sum(
            1
            for node in self.pbft_nodes.values()
            if len(node.commits_received) >= self._quorum and not node.is_byzantine
        )

        total_phases = 3
        consensus_reached = committed_count >= self._quorum

        if consensus_reached:
            added = blockchain.add_block(block)
            self._view += 1
            return ConsensusResult(
                success=added,
                block=block,
                proposer=leader,
                rounds=total_phases,
                message=(
                    f"PBFT consensus reached in {total_phases} phases. "
                    f"Leader={leader[:8]}.., "
                    f"prepares={len(prepare_msgs)}, commits={len(commit_msgs)}, "
                    f"byzantine={f}/{n}. Block #{block.index} finalized."
                ),
            )

        self._view += 1
        return ConsensusResult(
            success=False,
            proposer=leader,
            rounds=total_phases,
            message=(
                f"PBFT failed to reach consensus. "
                f"Only {committed_count}/{self._quorum} nodes committed "
                f"(byzantine={f}/{n})."
            ),
        )
