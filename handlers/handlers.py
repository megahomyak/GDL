from dataclasses import dataclass

from vk.dataclasses_ import Message


@dataclass
class HandlingResult:

    text: str

    def to_message(self, peer_id: int) -> Message:
        return Message(self.text, peer_id)


class Handlers:
    pass
