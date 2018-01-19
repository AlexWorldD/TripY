import requests
from lxml import html
import json
import re
from .crawler import HEADERS, COOKIES

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

link_paths = {
    'hotel': '//div[contains(@class,"hasDates")]/div[contains(@class,"prw_meta_hsx")]/div[@class="listing"]//div[@class="listing_title"]/a/@href',
    'attraction': '//div[@class="listing_title "]/a/@href',
    'restaurant': '//a[@class="property_title"]/@href'
}

details_xpath = "//div[@class='highlightedAmenity detailListItem']/text()"

class Entity():
    def __init__(self, url = ''):
        self.url = 'https://www.tripadvisor.ru' + url
        self.type = ''
        self.title = ''
        self.ID = 0
        self.address = {}
        self.contacts = Contacts()
        self.prices = ''
        self.avg_rating = 0
        self.reviews_count = 0
        self.review_link = ''
        self.reviews = []
        self.visitors = {}
        self.details = []

    def download(self, url = None):
        """
        Function for downloading HTML page from server to local machine.
        """
        # TODO try to modify for AJAX request, should be ~2.2 times faster
        if url is None:
            url = self.url
        
        page_response = requests.get(url = url, headers = HEADERS, cookies = COOKIES)
        if page_response.status_code == requests.codes.ok:
            return html.fromstring(page_response.content);
        else:
            print('bad response code: %d' %page_response.status_code)

    def collect_main_info(self, crawl_reviews = False, users_dict = None):
        root = self.download()
        if root is None:
            return;

        title = check(root, '//h1[@id="HEADING"]/text()')
        print(title)

        ID = root.xpath('//@data-locid');
        if len(ID) > 0:
            # Not sure if the first one is always the one we need
            self.ID = int(ID[0])

        _json = root.xpath('//script[@type="application/ld+json"]//text()')

        if len(_json) > 0:
            _json = json.loads(_json[0])
            
            self.type =  _json['@type']
            self.title = _json['name']
            
            self.address['country'] = _json['address']['addressCountry']['name'] 
            self.address['region'] = _json['address']['addressRegion']
            self.address['locality'] = _json['address']['addressLocality'] 
            self.address['street_full'] = _json['address']['streetAddress'] 
            self.address['postal_code'] = _json['address']['postalCode'] 

            self.prices = _json['priceRange'] if 'priceRange' in _json else ''
            self.avg_rating = float(_json['aggregateRating']['ratingValue']) if 'aggregateRating' in _json else 0
            self.reviews_count = int(_json['aggregateRating']['reviewCount']) if 'aggregateRating' in _json else 0

            if self.reviews_count > 0 and crawl_reviews:
                review_link_path = "//div[@class='review-container'][1]/div/div/div/div[2]/div/div[1]/div[2]/a/@href"
                review_link = root.xpath(review_link_path)
                if len(review_link) > 0:
                    self.review_link = 'https://www.tripadvisor.com/' + review_link[0]
                    while self.review_link != '':
                        review_page = self.download(self.review_link)
                        if review_page is not None:
                            next_page = check(review_page, "//div[@class='']/div/div/a[2]/@href")
                            self.review_link = 'https://www.tripadvisor.com/' + next_page if next_page != '' else ''
                            review_containers = review_page.xpath("//div[@class='reviewSelector']/div")
                            for container in review_containers:
                                # the first div inside the container contains a member info
                                review = {}
                                review['UID'] = check(container, 'div[1]/div/div/div[1]/@id')

                                if len(review['UID']) > 4:
                                    review['UID'] = (review['UID'][4:]).split('-')[0]

                                    if not review['UID'] in self.visitors:
                                        self.visitors[review['UID']] = 'https://www.tripadvisor.ru/MemberProfile-a_uid.' + review['UID']

                                review['user_nickname'] = check(container, 'div[1]/div/div/div[1]/div[2]/span/text()')
                                wrap = container.xpath('div[2]/div/div[1]')
                                if len(wrap) > 0:
                                    wrap = wrap[0]
                                    rating = check(wrap, 'div[1]/span[1]/@class')
                                    review['rating']  = .1 * float(rating[-2:]) if len(rating) > 1 else ''
                                    review['date']    = check(wrap, 'div[1]/span[2]/@title')
                                    review['quote']   = check(wrap, 'div[2]/a/span/text()')
                                    review['text']    = check(wrap, 'div[3]/div/p/text()')
                                    review['ratings'] = wrap.xpath('div[4]/div/ul/li/ul/li')
                                    for i in range(len(review['ratings'])):
                                        rating = {}
                                        rating['rating'] = check(review['ratings'][i], 'div[1]/@class')
                                        rating['title'] = check(review['ratings'][i], 'div[2]/text()')
                                        rating['rating']  = .1 * float(rating['rating'][-2:]) if len(rating['rating']) > 1 else ''
                                        review['ratings'][i] = dict(rating)
                                self.reviews.append(review)
            self.url = _json['url']
            self.details = root.xpath(details_xpath)

    def dictify(self):
        return {
            'type': self.type,
            'title': self.title,
            'url': self.url,
            'id': self.ID,
            'address': dict(self.address),
            'contacts': self.contacts.__dict__,
            'prices': self.prices,
            'avg_rating': self.avg_rating,
            'reviews_count': self.reviews_count,
            'reviews': self.reviews,
            'additional_details': list(self.details)
        }
