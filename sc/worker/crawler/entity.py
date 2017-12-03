import requests
from lxml import html
from abc import ABC, abstractmethod
from tqdm import tqdm
import re
import multiprocessing
from crawler import HEADERS, COOKIES
from pathos.multiprocessing import ProcessingPool as Pool

def get_value(it):
    """
    Simplest function for explicit outing of range
    :param it: parsing result
    :return:
    """
    return it[0] if len(it) > 0 else ''

def to_numbers(cur):
    """Helpful function for cleaning HTML string to int value"""
    if cur == '':
        return 0
    return int(''.join(re.findall("\d+", cur)))

def get_web(it, d_id, link):
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
    _url = 'https://www.tripadvisor.com/ShowUrl?&excludeFromVS=true&odc=MobileBusinessListingsUrl&d=' + d_id + '&url='
    if len(it) > 0:
        for _t in range(4):
            __url = _url + str(_t)
            _r = requests.post(url=__url, headers=_HEADERS, allow_redirects=False)
            if _r.status_code != 404:
                try:
                    _raw_web = _r.headers._store['location'][1]
                    return _raw_web.split('?')[0]
                except:
                    print("Error! Can't get WEB!", link)
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
        self.building = ''
	
    def print(self):
        print('Address:')
        print('    ZIP code: %d' %self.zip)
        print('    Country: %s' %self.country)
        print('    City: %s' %self.city)
        print('    Street: %s' %self.street)
        print('    Extended: %s' %self.extended)
        print('    Building: %s' %self.building)	
	
    def parse(self, it, link=''):
        """
        Function for parsing HTML-object to splitting values
        :param it: parent HTML-object, includes the address information
        :return:
        """
        # SPEED: 330 iterations per second
        # TODO make robust for nan values or not-find DOM element
        _st_add = ''
        try:
            _st_add = it.xpath('./div/span[@class="street-address"]/text()')[0].split(',')
        except IndexError:
            print("Can't parse street address: ", link)
        _l = len(_st_add)
        self.street = _st_add[0] if _l > 0 else ''
        self.building = _st_add[1] if _l > 1 else ''
        self.extended = str(get_value(it.xpath('./div/span[@class="extended-address"]/text()')))
        address = it.xpath('div[1]/span[@class="locality"]/text()')[0]

        try:
            self.zip = int(''.join(re.findall("\d+", address)))
        except:
            print("Can't parse ZIP:", link)
        try:
            self.city = ''.join(re.findall("\D+\\b", address))[0:-1]
        except:
            print("Can't parse city:", link)
        try:
            self.country = str(it.xpath('./div/span[@class="country-name"]/text()')[0])
        except:
            print("Can't parse country:", link)

class Contacts:
    """
    Simple structure for available contacts for entity
    """

    def __init__(self):
        """Empty instance of class"""
        self.phone = 0
        self.web = ''

    def print(self):
        print('Contacts:')
        print('    Phone number: %d' %self.phone)
        print('    Web-Site: %s' %self.web)

    def parse(self, it, d_id, link=''):
        """
        Function for parsing HTML-object to splitting values
        :param it: parent HTML-object, includes the contacts information
        :return:
        """
        # SPEED: 330 iterations per second
        # TODO make robust for nan values or not-find DOM element
        try:
            _st_add = get_value(it.xpath('div[contains(@class, "phone")][1]/span[2]/text()'))
            self.phone = to_numbers(_st_add)
        except:
            print("Can't parse phone number:", link)
        try:
            self.web = get_web(it[0].xpath('./div[@class="blEntry website"]/span/text()'), d_id, link)
        except:
            print("Can't parse WEB-site:", link)
            
class Entity(ABC):
    """
    Abstract class for THE Hotel/Restaurant and et. al.
    Includes common info such as link, address, rating and etc.
    """

    def __init__(self, url=''):
        """Abstract initialisation for class"""
        self.url = 'https://www.tripadvisor.ru' + url
        super(Entity, self).__init__()
        self.title = ''
        self.address = Address()
        self.contacts = Contacts()
        self.ID = None

    def download(self):
        """
        Function for downloading HTML page from server to local machine.
        """
        # TODO try to modify for AJAX request, should be ~2.2 times faster
        page_response = requests.get(url=self.url, headers=HEADERS, cookies=COOKIES)
        if page_response.status_code == requests.codes.ok:
            self.parser = html.fromstring(page_response.content)
        else:
            print('bad response code: %d' %page_response.status_code)

    @abstractmethod
    def collect_main_info(self):
        pass
