"""
Pre-built simulation scenarios for showcasing each consensus algorithm.

Each function sets up a realistic network topology and runs a multi-round
simulation, returning a detailed report.
"""

from typing import Optional

from blockchain_consensus.consensus.dpos import DelegatedProofOfStake
from blockchain_consensus.consensus.pbft import PracticalBFT
from blockchain_consensus.consensus.pos import ProofOfStake
from blockchain_consensus.consensus.pow import ProofOfWork
from blockchain_consensus.network.node import NetworkNode
from blockchain_consensus.network.simulator import (
    NetworkSimulator,
    SimulationConfig,
    SimulationReport,
)


def _default_config(num_rounds: int = 5, seed: Optional[int] = 42) -> SimulationConfig:
    return SimulationConfig(num_rounds=num_rounds, txs_per_round=3, random_seed=seed)


# ---------------------------------------------------------------------------
# Proof of Work
# ---------------------------------------------------------------------------

def run_pow_scenario(
    num_miners: int = 5,
    difficulty: int = 2,
    num_rounds: int = 5,
    seed: Optional[int] = 42,
) -> SimulationReport:
    """
    Simulate a Proof of Work network.

    Creates ``num_miners`` mining nodes competing to find valid block hashes
    with the given ``difficulty``.
    """
    nodes = [NetworkNode.create(f"miner-{i}", balance=50.0) for i in range(num_miners)]
    consensus = ProofOfWork(difficulty=difficulty)
    sim = NetworkSimulator(consensus=consensus, nodes=nodes)
    return sim.run(_default_config(num_rounds=num_rounds, seed=seed))


# ---------------------------------------------------------------------------
# Proof of Stake
# ---------------------------------------------------------------------------

def run_pos_scenario(
    num_validators: int = 5,
    num_rounds: int = 5,
    seed: Optional[int] = 42,
) -> SimulationReport:
    """
    Simulate a Proof of Stake network.

    Validators receive randomized stakes so selection probability varies.
    Coin-age weighting ensures even low-stake validators eventually produce
    blocks.
    """
    nodes = [
        NetworkNode.create(f"validator-{i}", balance=100.0, stake=10.0 * (i + 1))
        for i in range(num_validators)
    ]
    stakes = {n.address: n.stake for n in nodes}
    consensus = ProofOfStake(stakes=stakes, age_factor=0.15)
    sim = NetworkSimulator(consensus=consensus, nodes=nodes)
    return sim.run(_default_config(num_rounds=num_rounds, seed=seed))


# ---------------------------------------------------------------------------
# Delegated Proof of Stake
# ---------------------------------------------------------------------------

def run_dpos_scenario(
    num_candidates: int = 7,
    num_delegates: int = 3,
    num_rounds: int = 5,
    seed: Optional[int] = 42,
) -> SimulationReport:
    """
    Simulate a Delegated Proof of Stake network.

    ``num_candidates`` nodes vie for ``num_delegates`` delegate slots. Only
    the top-voted candidates produce blocks in round-robin fashion.
    """
    nodes = [
        NetworkNode.create(f"candidate-{i}", balance=100.0) for i in range(num_candidates)
    ]
    # Simulate voting: candidates with lower indices get more votes
    votes = {n.address: float(num_candidates - i) * 100 for i, n in enumerate(nodes)}
    consensus = DelegatedProofOfStake(votes=votes, num_delegates=num_delegates)
    sim = NetworkSimulator(consensus=consensus, nodes=nodes)
    return sim.run(_default_config(num_rounds=num_rounds, seed=seed))


# ---------------------------------------------------------------------------
# Practical Byzantine Fault Tolerance
# ---------------------------------------------------------------------------

def run_pbft_scenario(
    num_nodes: int = 7,
    byzantine_nodes: int = 2,
    num_rounds: int = 5,
    seed: Optional[int] = 42,
) -> SimulationReport:
    """
    Simulate a PBFT network.

    Runs a known validator set with ``byzantine_nodes`` faulty participants.
    The protocol tolerates up to floor((n-1)/3) Byzantine faults.
    """
    nodes = [
        NetworkNode.create(f"pbft-node-{i}", balance=100.0) for i in range(num_nodes)
    ]
    consensus = PracticalBFT(
        nodes=[n.address for n in nodes],
        byzantine_nodes=byzantine_nodes,
    )
    sim = NetworkSimulator(consensus=consensus, nodes=nodes)
    return sim.run(_default_config(num_rounds=num_rounds, seed=seed))


# ---------------------------------------------------------------------------
# Run all
# ---------------------------------------------------------------------------

def run_all_scenarios(num_rounds: int = 5, seed: Optional[int] = 42) -> dict[str, SimulationReport]:
    """Run all four consensus scenarios and return a mapping of name -> report."""
    return {
        "pow": run_pow_scenario(num_rounds=num_rounds, seed=seed),
        "pos": run_pos_scenario(num_rounds=num_rounds, seed=seed),
        "dpos": run_dpos_scenario(num_rounds=num_rounds, seed=seed),
        "pbft": run_pbft_scenario(num_rounds=num_rounds, seed=seed),
    }
