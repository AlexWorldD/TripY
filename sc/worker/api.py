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


def test():
    print('done')