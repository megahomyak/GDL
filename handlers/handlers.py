from typing import List, Tuple

import gd

import my_typing
from handlers import handler_helpers
from handlers.handler_helpers import (
    HandlingResult, HandlerHelpersWithDependencies
)
from main_logic_helpers import CommandsSection
from requests_workers import gd_worker
from requests_workers.requests_worker import RequestsWorker
from text_generators import gd_text_generators
from vk import vk_config

MOBILE_DEMONS_AMOUNT = 100
POINTERCRATE_DEMONS_AMOUNT = 150


class Handlers:

    def __init__(
            self, requests_worker: RequestsWorker,
            gd_worker_: gd_worker.GDWorker,
            handler_helpers_with_dependencies: HandlerHelpersWithDependencies):
        self.requests_worker = requests_worker
        self.gd_worker = gd_worker_
        self.helpers_with_dependencies = handler_helpers_with_dependencies

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
            demons_amount = MOBILE_DEMONS_AMOUNT
        else:
            beginning = ""
        site = await self.requests_worker.get_mobile_demons_site()
        return HandlingResult(
            beginning + "\n".join(
                demon.get_as_readable_string() for demon in (
                    handler_helpers.get_mobile_demons_info_from_soup(
                        site, get_compact_demon_info=True, limit=demons_amount
                    )
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
        return HandlingResult(demon.get_as_readable_string())

    async def get_pc_demonlist(
            self, demons_amount: int = POINTERCRATE_DEMONS_AMOUNT
            ) -> HandlingResult:
        if demons_amount > POINTERCRATE_DEMONS_AMOUNT:
            beginning = (
                f"Вы запросили {demons_amount} демонов, но там их "
                f"{POINTERCRATE_DEMONS_AMOUNT}, так что показываю все.\n"
            )
            demons_amount = POINTERCRATE_DEMONS_AMOUNT
        else:
            beginning = ""
        return HandlingResult(
            beginning + "\n".join(
                compact_demon_info.get_as_readable_string()
                for compact_demon_info in (
                    handler_helpers.get_compact_pc_demonlist_from_json(
                        await self.requests_worker.get_pc_demonlist_as_json(
                            demons_amount
                        )
                    )
                )
            )
        )

    async def get_pc_demon_info(self, demon_num: int) -> HandlingResult:
        if demon_num > POINTERCRATE_DEMONS_AMOUNT:
            return HandlingResult(
                f"Слишком большой номер демона! (больше "
                f"{POINTERCRATE_DEMONS_AMOUNT})"
            )
        return await (
            self.helpers_with_dependencies.get_handling_result_about_pc_demon(
                demon_num
            )
        )

    async def get_player_info(self, player_name: str) -> HandlingResult:
        try:
            return HandlingResult(
                await gd_text_generators.get_user_as_readable_string(
                    await self.gd_worker.get_player(player_name)
                )
            )
        except gd.MissingAccess:
            return HandlingResult(
                f"Пользователь с ником \"{player_name}\" не найден!"
            )

    async def get_level_info_by_name(self, level_name: str) -> HandlingResult:
        try:
            level = await self.gd_worker.get_level_by_name(level_name)
        except gd_worker.LevelNotFound:
            return HandlingResult(
                f"Уровня с названием \"{level_name}\" не найдено!"
            )
        else:
            return HandlingResult(
                await gd_text_generators.get_level_as_readable_string(level)
            )

    async def get_level_info_by_id(self, level_id: int) -> HandlingResult:
        try:
            level = await self.gd_worker.get_level_by_id(level_id)
        except gd.MissingAccess:
            return HandlingResult(f"Уровня с айди {level_id} не существует!")
        else:
            return HandlingResult(
                await gd_text_generators.get_level_as_readable_string(level)
            )

    async def get_pc_demon_info_by_demon_name(
            self, demon_name: str) -> HandlingResult:
        json_ = await self.requests_worker.get_pc_demonlist_as_json(
            POINTERCRATE_DEMONS_AMOUNT
        )
        lower_demon_name = demon_name.lower()
        for demon_info in json_:
            if demon_info["name"].lower() == lower_demon_name:
                return await (
                    self.helpers_with_dependencies
                    .get_handling_result_about_pc_demon(
                        demon_info["position"]
                    )
                )
        return HandlingResult(
            f"Демон с названием \"{demon_name}\" не найден в ПК-демонлисте!"
        )

    async def get_mobile_demon_info_by_demon_name(
            self, demon_name: str) -> HandlingResult:
        site = await self.requests_worker.get_mobile_demons_site()
        demon_info_tag = site.find(
            class_=handler_helpers.CLASS_WITH_ONE_DEMON_NAME
        )
        lower_demon_name = demon_name.lower()
        demon_num = 1
        while True:
            if demon_info_tag is None:
                return HandlingResult(
                    f"Демон с названием \"{demon_name}\" не найден в мобильном "
                    f"демонлисте!"
                )
            else:
                # Demon's name is the first stripped string
                if (
                    handler_helpers.get_demon_name_from_demon_tag(
                        demon_info_tag
                    ).lower() == lower_demon_name
                ):
                    return HandlingResult(
                        handler_helpers.get_mobile_demon_info_from_tag(
                            demon_info_tag, demon_num=demon_num
                        ).get_as_readable_string()
                    )
                else:
                    demon_info_tag = demon_info_tag.find_next(
                        class_=handler_helpers.CLASS_WITH_ONE_DEMON_NAME
                    )
            demon_num += 1

    async def get_levels_from_gd_search(
            self, level_name: str, page_num: int) -> HandlingResult:
        levels = await self.gd_worker.gd_client.search_levels(
            level_name, pages=[page_num - 1]
        )
        if levels:
            return HandlingResult(
                "\n".join(
                    f"- \"{level.name}\" от {level.creator}, айди - {level.id}"
                    for level in levels
                )
            )
        else:
            return HandlingResult(
                f"Уровней по запросу \"{level_name}\" на странице поиска "
                f"{page_num} не найдено!"
            )
