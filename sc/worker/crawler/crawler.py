import time
import requests
from lxml import html, etree
from abc import ABC, abstractmethod
from tqdm import tqdm
import re
import multiprocessing
from pathos.multiprocessing import ProcessingPool as Pool

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
	# 'X-Requested-With': 'XMLHttpRequest'
}

COOKIES = {"SetCurrency": "USD"}

class Crawler:
    """
    Base structure for entities such as Hotels/Restaurants and et. al.
    Includes common info such as link and numbers of that entity.
    """
    def __init__(self, url='', numbers=0, r_num=0, crawler=None):
        """Create class represents specific entity for city"""
        self.url = 'https://www.tripadvisor.ru' + url
        self.numbers = numbers
        self.reviews_number = r_num
        self.links = []
        self.data = []
        self.entity_crawler = crawler #entity_crawler var contains a constructor of specific entity crawler
	
    def get_links(self, url):
        page_response = requests.get(url=url, headers=HEADERS, cookies=COOKIES)
        parser = ''
        if page_response.status_code == requests.codes.ok:
            parser = html.fromstring(page_response.content)
        else:
            print('bad response code: %d' %page_response.status_code)
            return
        # return parser.xpath('//div[contains(@class,"hasDates")]/div[contains(@class,"prw_meta_hsx")]/div[@class="listing"]//div[@class="listing_title"]/a/@href')
        return parser.xpath(self.entity_crawler.link_path)

    def get_entity(self, url):
        entity = self.entity_crawler(url = url)
        entity.collect_main_info()
        return entity
        
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
        chunksize = 1
        # with multiprocessing.Pool() as pool:
        #     for it in tqdm(pool.imap_unordered(get_hotel, self.links, chunksize)):
        #         self.data.append(it)
        # Sequence execution: 1.3s per one hotel item
        # for it in tqdm(self.links):
        #     self.data.append(get_hotel(it))
        # TODO find balance for network bandwidth and CPU performance

        with multiprocessing.Pool(16) as pool:
            self.data = pool.map(self.get_entity, self.links)
            pool.close()
                
        download_end = time.time()
        print("Finished crawling:", download_end - download_start, ' s')

