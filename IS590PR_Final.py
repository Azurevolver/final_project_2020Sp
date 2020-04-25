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


def generate_date_list(start_date_str: str, end_date: datetime.date = datetime.datetime.strptime("04-22-2020", Constant.DATE_FORMAT)) -> list:
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

    date_list = [start + datetime.timedelta(days=x) for x in range(0, (end - start).days)]
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

    file_path = os.getcwd() + Constant.COVID_RAW_DATA_DIR + "/" + date + Constant.DATA_POSTFIX_CSV
    single_date_df = None
    if os.path.exists(file_path) is False:
        try:
            single_date_df = pd.read_csv(url, usecols=lambda x: x in ['Country/Region', 'Country_Region', 'Confirmed',
                                                                      'Deaths', 'Recovered'])
            # print("-----------------------------------------" + date + "--------------------------------------------------")
            # print(single_date_df.to_string())
        except FileNotFoundError as error:
            print("FileNotFoundError occurs: " + repr(error))
            return

        single_date_df.to_csv(file_path, header=True, index=False)
    else:
        single_date_df = pd.read_csv(file_path)

    single_date_df.columns = ['Country', 'Confirmed', 'Deaths', 'Recovered']
    single_date_df = single_date_df[single_date_df['Country'].isin(['US', 'Taiwan', 'Taiwan*', 'Taipei and environs'])]
    single_date_df = single_date_df.groupby(['Country']).sum().reset_index()
    single_date_df['Date'] = date

    return single_date_df


def create_data_folder(sub_directory: str):
    """
    Create new folder
    :param sub_directory: the folder name
    :return: None
    >>> test_directory = "/test"
    >>> create_data_folder(test_directory)
    Successfully created the directory
    >>> test_directory = "/test"
    >>> create_data_folder(test_directory)
    Data folder existed
    >>> empty_dir = ""
    >>> create_data_folder(empty_dir)
    Data folder existed
    """
    path = os.getcwd()
    # print("[DEBUG] The current working directory is %s" % path)

    # check whether current path has data folder
    path += sub_directory
    if os.path.exists(path):
        print("Data folder existed")
        return

    try:
        os.mkdir(path)
    except OSError:
        print("Creation of the directory %s failed" % path)
    else:
        print("Successfully created the directory")


def get_country_df(origin_df: pd.DataFrame, country: str = "") -> pd.DataFrame:
    """
    Access the specific COVID-19 data in the target country
    :param origin_df: origin data frame has specific date range and multiple conutries
    :param country: the target country string
    :return: a pandas dataframe of COVID-19 data in the country
    >>> start_date = "01-22-2020"
    >>> end_date_str = "01-24-2020"
    >>> end_date = datetime.datetime.strptime(end_date_str, Constant.DATE_FORMAT)
    >>> date_list = generate_date_list(start_date, end_date)
    >>> origin_df = fetch_countries_COVID19_data_with_dates(date_list)
    >>> origin_df.loc[origin_df['Country'] != Constant.US, 'Country'] = Constant.TAIWAN
    >>> empty_country_df = get_country_df(origin_df, "Some Country")
    Traceback (most recent call last):
    ValueError: No such country
    >>> start_date = "01-22-2020"
    >>> end_date_str = "01-24-2020"
    >>> end_date = datetime.datetime.strptime(end_date_str, Constant.DATE_FORMAT)
    >>> date_list = generate_date_list(start_date, end_date)
    >>> origin_df = fetch_countries_COVID19_data_with_dates(date_list)
    >>> origin_df.loc[origin_df['Country'] != Constant.US, 'Country'] = Constant.TAIWAN
    >>> tw_df = get_country_df(origin_df, Constant.TAIWAN)
    >>> tw_df.iloc[0]["Confirmed"]
    1.0
    """
    if country not in [Constant.TAIWAN, Constant.US] or country == "" or country is None:
        raise ValueError("No such country")

    if origin_df is None:
        raise ValueError("Origin data frame is not existed")

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

    df.loc[df['Country'] != 'US', 'Country'] = 'Taiwan'
    return df


def create_google_trend_df(pytrend: TrendReq, keywords: list, region: str,
                           start_date: str, end_date: str, save_csv: bool = False) -> pd.DataFrame:
    """
    Create google trend data frame with list of keywords, region, start date, and end date
    :param pytrend:
    :param keywords: a list contains keywords used to search on google trend
    :param region: the region for search
    :param start_date: the start date for search
    :param end_date: the end date for search
    :param save_csv: a boolean value for saving the file to local directory
    :return: a pandas data frame of google trend data
    >>> pytrend = TrendReq(hl='en-US', tz=360)
    >>> start_date = "2020-01-20"
    >>> end_date = "2020-01-31"
    >>> keyword_list = ['mask', 'sanitizer', 'toilet paper']
    >>> US_df = create_google_trend_df(pytrend, keyword_list, "US", start_date, end_date)
    >>> str(US_df.iloc[-1]["date"])
    '2020-01-31 00:00:00'
    >>> US_df.iloc[-1]["mask"]
    96
    """
    google_trend_df = None

    if region not in ["TW", "US"]:
        raise ValueError("Region is not well defined")
        return None

    file_path = os.getcwd() + Constant.GT_5_YR_DATA_DIR + "/GT_" + region + Constant.DATA_POSTFIX_CSV
    if os.path.exists(file_path):
        google_trend_df = pd.read_csv(file_path)
        google_trend_df['date'] = pd.to_datetime(google_trend_df['date']).dt.date
        return google_trend_df

    for i in range(len(keywords)):
        pytrend.build_payload(kw_list=[keywords[i]], cat=0, timeframe=start_date + " " + end_date, geo=region, gprop='')
        tmp_GT_df = pytrend.interest_over_time()
        if i == 0:
            google_trend_df = tmp_GT_df.reset_index().drop(['isPartial'], axis=1)
        else:
            google_trend_df[keywords[i]] = tmp_GT_df.reset_index()[keywords[i]]

    if save_csv and os.path.exists(file_path) is False:
        google_trend_df.to_csv(file_path, header=True, index=False)

    return google_trend_df


def plot_google_trend_of_item(df: pd.DataFrame, region: str, figure_stage='', select=[]):
    """
    Plot the google trend of each item. Item in the select list will be drew by red line. figure_stage is for figure
    saving name.
    :param df: google trend data frame
    :param region: region of plot
    :param figure_stage:
    :param select: list of items that are selected and will be drew by red line.
    :return:
    """
    fig, ax = plt.subplots(nrows=5, ncols=2, figsize=(12, 10))
    x = pd.to_datetime(df['date']).dt.date

    for i in range(df.shape[1] - 1):
        if df.columns[i + 1] in select:
            ax[i % 5, int(i / 5)].plot(x, df[df.columns[i + 1]], color='red')
        else:
            ax[i % 5, int(i / 5)].plot(x, df[df.columns[i + 1]])
        ax[i % 5, int(i / 5)].grid(True)
        ax[i % 5, int(i / 5)].set_title(region + ' - ' + df.columns[i + 1], fontsize=14)
        ax[i % 5, int(i / 5)].set_ylabel('Google Trend', fontsize=12)
    fig.autofmt_xdate()
    fig.tight_layout()

    file_path = os.getcwd() + Constant.GT_FIGURE_NAME_PREFIX + region + '_' + figure_stage + '.png'
    fig.savefig(file_path, bbox_inches="tight")


def select_item_impacted_by_covid19(df: pd.DataFrame) -> list:
    """
    Select the items impacted by COVID-19 in long-term observation.
    The selection criteria:
    1. high skew of the trend (extreme left skew)
    2. low max value of the search volume before COVID-19
    :param df: google trend dataframe of the items
    :return: list of items impacted by COVID-19
    """
    kw_list = []
    for item in df.columns[1:]:
        skew = df[item].skew()
        past_max = df[df['date'] < datetime.date(2020, 1, 1)][item].max()
        if skew > 4 and past_max < 50:
            kw_list.append(item)
    return kw_list


def select_representative_kw(df: pd.DataFrame, impacted_item: list):
    """
    - Select the representative items which has sharp increase due to COVID-19.
    The select criteria is
    1. low max value of the trend 2 weeks before the peak
    2. high max value of the trend during COVID-19
    - Create a dictionary for record of items' max value date
    :param df: google trend dataframe of the items
    :param impacted_item: items list generated by select_item_impacted_by_covid19()
    :return: representative keywords list and dictionary of items' trend max date
    """
    df = pd.concat([df['date'], df[impacted_item]], sort=False, axis=1)
    kw_list = []
    max_date_dict = {}
    for item in df.columns[1:]:
        max_idx = df[item].idxmax()
        max_date_dict[item] = df['date'][max_idx]
        date_bound = df['date'][max_idx] - datetime.timedelta(days=14)
        past_max = df[df['date'].dt.date < date_bound][item].max()
        current_max = df[df['date'].dt.date > date_bound][item].max()
        if past_max < 30 and current_max > 90:
            kw_list.append(item)
    return kw_list, max_date_dict


def awareness_date_report(first_confirmed_date: datetime, items_max_date: dict) -> dict:
    """
    Define the awareness date and report the first confirmed date, awareness date and time gap between first confirmed
    date and awareness date.
    The definition of awareness time gap is mean time interval between date of 1st confirmed case and date of max search
    volume of each item.
    The definition of awareness date the 1st confirmed case date + awareness time gap
    :param first_confirmed_date: date of first confirmed
    :param items_max_date: dictionary of each item's google trend max date
    :return: dictionary that record the first confirmed date, awareness date and time gap between first confirmed
    date and awareness date
    """
    report = {}
    report['first_confirmed_date'] = first_confirmed_date
    time_gap = {k: (v.date() - first_confirmed_date).days for k, v in items_max_date.items()}
    report['awareness_time_gap(days)'] = int(sum([time_gap[key] for key in time_gap]) / float(len(time_gap)))
    report['mean_awareness_date'] = first_confirmed_date + datetime.timedelta(
        days=report['awareness_time_gap(days)'])
    return report


def plot_items_with_confirmed_case(region_df: pd.DataFrame, item_name_list: list, first_confirmed_date: datetime,
                                   region: str):
    """
    Plot selective items' google trend and confirmed cases trend with 1st confirmed case date.
    :param first_confirmed_date: date of first confirmed
    :param region_df: combination dataframe of items google trend and confirmed number
    :param item_name_list: representative keywords list
    :param region: region of plot
    :return:
    TODO: Test case
    """
    x = region_df['date'].dt.date
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(x, region_df['Confirmed'], lw=2, label='Confirmed Num', color='black')
    ax.axvline(x=first_confirmed_date, color='darkred')
    ax.text(first_confirmed_date - datetime.timedelta(days=15), region_df['Confirmed'].max() / 3,
            'first confirmed date', bbox={'facecolor': 'white', 'pad': 5})
    ax.grid(True)
    ax.set_xticks(x[::3])
    ax.set_xticklabels(x[::3], rotation=45)
    ax.set_title(region, fontsize=20)
    ax.set_ylabel('Confirmed Number', fontsize=18, color="black")

    ax2 = ax.twinx()
    for i in item_name_list:
        ax2.plot(x, region_df[i], lw=2, label=i)
    ax2.set_xticks(x[::3])
    ax2.set_xticklabels(x[::3], rotation=45)
    ax2.set_ylabel('Google Trend', fontsize=18, color="Red")
    lines, labels = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(lines + lines2, labels + labels2, loc=0, fontsize=8)

    fig.savefig('ConfirmedTrend_GoogleTrend_Comp_' + region + '.png', bbox_inches="tight")


def plot_confirmed_number_and_awareness_comparison(region1_df: pd.DataFrame, region1: str,
                                                   region1_awareness_report: dict, region2_df: pd.DataFrame,
                                                   region2: str, region2_awareness_report: dict):
    """
    Plot confirmed number trend with first confirmed date and awareness date for two countries comparison.
    :param region1_df: 1st country's combination dataframe of items google trend and confirmed number
    :param region1: 1st country name
    :param region1_awareness_report: 1st country's awareness report generated by awareness_date_report()
    :param region2_df: 2nd country's combination dataframe of items google trend and confirmed number
    :param region2: 2nd country name
    :param region2_awareness_report: 2nd country's awareness report generated by awareness_date_report()
    :return:
    """
    fig, ax = plt.subplots(nrows=2, ncols=1, figsize=(12, 10))
    for i in range(2):
        if i == 0:
            region_df, region, region_awareness_report = region1_df, region1, region1_awareness_report
        else:
            region_df, region, region_awareness_report = region2_df, region2, region2_awareness_report
        x = region_df['date'].dt.date
        ax[i].plot(x, region_df['Confirmed'], lw=2, label='Confirmed Number')
        ax[i].axvline(x=region_awareness_report['first_confirmed_date'], color='darkred', lw=2)
        ax[i].text(region_awareness_report['first_confirmed_date'] - datetime.timedelta(days=8),
                   region_df['Confirmed'].max() / 3, 'first confirmed date', bbox={'facecolor': 'white', 'pad': 5})
        ax[i].axvline(x=region_awareness_report['mean_awareness_date'], color='darkred', lw=2)
        ax[i].text(region_awareness_report['mean_awareness_date'] - datetime.timedelta(days=5),
                   region_df['Confirmed'].max() / 2, 'awareness date', bbox={'facecolor': 'white', 'pad': 5})
        ax[i].axvspan(region_awareness_report['first_confirmed_date'], region_awareness_report['mean_awareness_date'],
                      alpha=0.5, color='yellow')
        ax[i].text(region_awareness_report['mean_awareness_date'] - datetime.timedelta(
            days=region_awareness_report['awareness_time_gap(days)'] / 2 + 3), region_df['Confirmed'].max() / 1.5,
                   str(int(region_awareness_report['awareness_time_gap(days)'])) + ' days',
                   bbox={'boxstyle': 'darrow,pad=0.8', 'fc': 'r', 'ec': 'k', 'alpha': 0.5})
        ax[i].grid(True)
        ax[i].set_xticks(x[::3])
        ax[i].set_xticklabels(x[::3], rotation=45)
        ax[i].set_title(region, fontsize=20)
        ax[i].set_ylabel('Google Trend', fontsize=18, color = 'blue')
        ax[i].legend()
    fig.tight_layout()
    fig.savefig('Confirmed_Number_Comparison.png', bbox_inches="tight")


if __name__ == '__main__':
    """
    H1:
    Steps:
    1) Pick 10 items, which is popular during COVID-19, from Journals and other resources  
    2) Use Google Trend (related_queries) to find out the "real keyword"
    3) 宏觀 Find the item which increase because of COVID-19 by examining each popular item in a 5-year trend
    4) 微觀 Find representative item by filtering time interval
    
    H2:
    1) Plot to see the trend between COVID-19 and popular items
    2) Find the time interval between the time of the 1st confirmed case and the time of the max volume of each popular item
    3) Determine which country has better public awareness about the COVID-19 by comparing the time inteval in different region
    """
    # Create COVID-19 data frame from start date to end date (default is 04-22-2020)
    create_data_folder(Constant.COVID_RAW_DATA_DIR)
    date_list = generate_date_list("01-22-2020")
    df = fetch_countries_COVID19_data_with_dates(date_list)

    # Get country's COVID-19 data frame
    df_TW = get_country_df(df, Constant.TAIWAN)
    df_US = get_country_df(df, Constant.US)

    # Create long-term(5 years) google trend for observation
    create_data_folder(Constant.GT_5_YR_DATA_DIR)
    pytrend = TrendReq(hl='en-US', tz=360)

    # Create US Google Trend data frame with key word list
    GT_US_df = create_google_trend_df(pytrend, Constant.KEY_WORDS_LIST_EN, Constant.US, "2015-04-19", "2020-04-19", True)

    # Create Taiwan Google Trend data frame with key word list
    GT_TW_df = create_google_trend_df(pytrend, Constant.KEY_WORDS_LIST_TW, Constant.TW, "2015-04-19", "2020-04-19", True)
    tw_col_names = Constant.KEY_WORDS_LIST_EN.copy()
    tw_col_names.insert(0, 'date')
    GT_TW_df.columns = tw_col_names

    # Plot the long-term(5 years) google trend of each item for observing the search trend.
    create_data_folder(Constant.GT_FIGURE_DIR)
    plot_google_trend_of_item(GT_US_df, Constant.US, '5_years')
    plot_google_trend_of_item(GT_TW_df, Constant.TW, '5_years')

    # Select the items that impacted by COVID-19.
    #  We assume that all items would have very low search volume before COVID-19
    #  , but reach high search volume during the COVID-19 outbreak.
    # The selection criteria:
    # 1. high skew of the trend (extreme left skew)
    # 2. low max value of the search volume before COVID-19
    impacted_item_US = select_item_impacted_by_covid19(GT_US_df)
    impacted_item_TW = select_item_impacted_by_covid19(GT_TW_df)

    # Plot the long-term(5 years) google trend of the items which is highly impacted by COVID-19 (in red)
    plot_google_trend_of_item(GT_US_df, Constant.US, '5_years_significant', impacted_item_US)
    plot_google_trend_of_item(GT_TW_df, Constant.TW, '5_years_significant', impacted_item_TW)

    """
    # Short-term google trend observation(this year)
    # Creat US Google Trend data frame
    keyword_list = ['disinfectants', 'thermometers', 'oat milk', 'rubbing alcohol', 'powdered milk',
                    'hydrogen peroxide', 'mask', 'sanitizer', 'toilet paper', 'disposable gloves']
    GT_US_df = create_google_trend_df(pytrend, keyword_list, "US", "2020-01-01", "2020-04-19")

    # Creat Taiwan Google Trend data frame
    keyword_list = ['消毒', '額溫槍', '燕麥奶', '酒精', '奶粉', '漂白水', '口罩', '乾洗手', '衛生紙', '手套']
    GT_TW_df = create_google_trend_df(pytrend, keyword_list, "TW", "2020-01-01", "2020-04-19")
    GT_TW_df.columns = ['date', 'disinfectants', 'thermometers', 'oat milk', 'rubbing alcohol', 'powdered milk',
                        'hydrogen peroxide', 'mask', 'sanitizer', 'toilet paper', 'disposable gloves']

    # From the long-term keyword selection, we then further select the representative items which has sharp increase
    # google trend during COVID-19 by observing short-term(this year) trend.
    # The select criteria is
    # 1. low max value of the trend 2 weeks before the peak
    # 2. high max value of the trend during COVID-19
    representative_item_US, items_max_date_US = select_representative_kw(GT_US_df, impacted_item_US)
    representative_item_TW, items_max_date_TW = select_representative_kw(GT_TW_df, impacted_item_TW)

    # Plot the short-term(this year) google trend of each item for observing the search trend and make the selected
    # representative items drew by red line.
    plot_google_trend_of_item(GT_US_df, 'US', representative_item_US, 'representative-obs')
    plot_google_trend_of_item(GT_TW_df, 'TW', representative_item_TW, 'representative-obs')

    # Combind confirmed data and google trend data
    # Use final representative keywords for google trend
    GT_US_df = pd.concat([GT_US_df['date'], GT_US_df[representative_item_US]], sort=False, axis=1)
    GT_TW_df = pd.concat([GT_TW_df['date'], GT_TW_df[representative_item_TW]], sort=False, axis=1)

    df_US['Date'] = pd.to_datetime(df_US['Date'])
    df_US_comb = GT_US_df.copy()
    df_US_comb = pd.merge(df_US_comb, df_US, left_on=['date'], right_on=['Date'], how='left').drop(['Date'], axis=1)
    df_US_comb['Country'] = df_US_comb['Country'].fillna('US')
    df_US_comb = df_US_comb.fillna(0)

    df_TW['Date'] = pd.to_datetime(df_TW['Date'])
    df_TW_comb = GT_TW_df.copy()
    df_TW_comb = pd.merge(df_TW_comb, df_TW, left_on=['date'], right_on=['Date'], how='left').drop(['Date'], axis=1)
    df_TW_comb['Country'] = df_TW_comb['Country'].fillna('Taiwan')
    df_TW_comb = df_TW_comb.fillna(0)

    first_confirmed_date_TW = datetime.date(2020, 1, 21)
    first_confirmed_date_US = datetime.date(2020, 1, 21)

    # Plot comparison between confirmed cases trend and google trend
    # TW
    plot_items_with_confirmed_case(df_TW_comb, representative_item_TW, first_confirmed_date_TW, "Taiwan")

    # US
    plot_items_with_confirmed_case(df_US_comb, representative_item_US, first_confirmed_date_US, "US")

    # Define the awareness date and report the first confirmed date, awareness date and time gap between first confirmed
    # date and awareness date.
    awareness_report_US = awareness_date_report(first_confirmed_date_US, items_max_date_US)
    awareness_report_TW = awareness_date_report(first_confirmed_date_TW, items_max_date_TW)

    # Plot confirmed number trend and time gap between first confirmed date and awareness date for two countries.
    plot_confirmed_number_and_awareness_comparison(df_US_comb, 'US', awareness_report_US, df_TW_comb, 'TW',
                                                   awareness_report_TW)
"""