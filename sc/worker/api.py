from datetime import datetime
from time import time
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


# action:API
# types:geo,nbrhd,hotel,theme_park
# filter:
# legacy_format:true
# urlList:true
# strictParent:true
# query:Перм
# max:6
# name_depth:3
# interleaved:true
# scoreThreshold:0.5
# strictAnd:false
# typeahead1_5:true
# disableMaxGroupSize:true
# geoBoostFix:true
# neighborhood_geos:true
# details:true
# link_type:hotel,vr,eat,attr
# rescue:true
# uiOrigin:trip_search_Hotels
# source:trip_search_Hotels
# startTime:1510670874327
# searchSessionId:4F676AF9780ADA335F1225290C3AB9E61510670583642ssid
# nearPages:true

def parse(location):
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
          '&link_type=hotel%2Cvr%2Ceat%2Cattr' \
          '&uiOrigin=GEOSCOPE' \
          '&source=GEOSCOPE' \
          '&query='+urllib.parse.quote(location)

    #  GET to TripAdvisor for required location:
    api_response = requests.get(url).json()
    url_from_autocomplete = "http://www.tripadvisor.com" + api_response['results'][0]['url']
    print(url_from_autocomplete)
    geo_id = api_response['results'][0]['value']
