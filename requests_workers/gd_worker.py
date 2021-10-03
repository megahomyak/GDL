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
        return await self.gd_client.search_user(player_name)

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
