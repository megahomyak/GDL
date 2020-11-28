from dataclasses import dataclass

from vk import vk_config
from vk.dataclasses_ import Message


@dataclass
class HandlingResult:

    text: str

    def to_message(self, peer_id: int) -> Message:
        return Message(self.text, peer_id)


class Handlers:

    # noinspection PyMethodMayBeStatic
    # because maybe in future I will use it as a normal method, so this prevents
    # it from being called directly from the class
    async def send_bot_info(self) -> HandlingResult:
        return HandlingResult(vk_config.BOT_INFO)
