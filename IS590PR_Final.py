# -*- coding: utf-8 -*-
"""
Created on Sat Apr 18 21:53:56 2020

@author: Jasmine Kuo
"""

import pandas as pd
import datetime
import matplotlib.pyplot as plt
from pytrends.request import TrendReq

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
    df.to_csv('confirmedData.csv', index = False)
    
    df_TW = df[df['Country']=='Taiwan'].copy()
    df_US = df[df['Country']=='US'].copy()
    
    # Plot - Taiwan & US Confirmed Number Comparison
    x1 = df_TW['Date']
    y1 = df_TW['Confirmed']
    x2 = df_US['Date']
    y2 = df_US['Confirmed']
    fig, ax1 = plt.subplots(figsize=(10, 4))
    ax1.plot(x1, y1, lw=2, color="blue")
    ax1.set_xticks(x2[::4])
    ax1.set_xticklabels(x2[::4], rotation=60)
    ax1.set_ylabel('US Confirmed', fontsize=18, color="red")
    ax1.set_ylabel('Taiwan Confirmed', fontsize=18, color="blue")
    for label in ax1.get_yticklabels():
        label.set_color("blue")
    ax2 = ax1.twinx()
    ax2.plot(x2, y2, lw=2, color="red")
    ax2.set_xticks(x2[::4])
    ax2.set_xticklabels(x2[::4], rotation=90)
    ax2.set_ylabel('US Confirmed', fontsize=18, color="red")
    for label in ax2.get_yticklabels():
        label.set_color("red")
    
    fig.savefig('Confirmed_Number_Comparison.png', bbox_inches = "tight")
    
    
    # Google Trend Data
    pytrend = TrendReq(hl='en-US', tz=360)
    
    # US Google Trend
    kwList = ['mask', 'alcohol', 'sanitizer', 'toilet paper', 'disinfectants']
    for i in range(len(kwList)):
        pytrend.build_payload(kw_list=[kwList[i]], cat=0, timeframe='2020-01-01 2020-04-19', geo='US', gprop='')
        tmp_GT = pytrend.interest_over_time()
        if i==0:
            df_GT_US = tmp_GT.reset_index().drop(['isPartial'], axis = 1)
        else:
            df_GT_US[kwList[i]] = tmp_GT.reset_index()[kwList[i]]
    df_GT_US.to_csv('GT_US.csv', index = False)
    
    # Taiwan Google Trend
    kwList = ['口罩', '酒精', '乾洗手', '衛生紙', '消毒']
    for i in range(len(kwList)):
        pytrend.build_payload(kw_list=[kwList[i]], cat=0, timeframe='2020-01-01 2020-04-19', geo='TW', gprop='')
        tmp_GT = pytrend.interest_over_time()
        if i==0:
            df_GT_TW = tmp_GT.reset_index().drop(['isPartial'], axis = 1)
        else:
            df_GT_TW[kwList[i]] = tmp_GT.reset_index()[kwList[i]]
    df_GT_TW.to_csv('GT_TW.csv', index = False)
    
    # Confirmed data and google trend data combination
    df_TW['Date'] = pd.to_datetime(df_TW['Date'])
    df_TW_comb = df_GT_TW.copy()
    df_TW_comb = pd.merge(df_TW_comb, df_TW, left_on = ['date'], right_on = ['Date'], how = 'left').drop(['Date'], axis = 1)
    df_TW_comb['Country'] = df_TW_comb['Country'].fillna('Taiwan')
    df_TW_comb = df_TW_comb.fillna(0)
    
    df_US['Date'] = pd.to_datetime(df_US['Date'])
    df_US_comb = df_GT_US.copy()
    df_US_comb = pd.merge(df_US_comb, df_US, left_on = ['date'], right_on = ['Date'], how = 'left').drop(['Date'], axis = 1)
    df_US_comb['Country'] = df_US_comb['Country'].fillna('US')
    df_US_comb = df_US_comb.fillna(0)
    
    # Plot - Confirmed Trend and Google Trend Comparison
    # TW
    x = df_TW_comb['date'].dt.date
    y1 = df_TW_comb['Confirmed']
    y2 = df_TW_comb['口罩']
    y3 = df_TW_comb['酒精']
    y4 = df_TW_comb['乾洗手']
    y5 = df_TW_comb['衛生紙']
    y6 = df_TW_comb['消毒']
    
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(x, y1, lw=4, label='Confirmed Number')
    ax.grid(True)
    ax.set_xticks(x[::3])
    ax.set_xticklabels(x[::3], rotation=60)
    ax.set_title('Taiwan', fontsize=24)
    ax.set_ylabel('Confirmed Number', fontsize=18, color="Blue")
    ax2 = ax.twinx()
    ax2.plot(x, y2, lw=2, label = 'mask')
    ax2.plot(x, y3, lw=2, label = 'alcohol')
    ax2.plot(x, y4, lw=2, label = 'sanitizer')
    ax2.plot(x, y5, lw=2, label = 'toilet paper')
    ax2.plot(x, y6, lw=2, label = 'disinfectants')
    ax2.set_xticks(x[::3])
    ax2.set_xticklabels(x[::3], rotation=60)
    ax2.set_ylabel('Google Trend', fontsize=18, color="Red")
    lines, labels = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(lines + lines2, labels + labels2, loc=0)
    
    fig.savefig('ConfirmedTrend_GoogleTrend_Comp_TW.png', bbox_inches = "tight")
    
    # US
    x = df_US_comb['date'].dt.date
    y1 = df_US_comb['Confirmed']
    y2 = df_US_comb['mask']
    y3 = df_US_comb['alcohol']
    y4 = df_US_comb['sanitizer']
    y5 = df_US_comb['toilet paper']
    y6 = df_US_comb['disinfectants']
    
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(x, y1, lw=4, label='Confirmed Number')
    ax.grid(True)
    ax.set_xticks(x[::3])
    ax.set_xticklabels(x[::3], rotation=60)
    ax.set_title('US', fontsize=24)
    ax.set_ylabel('Confirmed Number', fontsize=18, color="Blue")
    ax2 = ax.twinx()
    ax2.plot(x, y2, lw=2, label = 'mask')
    ax2.plot(x, y3, lw=2, label = 'alcohol')
    ax2.plot(x, y4, lw=2, label = 'sanitizer')
    ax2.plot(x, y5, lw=2, label = 'toilet paper')
    ax2.plot(x, y6, lw=2, label = 'disinfectants')
    ax2.set_xticks(x[::3])
    ax2.set_xticklabels(x[::3], rotation=60)
    ax2.set_ylabel('Google Trend', fontsize=18, color="Red")
    lines, labels = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(lines + lines2, labels + labels2, loc=0)
    
    fig.savefig('ConfirmedTrend_GoogleTrend_Comp_US.png', bbox_inches = "tight")
    
    
