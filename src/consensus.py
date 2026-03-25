import hashlib
import time
from typing import Dict, List, Set

class ConsensusNode:
    def __init__(self, node_id: str, stake: float = 1.0):
        self.node_id = node_id
        self.stake = stake
        self.proposals: Dict[str, any] = {}
        self.votes: Dict[str, Dict[str, bool]] = {}
        self.committed: Set[str] = set()
        self.peers: List['ConsensusNode'] = []

    def propose(self, proposal_id: str, value: any) -> None:
        """Submit a new proposal to the network"""
        self.proposals[proposal_id] = value
        self._broadcast_proposal(proposal_id, value)

    def vote(self, proposal_id: str, value: any) -> None:
        """Cast a weighted vote for a proposal"""
        if proposal_id not in self.votes:
            self.votes[proposal_id] = {}
        
        # Calculate vote based on proposal value
        vote_hash = hashlib.sha256(str(value).encode()).hexdigest()
        self.votes[proposal_id][self.node_id] = vote_hash
        self._broadcast_vote(proposal_id, vote_hash)

    def process_vote(self, proposal_id: str, node_id: str, vote: str) -> None:
        """Process an incoming vote from another node"""
        if proposal_id not in self.votes:
            self.votes[proposal_id] = {}
        self.votes[proposal_id][node_id] = vote
        self._check_consensus(proposal_id)

    def _check_consensus(self, proposal_id: str) -> bool:
        """Check if consensus has been reached using weighted voting"""
        if proposal_id in self.committed:
            return True

        if proposal_id not in self.votes:
            return False

        total_stake = sum(peer.stake for peer in self.peers) + self.stake
        vote_counts: Dict[str, float] = {}

        # Count weighted votes
        for node_id, vote in self.votes[proposal_id].items():
            node_stake = self.stake if node_id == self.node_id else \\
                        next((p.stake for p in self.peers if p.node_id == node_id), 0)
            vote_counts[vote] = vote_counts.get(vote, 0) + node_stake

        # Check if any option has > 2/3 weighted majority
        for vote_hash, stake_count in vote_counts.items():
            if stake_count > (2/3 * total_stake):
                self.committed.add(proposal_id)
                return True

        return False

    def _broadcast_proposal(self, proposal_id: str, value: any) -> None:
        """Broadcast a proposal to all peers"""
        for peer in self.peers:
            peer.on_proposal(self.node_id, proposal_id, value)

    def _broadcast_vote(self, proposal_id: str, vote: str) -> None:
        """Broadcast a vote to all peers"""
        for peer in self.peers:
            peer.process_vote(proposal_id, self.node_id, vote)

    def on_proposal(self, node_id: str, proposal_id: str, value: any) -> None:
        """Handle an incoming proposal from another node"""
        self.proposals[proposal_id] = value
        self.vote(proposal_id, value)

    def get_consensus_value(self, proposal_id: str) -> any:
        """Get the consensus value for a committed proposal"""
        if proposal_id not in self.committed:
            raise ValueError(f"No consensus reached for proposal {proposal_id}")
        return self.proposals[proposal_id]

    def add_peer(self, peer: 'ConsensusNode') -> None:
        """Add a peer to the network"""
        if peer not in self.peers:
            self.peers.append(peer)

    def remove_peer(self, peer: 'ConsensusNode') -> None:
        """Remove a peer from the network"""
        if peer in self.peers:
            self.peers.remove(peer)