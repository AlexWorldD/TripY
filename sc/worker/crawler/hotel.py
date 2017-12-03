from entity import Entity
import requests
import json
from lxml import html, etree

class Hotel(Entity):
    """
    Entity for Hotel
    """

    def collect_main_info(self):
        self.download()
        # print('Collecting main info')
        # TODO try to use hierarchical parsing
        # _parser_header = self.parser.xpath('//*[@id="taplc_hr_atf_north_star_nostalgic_0"]/div[1]')[0]
        # TODO add cleaning string
        # test_parsing(self.parser, '//h1[@id="HEADING"]/text()')
        # TODO add choosing of relative vs. absolute xPaths
        # self.title = self.parser.xpath("/html/body[@id='BODY_BLOCK_JQUERY_REFLOW']/div[@id='PAGE']/div[@id='taplc_hr_atf_north_star_nostalgic_0']/div[@class='atf_header_wrapper']/div[@class='atf_header ui_container is-mobile full_width']/div[@id='taplc_location_detail_header_hotels_0']/h1[@id='HEADING']/text()")
        _tmp = self.parser.xpath('//h1[@id="HEADING"]/text()')
        self.title = _tmp[0] if len(_tmp) > 0 else ''
        print('title: %s' %self.title)
        _tmp = self.parser.xpath(
            "/html/body[@id='BODY_BLOCK_JQUERY_REFLOW']/div[@id='PAGE']/div[@id='taplc_hr_atf_north_star_nostalgic_0']/div[@class='atf_header_wrapper']/div[@class='atf_header ui_container is-mobile full_width']/div[@id='taplc_location_detail_header_hotels_0']/div[@class='prw_rup prw_common_atf_header_bl headerBL']/div[@class='blRow']")
        _tmp = _tmp if len(_tmp) > 0 else self.parser.xpath('//div[@class="blRow"]')
        self.ID = str(_tmp[0].xpath('@data-locid')[0])
        data = json.loads(self.parser.xpath('//script[@type="application/ld+json"]//text()')[0])
        self.prices = data['priceRange'] if 'priceRange' in data else '???'
        self.avg_rating = data['aggregateRating']['ratingValue'] if 'aggregateRating' in data else '???'
        self.reviews_count = data['aggregateRating']['reviewCount']  if 'aggregateRating' in data else '???'
        if len(_tmp) > 0:
            self.address.parse(_tmp[0], link=self.url)
            self.contacts.parse(_tmp[0], d_id=self.ID, link=self.url)
        # TODO after all data parsing we MUST DELETE HTML-Element from class instance, otherwise is F8cking errors
        self.parser = ''
