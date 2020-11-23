from dataclasses import dataclass


@dataclass
class Message:
    text: str
    peer_id: int
