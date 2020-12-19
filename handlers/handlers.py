from typing import Dict, List, Callable, Tuple

from handlers.handler_helpers import HandlingResult
from main_logic_helpers import CommandsSection
from vk import vk_config


class Handlers:

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
                    (
                        # Here desc_func is a Command.get_full_description,
                        # if I set Command.get_full_description as a type -
                        # I wouldn't get any IDE hints anyway
                        desc_func(include_heading=True)
                        for desc_func in command_descriptions[command_name]
                    )
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
                        f"{', '.join(quoted_not_found_commands)} "
                        f"не найдены!"
                    ), *command_descriptions_as_strings
                )
            ) if quoted_not_found_commands else
            command_descriptions_as_strings
        )

    # noinspection PyMethodMayBeStatic
    # because maybe in future I will use it as a normal method, so this prevents
    # it from being called directly from the class
    async def get_help_message(
            self, commands: Tuple[CommandsSection, ...]) -> HandlingResult:
        return HandlingResult("\n\n".join([
            "• Команды бота:\n\n", *[
                command.get_compact_command_descriptions()
                for command in commands
            ]
        ]))

    # noinspection PyMethodMayBeStatic
    # because maybe in future I will use it as a normal method, so this prevents
    # it from being called directly from the class
    async def get_memo(self) -> HandlingResult:
        return HandlingResult(vk_config.MEMO)
