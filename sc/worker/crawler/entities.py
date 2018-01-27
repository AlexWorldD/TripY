import requests
from lxml import html
import json
link_paths = {
    'hotel': '//div[contains(@class,"hasDates")]/div[contains(@class,"prw_meta_hsx")]/div[@class="listing"]//div[@class="listing_title"]/a/@href',
    'attraction': '//div[@class="listing_title "]/a/@href',
    'restaurant': '//a[@class="property_title"]/@href'
}

details_xpath = "//div[@class='highlightedAmenity detailListItem']/text()"


class Entity():
    def __init__(self, url=''):
        self.url = 'https://www.tripadvisor.ru' + url
        self.type = ''
        self.title = ''
        self.ID = 0
        self.address = {}
        self.prices = ''
        self.avg_rating = 0
        self.reviews_count = 0
        self.review_link = ''
        self.reviews = []
        self.visitors = {}
        self.details = []
    def collect_main_info(self, crawl_reviews = False):
        root = download(self.url)

        if root is not None:
            title = check(root, '//h1[@id="HEADING"]/text()')

            print('collecting info about: ', title)
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
                            review_page = download(self.review_link)
                            if review_page is not None:
                                next_page = check(review_page, "//div[@class='']/div/div/a[2]/@href")
                                self.review_link = 'https://www.tripadvisor.com/' + next_page if next_page != '' else ''
                                review_containers = review_page.xpath("//div[@class='reviewSelector']/div")
                                for container in review_containers:
                                    # the first div inside the container contains a member info
                                    review = {}
                                    user_id = check(container, 'div[1]/div/div/div[1]/@id')
                                    user_nickname = check(container, 'div[1]/div/div/div[1]/div[2]/span/text()')

                                    if len(user_id) > 4:
                                        user_id = user_id[4:].split('-')[0]

                                        if not user_id in self.visitors:
                                            self.visitors[user_id] = {
                                                'nickname': user_nickname,
                                                'url': 'https://www.tripadvisor.ru/MemberProfile-a_uid.' + user_id
                                            }
                                            
                                    review['UID'] = user_id
                                    review['user_nickname'] = user_nickname
                                    
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
                self.details = root.xpath(details_xpath)

    def dictify(self):
        res = {
            'type': self.type,
            'title': self.title,
            'url': self.url,
            '_id': int(self.ID),
            'address': dict(self.address),
            'prices': self.prices,
            'avg_rating': self.avg_rating,
            'reviews_count': self.reviews_count,
            'reviews': self.reviews,
            'additional_details': list(self.details)
        }
        
from .crawler import download, check, to_numbers
