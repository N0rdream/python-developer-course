import asyncio
import aiohttp
import os
import hashlib
import argparse
import logging
from collections import namedtuple
from bs4 import BeautifulSoup


BASE_URL = 'https://news.ycombinator.com'
COMMENTS_BASE_URL = 'https://news.ycombinator.com/item?id='

Page = namedtuple('Page', ['url', 'html'])
Topic = namedtuple('Topic', ['link', 'id'])


class Handler:

    def __init__(self, max_connections, connect_timeout, 
                reconnect_max_attempts, reconnect_delay):
        self.max_connections = max_connections
        self.connect_timeout = aiohttp.ClientTimeout(total=connect_timeout)
        self.reconnect_max_attempts = reconnect_max_attempts
        self.reconnect_delay = reconnect_delay
        self.semaphores = {}

    async def fetch(self, url, session):
        async with session.get(url) as response:
            try:
                if 'text/html' in response.headers['Content-Type']:
                    html = await response.read()
                    return Page(url, html)
                else:
                    logging.info(f'Not html: {url}')
                    return
            except KeyError:
                logging.info(f'Bad headers: {url}')
                return

    def get_semaphore(self, url):
        url_root = url.split('/')[2]
        if not url_root in self.semaphores:
            self.semaphores[url_root] = asyncio.Semaphore(self.max_connections)
        return self.semaphores[url_root]

    async def get_html(self, url):
        semaphore = self.get_semaphore(url)
        async with semaphore:
            async with aiohttp.ClientSession(timeout=self.connect_timeout) as session:
                attempts = 0
                while True:
                    try:
                        return await self.fetch(url, session)
                    except asyncio.TimeoutError:
                        if attempts < self.reconnect_max_attempts:
                            attempts += 1
                            await asyncio.sleep(self.reconnect_delay)
                            logging.info(f'Reconnect #{attempts}. URL: {url}.')
                        else:
                            logging.info(f'Connection timeout: {url}')
                            return
                    except aiohttp.client_exceptions.ClientConnectorError:
                        logging.info(f'No address associated with hostname: {url}')
                        return

    def clear(self):
        self.semaphores = {}


def get_topics(html):
    soup = BeautifulSoup(html, 'lxml')
    rows = soup.find_all('tr', class_='athing')
    for row in rows:
        a = row.find('a', class_='storylink')
        if is_link_external(a['href']):
            yield Topic(a['href'], row['id'])


def save_page(html, topic_dir, url):
    page_name = hashlib.md5(url.encode()).hexdigest()
    path = os.path.join(topic_dir, page_name + '.html')
    with open(path, 'wb') as fp:
        fp.write(html)


def get_comments_links(html):
    soup = BeautifulSoup(html, 'lxml')
    anchors = soup.find_all('a')
    for a in anchors:
        if is_link_external(a['href']):
            yield a['href']


def is_link_external(link):
    return link.startswith('http') and 'ycombinator' not in link


async def process_topic(topic, handler, topics_dir):
    
    if not os.path.exists(topics_dir):
        os.makedirs(topics_dir)

    topic_dir = os.path.join(topics_dir, topic.id)
    if os.path.exists(topic_dir):
        logging.info(f'Already parsed: {topic.link}')
        return

    topic_page = await handler.get_html(topic.link)
    if topic_page is None:
        return

    loop = asyncio.get_running_loop()

    os.makedirs(topic_dir)
    await loop.run_in_executor(
        None, 
        save_page, 
        topic_page.html, topic_dir, topic_page.url
    )

    link_page = await handler.get_html(COMMENTS_BASE_URL + topic.id)
    if link_page is None:
        return

    links_from_comments = list(set(get_comments_links(link_page.html)))
    tasks = [handler.get_html(link) for link in links_from_comments]
    for task in asyncio.as_completed(tasks):
        link_page =  await task
        if link_page is None:
            continue
        await loop.run_in_executor(
            None,
            save_page, 
            link_page.html, topic_dir, link_page.url
        )


def get_cmd_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--max_connections', type=int, default=3)
    parser.add_argument('-t', '--connect_timeout', type=int, default=10)
    parser.add_argument('-i', '--sleep_interval', type=int, default=60)
    parser.add_argument('-a', '--reconnect_max_attempts', type=int, default=3)
    parser.add_argument('-d', '--reconnect_delay', type=float, default=0.5)
    parser.add_argument('-f', '--topics_dir', type=str, default='')
    return parser.parse_args()


async def worker(handler, topics_dir):
    logging.info('Started.')
    main_page = await handler.get_html(BASE_URL)
    topics = get_topics(main_page.html)
    tasks = [process_topic(topic, handler, topics_dir) for topic in topics]
    await asyncio.wait(tasks)
    logging.info('Finished.')


async def main():

    args = get_cmd_args()
    logging.basicConfig(
        level=logging.INFO,
        filename=None,
        format='[%(asctime)s] %(levelname).1s %(message)s',
        datefmt='%Y.%m.%d %H:%M:%S'
    )

    handler = Handler(args.max_connections, args.connect_timeout, 
        args.reconnect_max_attempts, args.reconnect_delay)

    try:
        while True:
            asyncio.create_task(worker(handler, args.topics_dir))
            await asyncio.sleep(args.sleep_interval)
            if len(asyncio.all_tasks()) == 1:
                handler.clear()
    except Exception as e:
        logging.exception(f'Unexpected error: {e}')


if __name__ == '__main__':
    asyncio.run(main())
