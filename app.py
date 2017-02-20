import asyncio

print("Hello, world!")

# Database
import sqlalchemy as sa
from sqlalchemy.orm.session import sessionmaker
from aiopg.sa import create_engine

metadata = sa.MetaData()

threads_table = sa.Table('threads', metadata,
                         sa.Column('id', sa.Integer, primary_key=True),
                         sa.Column('title', sa.Text()),
                         sa.Column('url', sa.Text()))

def default_engine():
    return create_engine(user='postgres',
                         password='postgres',
                         database='postgres',
                         host='postgres')

async def ensure_tables_exist():
    async with default_engine() as engine:
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
            return (url, text)

    return filter(lambda x: x is not None, [parse_link(link) for link in links])

async def store_front_page(links):
    """Downloads the front page, and adds it to the DB."""
    async with default_engine() as engine:
        async with engine.acquire() as conn:
            # aiopg doesn't support executemany
            for (url, title) in links:
                await conn.execute(threads_table.insert().values(title=title, url=url))

        async with engine.acquire() as conn:
            result = await conn.execute("SELECT * FROM threads")
            selected = await result.fetchall()
            print(len(selected))

# Entry point

loop = asyncio.get_event_loop()
loop.run_until_complete(ensure_tables_exist())
links = loop.run_until_complete(get_front_page())
print("Boutta store the front page")
loop.run_until_complete(store_front_page(links))
print("Stored the front page")
loop.close()
