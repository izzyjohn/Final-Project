import unittest
import sqlite3
import json
import os
<<<<<<< HEAD
=======
import requests

uk_url = 'https://api.coronavirus.data.gov.uk/v1/data'
canada_url = 'https://api.covid19tracker.ca/reports'
us_url = 'https://api.covidtracking.com/v2/us/daily.json'

def read_api(url):
    r = requests.get(url)
    info = r.text
    d = json.loads(info)
    return d
>>>>>>> 2e6819e9a6a10115b70810864d606a9ffe7358d8

def uk_data(cur, conn):
    pass

def canada_data(api_data, cur, con):
    data_dict = api_data['data']
    for x in data_dict:
        date = x['date']
        total_cases = x['total_cases']
        change_cases = x['change_cases']
        total_fatalities = x['total_fatalities']
        change_fatalities = x['change_fatalities']
        total_criticals = x['total_criticals']
        total_hospitalizations = x['total_hospitalizations']




    pass

data = read_api(canada_url)
print(canada_data(data))

def us_data(cur, conn):
    pass