from dataclasses import dataclass
from typing import AsyncIterable

from vk.dataclasses_ import Message


@dataclass
class HandlingResult:

    text: str

    def to_message(self, peer_id: int) -> Message:
        return Message(self.text, peer_id)


async def async_join(iterable: AsyncIterable[str], separator: str) -> str:
    result = ""
    async for i in iterable:
        if result:  # If this is not the first element of the iterable
            result += separator
        result += i
    return result
