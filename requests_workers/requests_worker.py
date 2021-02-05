from typing import List

import aiohttp
import bs4

POINTERCRATE_DEMONS_LINK = "https://pointercrate.com/api/v1/demons/"
POINTERCRATE_DEMONS_LIMIT = 100


class RequestsWorker:

    def __init__(self, aiohttp_session: aiohttp.ClientSession):
        self.aiohttp_session = aiohttp_session

    async def get_mobile_demons_site(self) -> bs4.BeautifulSoup:
        return bs4.BeautifulSoup(
            await (
                await self.aiohttp_session.get(
                    "https://sites.google.com/view/gd-mobile-lists"
                    "/top-100-demons-completed"
                )
            ).text(), "html.parser"
        )

    async def get_pc_demonlist_as_json(
            self, demons_amount: int) -> List[dict]:
        first_part = await self.aiohttp_session.get(
            POINTERCRATE_DEMONS_LINK,
            params={"limit": min(demons_amount, POINTERCRATE_DEMONS_LIMIT)}
            # Pointercrate isn't allowing to go above the limit
        )
        if demons_amount > POINTERCRATE_DEMONS_LIMIT:
            second_part = await self.aiohttp_session.get(
                POINTERCRATE_DEMONS_LINK,
                params={
                    "after": POINTERCRATE_DEMONS_LIMIT,
                    "limit": demons_amount - POINTERCRATE_DEMONS_LIMIT
                }
                # Getting remaining demons
            )
            return await first_part.json() + await second_part.json()
        return await first_part.json()


if __name__ == '__main__':
    import asyncio
    from handlers import handler_helpers


    async def main():
        async with aiohttp.ClientSession() as session:
            rw = RequestsWorker(session)
            site = await rw.get_mobile_demons_site()
            for demon_info in (
                handler_helpers.get_mobile_demons_info_from_soup(site)
            ):
                print(demon_info)


    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
