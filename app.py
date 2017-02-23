import asyncio

# Database
import sqlalchemy as sa


metadata = sa.MetaData()

Posts = sa.Table('threads', metadata,
                         sa.Column('id', sa.Integer, primary_key=True),
                         sa.Column('title', sa.Text()),
                         sa.Column('url', sa.Text()))
engine = sa.create_engine('postgresql://postgres:postgres@postgres/postgres')

def ensure_tables_exist():
    with engine.connect() as conn:
        conn.execute('DROP TABLE threads')
        conn.execute(sa.schema.CreateTable(Posts))

# Scraper
from tornado import httpclient
from bs4 import BeautifulSoup
from datetime import timedelta
from tornado.gen import with_timeout, convert_yielded


async def get_front_page():
    """Download and scrape the front page, returning a tuple of link URL and title."""
    http_client = httpclient.HTTPClient()
    response = http_client.fetch('https://news.ycombinator.com/')
    html = response.body
    http_client.close()

    soup = BeautifulSoup(html, 'html.parser')
    links = soup.find_all('a')

    # Ideally, turn this into a (Python 3.6-only) async generator
    def parse_link(link):
        if link.get('class', None) == ['storylink']:
            url = link['href']
            title = link.string
            return (url, title)

    return filter(lambda x: x is not None, [parse_link(link) for link in links])

def store_front_page(links):
    """Downloads the front page, and adds it to the DB."""
    with engine.connect() as conn:
        conn.execute(Posts.insert(),
                     [{ 'title': title, 'url': url } for (url, title) in links])

# Server

import json

import tornado.ioloop
import tornado.web


class PostsHandler(tornado.web.RequestHandler):
    """
    Handler for the posts resource.
    """

    def get_data(self):
        with engine.connect() as conn:
            result = conn.execute(Posts.select())
            return result.fetchall()

    async def get(self):
        """
        Return a list of posts from the database.
        """
        data = self.get_data()
        self.write(json.dumps([{ 'title': title, 'url': url }
                               for (id, title, url) in data]))


class RefreshHandler(tornado.web.RequestHandler):
    """
    Handler for scraping Hacker News again.
    """

    async def get(self):
        links = await get_front_page()
        store_front_page(links)
        self.write({ 'status': 'ok' })


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")


class Application(tornado.web.Application):
    def __init__(self):
        tornado.web.Application.__init__(self, [
            (r"/posts", PostsHandler),
            (r"/refresh", RefreshHandler),
            (r'/', MainHandler)
        ], debug=True)

# Entry point

ensure_tables_exist()

app = Application()
app.listen(5000)
tornado.ioloop.IOLoop.current().start()
