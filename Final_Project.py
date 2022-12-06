import unittest
import sqlite3
import json
import os
import requests

uk_url = 'https://api.coronavirus.data.gov.uk/v1/data'
india_url = 'https://data.covid19india.org/v4/min/timeseries.min.json'
us_url = 'https://api.covidtracking.com/v2/us/daily.json'

def open_database(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def read_api(url):
    r = requests.get(url)
    info = r.text
    d = json.loads(info)
    return d


def uk_data(cur, conn):
    pass

def india_data(cur, conn):
    pass

def us_data():
    data = read_api(us_url)
    dates = data['data']
    for date_info in dates:
        date = date_info['date']
        total_cases = date_info['cases']['total']['value']
        new_cases = date_info['cases']['total']['calculated']['change_from_prior_day']
        total_deaths = date_info['outcomes']['death']['total']['value']
        new_deaths = date_info['outcomes']['death']['calculated']['change_from_prior_day']
        current_hospital = date_info['outcomes']['hospitalized']['currently']['value']
        current_icu = date_info['outcomes']['hospitalized']['in_icu']['currently']['value']
      



