import gd


class LevelNotFound(Exception):
    pass


class GDWorker:

    def __init__(self, gd_client: gd.Client):
        self.gd_client = gd_client

    async def get_player(self, player_name: str) -> gd.User:
        """
        Can throw gd.MissingAccess
        """
        player = await self.gd_client.find_user(player_name)
        full_player = await player.to_user()
        return full_player

    async def get_level_by_id(self, level_id: int) -> gd.Level:
        """
        Can throw gd.MissingAccess
        """
        return await self.gd_client.get_level(level_id)

    async def get_level_by_name(self, level_name: str) -> gd.Level:
        """
        Can throw LevelNotFound
        """
        levels = await self.gd_client.search_levels(level_name, pages=[0])
        if levels:
            return levels[0]
        raise LevelNotFound(f"Level with name {level_name} not found!")


async def get_user_as_readable_string(user: gd.User) -> str:
    if user.role == gd.StatusLevel.MODERATOR:
        role = " [МОДЕРАТОР]"
    elif user.role == gd.StatusLevel.ELDER_MODERATOR:
        role = " [СТАРШИЙ МОДЕРАТОР]"
    else:
        role = ""
    creator_points_str = f"\n- Очков создания: {user.cp}\n" if user.cp else ""
    try:
        last_user_post_str = (
            f"\n- Последний пост игрока: "
            f"\"{(await user.get_page_comments())[0].body}\""
        )
    except gd.NothingFound:
        last_user_post_str = ""
    try:
        level_names_in_quotes = (
            f"\"{level.name}\""
            for level in (await user.get_levels_on_page())[0:3]
        )
    except gd.MissingAccess:
        last_user_levels_str = ""
    else:
        last_user_levels_str = (
            f"\n- Последние 3 уровня игрока: {', '.join(level_names_in_quotes)}"
        )
    return (
        f"• Игрок {user.name}{role}:\n\n"
        f"- Звезд на аккаунте: {user.stars}\n"
        f"- Алмазов на аккаунте: {user.diamonds}\n"
        f"- Монеток: {user.coins}\n"
        f"- Пользовательских монеток: {user.user_coins}\n"
        f"- Пройдено демонов: {user.demons}"
        f"{creator_points_str}"
        f"{last_user_post_str}"
        f"{last_user_levels_str}"
    )
