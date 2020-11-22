import aiohttp
import pymorphy2
import pytest

import constants
from articles import process_article, get_words


@pytest.fixture
async def session():
    async with aiohttp.ClientSession() as session:
        yield session


@pytest.fixture
async def negatives():
    words = await get_words(constants.NEGATIVE_WORDS)
    yield words


@pytest.fixture(scope="module")
def morph():
    morph = pymorphy2.MorphAnalyzer()
    yield morph


@pytest.fixture(scope="module")
def url():
    url = "https://inosmi.ru/social/20201119/248573478.html"
    yield url


@pytest.mark.asyncio
async def test_process_article(session, url, morph, negatives):
    results = []
    await process_article(
        session=session, url=url, charged_words=negatives, morph=morph, results=results,
    )

    assert results
    assert results[0]['Статус'] == 'OK'


@pytest.mark.asyncio
async def test_process_wrong_url(session, morph, negatives):
    results = []
    url = 'http://example.com'
    await process_article(
        session=session, url=url, charged_words=negatives, morph=morph, results=results,
    )

    assert results
    assert results[0]['Статус'] == 'PARSING ERROR'


@pytest.mark.asyncio
async def test_process_with_timeout(session, url, morph, negatives):
    results = []
    await process_article(
        session=session, url=url, charged_words=negatives, morph=morph, results=results, max_timeout=0,
    )

    assert results
    assert results[0]['Статус'] == 'TIMEOUT'


@pytest.mark.asyncio
async def test_process_with_invalid_url(session, morph, negatives):
    results = []
    url = 'https://inosmi.ru/science/123/123.html'
    await process_article(
        session=session, url=url, charged_words=negatives, morph=morph, results=results,
    )

    assert results
    assert results[0]['Статус'] == 'FETCH ERROR'
