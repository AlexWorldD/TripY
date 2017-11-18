from datetime import datetime
import time
import codecs
import requests
import unicodecsv as csv
import argparse
import os, re, json
import numpy as np
import pandas as pd
import urllib3
import urllib.request
from lxml import html, etree
import multiprocessing
from tqdm import tqdm, tqdm_pandas
from worker.hotels import *

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

try:
    from lxml import html, etree
except:
    print("Please install `Python lXML` with this command before using `TripY`:")
    print()
    print("sudo apt-get install python3-lxml")
    quit()


class PlacesType:
    """Specific structure for entities such as Hotels/Restaurants and et. al."""

    def __init__(self, url='', descr='', numbers=0, r_num=0):
        """Create class represents specific entity for city"""
        self.url = 'https://www.tripadvisor.ru' + url
        # self.description = descr
        self.numbers = numbers
        self.reviews_number = r_num


def to_numbers(cur):
    """Helpful function for cleaning HTML string to int value"""
    return int(''.join(re.findall("\d+", cur)))


def main_page(query):
    download_start = time.time()
    tmp = 'https://www.tripadvisor.ru/TypeAheadJson?action=API' \
          '&types=geo%2Cnbrhd%2Chotel%2Ctheme_park' \
          '&filter=' \
          '&legacy_format=true' \
          '&urlList=true' \
          '&strictParent=true' \
          '&query=%D0%9F%D0%B5%D1%80%D0%BC' \
          '&max=6' \
          '&name_depth=3' \
          '&interleaved=true' \
          '&scoreThreshold=0.5' \
          '&strictAnd=false' \
          '&typeahead1_5=true' \
          '&disableMaxGroupSize=true' \
          '&geoBoostFix=true' \
          '&neighborhood_geos=true' \
          '&details=true' \
          '&link_type=hotel%2Cvr%2Ceat%2Cattr' \
          '&rescue=true' \
          '&uiOrigin=trip_search_Hotels' \
          '&source=trip_search_Hotels' \
          '&startTime=1510670874327' \
          '&searchSessionId=4F676AF9780ADA335F1225290C3AB9E61510670583642ssid' \
          '&nearPages=true'
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
    # possible_types = ['hotels', 'flights', 'attractions', 'restaurants', 'vacationRentals', 'forum']
    possible_types = {'hotels': Hotels}
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
        RESULT[key.upper()] = possible_types[key](url=_url,
                                                  numbers=_numbers,
                                                  r_num=_r_num)
    RESULT['HOTELS'].collect_links()
    download_end = time.time()
    print("Finish crawling MAIN page: ", download_end - download_start, ' s')
    return RESULT
