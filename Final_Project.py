import unittest
import sqlite3
import json
import os
import requests

uk_url = 'https://api.coronavirus.data.gov.uk/v1/data'
canada_url = 'https://api.covid19tracker.ca/reports'
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

def canada_data(api_data, cur, conn):
    data_dict = api_data['data']
    cur. execute("DROP TABLE IF EXISTS Canada")
    cur.execute('CREATE TABLE IF NOT EXISTS Canada (date TEXT, total_cases INTEGER, change_cases INTEGER, total_fatalities INTEGER, change_fatalities INTEGER, total_criticals INTEGER, total_hospitalizations INTEGER)')
    for x in data_dict:
        date = x['date']
        total_cases = x['total_cases']
        change_cases = x['change_cases']
        total_fatalities = x['total_fatalities']
        change_fatalities = x['change_fatalities']
        total_criticals = x['total_criticals']
        total_hospitalizations = x['total_hospitalizations']
        cur.execute("INSERT OR IGNORE INTO Canada (date, total_cases, change_cases, total_fatalities, change_fatalities, total_criticals, total_hospitalizations) VALUES (?, ?, ?, ?, ?, ?, ?)", (date, total_cases, change_cases, total_fatalities, change_fatalities, total_criticals, total_hospitalizations))
    conn.commit()

data = read_api(canada_url)
print(canada_data(data))

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
      



