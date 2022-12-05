import unittest
import sqlite3
import json
import os
import requests

uk_url = 'https://api.coronavirus.data.gov.uk/v1/data'
india_url = 'https://data.covid19india.org/v4/min/timeseries.min.json'
us_url = 'https://api.covidtracking.com/v2/us/daily.json

def read_api(url):
    r = requests.get(url)
    info = r.text
    d = json.loads(info)
    return d


def uk_data(cur, conn):
    pass

def india_data(cur, conn):
    pass

def us_data(cur, conn):
    pass