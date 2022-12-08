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

def uk_data(cur, conn):
    api_data = read_api(uk_url)
    data_dict = api_data['data']
    reversed_list = data_dict[::-1]
    cur.execute('CREATE TABLE IF NOT EXISTS UK (date TEXT, new_cases INTEGER, total_cases INTEGER, \
    n_death_id TEXT, total_deaths INTEGER)')
    res = cur.execute("SELECT * FROM UK")
    num_entries = len(res.fetchall())
    dates25 = reversed_list[num_entries:num_entries + 25]
    for d in dates25:
        date = d["date"]
        new_cases = d["latestBy"]
        total_cases = d['confirmed']
        new_deaths = d['deathNew']
        if new_deaths == "None":
            n_death_category = "very low"
        elif type(new_deaths) == int:
            if new_deaths < 10:
                n_death_category = "very low"
            elif new_deaths < 50:
                n_death_category = "low"
            elif new_deaths < 150:
                n_death_category = "medium"
            elif new_deaths < 275:
                n_death_category = "high"
            else:
                n_death_category = "very high"
        else:
            n_death_category = "very low"
        res = cur.execute(f"SELECT id FROM death_category WHERE category = '{n_death_category}'")
        n_death_id = res.fetchone()[0]
        total_deaths = d['death']
        cur.execute("INSERT OR IGNORE INTO UK (date, new_cases, total_cases, n_death_id, total_deaths) \
        VALUES (?, ?, ?, ?, ?)", (date, new_cases, total_cases, n_death_id, total_deaths))
    conn.commit()

def uk_category_table(cur, conn):
    cur.execute("CREATE TABLE IF NOT EXISTS death_category (id INTEGER PRIMARY KEY, category TEXT UNIQUE)")
    categories = ["very low", "low", "medium", "high", "very high"]
    for i in range(len(categories)):
        cur.execute("INSERT OR IGNORE INTO death_category (id, category) VALUES (?, ?)", (i,categories[i]))
    conn.commit()

def canada_data(cur, conn):
    api_data = read_api(canada_url)
    data_dict = api_data['data']
    cur.execute('CREATE TABLE IF NOT EXISTS Canada (date TEXT, total_cases INTEGER, change_cases INTEGER, \
    total_fatalities INTEGER, change_fatalities INTEGER, total_criticals INTEGER, total_hospitalizations INTEGER)')
    res = cur.execute("SELECT * FROM Canada")
    num_entries = len(res.fetchall())
    dates25 = data_dict[num_entries:num_entries + 25]
    for x in dates25:
        date = x['date']
        total_cases = x['total_cases']
        change_cases = x['change_cases']
        total_fatalities = x['total_fatalities']
        change_fatalities = x['change_fatalities']
        total_criticals = x['total_criticals']
        total_hospitalizations = x['total_hospitalizations']
        cur.execute("INSERT OR IGNORE INTO Canada (date, total_cases, change_cases, total_fatalities, change_fatalities, \
        total_criticals, total_hospitalizations) VALUES (?, ?, ?, ?, ?, ?, ?)", (date, total_cases, change_cases, \
        total_fatalities, change_fatalities, total_criticals, total_hospitalizations))
    conn.commit()

def us_data(cur, conn):
    data = read_api(us_url)
    dates = data['data']
    reversed_list = dates[::-1]
    cur.execute('CREATE TABLE IF NOT EXISTS usa (date TEXT, total_cases INTEGER, change_cases INTEGER, total_deaths INTEGER,\
         change_deaths INTEGER, current_hospital INTEGER, current_icu INTEGER)')
    res = cur.execute("SELECT * FROM usa")
    num_entries = len(res.fetchall())
    dates25 = reversed_list[num_entries:num_entries + 25]
    for date_info in dates25:
        date = date_info['date']
        total_cases = date_info['cases']['total']['value']
        change_cases = date_info['cases']['total']['calculated']['change_from_prior_day']
        total_deaths = date_info['outcomes']['death']['total']['value']
        change_deaths = date_info['outcomes']['death']['total']['calculated']['change_from_prior_day']
        current_hospital = date_info['outcomes']['hospitalized']['currently']['value']
        current_icu = date_info['outcomes']['hospitalized']['in_icu']['currently']['value']
        cur.execute("INSERT OR IGNORE INTO usa (date, total_cases, change_cases, total_deaths, change_deaths, current_hospital, current_icu) \
            VALUES(?,?,?,?,?,?,?)", (date, total_cases, change_cases, total_deaths, change_deaths, current_hospital, current_icu))
    conn.commit()

def main():
    cur, conn = open_database('covid.db')
    uk_category_table(cur, conn)
    uk_data(cur, conn)
    canada_data(cur, conn)
    us_data(cur, conn)

main()

