import time
import requests
# TODO add to Docker
from lxml import html, etree
from tqdm import tqdm
import re
import multiprocessing

# CONSTANTS
HEADERS = {
	'Accept': 'text/javascript, text/html, application/xml, text/xml, */*',
	'Accept-Encoding': 'gzip,deflate',
	'Accept-Language': 'en-US,en;q=0.5',
	'Cache-Control': 'no-cache',
	'Connection': 'keep-alive',
	'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
	'Host': 'www.tripadvisor.com',
	'Pragma': 'no-cache',
	'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.89 Safari/537.36'
}

COOKIES = {"SetCurrency": "USD"}

def download(url):
    page_response = requests.get(url = url, headers = HEADERS, cookies = COOKIES)
    if page_response.status_code == requests.codes.ok:
        return html.fromstring(page_response.content);
    else:
        print('bad response code: %d' %page_response.status_code)

def check(root, query):
    tmp = root.xpath(query)
    return tmp[0] if len(tmp) > 0 else ''

def to_numbers(cur):
    if cur == '':
        return 0
    return int(''.join(re.findall("\d+", cur)))

from .entities import Entity
from .users import User

class Crawler:
    def __init__(self, url = '', numbers = 0, path = '', crawl_reviews = False):
        self.url = 'https://www.tripadvisor.ru' + url
        self.numbers = numbers
        self.entity_links = []
        self.entities = []
        self.users = {}
        self.path = path
        self.crawl_reviews = crawl_reviews
    
    def get_links(self, url):
        page_response = requests.get(url=url, headers=HEADERS, cookies=COOKIES)
        parser = ''
        if page_response.status_code == requests.codes.ok:
            parser = html.fromstring(page_response.content)
        else:
            print('bad response code: %d' % page_response.status_code)
            return
        return parser.xpath(self.path)

    def get_entity(self, url):
        entity = Entity(url = url)
        entity.collect_main_info(self.crawl_reviews)
        return entity

    def get_user(self, user_info):
        user = User(id = user_info['id'],
            nickname = user_info['nickname'],
            url = user_info['url'])
        user.collect_main_info()
        return user
    def collect_links(self):
        """
        Simple function for collection links to Hotels from different pages of search result
        :return:
        """
        # TODO fix this exception
        try:
            _link_l = '-'.join(self.url.split('-')[0:2])
            _link_r = '-'.join(self.url.split('-')[2:4])
        except:
            print("Can't split URL:", self.url, " to 2 parts!")

        _parts = self.numbers // 30 + 1
        # Parallel version:
        _part_url = []
        for it in range(_parts):
            _part_url.append(_link_l + '-oa' + str(it * 30) + '-' + _link_r)
        chunksize = 1
        with multiprocessing.Pool() as pool:
            for it in tqdm(pool.imap_unordered(self.get_links, _part_url, chunksize)):
                self.entity_links.extend(it)
            pool.close()
            
    def collect_entities(self, entity = None):
        """
        Function for collecting data from provided list of links
        :return:
        """
        download_start = time.time()
        chunksize = 1
        with multiprocessing.Pool(16) as pool:
            self.entities = pool.map(self.get_entity, self.entity_links)
            self.entities = [entry for entry in self.entities if (entry is not None and entry.title != '')]
            pool.close()

        download_end = time.time()
        print("Finished crawling entities:", download_end - download_start, ' s')

    def collect_users(self):
        """
        Function for collecting data from provided list of links
        :return:
        """
        download_start = time.time()
        chunksize = 1

        users = []
        for id in self.users:
            user = {
                'id': id,
                'url': self.users[id]['url'],
                'nickname': self.users[id]['nickname']
            }
            users.append(user)
                    
        with multiprocessing.Pool(16) as pool:
            self.users = pool.map(self.get_user, users)
            self.users = [entry for entry in self.users if entry is not None]
            pool.close()
                
        download_end = time.time()
        print("Finished crawling users:", download_end - download_start, ' s')

