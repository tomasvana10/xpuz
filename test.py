import aiohttp
import asyncio
from json import loads


async def main():
    async def fetch(session, url):
        async with session.get(url) as response:
            print(response.status)
            return await response.text()
        
    async with aiohttp.ClientSession() as session:
        html = await fetch(session, 'https://api.github.com/repos/tomasvana10/crossword_puzzle/releases/latest')
        print(loads(html)["name"])

# Run the main function
asyncio.run(main())