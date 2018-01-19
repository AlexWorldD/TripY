from __future__ import absolute_import
import time
from .worker import parse_link
from .entity import HEADERS, COOKIES
import requests
# TODO add to Docker
from lxml import html
from tqdm import tqdm
import multiprocessing



class Crawler:
    """
    Base structure for entities such as Hotels/Restaurants and et. al.
    Includes common info such as link and numbers of that entity.
    """

    def __init__(self, url='', numbers=0, r_num=0, path='', key='hotels'):
        """Create class represents specific entity for city"""
        self.url = 'https://www.tripadvisor.ru' + url
        self.numbers = numbers
        self.reviews_number = r_num
        self.links = []
        self.data = []
        self.path = path
        self.key = key

    def get_links(self, url):
        page_response = requests.get(url=url, headers=HEADERS, cookies=COOKIES)
        parser = ''
        if page_response.status_code == requests.codes.ok:
            parser = html.fromstring(page_response.content)
        else:
            print('bad response code: %d' % page_response.status_code)
            return
        return parser.xpath(self.path)

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
                self.links.extend(it)
            pool.close()

    def collect_data(self):
        """
        Function for collecting data from provided list of links
        :return:
        """
        download_start = time.time()
        for link in self.links:
            # Add new link for parsing to the queue
            parse_link.delay(link, self.key)
        download_end = time.time()
        print("Finished broadcasting links:", download_end - download_start, ' s')
