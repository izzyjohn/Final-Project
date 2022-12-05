import unittest
import sqlite3
import json
import os
<<<<<<< HEAD
=======
import requests

uk_url = 'https://api.coronavirus.data.gov.uk/v1/data'
india_url = 'https://data.covid19india.org/v4/min/timeseries.min.json'
us_url = 'https://api.covidtracking.com/v2/us/daily.json

def read_api(url):
    r = requests.get(url)
    info = r.text
    d = json.loads(info)
    return d
>>>>>>> 2e6819e9a6a10115b70810864d606a9ffe7358d8


def uk_data(cur, conn):
    pass

def india_data(cur, conn):
    pass

def us_data(cur, conn):
    pass