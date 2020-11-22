import pymorphy2
from aiohttp import web, ClientSession

import constants
from main import get_words, process_article
from anyio import create_task_group


async def index(request: web.Request):
    morph = pymorphy2.MorphAnalyzer()
    negative_words = await get_words(constants.NEGATIVE_WORDS)
    urls = request.query.get('urls')
    results = []

    async with ClientSession() as session:
        for url in constants.TEST_ARTICLES:
            async with create_task_group() as tg:
                await tg.spawn(process_article, session, url, negative_words, morph, results)

    return web.json_response(results)


app = web.Application()
app.add_routes(
    [web.get('/', index)]
)

if __name__ == '__main__':
    web.run_app(app)
