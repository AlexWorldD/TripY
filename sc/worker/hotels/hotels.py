import time
import requests
from tqdm import tqdm
from abc import ABC, abstractmethod
import re, json

try:
    from lxml import html, etree
except:
    print("Please install `Python lXML` with this command before using `TripY`:")
    print()
    print("sudo apt-get install python3-lxml")
    quit()


def test_parsing(parser, queue, iterations=10000):
    """
    DEV function for testing parsing performance for required queue
    :param parser: HTML parser object
    :param queue: xPath
    :return: Spend times
    """
    if len(parser.xpath(queue)) == 0:
        print('Wrong queue!')
        return 0
    download_start = time.time()
    for it in tqdm(range(iterations)):
        parser.xpath(queue)
    download_end = time.time()
    print('\nxPath: ', queue)
    print("Finish crawling:", download_end - download_start, ' s')


def show_xpath(data):
    """
    DEV function for printing xPath parsing results
    :param data: return from xPath parser
    :return:
    """
    print(etree.tostring(data[0], pretty_print=True))


def to_numbers(cur):
    """Helpful function for cleaning HTML string to int value"""
    if cur == '':
        return 0
    return int(''.join(re.findall("\d+", cur)))


def get_value(it):
    """
    Simplest funtion for explicit outing of range
    :param it: parsing result
    :return:
    """
    return it[0] if len(it) > 0 else ''


def get_web(it, d_id):
    """
    Special function for getting WEB-address via HTTP-request as mobile device and parsing response headers
    :param d_id: location id, required for request to server
    :return: link to the official site
    """
    _HEADERS = {
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Host': 'www.tripadvisor.com',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.89 Safari/537.36'
    }
    _url = 'https://www.tripadvisor.com/ShowUrl?&excludeFromVS=true&odc=MobileBusinessListingsUrl&d=' + d_id + '&url=1'
    if len(it) > 0:
        _raw_web = requests.post(url=_url, headers=_HEADERS, allow_redirects=False).headers._store['location'][1]
        return _raw_web.split('?')[0]
    else:
        return ''


class Address:
    """
    Simple structure for address entity: country, city, street and et al.
    """

    def __init__(self):
        """Create class represents specific entity for city"""
        self.zip = 0
        self.country = ''
        self.city = ''
        self.street = ''
        self.extended = ''
        self.building = 0

    def parse(self, it):
        """
        Function for parsing HTML-object to splitting values
        :param it: parent HTML-object, includes the address information
        :return:
        """
        # SPEED: 330 iterations per second
        # TODO make robust for nan values or not-find DOM element
        _st_add = it.xpath('./div/span[@class="street-address"]/text()')[0].split(',')
        self.street = _st_add[0]
        self.building = _st_add[1]
        # _tmp = it.xpath('./div/span[@class="extended-address"]/text()')
        # _tmp = _tmp[0] if len(_tmp) > 0 else ''
        self.extended = str(get_value(it.xpath('./div/span[@class="extended-address"]/text()')))
        _st_add = it.xpath('./div/span[@class="locality"]/text()')[0]
        self.zip = int(''.join(re.findall("\d+", _st_add)))
        self.city = ''.join(re.findall("\D+\\b", _st_add))[0:-1]
        self.country = str(it.xpath('./div/span[@class="country-name"]/text()')[0])


class Contacts:
    """
    Simple structure for available contacts for entity
    """

    def __init__(self):
        """Empty instance of class"""
        self.phone = 0
        self.web = ''

    def parse(self, it, d_id):
        """
        Function for parsing HTML-object to splitting values
        :param it: parent HTML-object, includes the contacts information
        :return:
        """
        # SPEED: 330 iterations per second
        # TODO make robust for nan values or not-find DOM element
        _st_add = get_value(it[0].xpath('./div[@class="blEntry phone"]/span/text()'))
        self.phone = to_numbers(_st_add)
        # TODO try to parse link to official site...
        self.web = get_web(it[0].xpath('./div[@class="blEntry website"]/span/text()'), d_id)


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
        self.parser = ''

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
        self.title = ''
        self.address = Address()
        self.contacts = Contacts()
        self.ID = None

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
        self.download()
        print('Collecting main info')
        # TODO try to use hierarchical parsing
        # _parser_header = self.parser.xpath('//*[@id="taplc_hr_atf_north_star_nostalgic_0"]/div[1]')[0]
        # TODO add cleaning string
        # test_parsing(self.parser, '//h1[@id="HEADING"]/text()')
        # TODO add choosing of relative vs. absolute xPaths
        # self.title = self.parser.xpath("/html/body[@id='BODY_BLOCK_JQUERY_REFLOW']/div[@id='PAGE']/div[@id='taplc_hr_atf_north_star_nostalgic_0']/div[@class='atf_header_wrapper']/div[@class='atf_header ui_container is-mobile full_width']/div[@id='taplc_location_detail_header_hotels_0']/h1[@id='HEADING']/text()")
        _tmp = self.parser.xpath('//h1[@id="HEADING"]/text()')
        self.title = _tmp[0] if len(_tmp) > 0 else ''
        _tmp = self.parser.xpath(
            "/html/body[@id='BODY_BLOCK_JQUERY_REFLOW']/div[@id='PAGE']/div[@id='taplc_hr_atf_north_star_nostalgic_0']/div[@class='atf_header_wrapper']/div[@class='atf_header ui_container is-mobile full_width']/div[@id='taplc_location_detail_header_hotels_0']/div[@class='prw_rup prw_common_atf_header_bl headerBL']/div[@class='blRow']")
        _tmp = _tmp if len(_tmp) > 0 else self.parser.xpath('//div[@class="blRow"]')
        self.ID = str(_tmp[0].xpath('@data-locid')[0])
        self.json = json.loads(self.parser.xpath('//script[@type="application/ld+json"]//text()')[0])
        if len(_tmp) > 0:
            self.address.parse(_tmp[0])
            self.contacts.parse(_tmp, d_id=self.ID)
        print('fine')


# https://www.tripadvisor.com/ShowUrl?&excludeFromVS=true&odc=MobileBusinessListingsUrl&d=543462&url=1


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
