import aiohttp


class QuotesAPIClient:
    def __init__(self, api_url: str):
        self.api_url = api_url

    async def get_quote(self) -> str:
        async with aiohttp.ClientSession() as session:
            async with session.get(self.api_url) as resp:
                data = await resp.json()
                return data["quote"]
