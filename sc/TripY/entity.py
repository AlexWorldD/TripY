import requests
from lxml import html
import json
import re
from pymongo import MongoClient
from TripY.cluster_managment import default_config as CONFIG

client = MongoClient(CONFIG.MONGO)  # change the ip and port to your mongo database's
DB = client.TripY

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
    _url = 'https://www.tripadvisor.com/ShowUrl?&excludeFromVS=true&odc=MobileBusinessListingsUrl&d=' + str(
        d_id) + '&url='
    if len(it) > 0:
        for _t in range(4):
            __url = _url + str(_t)
            _r = requests.post(url=__url, headers=_HEADERS, allow_redirects=False)
            if _r.status_code != 404:
                try:
                    _raw_web = _r.headers._store['location'][1]
                    return _raw_web.split('?')[0]
                except:
                    continue
                    print("Error! Can't get WEB!", link)
    else:
        return ''


def check(root, query):
    tmp = root.xpath(query)
    return tmp[0] if len(tmp) > 0 else ''


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
        print('    Phone number: %d' % self.phone)
        print('    Web-Site: %s' % self.web)

    def parse(self, it, d_id, link=''):
        """
        Function for parsing HTML-object to splitting values
        :param it: parent HTML-object, includes the contacts information
        :return:
        """
        # SPEED: 330 iterations per second
        # TODO make robust for nan values or not-find DOM element
        try:
            _st_add = get_value(it[0].xpath('div[contains(@class, "phone")][1]/span[2]/text()'))
            self.phone = to_numbers(_st_add)
        except:
            pass
            # print("Can't parse phone number:", link)
        try:
            self.web = get_web(it[0].xpath('./div[@class="blEntry website"]/span/text()'), d_id, link)
        except:
            pass
            # print("Can't parse WEB-site:", link)


link_paths = {
    'hotel': '//div[contains(@class,"hasDates")]/div[contains(@class,"prw_meta_hsx")]/div[@class="listing"]//div[@class="listing_title"]/a/@href',
    'attraction': '//div[@class="listing_title "]/a/@href',
    'restaurant': '//a[@class="property_title"]/@href'
}

details_xpath = "//div[@class='highlightedAmenity detailListItem']/text()"


class Entity():
    def __init__(self, url='', collection='hotels', geo_id=0):
        self.url = 'https://www.tripadvisor.ru' + url
        self.success = False
        self.type = ''
        self.title = ''
        self.ID = 0
        self.address = {}
        self.contacts = Contacts()
        self.prices = ''
        self.avg_rating = 0
        self.reviews_count = 0
        self.details = []
        self.collection = collection
        self.geo_id = geo_id

    def download(self):
        """
        Function for downloading HTML page from server to local machine.
        """
        # TODO try to modify for AJAX request, should be ~2.2 times faster
        page_response = requests.get(url=self.url, headers=HEADERS, cookies=COOKIES, allow_redirects=False)
        if page_response.status_code == requests.codes.ok:
            return html.fromstring(page_response.content)
        else:
            print('bad response code: %d' % page_response.status_code)

    def collect_main_info(self):
        root = self.download()
        if root is None:
            return

        title = check(root, '//h1[@id="HEADING"]/text()')
        print("Parsing '%s' . . . " % title, end='')

        # ID = root.xpath('//div[@class="blRow"]/@data-locid')
        ID = root.xpath('//@data-locid')
        if len(ID) > 0:
            # Not sure if the first one is always the one we need
            self.ID = int(ID[0])
            # For testing WEB parsing
            # if self.ID == 300189:
            #     print('t')
        #     Parsing WEB and Phone
        _tmp = root.xpath(
            "/html/body[@id='BODY_BLOCK_JQUERY_REFLOW']/div[@id='PAGE']/div[@id='taplc_hr_atf_north_star_nostalgic_0']/div[@class='atf_header_wrapper']/div[@class='atf_header ui_container is-mobile full_width']/div[@id='taplc_location_detail_header_hotels_0']/div[@class='prw_rup prw_common_atf_header_bl headerBL']/div[@class='blRow']")
        _tmp = _tmp if len(_tmp) > 0 else root.xpath('//div[@class="blRow"]')
        self.contacts.parse(_tmp, d_id=self.ID, link=self.url)
        # ---------
        _json = root.xpath('//script[@type="application/ld+json"]//text()')

        if len(_json) > 0:
            print('Succeeded')

            _json = json.loads(_json[0])

            self.type = _json['@type']
            self.title = _json['name']

            self.address['country'] = _json['address']['addressCountry']['name']
            self.address['region'] = _json['address']['addressRegion']
            self.address['locality'] = _json['address']['addressLocality']
            self.address['street_full'] = _json['address']['streetAddress']
            self.address['postal_code'] = _json['address']['postalCode']

            self.prices = _json['priceRange'] if 'priceRange' in _json else ''
            self.avg_rating = _json['aggregateRating']['ratingValue'] if 'aggregateRating' in _json else -1
            self.reviews_count = _json['aggregateRating']['reviewCount'] if 'aggregateRating' in _json else -1

            self.url = _json['url']

            self.details = root.xpath(details_xpath)

        else:
            print('Failed')

    def dictify(self):
        res = {
            'GEO_ID': self.geo_id,
            'type': self.type,
            'title': self.title,
            'url': self.url,
            'id': int(self.ID),
            'address': dict(self.address),
            'contacts': self.contacts.__dict__,
            'prices': self.prices,
            'avg_rating': float(self.avg_rating),
            'reviews_count': int(self.reviews_count),
            'additional_details': list(self.details)
        }
        DB[self.collection].insert_one(res)
        self.success = True
