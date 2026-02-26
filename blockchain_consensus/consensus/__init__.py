"""
Consensus algorithm implementations.

Each algorithm implements the ConsensusProtocol interface defined in base.py.
"""

from blockchain_consensus.consensus.base import ConsensusProtocol
from blockchain_consensus.consensus.pow import ProofOfWork
from blockchain_consensus.consensus.pos import ProofOfStake
from blockchain_consensus.consensus.dpos import DelegatedProofOfStake
from blockchain_consensus.consensus.pbft import PracticalBFT

__all__ = [
    "ConsensusProtocol",
    "ProofOfWork",
    "ProofOfStake",
    "DelegatedProofOfStake",
    "PracticalBFT",
]
