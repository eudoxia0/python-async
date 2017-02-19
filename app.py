import asyncio

print("Hello, world!")

# Database

import sqlalchemy as sa
from aiopg.sa import create_engine


metadata = sa.MetaData()

threads_table = sa.Table('threads', metadata,
                         sa.Column('id', sa.Integer, primary_key=True),
                         sa.Column('title', sa.Text()),
                         sa.Column('url', sa.Text()))


async def ensure_tables_exist():
    async with create_engine(user='postgres',
                             password='postgres',
                             database='postgres',
                             host='postgres') as engine:
        async with engine.acquire() as conn:
            await conn.execute('DROP TABLE threads')
            await conn.execute(sa.schema.CreateTable(threads_table))
        print("Created tables!")

# Scraper

from aiohttp import client
from bs4 import BeautifulSoup


async def get_front_page():
    response = await client.get('https://news.ycombinator.com/')
    html = await response.read()
    soup = BeautifulSoup(html, 'html.parser')
    links = soup.find_all('a')

    # Python 3.6 lets supports asynchronous generators, which would fit this
    # case, but for this example returning the full list is fine since all the
    # processing is in the CPU

    def parse_link(link):
        if link.get('class', None) == ['storylink']:
            url = link['href']
            text = link.string
            # Despite the aiohttp documentation, the response is not UTF-8 encoded
            return (url, text.encode('utf-8'))

    return filter(lambda x: x is not None, [parse_link(link) for link in links])

# Entry point

loop = asyncio.get_event_loop()
loop.run_until_complete(ensure_tables_exist())
links = loop.run_until_complete(get_front_page())
for l in links:
    try:
        print(l)
    except:
        print("Error")
loop.close()
