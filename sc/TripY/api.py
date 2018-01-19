import urllib.request
import os, sys
import time
import requests
from .crawler import Crawler
from .entity import to_numbers, link_paths
from pymongo import MongoClient
from TripY.cluster_managment import default_config as CONFIG

client = MongoClient(CONFIG.MONGO)
DB = client.TripY

sys.path.insert(0, os.path.abspath(".."))
try:
    from lxml import html, etree
except:
    print("Please install `Python lXML` with this command before using `TripY`:")
    print()
    print("sudo apt-get install python3-lxml")
    quit()


def main_page(query):
    download_start = time.time()
    RESULT = {}
    url = 'https://www.tripadvisor.ru/TypeAheadJson?action=API' \
          '&types=geo,hotel,vr,eat,attr' \
          '&max=6' \
          '&scoreThreshold=0.5' \
          '&strictAnd=false' \
          '&typeahead1_5=true' \
          '&disableMaxGroupSize=true' \
          '&geoBoostFix=true' \
          '&neighborhood_geos=true' \
          '&details=true' \
          '&link_type=geo,hotel,vr,eat,attr' \
          '&uiOrigin=GEOSCOPE' \
          '&source=GEOSCOPE' \
          '&query=' + urllib.parse.quote(query)
    #  GET to TripAdvisor for required location:
    api_response = requests.get(url).json()
    url_from_autocomplete = "http://www.tripadvisor.com" + api_response['results'][0]['url']
    print("URL for required location: ", url_from_autocomplete)

    # Parsing main INFO from RESPONSE:

    RESULT['GEO_ID'] = api_response['results'][0]['value']
    RESULT['Location'] = api_response['results'][0]['details']['name']
    RESULT['Country'] = api_response['results'][0]['details']['parent_name']
    RESULT['Continent'] = api_response['results'][0]['details']['grandparent_name']
    RESULT['Coordinates'] = [float(t) for t in api_response['results'][0]['coords'].split(',')]

    # Start crawling MAIN-PAGE HTML page about required location:
    print("Downloading search results page")
    # TODO ~1.3s/request
    page_response = requests.post(url=url_from_autocomplete).text
    # urllib.request.urlretrieve(url_from_autocomplete, 'test.html') # Test downloading page for visual comparing.
    parser = html.fromstring(page_response)
    # Get INFO from main page:
    XPATH_TEXT = '//*[@id="taplc_expanding_read_more_box_0"]/div/div[1]/text()'
    _descr = parser.xpath(XPATH_TEXT)

    RESULT['Description'] = _descr[0][1:-1] if len(_descr) > 0 else ''

    # Specify all possible places for city
    # possible_types = link_paths.keys()
    possible_types = ['hotel']  # for testing

    for key in possible_types:
        # TODO test different xpathes and there performance
        XPATH_URL = parser.xpath(
            '//*[@id="BODYCON"]/div[1]/div[1]/div/div[2]/div[2]/ul/li[contains(@class,"' + key + '")]/a/@href')
        XPATH_NUMBERS = parser.xpath(
            '//*[@id="BODYCON"]/div[1]/div[1]/div/div[2]/div[2]/ul/li[contains(@class,"' + key + '")]/a/span[3]/text()')
        XPATH_REVIEW_NUMBERS = parser.xpath(
            '//*[@id="BODYCON"]/div[1]/div[1]/div/div[2]/div[2]/ul/li[contains(@class,"' + key + '")]/a/span[4]/text()')
        _url = XPATH_URL[0] if len(XPATH_URL) > 0 else ''
        _numbers = to_numbers(XPATH_NUMBERS[0]) if len(XPATH_NUMBERS) else 0
        _r_num = to_numbers(XPATH_REVIEW_NUMBERS[0]) if len(XPATH_REVIEW_NUMBERS) else 0
        crawler = Crawler(url=_url,
                          numbers=_numbers,
                          r_num=_r_num,
                          path=link_paths[key],
                          key=key
                          )
        crawler.collect_links()
        print('%d links collected' % len(crawler.links))
        crawler.collect_data()
        DB['GEO'].insert_one(RESULT)
        # RESULT['Entities'][key + 's'] = [entity.dictify() for entity in crawler.data]
    download_end = time.time()
    print("Finished crawling MAIN page: ", download_end - download_start, ' s')
    return RESULT
