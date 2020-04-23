# -*- coding: utf-8 -*-
"""
Created on Sat Apr 18 21:53:56 2020

@author: Jasmine Kuo, Alan Chen
"""

import pandas as pd
import datetime
import matplotlib.pyplot as plt
from pytrends.request import TrendReq
import Constant
import doctest
import os


def generate_date_list(start_date_str: str, end_date: datetime.date = datetime.datetime.today()) -> list:
    """
    Create a list of date
    :param start_date_str: date string in %m-%d-%Y format
    :param end_date: date string in %m-%d-%Y format
    :return: a list of date

    >>> start_date = ""
    >>> generate_date_list(start_date)
    Traceback (most recent call last):
    ValueError: Empty start date
    >>> start_date = "01-22-2020"
    >>> end_date = ""
    >>> generate_date_list(start_date, end_date)
    Traceback (most recent call last):
    ValueError: Empty end date
    >>> start_date = "01-32-2020"
    >>> generate_date_list(start_date)
    Value Error occur: ValueError("time data '01-32-2020' does not match format '%m-%d-%Y'")
    >>> start_date = "01/22/2020"
    >>> generate_date_list(start_date)
    Value Error occur: ValueError("time data '01/22/2020' does not match format '%m-%d-%Y'")
    >>> start_date = "01-22-2020"
    >>> end_date = "04-18-2020"
    >>> generate_date_list(start_date, end_date)
    Traceback (most recent call last):
    TypeError: Type Error: end date should be datetime.date type
    >>> start_date = "04-21-2020"
    >>> end_date_str = "04-18-2020"
    >>> end_date = datetime.datetime.strptime(end_date_str, Constant.DATE_FORMAT)
    >>> generate_date_list(start_date, end_date)
    Traceback (most recent call last):
    ValueError: Start date cannot larger than end date
    >>> start_date = "04-11-2020"
    >>> end_date_str = "04-13-2020"
    >>> end_date = datetime.datetime.strptime(end_date_str, Constant.DATE_FORMAT)
    >>> date_list = generate_date_list(start_date, end_date)
    >>> print(date_list)
    ['04-11-2020', '04-12-2020']
    """
    if start_date_str == "" or start_date_str is None:
        raise ValueError("Empty start date")
        return
    elif end_date == "" or end_date is None:
        raise ValueError("Empty end date")
        return

    start = None
    try:
        start = datetime.datetime.strptime(start_date_str, Constant.DATE_FORMAT)
    except ValueError as error:
        print("Value Error occur:", repr(error))
        return

    end = end_date
    if isinstance(end, datetime.date) is False:
        raise TypeError("Type Error: end date should be datetime.date type")
        return

    if end < start:
        raise ValueError("Start date cannot larger than end date")
        return

    date_list = [start + datetime.timedelta(days=x) for x in range(0, (end-start).days)]
    date_list = [date.strftime(Constant.DATE_FORMAT) for date in date_list]
    return date_list


def get_CODIV19_data_from_remote(url: str, date: str) -> pd.DataFrame:
    """
    Access the COVID-19 confirmed cases from Taiwan CDC and US CDC through JHU open-sourced project on github
    :param url: the prefix of JHU open-sourced project URL
    :param date: one specific date in %m-%d-%Y format
    :return: a data frame contains COVID-19 data within target countries
    >>> date = "01-22-2020"
    >>> url = Constant.DATA_URL + date + Constant.DATA_POSTFIX_CSV
    >>> jan_22_df = get_CODIV19_data_from_remote(url, date)
    >>> jan_22_df.iloc[0].Country
    'Taiwan'
    >>> jan_22_df.iloc[0].Confirmed
    1.0
    >>> empty_date_df = get_CODIV19_data_from_remote(url, "")
    Traceback (most recent call last):
    ValueError: Empty date
    """
    if date == "" or date is None:
        raise ValueError("Empty date")
        return

    file_path = os.getcwd() + "/data/" + date + Constant.DATA_POSTFIX_CSV
    single_date_df = None
    if os.path.exists(file_path) is False:
        try:
            single_date_df = pd.read_csv(url, usecols=lambda x: x in ['Country/Region', 'Country_Region', 'Confirmed', 'Deaths', 'Recovered'])
            # print("-----------------------------------------" + date + "--------------------------------------------------")
            # print(single_date_df.to_string())
        except FileNotFoundError as error:
            print("FileNotFoundError occurs: " + repr(error))
            return

        single_date_df.to_csv(file_path, header=True, index=False)
    else:
        single_date_df = pd.read_csv(file_path)
        # print("[DEBUG] " + date + "data file exist")

    single_date_df.columns = ['Country', 'Confirmed', 'Deaths', 'Recovered']
    single_date_df = single_date_df[single_date_df['Country'].isin(['US', 'Taiwan', 'Taiwan*', 'Taipei and environs'])]
    single_date_df = single_date_df.groupby(['Country']).sum().reset_index()
    single_date_df['Date'] = date

    return single_date_df


def create_data_folder():
    path = os.getcwd()
    # print("[DEBUG] The current working directory is %s" % path)

    # check whether current path has data folder
    path += "/data"
    if os.path.exists(path):
        # print("[DEBUG] data folder existed")
        return

    try:
        os.mkdir(path)
    except OSError:
        print("Creation of the directory %s failed" % path)
    else:
        print("Successfully created the directory %s " % path)


def get_dependent_df_by_country(origin_df: pd.DataFrame, country: str = "") -> pd.DataFrame:
    """
    Access the specific COVID-19 data in the target country
    :param origin_df: origin data frame has specific date range and multiple conutries
    :param country: the target country string
    :return: a pandas dataframe of COVID-19 data in the country
    #TODO: Test cases
    """
    if country not in ["Taiwan", "US"] or country == "" or country is None:
        raise ValueError("No such country")

    return origin_df[origin_df['Country'] == country].copy()


def fetch_countries_COVID19_data_with_dates(dates: list) -> pd.DataFrame:
    """
    Create new time-series data frame of COVID-19 by sending request to JHU open-sourced project on Github
    :param dates: dates list
    :return: a data frame of COVID-19 within specific countries and time
    >>> dates = []
    >>> fetch_countries_COVID19_data_with_dates(dates)
    Traceback (most recent call last):
    ValueError: Empty date list
    >>> start = "01-22-2020"
    >>> end = datetime.datetime.strptime("01-23-2020", Constant.DATE_FORMAT)
    >>> date_list = generate_date_list(start, end)
    >>> new_df = fetch_countries_COVID19_data_with_dates(date_list)
    >>> print(new_df.iloc[0].Country + " has " + str(new_df.iloc[0].Confirmed) + " confirmed case(s)")
    Taiwan has 1.0 confirmed case(s)
    """
    if len(dates) == 0:
        raise ValueError("Empty date list")
        return None

    df = pd.DataFrame(columns=['Date', 'Country', 'Confirmed', 'Deaths', 'Recovered'])
    for date in dates:
        request_url = Constant.DATA_URL + date + Constant.DATA_POSTFIX_CSV
        date_info = get_CODIV19_data_from_remote(request_url, date)
        df = pd.concat([df, date_info], sort=False)

    return df


def create_google_trend_df(pytrend: TrendReq, keywords: list, region: str,
                           start_date: str, end_date: str, save_csv: bool = False) -> pd.DataFrame:
    """
    Create google trend data frame with list of keywords and region
    :param keywords: a list contains keywords used to search on google trend
    :param region: the region
    :param save_csv:
    :return: a data frame of keywords search volume in target region
    >>> pytrend = TrendReq(hl='en-US', tz=360)
    >>> start_date = "2020-01-20"
    >>> end_date = "2020-01-31"
    >>> keyword_list = ['mask', 'sanitizer', 'toilet paper']
    >>> US_df = create_google_trend_df(pytrend, keyword_list, "US", start_date, end_date)
    >>> str(US_df.iloc[-1]["date"])
    '2020-01-31 00:00:00'
    >>> US_df.iloc[-1]["mask"]
    98
    #TODO: Finish test case
    """
    if region not in ["TW", "US"]:
        raise ValueError("Region is not well defined")
        return

    google_trend_df = None
    for i in range(len(keywords)):
        pytrend.build_payload(kw_list=[keywords[i]], cat=0, timeframe=start_date + " " + end_date, geo=region, gprop='')
        tmp_GT_df = pytrend.interest_over_time()
        if i == 0:
            google_trend_df = tmp_GT_df.reset_index().drop(['isPartial'], axis=1)
        else:
            google_trend_df[keywords[i]] = tmp_GT_df.reset_index()[keywords[i]]

    if save_csv:
        google_trend_df.to_csv("GT_" + region + ".csv", index=False)

    return google_trend_df


if __name__ == '__main__':
    """
    H1:
    Steps:
    1) Pick 10 items, which is popular during COVID-19, from Journals and other resources  
    2) Use Google Trend (related_queries) to find out the "real keyword"
    3) 宏觀 Find the item which increase because of COVID-19 by examining each popular item in a 5-year trend map
    4) 微觀 Find representative item by filtering time interval
    
    H2:
    1) Plot to see the trend between COVID-19 and popular items
    2) Find the time interval between the time of the 1st confirmed case and the time of the max volume of each popular item
    3) Determine which country has better public awareness about the COVID-19 by comparing the time inteval in different region
    
    Alan - H1.2, functions, 
    Jasmine - H1.3(畫圖) H1.4, H2.2
    """
    create_data_folder()

    start_date = "01-22-2020"
    date_list = generate_date_list(start_date)

    df = fetch_countries_COVID19_data_with_dates(date_list)

    df.loc[df['Country'] != 'US', 'Country'] = 'Taiwan'
    df.to_csv('confirmedData.csv', index=False)

    # Get independent data frame
    df_TW = get_dependent_df_by_country(df, "Taiwan")
    df_US = get_dependent_df_by_country(df, "US")
    
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

    # Init Google Trend instance
    pytrend = TrendReq(hl='en-US', tz=360)
    
    # Creat US Google Trend data frame
    #TODO: save the good trend data?!
    keyword_list = ['mask', 'alcohol', 'sanitizer', 'toilet paper', 'disinfectants']
    GT_US_df = create_google_trend_df(pytrend, keyword_list, "US", "2020-01-01", "2020-04-19")

    # Creat Taiwan Google Trend data frame
    keyword_list = ['口罩', '酒精', '乾洗手', '衛生紙', '消毒']
    GT_TW_df = create_google_trend_df(pytrend, keyword_list, "TW", "2020-01-01", "2020-04-19")
    
    # Confirmed data and google trend data combination
    df_TW['Date'] = pd.to_datetime(df_TW['Date'])
    df_TW_comb = GT_TW_df.copy()
    df_TW_comb = pd.merge(df_TW_comb, df_TW, left_on = ['date'], right_on = ['Date'], how = 'left').drop(['Date'], axis = 1)
    df_TW_comb['Country'] = df_TW_comb['Country'].fillna('Taiwan')
    df_TW_comb = df_TW_comb.fillna(0)
    
    df_US['Date'] = pd.to_datetime(df_US['Date'])
    df_US_comb = GT_US_df.copy()
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
    
    fig.savefig('ConfirmedTrend_GoogleTrend_Comp_US.png', bbox_inches="tight")

