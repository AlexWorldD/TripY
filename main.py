#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
import json
import sys
import TripY.api as TripY
from pymongo import MongoClient

if __name__ == '__main__':
    query = sys.argv[1] if len(sys.argv) > 1 else 'Perm'
    # out = sys.argv[2] if len(sys.argv) > 2 else 'output.json'

    query = input('Please enter a city: ')
    # out = input('Please enter filename: ')
    # out = out if len(out) > 0 else 'output.json'
    result = TripY.main_page(query if len(query) > 0 else 'Санкт')
    # with open(out, 'w') as f:
    #     json.dump(result, f, indent=4, ensure_ascii=False)
    print('Done')
