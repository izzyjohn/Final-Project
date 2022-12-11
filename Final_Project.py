import unittest
import sqlite3
import json
import os
import requests
import plotly.graph_objects as go
import plotly.express as px

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
        if new_deaths == None:
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
        if total_deaths == None:
            total_deaths = 0
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
        if total_cases == None:
            total_cases = 0
        change_cases = date_info['cases']['total']['calculated']['change_from_prior_day']
        if change_cases == None:
            change_cases = 0
        total_deaths = date_info['outcomes']['death']['total']['value']
        if total_deaths == None:
            total_deaths = 0
        change_deaths = date_info['outcomes']['death']['total']['calculated']['change_from_prior_day']
        if change_deaths == None:
            change_deaths = 0
        current_hospital = date_info['outcomes']['hospitalized']['currently']['value']
        if current_hospital == None:
            current_hospital = 0
        current_icu = date_info['outcomes']['hospitalized']['in_icu']['currently']['value']
        if current_icu == None:
            current_icu = 0
        cur.execute("INSERT OR IGNORE INTO usa (date, total_cases, change_cases, total_deaths, change_deaths, current_hospital, current_icu) \
            VALUES(?,?,?,?,?,?,?)", (date, total_cases, change_cases, total_deaths, change_deaths, current_hospital, current_icu))
    conn.commit()

def dif_Us_Canada_Average_Icu(cur, conn):
    res = cur.execute('SELECT Canada.date, usa.date, Canada.total_criticals, usa.current_icu \
    FROM Canada JOIN usa ON Canada.date = usa.date')
    tup_list = res.fetchall()
    num_dates = len(tup_list)
    canada_total = 0
    for date in tup_list:
        canada_total += date[2]
    canada_average = canada_total/num_dates
    us_total = 0
    for date in tup_list:
        us_total += date[3]
    us_average = us_total/num_dates
    dif_average = us_average - canada_average
    rounded_average = round(dif_average, 3)
    return rounded_average

def dif_Us_Canada_Average_Hospital(cur, conn):
    res = cur.execute('SELECT Canada.date, usa.date, Canada.total_hospitalizations, usa.current_hospital \
    FROM Canada JOIN usa ON Canada.date = usa.date')
    tup_list = res.fetchall()
    num_dates = len(tup_list)
    canada_total = 0
    for date in tup_list:
        canada_total += date[2]
    canada_average = canada_total/num_dates
    us_total = 0
    for date in tup_list:
        us_total += date[3]
    us_average = us_total/num_dates
    dif_average = us_average - canada_average
    rounded_average = round(dif_average, 3)
    return rounded_average

def uk_new_cases_average(cur, conn):
    res = cur.execute('SELECT new_cases FROM UK')
    tup_list = res.fetchall()
    case_total = 0
    num_dates = len(tup_list)
    for date in tup_list:
        case_total += date[0]
    uk_average = case_total/num_dates
    rounded_average = round(uk_average, 3)
    return rounded_average

def us_new_cases_average(cur, conn):
    res = cur.execute('SELECT change_cases FROM usa')
    tup_list = res.fetchall()
    case_total = 0
    num_dates = len(tup_list)
    for date in tup_list:
        case_total += date[0]
    us_average = case_total/num_dates
    rounded_average = round(us_average, 3)
    return rounded_average

def canada_new_cases_average(cur, conn):
    res = cur.execute('SELECT change_cases FROM Canada')
    tup_list = res.fetchall()
    case_total = 0
    num_dates = len(tup_list)
    for date in tup_list:
        case_total += date[0]
    canada_average = case_total/num_dates
    rounded_average = round(canada_average, 3)
    return rounded_average


def write_textfile(file_name, cur, conn):
    f = open(file_name, "w")
    dif_Average_Hospital = dif_Us_Canada_Average_Hospital(cur, conn)
    dif_Average_Icu = dif_Us_Canada_Average_Icu(cur, conn)
    uk_average = uk_new_cases_average(cur, conn)
    us_average = us_new_cases_average(cur, conn)
    canada_average = canada_new_cases_average(cur, conn)
    f.write("Difference between Average Hospitalizations for USA and Canada: " + str(dif_Average_Hospital) + "\n")
    f.write("Difference between Average Number of Patients in the ICU for USA and Canada: " + str(dif_Average_Icu) + "\n")
    f.write("Average Number of new Covid Cases in the UK: " + str(uk_average) + "\n")
    f.write("Average Number of new Covid Cases in the USA: " + str(us_average) + "\n")
    f.write("Average Number of new Covid Cases in Canada: " + str(canada_average) + "\n")

def visualization_1(cur, conn):
    date = cur.execute("SELECT date FROM usa")
    date_tup_list = date.fetchall()
    canada_hospital = cur.execute("SELECT total_hospitalizations FROM Canada")
    canada_tup_list = canada_hospital.fetchall()
    USA_hospital = cur.execute("SELECT current_hospital FROM usa")
    usa_tup_lst = USA_hospital.fetchall()
    date_lst = []
    canada_lst = []
    usa_lst = []
    for x in date_tup_list:
        date_lst.append(x[0])
    for x in canada_tup_list:
        canada_lst.append(x[0])
    for x in usa_tup_lst:
        usa_lst.append(x[0])
    fig = go.Figure(data = [
        go.Bar(name = "Canada", x=date_lst, y=canada_lst, marker_color = 'rgb(200, 0, 255)'),
        go.Bar(name = "USA", x=date_lst, y=usa_lst, marker_color = 'rgb(0, 0, 20)')])
    title_str = "The Number of Hospitalizations Between the US and Canada"
    fig.update_layout(title = title_str, xaxis_tickangle=-45, barmode='group')
    fig.show()

def visualization_2(cur, conn):
    date = cur.execute("SELECT date FROM usa")
    date_tup_list = date.fetchall()
    canada_icu = cur.execute("SELECT total_criticals FROM Canada")
    canada_tup_list = canada_icu.fetchall()
    USA_icu = cur.execute("SELECT current_icu FROM usa")
    usa_tup_lst = USA_icu.fetchall()
    date_lst = []
    canada_lst = []
    usa_lst = []
    for x in date_tup_list:
        date_lst.append(x[0])
    for x in canada_tup_list:
        canada_lst.append(x[0])
    for x in usa_tup_lst:
        usa_lst.append(x[0])
    fig = go.Figure(data = [
        go.Bar(name = "Canada", x=date_lst, y=canada_lst, marker_color = 'rgb(200, 0, 255)'),
        go.Bar(name = "USA", x=date_lst, y=usa_lst, marker_color = 'rgb(0, 0, 20)')])
    title_str = "The Number of Hospitalizations Between the US and Canada"
    fig.update_layout(title = title_str, xaxis_tickangle=-45, barmode='group')
    fig.show()

def visualization_3(cur, conn):
    uk = uk_new_cases_average(cur, conn)
    canada = canada_new_cases_average(cur, conn)
    usa = us_new_cases_average(cur, conn)
    fig = go.Figure({
        'data' : [{'type': 'bar',
            'x': ['UK', 'Canada', 'USA'],
            'y': [uk, canada, usa]}],
        'layout': {'title': {'text': 'Average Number of New Covid Cases by Country'}}
    })
    fig.show()

def visualization_4(cur, conn):
    date = cur.execute("SELECT date FROM Canada")
    date_tup_list = date.fetchall()
    canada_icu = cur.execute("SELECT change_cases FROM Canada")
    canada_tup_list = canada_icu.fetchall()
    date_lst = []
    canada_lst = []
    for x in date_tup_list:
        date_lst.append(x[0])
    for x in canada_tup_list:
        canada_lst.append(x[0])
    fig = go.Figure({
        'data' : [{'type': 'bar',
            'x': date_lst,
            'y': canada_lst}],
        'layout': {'title': {'text': 'Current Number of Covid Cases in Canada'}}
    })
    fig.show()

def visualization_5(cur, conn):
    res = cur.execute('SELECT UK.n_death_id, death_category.category, death_category.id FROM UK JOIN death_category ON UK.n_death_id = death_category.id')
    tup_list = res.fetchall()
    x_lst = []
    id_lst = []
    entire_id_lst = []
    y_lst = []
    for x in tup_list:
        if(x[1] not in x_lst):
            x_lst.append(x[1])
            id_lst.append(x[0])
        entire_id_lst.append(x[0])
    for x in id_lst:
        y_lst.append(entire_id_lst.count(x))
    fig = go.Figure({
        'data' : [{'type': 'bar',
            'x': x_lst,
            'y': y_lst}],
        'layout': {'title': {'text': 'Number of People in Each Death Category'}}
    })
    fig.show()
    pass

def main():
    cur, conn = open_database('covid.db')
    uk_category_table(cur, conn)
    uk_data(cur, conn)
    canada_data(cur, conn)
    us_data(cur, conn)
    write_textfile("Covid-Calculations.txt", cur, conn)
    visualization_1(cur, conn)
    visualization_2(cur, conn)
    visualization_3(cur, conn)
    visualization_4(cur, conn)
    visualization_5(cur, conn)

main()

