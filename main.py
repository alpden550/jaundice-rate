import asyncio
import time
from contextlib import asynccontextmanager

import aiofiles
import aiohttp
import pymorphy2
from anyio import create_task_group
from async_timeout import timeout
from loguru import logger

import adapters
import constants
import statuses
import text_tools
from adapters.inosmi_ru import sanitize


async def get_words(path: str) -> list:
    words = []
    async with aiofiles.open(path) as wf:
        async for line in wf:
            words.append(line.strip())
    return words


@asynccontextmanager
async def measure_execution_time():
    start = time.monotonic()
    yield
    finished = round(time.monotonic() - start, 2)
    logger.info(f"Анализ закончен за {finished} сек.")


async def fetch(session: aiohttp.ClientSession, url: str):
    async with session.get(url) as response:
        response.raise_for_status()
        return await response.text()


async def score_text(morph: pymorphy2.MorphAnalyzer, text: str, negative: list):
    words = text_tools.split_by_words(morph=morph, text=text)
    return text_tools.calculate_jaundice_rate(words, negative)


async def process_article(
        session: aiohttp.ClientSession,
        url: str,
        charged_words: list,
        morph: pymorphy2.MorphAnalyzer,
        results: list,
):
    about = {
        "URL": url,
        "Рейтинг": None,
        "Слов в статье": None,
        "Статус": None,
    }
    try:
        async with timeout(constants.ASYNC_TIMEOUT):
            html = await fetch(session=session, url=url)
            text = sanitize(html=html, plaintext=True)
            async with measure_execution_time():
                score = await score_text(morph=morph, text=text, negative=charged_words)

    except aiohttp.ClientError:
        about['Статус'] = statuses.ProcessingStatus.FETCH_ERROR.value
    except adapters.ArticleNotFound:
        about['Статус'] = statuses.ProcessingStatus.PARSING_ERROR.value
    except asyncio.TimeoutError:
        about['Статус'] = statuses.ProcessingStatus.TIMEOUT.value
    else:
        about['Статус'] = statuses.ProcessingStatus.OK.value
        about['Рейтинг'] = score
        about['Слов в статье'] = len(text)

    results.append(about)


async def main():
    negative_words = await get_words(path=constants.NEGATIVE_WORDS)
    morph = pymorphy2.MorphAnalyzer()
    async with aiohttp.ClientSession() as session:
        results = []
        for url in constants.TEST_ARTICLES:
            async with create_task_group() as tg:
                await tg.spawn(process_article, session, url, negative_words, morph, results)

        print(*results)


if __name__ == '__main__':
    asyncio.run(main())
