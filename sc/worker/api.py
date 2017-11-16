from datetime import datetime
import time
import requests
import unicodecsv as csv
import argparse
import os, re, json
import numpy as np
import pandas as pd
import urllib3
import urllib.request
import multiprocessing
from tqdm import tqdm, tqdm_pandas

try:
    from lxml import html, etree
except:
    print("Please install `Python lXML` with this command before using `TripY`:")
    print()
    print("sudo apt-get install python3-lxml")
    quit()


class Type:
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
    download_start = time.time()
    api_response = requests.get(url).json()
    url_from_autocomplete = "http://www.tripadvisor.com" + api_response['results'][0]['url']
    print("URL for required location: ", url_from_autocomplete)
    # Parsing main INFO from response:
    RESULT['GEO_ID'] = api_response['results'][0]['value']
    RESULT['Location'] = api_response['results'][0]['details']['name']
    RESULT['Country'] = api_response['results'][0]['details']['parent_name']
    RESULT['Continent'] = api_response['results'][0]['details']['grandparent_name']
    RESULT['Coordinates'] = [float(t) for t in api_response['results'][0]['coords'].split(',')]
    print("Downloading search results page")
    # TODO ~1.3s/request
    page_response = requests.post(url=url_from_autocomplete).text
    # urllib.request.urlretrieve(url_from_autocomplete, 'test.html')
    parser = html.fromstring(page_response)

    # Get INFO from main page:
    XPATH_TEXT = '//*[@id="taplc_expanding_read_more_box_0"]/div/div[1]/text()'
    RESULT['Description'] = parser.xpath(XPATH_TEXT)[0][1:-1]

    # TODO test different xpathes and there performance
    XPATH_HOTEL_URL = '//*[@id="BODYCON"]/div[1]/div[1]/div/div[2]/div[2]/ul/li[contains(@class,"hotels")]/a/@href'
    XPATH_HOTEL_NUMBERS = '//*[@id="BODYCON"]/div[1]/div[1]/div/div[2]/div[2]/ul/li[contains(@class,"hotels")]/a/span[3]/text()'
    XPATH_HOTEL_REVIEW_NUMBERS = '//*[@id="BODYCON"]/div[1]/div[1]/div/div[2]/div[2]/ul/li[contains(@class,"hotels")]/a/span[4]/text()'
    # RESULT['URL_Hotel'] = parser.xpath(XPATH_HOTEL_URL)[0]
    # RESULT['Hotels_number'] = int(parser.xpath(XPATH_HOTEL_NUMBERS)[0][1:-1])
    # RESULT['Hotels_rew_number'] = int(''.join(re.findall("\d+", parser.xpath(XPATH_REVIEW_NUMBERS)[0])))
    hotels = Type(url=parser.xpath(XPATH_HOTEL_URL)[0],
                  numbers=to_numbers(parser.xpath(XPATH_HOTEL_NUMBERS)[0]),
                  r_num=to_numbers(parser.xpath(XPATH_HOTEL_REVIEW_NUMBERS)[0]))
    # TODO add loop for this similar items:
    XPATH_ATR_URL = '//*[@id="BODYCON"]/div[1]/div[1]/div/div[2]/div[2]/ul/li[contains(@class,"attractions")]/a/@href'
    XPATH_ATR_NUMBERS = '//*[@id="BODYCON"]/div[1]/div[1]/div/div[2]/div[2]/ul/li[contains(@class,"attractions")]/a/span[3]/text()'
    XPATH_ATR_REVIEW_NUMBERS = '//*[@id="BODYCON"]/div[1]/div[1]/div/div[2]/div[2]/ul/li[contains(@class,"attractions")]/a/span[4]/text()'
    attractions = Type(url=parser.xpath(XPATH_ATR_URL)[0],
                       numbers=to_numbers(parser.xpath(XPATH_ATR_NUMBERS)[0]),
                       r_num=to_numbers(parser.xpath(XPATH_ATR_REVIEW_NUMBERS)[0]))
    RESULT['HOTELS'] = hotels
    RESULT['ATTRACTIONS'] = attractions
    download_end = time.time()
    print("Finish: ", download_end - download_start, ' s')
