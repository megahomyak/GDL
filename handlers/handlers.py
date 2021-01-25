from typing import Dict, List, Callable, Tuple

# noinspection PyUnresolvedReferences
# IDK why it thinks that handlers resolves to its containing file
from handlers.handler_helpers import HandlingResult
from main_logic_helpers import CommandsSection
from requests_workers.requests_worker import RequestsWorker
from vk import vk_config


class Handlers:

    def __init__(self, requests_worker: RequestsWorker):
        self.requests_worker = requests_worker

    # noinspection PyMethodMayBeStatic
    # because maybe in future I will use it as a normal method, so this prevents
    # it from being called directly from the class
    async def send_bot_info(self) -> HandlingResult:
        return HandlingResult(vk_config.BOT_INFO)

    # noinspection PyMethodMayBeStatic
    # because maybe in future I will use it as a normal method, so this prevents
    # it from being called directly from the class
    async def get_help_message_for_specific_commands(
            self, command_descriptions: Dict[str, List[Callable[..., str]]],
            command_names: Tuple[str, ...]) -> HandlingResult:
        command_descriptions_as_strings = []
        quoted_not_found_commands: List[str] = []
        for command_name in command_names:
            try:
                command_descriptions_as_strings.extend(
                    # Here desc_func is a
                    # Command.get_short_full_description, if I set
                    # Command.get_short_full_description as a type -
                    # I wouldn't get any IDE hints anyway
                    desc_func()
                    for desc_func in command_descriptions[command_name]
                )
            except KeyError:
                quoted_not_found_commands.append(f"\"{command_name}\"")
        return HandlingResult(
            "\n".join(
                (
                    (
                        f"Команда с названием "
                        f"{quoted_not_found_commands[0]} не найдена!"
                        if len(quoted_not_found_commands) == 1 else
                        f"Команды с названиями "
                        f"{', '.join(quoted_not_found_commands)} не найдены!"
                    ), *command_descriptions_as_strings
                ) if quoted_not_found_commands else
                command_descriptions_as_strings
            )
        )

    # noinspection PyMethodMayBeStatic
    # because maybe in future I will use it as a normal method, so this prevents
    # it from being called directly from the class
    async def get_help_message(
            self,
            command_sections: Tuple[CommandsSection, ...]) -> HandlingResult:
        return HandlingResult("\n\n".join([
            "• Команды бота:", *[
                command.get_compact_command_descriptions(
                    add_dot_before_name=True
                ) for command in command_sections
            ]
        ]))

    # noinspection PyMethodMayBeStatic
    # because maybe in future I will use it as a normal method, so this prevents
    # it from being called directly from the class
    async def get_memo(self) -> HandlingResult:
        return HandlingResult(vk_config.MEMO)

    async def get_mobile_demonlist(self) -> HandlingResult:
        return HandlingResult("\n".join(
            f"{demon_index + 1}. \"{demon.name}\" от {demon.authors}"
            f"{' и других' if demon.there_is_more_authors else ''}"
            for demon_index, demon in enumerate(
                await self.requests_worker.get_mobile_demons()
            )
        ))
