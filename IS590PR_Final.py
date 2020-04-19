# -*- coding: utf-8 -*-
"""
Created on Sat Apr 18 21:53:56 2020

@author: Jasmine Kuo
"""

import pandas as pd
import datetime


def dateListGenerate():
    start = datetime.datetime.strptime('01-22-2020', '%m-%d-%Y')
    end = datetime.datetime.today()
    datelist = [start + datetime.timedelta(days=x) for x in range(0, (end-start).days)]
    datelist = [date.strftime("%m-%d-%Y") for date in datelist]
    return datelist

def getCOVID19DataFromRemote(url, date):
    df = pd.read_csv(url, usecols = lambda x: x in ['Country/Region', 'Country_Region', 'Confirmed', 'Deaths', 'Recovered'])
    df.columns = ['Country', 'Confirmed', 'Deaths', 'Recovered']
    df = df[df['Country'].isin(['US', 'Taiwan', 'Taiwan*', 'Taipei and environs'])]
    df = df.groupby(['Country']).sum().reset_index()
    df['Date'] = date
    return df

if __name__ == '__main__':
    datelist = dateListGenerate()
    df = pd.DataFrame(columns = ['Date', 'Country', 'Confirmed', 'Deaths', 'Recovered'])
    for date in datelist:
        url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/'+date+'.csv'
        date_info = getCOVID19DataFromRemote(url, date)
        df = pd.concat([df, date_info], sort=False)
    df.loc[df['Country']!='US', 'Country'] = 'Taiwan'
    df_TW = df[df['Country']=='Taiwan']
    df_US = df[df['Country']=='US']

# Plot
import matplotlib.pyplot as plt
x1 = df_TW['Date']
y1 = df_TW['Confirmed']
x2 = df_US['Date']
y2 = df_US['Confirmed']
fig, ax1 = plt.subplots()
ax1.plot(x1, y1, lw=2, color="blue")
ax1.set_xticks(x2[::3])
ax1.set_xticklabels(x2[::3], rotation=90)
ax1.set_ylabel('US Confirmed', fontsize=18, color="red")
ax1.set_ylabel('Taiwan Confirmed', fontsize=18, color="blue")
for label in ax1.get_yticklabels():
    label.set_color("blue")
ax2 = ax1.twinx()
ax2.plot(x2, y2, lw=2, color="red")
ax2.set_xticks(x2[::3])
ax2.set_xticklabels(x2[::3], rotation=90)
ax2.set_ylabel('US Confirmed', fontsize=18, color="red")
for label in ax2.get_yticklabels():
    label.set_color("red")



