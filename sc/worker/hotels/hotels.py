import time
import requests
from tqdm import tqdm
from abc import ABC, abstractmethod

try:
    from lxml import html, etree
except:
    print("Please install `Python lXML` with this command before using `TripY`:")
    print()
    print("sudo apt-get install python3-lxml")
    quit()


class PlacesType:
    """
    Base structure for entities such as Hotels/Restaurants and et. al.
    Includes common info such as link and numbers of that entity.
    """

    def __init__(self, url='', numbers=0, r_num=0):
        """Create class represents specific entity for city"""
        self.url = 'https://www.tripadvisor.ru' + url
        self.numbers = numbers
        self.reviews_number = r_num
        self.host = 'https://www.tripadvisor.ru'
        self.parser=''

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
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.89 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest'
    }
    COOKIES = {"SetCurrency": "USD"}


class AbstractPlace(ABC):
    """
    Abstract class for THE Hotel/Restaurant and et. al.
    Includes common info such as link, address, rating and etc.
    """

    def __init__(self, url=''):
        """Abstract initialisation for class"""
        self.url = 'https://www.tripadvisor.ru' + url
        self.host = 'https://www.tripadvisor.ru'
        super(AbstractPlace, self).__init__()

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

    def download(self):
        """
        Function for downloading HTML page from server to local machine.
        """
        # TODO try to modify for AJAX request, should be ~2.2 times faster
        page_response = requests.get(url=self.url, headers=self.HEADERS, cookies=self.COOKIES).text
        self.parser = html.fromstring(page_response)

    @abstractmethod
    def collect_main_info(self):
        pass


class Hotel(AbstractPlace):
    """
    Entity for Hotel
    """
    def collect_main_info(self):
        print('Collecting main info')


class Hotels(PlacesType):
    """
    Specific class for hotel entity
    """
    links = []

    def collect_links(self):
        """
        Special function for crawling data about Hotels form search queue
        """
        # HEADERS['Referer'] = referer
        # Start crawling MAIN-PAGE HTML page about required location:
        print("Downloading HOTELS search results page")
        self._get()

    def _get(self):
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
        for it in tqdm(range(_parts)):
            _part_url = _link_l + '-oa' + str(it * 30) + '-' + _link_r
            # TODO ~1.3s/request
            # TODO using with headers increase loading size 3 times: from 18k of lines to 8k.
            page_response = requests.get(url=_part_url, headers=self.HEADERS, cookies=self.COOKIES).text
            parser = html.fromstring(page_response)
            self.links.extend(parser.xpath(
                '//div[contains(@class,"hasDates")]/div[contains(@class,"prw_meta_hsx")]/div[@class="listing"]//div[@class="listing_title"]/a/@href'))
