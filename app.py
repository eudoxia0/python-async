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


async def ensure_tables_exist(engine):
    async with engine.acquire() as conn:
        await conn.execute('DROP TABLE IF EXISTS ')
        await conn.execute('''CREATE TABLE tbl (
                                  id serial PRIMARY KEY,
                                  val varchar(255))''')


async def go():
    async with create_engine(user='pg',
                             database='hn',
                             host='postgres',
                             password='pg') as engine:
        await ensure_tables_exist(engine)
        print("Created tables!")

# Entry point

loop = asyncio.get_event_loop()
loop.run_until_complete(go())
