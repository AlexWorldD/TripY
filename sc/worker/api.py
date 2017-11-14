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


def parse(location):
    geo_url = 'https://www.tripadvisor.com/TypeAheadJson?action=API&startTime=' + str(int(
        time())) + '&uiOrigin=GEOSCOPE&source=GEOSCOPE&interleaved=true&types=geo,theme_park&neighborhood_geos=true&link_type=hotel&details=true&max=12&injectNeighborhoods=true&query=' + location
    api_response = requests.get(geo_url).json()
    # getting the TA url for th equery from the autocomplete response
    url_from_autocomplete = "http://www.tripadvisor.com" + api_response['results'][0]['url']
    geo = api_response['results'][0]['value']