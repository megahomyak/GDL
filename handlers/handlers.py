from typing import List, Tuple

import my_typing
from handlers import handler_helpers
from handlers.handler_helpers import HandlingResult
from main_logic_helpers import CommandsSection
from requests_workers.requests_worker import RequestsWorker
from vk import vk_config

MOBILE_DEMONS_AMOUNT = 100
POINTERCRATE_DEMONS_AMOUNT = 150


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
            self, command_descriptions: my_typing.CommandDescriptionsDict,
            command_names: Tuple[str, ...]) -> HandlingResult:
        command_descriptions_as_strings = []
        quoted_not_found_commands: List[str] = []
        for command_name in command_names:
            try:
                command_descriptions_as_strings.extend(
                    # Here description_method is a
                    # Command.get_short_full_description, if I set
                    # Command.get_short_full_description as a type -
                    # I wouldn't get any IDE hints anyway
                    description_method()
                    for description_method in command_descriptions[command_name]
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

    async def get_mobile_demonlist(
            self, demons_amount: int = MOBILE_DEMONS_AMOUNT) -> HandlingResult:
        if demons_amount > MOBILE_DEMONS_AMOUNT:
            beginning = (
                f"Вы запросили {demons_amount} демонов, но там их "
                f"{MOBILE_DEMONS_AMOUNT}, так что показываю все.\n"
            )
            demons_amount = 150
        else:
            beginning = ""
        site = await self.requests_worker.get_mobile_demons_site()
        return HandlingResult(
            beginning + "\n".join(
                f"{demon_index}. {demon.get_as_readable_string()}"
                for demon_index, demon in enumerate(
                    handler_helpers.get_mobile_demons_info_from_soup(
                        site, get_compact_demon_info=True, limit=demons_amount
                    ), start=1
                )
            )
        )

    async def get_mobile_demon_info(self, demon_num: int) -> HandlingResult:
        if demon_num > MOBILE_DEMONS_AMOUNT:
            return HandlingResult(
                f"Слишком большой номер демона! (больше {MOBILE_DEMONS_AMOUNT})"
            )
        soup = await self.requests_worker.get_mobile_demons_site()
        demon = handler_helpers.get_mobile_demon_info_from_soup_by_num(
            soup, demon_num
        )
        return HandlingResult(f"{demon_num}. {demon.get_as_readable_string()}")

    async def get_pc_demonlist(
            self, demons_amount: int = POINTERCRATE_DEMONS_AMOUNT
            ) -> HandlingResult:
        if demons_amount > POINTERCRATE_DEMONS_AMOUNT:
            beginning = (
                f"Вы запросили {demons_amount} демонов, но там их "
                f"{POINTERCRATE_DEMONS_AMOUNT}, так что показываю все.\n"
            )
            demons_amount = 150
        else:
            beginning = ""
        return HandlingResult(
            beginning + "\n".join(
                f"{demon_index}. {compact_demon_info.get_as_readable_string()}"
                for demon_index, compact_demon_info in enumerate(
                    handler_helpers.get_compact_pc_demonlist_from_json(
                        await self.requests_worker.get_pc_demonlist_as_json(
                            demons_amount
                        )
                    ), start=1
                )
            )
        )

    async def get_pc_demon_info(self, demon_num: int) -> HandlingResult:
        if demon_num > POINTERCRATE_DEMONS_AMOUNT:
            return HandlingResult(
                f"Слишком большой номер демона! (больше "
                f"{POINTERCRATE_DEMONS_AMOUNT})"
            )
        return HandlingResult(
            handler_helpers.get_pc_demon_from_json(
                await self.requests_worker.get_pc_demon_as_json(demon_num)
            ).get_as_readable_string()
        )
