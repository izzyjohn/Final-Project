import unittest
import sqlite3
import json
import os
import requests

uk_url = 'https://api.coronavirus.data.gov.uk/v1/data'
india_url = 'https://data.covid19india.org/v4/min/timeseries.min.json'
us_url = 'https://api.covidtracking.com/v2/us/daily.json'

def read_api(url):
    r = requests.get(url)
    info = r.text
    d = json.loads(info)
    return d
#print(read_api(uk_url))

def uk_data(curr, conn):
    api_data = read_api(uk_url)
    data_dict = api_data['data']
    for d in data_dict:
        date = d["date"]
        area_name = d['areaName']
        area_code = d['areaCode']
        new_cases = d["latest_by"]
        total_cases = d['confirmed']
        new_deaths = d['deathNew']
        total_deaths = d['death']
    pass

print(uk_data())

def india_data(cur, conn):
    pass

def us_data(cur, conn):
    pass