#!/usr/bin/env python3
"""
Blockchain Consensus Algorithm Showcase - Main Runner

Demonstrates all four consensus algorithms side-by-side:
  1. Proof of Work (PoW)
  2. Proof of Stake (PoS)
  3. Delegated Proof of Stake (DPoS)
  4. Practical Byzantine Fault Tolerance (PBFT)

Usage:
    python -m blockchain_consensus.run_showcase [--rounds N] [--seed S] [--algorithm ALG]

Examples:
    # Run all algorithms with 10 rounds each
    python -m blockchain_consensus.run_showcase --rounds 10

    # Run only PoW with a specific seed
    python -m blockchain_consensus.run_showcase --algorithm pow --seed 123

    # Run PBFT with 8 rounds
    python -m blockchain_consensus.run_showcase --algorithm pbft --rounds 8
"""

import argparse
import sys

from blockchain_consensus.simulation.scenarios import (
    run_all_scenarios,
    run_dpos_scenario,
    run_pbft_scenario,
    run_pos_scenario,
    run_pow_scenario,
)


ALGORITHM_MAP = {
    "pow": run_pow_scenario,
    "pos": run_pos_scenario,
    "dpos": run_dpos_scenario,
    "pbft": run_pbft_scenario,
}

DESCRIPTIONS = {
    "pow": (
        "Proof of Work (PoW)\n"
        "  Miners compete to solve a cryptographic puzzle (finding a nonce that\n"
        "  produces a hash with leading zeros). Energy-intensive but battle-tested.\n"
        "  Used by: Bitcoin, Litecoin."
    ),
    "pos": (
        "Proof of Stake (PoS)\n"
        "  Validators are selected to propose blocks proportional to their staked\n"
        "  tokens. Energy-efficient with coin-age weighting.\n"
        "  Used by: Ethereum 2.0, Cardano."
    ),
    "dpos": (
        "Delegated Proof of Stake (DPoS)\n"
        "  Token holders vote for delegates who take turns producing blocks in\n"
        "  round-robin order. High throughput, democratic governance.\n"
        "  Used by: EOS, Tron, Lisk."
    ),
    "pbft": (
        "Practical Byzantine Fault Tolerance (PBFT)\n"
        "  A three-phase protocol (Pre-Prepare, Prepare, Commit) that tolerates\n"
        "  up to f=floor((n-1)/3) Byzantine faults. Immediate finality.\n"
        "  Used by: Hyperledger Fabric, Zilliqa."
    ),
}


def print_header() -> None:
    """Print the showcase banner."""
    print(
        "\n"
        "============================================================\n"
        "   BLOCKCHAIN CONSENSUS ALGORITHM SHOWCASE\n"
        "============================================================\n"
        "   Demonstrating how different consensus mechanisms reach\n"
        "   agreement in a distributed blockchain network.\n"
        "============================================================\n"
    )


def print_algorithm_intro(key: str) -> None:
    """Print a brief description of the algorithm before its simulation."""
    desc = DESCRIPTIONS.get(key, "")
    print(f"\n>>> {desc}\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Blockchain Consensus Algorithm Showcase",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--rounds",
        type=int,
        default=5,
        help="Number of consensus rounds per algorithm (default: 5)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility (default: 42)",
    )
    parser.add_argument(
        "--algorithm",
        choices=["pow", "pos", "dpos", "pbft", "all"],
        default="all",
        help="Which algorithm to run (default: all)",
    )
    args = parser.parse_args()

    print_header()

    if args.algorithm == "all":
        reports = run_all_scenarios(num_rounds=args.rounds, seed=args.seed)
        for key, report in reports.items():
            print_algorithm_intro(key)
            print(report.summary())
    else:
        print_algorithm_intro(args.algorithm)
        runner = ALGORITHM_MAP[args.algorithm]
        report = runner(num_rounds=args.rounds, seed=args.seed)
        print(report.summary())

    print(
        "\n============================================================\n"
        "   COMPARISON SUMMARY\n"
        "============================================================\n"
    )
    comparison = [
        ("Algorithm", "Finality", "Energy", "Throughput", "Decentralization"),
        ("PoW", "Probabilistic", "Very High", "Low", "High"),
        ("PoS", "Probabilistic", "Low", "Medium", "Medium"),
        ("DPoS", "Deterministic", "Low", "High", "Low"),
        ("PBFT", "Immediate", "Low", "Medium", "Low (permissioned)"),
    ]
    col_widths = [max(len(row[i]) for row in comparison) + 2 for i in range(5)]
    for row in comparison:
        line = "  ".join(cell.ljust(col_widths[i]) for i, cell in enumerate(row))
        print(f"  {line}")

    print(
        "\n============================================================\n"
        "   END OF SHOWCASE\n"
        "============================================================\n"
    )


if __name__ == "__main__":
    main()
