"""
Network simulator.

Orchestrates a multi-node blockchain network running a pluggable consensus
algorithm, producing blocks over a configurable number of rounds.
"""

import random
from typing import List, Optional

from pydantic import BaseModel, Field

from blockchain_consensus.consensus.base import ConsensusProtocol, ConsensusResult
from blockchain_consensus.core.chain import Blockchain
from blockchain_consensus.core.transaction import Transaction
from blockchain_consensus.network.node import NetworkNode


class SimulationConfig(BaseModel):
    """Configuration for a simulation run."""

    num_rounds: int = Field(default=5, description="Number of consensus rounds to simulate")
    txs_per_round: int = Field(default=3, description="Transactions generated per round")
    random_seed: Optional[int] = Field(default=None, description="Seed for reproducibility")


class RoundResult(BaseModel):
    """Result of a single simulation round."""

    round_number: int
    consensus_result: ConsensusResult
    chain_height: int
    pending_txs: int


class SimulationReport(BaseModel):
    """Full report of a simulation run."""

    algorithm: str
    config: SimulationConfig
    rounds: List[RoundResult]
    final_chain_height: int
    successful_rounds: int
    failed_rounds: int
    total_transactions_processed: int

    def summary(self) -> str:
        """Return a human-readable summary of the simulation."""
        lines = [
            "",
            f"{'=' * 70}",
            f"  Simulation Report: {self.algorithm}",
            f"{'=' * 70}",
            f"  Rounds executed:       {len(self.rounds)}",
            f"  Successful rounds:     {self.successful_rounds}",
            f"  Failed rounds:         {self.failed_rounds}",
            f"  Final chain height:    {self.final_chain_height}",
            f"  Total txs processed:   {self.total_transactions_processed}",
            f"{'=' * 70}",
            "",
            "  Round Details:",
            f"  {'-' * 66}",
        ]
        for r in self.rounds:
            status = "OK" if r.consensus_result.success else "FAIL"
            proposer = (r.consensus_result.proposer or "N/A")[:8]
            lines.append(
                f"  Round {r.round_number:>3}: [{status:>4}] "
                f"proposer={proposer}..  height={r.chain_height}"
            )
            lines.append(f"            {r.consensus_result.message}")
        lines.append(f"  {'-' * 66}")
        lines.append("")
        return "\n".join(lines)


class NetworkSimulator:
    """
    Runs a blockchain network simulation with a given consensus algorithm.

    Usage::

        nodes = [NetworkNode.create(f"node-{i}") for i in range(5)]
        sim = NetworkSimulator(
            consensus=ProofOfWork(difficulty=2),
            nodes=nodes,
        )
        report = sim.run(SimulationConfig(num_rounds=10))
        print(report.summary())
    """

    def __init__(
        self,
        consensus: ConsensusProtocol,
        nodes: List[NetworkNode],
        blockchain: Optional[Blockchain] = None,
    ) -> None:
        self.consensus = consensus
        self.nodes = nodes
        self.blockchain = blockchain or Blockchain()

    def _generate_transactions(self, count: int) -> List[Transaction]:
        """Generate random transactions between nodes."""
        if len(self.nodes) < 2:
            return []

        txs: List[Transaction] = []
        for _ in range(count):
            sender, recipient = random.sample(self.nodes, 2)
            amount = round(random.uniform(0.1, 10.0), 2)
            txs.append(
                Transaction(
                    sender=sender.address,
                    recipient=recipient.address,
                    amount=amount,
                )
            )
        return txs

    def run(self, config: Optional[SimulationConfig] = None) -> SimulationReport:
        """
        Execute the full simulation.

        Args:
            config: Simulation parameters; defaults are used if not supplied.

        Returns:
            A ``SimulationReport`` with detailed round-by-round results.
        """
        config = config or SimulationConfig()
        if config.random_seed is not None:
            random.seed(config.random_seed)

        node_addresses = [n.address for n in self.nodes if n.is_active]
        rounds: List[RoundResult] = []
        total_txs = 0

        for i in range(1, config.num_rounds + 1):
            txs = self._generate_transactions(config.txs_per_round)
            result = self.consensus.run_round(self.blockchain, txs, node_addresses)

            if result.success:
                total_txs += len(txs)
                # Update node stats
                for node in self.nodes:
                    if node.address == result.proposer:
                        node.blocks_produced += 1

            rounds.append(
                RoundResult(
                    round_number=i,
                    consensus_result=result,
                    chain_height=self.blockchain.height,
                    pending_txs=len(self.blockchain.pending_transactions),
                )
            )

        successful = sum(1 for r in rounds if r.consensus_result.success)

        return SimulationReport(
            algorithm=self.consensus.name,
            config=config,
            rounds=rounds,
            final_chain_height=self.blockchain.height,
            successful_rounds=successful,
            failed_rounds=len(rounds) - successful,
            total_transactions_processed=total_txs,
        )
