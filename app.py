import logging
import requests
import functools
import sys

from urllib.parse import urljoin
from bs4 import BeautifulSoup

logging.basicConfig(
    format='%(asctime)s %(levelname)s:%(message)s',
    level=logging.INFO)


url_to_crawl = 'https://google.com'
use_tor_network = False

if len(sys.argv) > 1: url_to_crawl = sys.argv[1]

session = requests.session()
if use_tor_network:
    session.request = functools.partial(session.request, timeout=30)
    session.proxies = {'http':  'socks5h://localhost:9050',
                        'https': 'socks5h://localhost:9050'}

class Crawler:
    def __init__(self, url):
        self.visited_urls = []
        self.original_url = url
        self.urls_to_visit = [url]

    def get_html_content(self, url):
        return session.get(url).text

    def get_linked_urls(self, url, html):
        soup = BeautifulSoup(html, 'html.parser')
        for link in soup.find_all('a'):
            path = link.get('href')
            if path and path.startswith('/'):
                path = urljoin(url, path)
            yield path
        
        for button in soup.find_all('button'):
            path = button.get('onclick')
            path = path.replace(' ','')
            path = path[path.find('location.href='):].replace('location.href=','')
            path = path.replace('\'', '')
            path = path.replace('\"', '')
            path = path.replace('`', '')
            if path and path.startswith('/'):
                path = urljoin(url, path)
            yield path

    def add_url_to_visit(self, url):
        if url and (url not in self.visited_urls) and (url not in self.urls_to_visit):
            self.urls_to_visit.append(url)

    def crawl(self, url):
        html = self.get_html_content(url)
        for url in self.get_linked_urls(url, html):
            if url and '://' not in url:
                url = urljoin(self.original_url, url)
            self.add_url_to_visit(url)

    def run(self):
        while self.urls_to_visit:
            url = self.urls_to_visit.pop(0)
            try:
                if (url not in self.visited_urls) and (url.startswith(self.original_url)):
                    logging.info(f'Crawling: {url}')
                    self.crawl(url)
            except Exception:
                logging.info(f'Failed to crawl: {url}')
            finally:
                if url not in self.visited_urls:
                    self.visited_urls.append(url)
        
        return self.visited_urls


sitemap = Crawler(url_to_crawl).run()

print('\nCrawled {} urls:\n'.format(len(sitemap)))
for url in sitemap: print(url)