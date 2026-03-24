from typing import List, Set, Dict
from dataclasses import dataclass
import hashlib
import time

@dataclass
class Message:
    sender: str
    value: any
    timestamp: float
    signature: str

class ByzantineConsensus:
    def __init__(self, node_id: str, nodes: List[str], f: int):
        self.node_id = node_id
        self.nodes = set(nodes)
        self.f = f  # Maximum number of faulty nodes tolerated
        self.messages: Dict[str, Set[Message]] = {}
        self.decided = False
        self.decision = None

    def _sign_message(self, value: any) -> str:
        message = f"{self.node_id}:{value}:{time.time()}"
        return hashlib.sha256(message.encode()).hexdigest()

    def propose(self, value: any):
        """Propose a value to the network"""
        signature = self._sign_message(value)
        message = Message(
            sender=self.node_id,
            value=value,
            timestamp=time.time(),
            signature=signature
        )
        self._broadcast(message)

    def _broadcast(self, message: Message):
        """Broadcast message to all nodes in the network"""
        for node in self.nodes:
            if node not in self.messages:
                self.messages[node] = set()
            self.messages[node].add(message)

    def receive_message(self, message: Message):
        """Handle receiving a message from another node"""
        if message.sender not in self.nodes:
            return
            
        if message.sender not in self.messages:
            self.messages[message.sender] = set()
        
        self.messages[message.sender].add(message)
        self._try_decide()

    def _try_decide(self):
        """Try to reach consensus based on received messages"""
        if self.decided:
            return

        # Count occurrences of each proposed value
        value_counts: Dict[any, int] = {}
        for node, msgs in self.messages.items():
            for msg in msgs:
                if msg.value not in value_counts:
                    value_counts[msg.value] = 0
                value_counts[msg.value] += 1

        # Check if any value has more than 2f+1 votes
        quorum = 2 * self.f + 1
        for value, count in value_counts.items():
            if count > quorum:
                self.decided = True
                self.decision = value
                break

    def get_decision(self) -> any:
        """Get the consensus decision if one has been reached"""
        return self.decision if self.decided else None
