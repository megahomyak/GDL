import asyncio
import datetime
import itertools
import logging
import sys
import traceback
from typing import NoReturn, Optional, List, Tuple, Dict, Callable

import aiohttp
import simple_avk

import lexer
from handlers.handler_helpers import HandlingResult
from handlers.handlers import Handlers
from lexer.arg_implementations import SequenceArgType, StringArgType
from lexer.constant_metadata_implementations import (
    CommandsConstantMetadataElement, CommandDescriptionsConstantMetadataElement
)
from lexer.lexer_classes import Command
from lexer.lexer_classes import ConstantContext, Context, Arg
from main_logic_helpers import CommandsSection
from vk import vk_config
from vk.dataclasses_ import Message
from vk.vk_worker import VKWorker


class MainLogic:

    def __init__(
            self, vk_worker: VKWorker, handlers: Handlers,
            logger: Optional[logging.Logger] = None):
        self.vk_worker = vk_worker
        self.logger = logger
        self.command_sections: Tuple[CommandsSection, ...] = (
            CommandsSection(
                "Ознакомление",
                (
                    Command(
                        names=("памятка", "memo"),
                        handler=handlers.get_memo,
                        description="показывает памятку по использованию бота"
                    ),
                )
            ),
            CommandsSection(
                "Информация",
                (
                    Command(
                        names=("инфо", "info"),
                        handler=handlers.send_bot_info,
                        description="показывает общую информацию о боте"
                    ),
                )
            ),
            CommandsSection(
                "Навигация",
                (
                    Command(
                        names=("помощь", "help"),
                        handler=handlers.get_help_message,
                        description=(
                            "показывает помощь по командам и их написанию"
                        ),
                        constant_metadata=(CommandsConstantMetadataElement,)
                    ),
                    Command(
                        names=("помощь", "help"),
                        handler=handlers.get_help_message_for_specific_commands,
                        description=(
                            "показывает помощь по конкретным командам и их "
                            "написанию"
                        ),
                        constant_metadata=(
                            CommandDescriptionsConstantMetadataElement,
                        ),
                        arguments=(
                            Arg(
                                (
                                    "команды, к которым нужно получить "
                                    "подсказку (через запятую)"
                                ), SequenceArgType(StringArgType())
                            ),
                        )
                    )
                )
            )
        )
        command_descriptions: Dict[str, List[Callable[[], str]]] = {}
        for section in self.command_sections:
            for command in section.commands:
                for name in command.names:
                    try:
                        command_descriptions[name].append(
                            command.get_short_full_description
                        )
                    except KeyError:
                        command_descriptions[name] = [
                            command.get_short_full_description
                        ]
        self.commands_list = list(itertools.chain(
            *[section.commands for section in self.command_sections]
        ))
        self.constant_context = ConstantContext(
            self.command_sections, command_descriptions
        )

    async def handle_command(
            self, current_chat_peer_id: int, command: str,
            vk_message_info: dict) -> Message:
        error_args_amount = 0
        for command_ in self.commands_list:
            try:
                converted_command = command_.convert_command_to_args(command)
            except lexer.exceptions.ParsingError as parsing_error:
                if parsing_error.args_num > error_args_amount:
                    error_args_amount = parsing_error.args_num
            else:
                handling_result: HandlingResult = await command_.handler(
                    *command_.get_converted_metadata(
                        Context(vk_message_info, datetime.date.today())
                    ),
                    *command_.get_converted_constant_metadata(
                        self.constant_context
                    ),
                    *command_.fillers,
                    *converted_command.arguments
                )
                return handling_result.to_message(current_chat_peer_id)
        if error_args_amount == 0:
            error_msg = "Ошибка обработки команды на её названии!"
            if self.logger is not None:
                self.logger.debug(
                    f"Ошибка обработки команды \"{command}\" на её названии!"
                )
        else:
            error_msg = (
                f"Ошибка обработки команды на аргументе номер "
                f"{error_args_amount} (он неправильный или пропущен)"
            )
            if self.logger is not None:
                self.logger.debug(
                    f"Ошибка обработки команды \"{command}\" на аргументе "
                    f"номер {error_args_amount} (он неправильный или пропущен)"
                )
        return Message(error_msg, current_chat_peer_id)

    async def reply_to_vk_message(
            self, current_chat_peer_id: int, command: str,
            message_info: dict) -> None:
        await self.vk_worker.reply(await self.handle_command(
            current_chat_peer_id, command, message_info
        ))

    async def future_done_callback(
            self, peer_id: int, text: str,
            future: asyncio.Future) -> None:
        exc = future.exception()
        if exc:
            if self.logger is not None:
                self.logger.error(
                    f"Ошибка на команде \"{text}\":\n" + "".join(
                        traceback.TracebackException.from_exception(
                            exc
                        ).format()
                    )
                )
            await self.vk_worker.reply(Message(
                f"Тут у юзера при обработке команды \"{text}\" произошла "
                f"ошибка \"{str(exc)}\", это в логах тоже есть, "
                f"гляньте, разберитесь...", vk_config.DEBUG_CHAT_PEER_ID
            ))
            if peer_id != vk_config.DEBUG_CHAT_PEER_ID:
                await self.vk_worker.reply(Message(
                    f"При обработке команды \"{text}\" произошла ошибка. "
                    f"Она была залоггирована, админы - уведомлены.", peer_id
                ))

    async def listen_for_vk_events(self) -> NoReturn:
        async for message_info in self.vk_worker.listen_for_messages():
            text: str = message_info["text"]
            peer_id: int = message_info["peer_id"]
            if text.startswith("/"):
                text = text[1:]  # Cutting /
                asyncio.create_task(
                    self.reply_to_vk_message(peer_id, text, message_info)
                ).add_done_callback(lambda future: asyncio.create_task(
                    self.future_done_callback(peer_id, text, future)
                ))

    async def send_commands_from_stdin(self) -> NoReturn:
        while True:
            message_text = input("Enter the command: ")
            output = await self.handle_command(
                # Fake peer_id and vk_message_info
                123, message_text, {"from_id": 456}
            )
            print(output.text)


async def main(debug: bool = False):
    async with aiohttp.ClientSession() as aiohttp_session:
        vk_worker = VKWorker(
            simple_avk.SimpleAVK(
                aiohttp_session,
                vk_config.TOKEN,
                vk_config.GROUP_ID
            )
        )
        logging.basicConfig(
            level=logging.INFO,
            format="[%(asctime)s | %(name)s | %(levelname)s] - %(message)s"
        )
        main_logic = MainLogic(
            vk_worker,
            Handlers(),
            logging.getLogger("command_handling_errors")
        )
        if debug:
            await main_logic.send_commands_from_stdin()
        else:
            await main_logic.listen_for_vk_events()


if __name__ == "__main__":
    asyncio.run(main(debug="--local" in sys.argv))