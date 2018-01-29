import requests
import fake_useragent
from lxml import html
import json
import re
import time
from pymongo import MongoClient
from pymongo.errors import BulkWriteError, DuplicateKeyError
from TripY.cluster_managment import default_config as CONFIG

client = MongoClient(CONFIG.MONGO)  # change the ip and port to your Mongo database's
DB = client.TripY


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


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

_HEADERS_min = {
    'Accept': 'text/javascript, text/html, application/xml, text/xml, */*',
    'Connection': 'keep-alive',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.89 Safari/537.36'
}

COOKIES = {"SetCurrency": "USD"}


def random_header():
    _H = HEADERS
    _H['User-Agent'] = CONFIG.ui.random
    return _H


def download(url):
    """
    Function for downloading HTML page from server to local machine.
    """
    page_response = requests.get(url=url, headers=random_header(), cookies=COOKIES, allow_redirects=False)
    cnt = 0
    while page_response.status_code == 301:
        page_response = requests.get(url=url, headers=random_header(), cookies=COOKIES, allow_redirects=False)
        cnt += 1
        if cnt % 10 == 0:
            time.sleep(5)
        if cnt > 100:
            break
    if page_response.status_code == requests.codes.ok:
        return html.fromstring(page_response.content)
    elif page_response.status_code == 302:
        print('Redirect to', page_response.headers['Location'])
        page_response = requests.get(url=page_response.headers['Location'], headers=_HEADERS_min, cookies=COOKIES,
                                     allow_redirects=False)
        if page_response.status_code == requests.codes.ok:
            return html.fromstring(page_response.content)
        else:
            print(bcolors.WARNING + '[REVIEWS] bad response code: '+bcolors.ENDC, page_response.status_code)
    else:
        print(bcolors.WARNING+'[REVIEWS] bad response code after 100 repeats: '+bcolors.ENDC, page_response.status_code)


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
            self.phone = str(to_numbers(_st_add))
        except:
            pass
            # print("Can't parse phone number:", link)
        try:
            self.web = str(get_web(it[0].xpath('./div[@class="blEntry website"]/span/text()'), d_id, link))
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
    def __init__(self, url='', collection='hotel', geo_id=0, reviews=False):
        # TODO try to change to .com let's see)
        self.url = 'https://www.tripadvisor.ru' + url
        self.success = False
        self.type = ''
        self.title = ''
        self.ID = 0
        self.address = dict()
        self.contacts = Contacts()
        self.prices = ''
        self.avg_rating = 0
        self.crawl_reviews = reviews
        self.reviews_count = 0
        self.review_link = ''
        self.reviews = []
        self.visitors = dict()
        self.details = []
        self.collection = collection
        self.geo_id = geo_id

    def download(self):
        """
        Function for downloading HTML page from server to local machine.
        """
        page_response = requests.get(url=self.url, headers=random_header(), cookies=COOKIES, allow_redirects=False)
        cnt = 0
        while page_response.status_code == 301:
            page_response = requests.get(url=self.url, headers=random_header(), cookies=COOKIES, allow_redirects=False)
            cnt += 1
            if cnt % 10 == 0:
                print('Repeat request after 5s')
                time.sleep(5)
            if cnt > 100:
                break
        if page_response.status_code == requests.codes.ok:
            return html.fromstring(page_response.content)
        elif page_response.status_code == 302:
            print('Redirect to', page_response.url)
            print('Redirect2 to', page_response.headers['Location'])
            page_response = requests.get(url=page_response.url, headers=_HEADERS_min, cookies=COOKIES,
                                         allow_redirects=False)
            if page_response.status_code == requests.codes.ok:
                print('After redirect all cool!')
                return html.fromstring(page_response.content)
            else:
                print(page_response.history)
                print(bcolors.WARNING + 'bad response code: '+bcolors.ENDC, page_response.status_code)
        else:
            print('bad response code after 100 retries(: ', page_response.status_code)

    def collect_main_info(self):
        root = self.download()
        if root is None:
            print(bcolors.WARNING + 'Root is NONE for' + bcolors.ENDC, self.url)
            return
        title = check(root, '//h1[@id="HEADING"]/text()')
        print('Parsing: ', title)

        # ID = root.xpath('//div[@class="blRow"]/@data-locid')
        ID = root.xpath('//@data-locid')
        if len(ID) > 0:
            self.ID = int(ID[0])
        else:
            print(bcolors.WARNING + '[ERROR] ID not found!' + bcolors.ENDC, self.url)
        # Contacts parsing:
        _tmp = root.xpath(
            "/html/body[@id='BODY_BLOCK_JQUERY_REFLOW']/div[@id='PAGE']/div[@id='taplc_hr_atf_north_star_nostalgic_0']/div[@class='atf_header_wrapper']/div[@class='atf_header ui_container is-mobile full_width']/div[@id='taplc_location_detail_header_hotels_0']/div[@class='prw_rup prw_common_atf_header_bl headerBL']/div[@class='blRow']")
        _tmp = _tmp if len(_tmp) > 0 else root.xpath('//div[@class="blRow"]')
        if CONFIG._CONTACTS:
            self.contacts.parse(_tmp, d_id=self.ID, link=self.url)
        self.success = True
        # ---------
        _json = root.xpath('//script[@type="application/ld+json"]//text()')

        if len(_json) > 0:
            _json = json.loads(_json[0])
            self.type = _json['@type']
            self.title = _json['name']
            self.address['country'] = _json['address']['addressCountry']['name']
            self.address['region'] = _json['address']['addressRegion']
            self.address['locality'] = _json['address']['addressLocality']
            self.address['street_full'] = _json['address']['streetAddress']
            self.address['postal_code'] = _json['address']['postalCode']
            self.prices = _json['priceRange'] if 'priceRange' in _json else ''
            self.avg_rating = float(_json['aggregateRating']['ratingValue']) if 'aggregateRating' in _json else -1
            self.reviews_count = int(_json['aggregateRating']['reviewCount']) if 'aggregateRating' in _json else -1
            self.url = _json['url']

            # Reviews crawling:
            if self.reviews_count > 0 and self.crawl_reviews:
                _parsed_r = 0
                review_link_path = "//div[@class='review-container'][1]/div/div/div/div[2]/div/div[1]/div[2]/a/@href"
                review_link = root.xpath(review_link_path)
                if len(review_link) > 0:
                    self.review_link = 'https://www.tripadvisor.com/' + review_link[0]
                    while self.review_link != '':
                        review_page = download(self.review_link)
                        if review_page is not None:
                            self.reviews = []
                            next_page = check(review_page, "//div[@class='']/div/div/a[2]/@href")
                            self.review_link = 'https://www.tripadvisor.com/' + next_page if next_page != '' else ''
                            review_containers = review_page.xpath("//div[@class='reviewSelector']")
                            for container in review_containers:
                                # the first div inside the container contains a member info
                                review = dict()
                                review['ID'] = container.attrib['data-reviewid']
                                review['GEO_ID'] = self.geo_id
                                review['type'] = self.collection
                                user_id = check(container, 'div/div[1]/div/div/div[1]/@id')
                                user_nickname = check(container, 'div/div[1]/div/div/div[1]/div[2]/span/text()')

                                if len(user_id) > 4:
                                    user_id = user_id[4:].split('-')[0]

                                    if not user_id in self.visitors:
                                        self.visitors[user_id] = {
                                            'nickname': user_nickname,
                                            'url': 'https://www.tripadvisor.ru/MemberProfile-a_uid.' + user_id
                                        }
                                review['UID'] = user_id
                                review['user_nickname'] = user_nickname
                                wrap = container.xpath('div/div[2]/div/div[1]')
                                if len(wrap) > 0:
                                    wrap = wrap[0]
                                    rating = check(wrap, 'div[1]/span[1]/@class')
                                    review['rating'] = .1 * float(rating[-2:]) if len(rating) > 1 else ''
                                    review['date'] = check(wrap, 'div[1]/span[2]/@title')
                                    review['quote'] = check(wrap, 'div[2]/a/span/text()')
                                    review['text'] = check(wrap, 'div[3]/div/p/text()')
                                    review['ratings'] = wrap.xpath('div[4]/div/ul/li/ul/li')
                                    for i in range(len(review['ratings'])):
                                        rating = {}
                                        rating['rating'] = check(review['ratings'][i], 'div[1]/@class')
                                        rating['title'] = check(review['ratings'][i], 'div[2]/text()')
                                        rating['rating'] = .1 * float(rating['rating'][-2:]) if len(
                                            rating['rating']) > 1 else ''
                                        review['ratings'][i] = dict(rating)
                                self.reviews.append(review)
                            _parsed_r += len(self.reviews)
                            try:
                                DB.reviews.insert_many(self.reviews)
                            except BulkWriteError as exc:
                                t = exc.details
                                print(t)
                            print('Collected: ', _parsed_r, '/', self.reviews_count)
                        else:
                            print(bcolors.WARNING + 'Can\'t find review page! Continue parsing...' + bcolors.ENDC)
                            break
            self.details = root.xpath(details_xpath)
            print(bcolors.OKGREEN + 'Succeeded' + bcolors.ENDC)
        else:
            print(bcolors.WARNING + 'Failed with JSON' + bcolors.ENDC)

    def dictify(self):
        res = {
            'GEO_ID': self.geo_id,
            'type': self.type,
            'title': self.title,
            'url': self.url,
            '_id': int(self.ID),
            'address': dict(self.address),
            'contacts': self.contacts.__dict__,
            'prices': self.prices,
            'avg_rating': self.avg_rating,
            'reviews_count': self.reviews_count,
            'additional_details': list(self.details)
        }
        try:
            # DB[self.collection].update_one({'_id': res['_id']}, res, upsert=True)
            DB[self.collection].insert_one(res)
            # DB[self.collection].update({"noExist": True}, {"$setOnInsert": res}, True)
        except (BulkWriteError, DuplicateKeyError) as exc:
            print(bcolors.WARNING + '[ITEMS] Duplicate found!' + bcolors.ENDC, self.url)
            pass
        self.success = True
