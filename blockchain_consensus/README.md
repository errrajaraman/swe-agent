# Blockchain Consensus Algorithm Showcase

A comprehensive demonstration of consensus algorithms used in blockchain technology, built using patterns from the SWE Agent codebase (Pydantic models, modular architecture).

## Algorithms Implemented

### 1. Proof of Work (PoW)
Miners compete to solve a cryptographic puzzle by finding a nonce that produces a hash with a required number of leading zeros. The first miner to solve it gets to add the block.

- **Used by**: Bitcoin, Litecoin
- **Finality**: Probabilistic
- **Energy**: Very High
- **Throughput**: Low
- **Decentralization**: High

### 2. Proof of Stake (PoS)
Validators are selected to propose blocks proportional to their staked tokens. Includes coin-age weighting so that validators who haven't produced blocks recently get a higher selection probability.

- **Used by**: Ethereum 2.0, Cardano, Solana
- **Finality**: Probabilistic
- **Energy**: Low
- **Throughput**: Medium
- **Decentralization**: Medium

### 3. Delegated Proof of Stake (DPoS)
Token holders vote for a fixed set of delegates who take turns producing blocks in round-robin order. Provides high throughput through democratic governance.

- **Used by**: EOS, Tron, Lisk
- **Finality**: Deterministic
- **Energy**: Low
- **Throughput**: High
- **Decentralization**: Low

### 4. Practical Byzantine Fault Tolerance (PBFT)
A three-phase protocol (Pre-Prepare, Prepare, Commit) that tolerates up to `f = floor((n-1)/3)` Byzantine faults among `n` nodes. Provides immediate finality.

- **Used by**: Hyperledger Fabric, Zilliqa, Tendermint (variant)
- **Finality**: Immediate
- **Energy**: Low
- **Throughput**: Medium
- **Decentralization**: Low (permissioned networks)

## Project Structure

```
blockchain_consensus/
├── __init__.py              # Package metadata
├── __main__.py              # Entry point for python -m
├── run_showcase.py          # CLI runner for demonstrations
├── README.md                # This file
├── core/                    # Blockchain primitives
│   ├── transaction.py       # Transaction model (Pydantic)
│   ├── block.py             # Block model with mining support
│   └── chain.py             # Blockchain management
├── consensus/               # Algorithm implementations
│   ├── base.py              # Abstract ConsensusProtocol interface
│   ├── pow.py               # Proof of Work
│   ├── pos.py               # Proof of Stake
│   ├── dpos.py              # Delegated Proof of Stake
│   └── pbft.py              # Practical Byzantine Fault Tolerance
├── network/                 # Network simulation
│   ├── node.py              # NetworkNode model
│   └── simulator.py         # NetworkSimulator orchestrator
└── simulation/              # Pre-built scenarios
    └── scenarios.py         # Ready-to-run scenario functions
```

## Quick Start

```bash
# From the repository root
cd swe-agent

# Run all algorithms (default: 5 rounds each)
python -m blockchain_consensus

# Run with more rounds
python -m blockchain_consensus --rounds 10

# Run a specific algorithm
python -m blockchain_consensus --algorithm pow
python -m blockchain_consensus --algorithm pos
python -m blockchain_consensus --algorithm dpos
python -m blockchain_consensus --algorithm pbft

# Set a random seed for reproducibility
python -m blockchain_consensus --rounds 8 --seed 123
```

## Architecture & Design Patterns

This showcase follows the same architectural patterns used in the SWE Agent:

- **Pydantic Models**: All data structures (Block, Transaction, ConsensusResult, etc.) use Pydantic `BaseModel` for type safety and validation, mirroring the SWE Agent's entity design.
- **Modular Architecture**: Each consensus algorithm is a separate module implementing a common `ConsensusProtocol` interface, similar to how the SWE Agent separates architect and developer agents.
- **State Management**: The simulation tracks state through well-defined Pydantic models, echoing the SWE Agent's `AgentState` pattern.
- **Pluggable Design**: Consensus algorithms are interchangeable via the `ConsensusProtocol` abstract base class, just as the SWE Agent's tools are pluggable.

## API Usage

You can also use the components programmatically:

```python
from blockchain_consensus.core import Blockchain, Transaction
from blockchain_consensus.consensus import ProofOfWork
from blockchain_consensus.network import NetworkNode, NetworkSimulator
from blockchain_consensus.network.simulator import SimulationConfig

# Create nodes
nodes = [NetworkNode.create(f"miner-{i}") for i in range(5)]

# Choose a consensus algorithm
consensus = ProofOfWork(difficulty=2)

# Run simulation
sim = NetworkSimulator(consensus=consensus, nodes=nodes)
report = sim.run(SimulationConfig(num_rounds=10, txs_per_round=3))

# Print results
print(report.summary())
```

## How Consensus Works

### The Problem
In a decentralized network, nodes must agree on the state of the ledger without trusting each other. This is the **Byzantine Generals Problem** - how to achieve agreement when some participants may be faulty or malicious.

### The Solutions

| Property | PoW | PoS | DPoS | PBFT |
|---|---|---|---|---|
| **Selection** | Computational puzzle | Weighted random by stake | Voted delegates, round-robin | Rotating leader |
| **Finality** | Probabilistic (6 blocks) | Probabilistic | Deterministic | Immediate |
| **Fault Tolerance** | 51% hash power | 51% stake | 51% votes | 33% Byzantine |
| **Scalability** | Global (thousands) | Global (thousands) | Semi-global (hundreds) | Permissioned (tens) |
| **Energy Cost** | Very high | Minimal | Minimal | Minimal |
