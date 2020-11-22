import pymorphy2
from aiohttp import web, ClientSession
from aiohttp_utils import run
from anyio import create_task_group

import constants
from main import get_words, process_article


async def index(request: web.Request):
    query_urls = request.query.get('urls')
    if not query_urls:
        return web.json_response(data={"error": "No url founded in the request."}, status=400)

    morph = pymorphy2.MorphAnalyzer()
    negative_words = await get_words(constants.NEGATIVE_WORDS)

    urls = query_urls.split(",")
    if len(urls) > constants.URLS_LIMIT:
        return web.json_response(data={"error": "too many urls in request, should be 10 or less"}, status=400)

    articles_results = await handle_urls(urls=urls, morph=morph, charged=negative_words)

    return web.json_response(articles_results)


async def handle_urls(urls: list, morph: pymorphy2.MorphAnalyzer, charged: list):
    results = []
    async with ClientSession() as session:
        for url in urls:
            async with create_task_group() as tg:
                await tg.spawn(process_article, session, url, charged, morph, results)
    return results


app = web.Application()
app.add_routes(
    [web.get('/', index)]
)

if __name__ == '__main__':
    run(app, reload=True, app_uri="server:app")
