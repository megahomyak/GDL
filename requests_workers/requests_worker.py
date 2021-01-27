import aiohttp
import bs4


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


if __name__ == '__main__':
    import asyncio
    from handlers import handler_helpers


    async def main():
        async with aiohttp.ClientSession() as session:
            rw = RequestsWorker(session)
            site = await rw.get_mobile_demons_site()
            for demon_info in handler_helpers.get_demons_info_from_soup(site):
                print(demon_info)


    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
