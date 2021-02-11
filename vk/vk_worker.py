import logging
import random
from typing import Optional, AsyncGenerator, Any

from simple_avk import SimpleAVK

from vk import vk_config
from vk.dataclasses_ import Message


class VKWorker:

    def __init__(
            self, simple_avk: SimpleAVK,
            logger: Optional[logging.Logger] = None):
        self.vk = simple_avk
        self.logger = logger

    async def listen_for_messages(self) -> AsyncGenerator[Any, None]:
        async for event in self.vk.listen():
            if event["type"] == "message_new":
                message_info = event["object"]["message"]
                if self.logger is not None:
                    self.logger.debug(
                        f"Новое сообщение из чата с peer_id "
                        f"{message_info['peer_id']}: {message_info['text']}"
                    )
                yield message_info

    async def reply(self, message: Message) -> None:
        text_parts = (
            message.text[i:i + vk_config.SYMBOLS_PER_MESSAGE]
            for i in range(0, len(message.text), vk_config.SYMBOLS_PER_MESSAGE)
        )
        for part in text_parts:
            # noinspection SpellCheckingInspection
            await self.vk.call_method(
                "messages.send",
                {
                    "peer_id": message.peer_id,
                    "message": part,
                    "random_id": random.randint(-1_000_000, 1_000_000),
                    "disable_mentions": 1,
                    "dont_parse_links": 1
                }
            )
        if self.logger is not None:
            self.logger.debug(
                f"Отправлено сообщение в чат с peer_id {message.peer_id}: "
                f"{message.text}"
            )
