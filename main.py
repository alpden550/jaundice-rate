import asyncio

import aiofiles
import aiohttp
import pymorphy2

import text_tools
from adapters.inosmi_ru import sanitize

NEGATIVE_WORDS = "charged_dict/negative_words.txt"
POSITIVE_WORDS = "charged_dict/positive_words.txt"


async def fetch(session, url, morph):
    async with session.get(url) as response:
        response.raise_for_status()
        content = await response.text()

        sanitazed_text = sanitize(content, plaintext=True)
        return await scoore_text(morph, sanitazed_text)


async def scoore_text(morph: pymorphy2.MorphAnalyzer, text: str):
    words = text_tools.split_by_words(morph=morph, text=text)
    negative_words = await get_words(NEGATIVE_WORDS)
    print(negative_words)
    print(text_tools.calculate_jaundice_rate(words, negative_words))


async def get_words(path: str) -> list:
    words = []
    async with aiofiles.open(path) as wf:
        async for line in wf:
            words.append(line.strip())
    return words


async def main():
    morph = pymorphy2.MorphAnalyzer()
    async with aiohttp.ClientSession() as session:
        html = await fetch(session, 'https://inosmi.ru/economic/20190629/245384784.html', morph)
        print(html)


asyncio.run(main())
