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


def create_data_folder(sub_directory: str):
    """
    Create new folder
    :param sub_directory: the folder name
    :return: None
    >>> test_directory = "/test"
    >>> create_data_folder(test_directory)
    Successfully created the directory
    >>> test_directory = "/COVID_RAW_DATA"
    >>> create_data_folder(test_directory)
    /COVID_RAW_DATAData folder existed
    >>> empty_dir = ""
    >>> create_data_folder(empty_dir)
    Data folder existed
    """
    path = os.getcwd()
    # print("[DEBUG] The current working directory is %s" % path)

    # check whether current path has data folder
    path += sub_directory
    if os.path.exists(path):
        print(sub_directory + "Data folder existed")
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
    >>> end = datetime.datetime.strptime("01-23-20", Constant.DATE_FORMAT)
    >>> origin_df = fetch_countries_COVID19_data_with_dates(end)
    >>> empty_country_df = get_country_df(origin_df, "Some Country")
    Traceback (most recent call last):
    ValueError: No such country
    >>> empty_country_df = get_country_df(None, "Some Country")
    Traceback (most recent call last):
    ValueError: No such country
    >>> end = datetime.datetime.strptime("01-23-20", Constant.DATE_FORMAT)
    >>> origin_df = fetch_countries_COVID19_data_with_dates(end)
    >>> tw_df = get_country_df(origin_df, Constant.TAIWAN)
    >>> tw_df.iloc[0]["Confirmed"]
    1
    """
    if country == Constant.TW:
        country = Constant.TAIWAN

    if country not in [Constant.TAIWAN, Constant.US] or country == "" or country is None:
        raise ValueError("No such country")

    if origin_df is None:
        raise ValueError("Origin data frame is not existed")

    df = origin_df[origin_df['Country/Region'] == country].copy()
    df.loc[df['Country/Region'] == 'Taiwan*', 'Country/Region'] = 'Taiwan'
    df = pd.melt(df, id_vars='Country/Region', value_vars=df.columns[1:])
    df.columns = ['Country', 'Date', 'Confirmed']
    df['Date'] = pd.to_datetime(df['Date'])

    return df


def fetch_countries_COVID19_data_with_dates(end: datetime) -> pd.DataFrame:
    """
    Create new time-series data frame of COVID-19 by sending request to JHU open-sourced project on Github
    :param end: datetime
    :return: a data frame of COVID-19 within specific countries and time
    >>> fetch_countries_COVID19_data_with_dates("")
    Traceback (most recent call last):
    ValueError: Empty end date
    >>> end = datetime.datetime.strptime("01-23-20", Constant.DATE_FORMAT)
    >>> new_df = fetch_countries_COVID19_data_with_dates(end)
    >>> print(new_df.iloc[207]["Country/Region"] + " has " + str(new_df.iloc[207]["1/23/20"]) + " confirmed case(s)")
    Taiwan* has 1 confirmed case(s)
    """
    if end == "" or end is None:
        raise ValueError("Empty end date")
        return

    file_path = os.getcwd() + Constant.COVID_RAW_DATA_DIR + "/COVID19_till_" + end.strftime('%Y-%m-%d') + Constant.DATA_POSTFIX_CSV
    whole_df = None
    if os.path.exists(file_path) is False:
        try:
            request_url = Constant.DATA_URL + Constant.DATA_POSTFIX_CSV
            whole_df = pd.read_csv(request_url, usecols=lambda x: x not in (['Province/State', 'Lat', 'Long']))

        except FileNotFoundError as error:
            print("FileNotFoundError occurs: " + repr(error))
            return

        # calculate how many columns need to save
        start = datetime.datetime.strptime("01-22-20", Constant.DATE_FORMAT)
        num_of_col = 1 + (end - start).days
        whole_df = whole_df.iloc[:, 0:num_of_col + 1]
        whole_df.to_csv(file_path, header=True, index=False)
    else:
        whole_df = pd.read_csv(file_path)

    return whole_df


def get_keyword_list(country: str) -> list:
    """
    Access the keyword list for google search
    :param country: country abbreviation
    :return: a keyword list
    >>> new_country = Constant.US
    >>> us_list = get_keyword_list(new_country)
    >>> us_list[0]
    'disinfectants'
    >>> get_keyword_list("")
    Traceback (most recent call last):
    ValueError: Country is empty
    """
    if country is None or country == "":
        raise ValueError("Country is empty")

    keywords = []
    if country == Constant.US:
        keywords = Constant.KEY_WORDS_LIST_EN
    elif country == Constant.TW:
        keywords = Constant.KEY_WORDS_LIST_TW

    return keywords


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
    '2020-04-22 00:00:00'
    >>> US_df.iloc[-1]["mask"]
    29
    >>> spain_df = create_google_trend_df(pytrend, keyword_list, "Spain", start_date, end_date)
    Traceback (most recent call last):
    ValueError: Region is not well defined
    """
    google_trend_df = None

    if region not in [Constant.TW, Constant.US]:
        raise ValueError("Region is not well defined")
        return None

    file_path = os.getcwd() + Constant.GT_5_YR_DATA_DIR + "/GT_" + region + Constant.DATA_POSTFIX_CSV
    if datetime.datetime.strptime(start_date, Constant.PLOT_DATE_FORMAT) > \
            datetime.datetime.strptime("2019-12-31", Constant.PLOT_DATE_FORMAT):
        file_path = os.getcwd() + Constant.GT_RECENT_DATA_DIR + "/GT_" + region + Constant.DATA_POSTFIX_CSV

    if os.path.exists(file_path):
        google_trend_df = pd.read_csv(file_path)
        google_trend_df['date'] = pd.to_datetime(google_trend_df['date'])
        return google_trend_df

    for i in range(len(keywords)):
        pytrend.build_payload(kw_list=[keywords[i]], cat=0, timeframe=start_date + " " + end_date, geo=region, gprop='')
        tmp_GT_df = pytrend.interest_over_time()
        if i == 0:
            google_trend_df = tmp_GT_df.reset_index().drop(['isPartial'], axis=1)
        else:
            google_trend_df[keywords[i]] = tmp_GT_df.reset_index()[keywords[i]]

    # convert the column name to English for non-English speaking countries
    col_names = Constant.KEY_WORDS_LIST_EN.copy()
    col_names.insert(0, 'date')
    google_trend_df.columns = col_names
    google_trend_df['date'] = pd.to_datetime(google_trend_df['date'])

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
    >>> pytrend = TrendReq(hl='en-US', tz=360)
    >>> keyword_list = ['mask', 'sanitizer', 'toilet paper']
    >>> df = create_google_trend_df(pytrend, keyword_list, "US", "2020-01-20", "2020-01-31", True)
    >>> df.iloc[0]
    date                 2020-01-01 00:00:00
    disinfectants                          3
    thermometers                           3
    oat milk                              35
    rubbing alcohol                        9
    powdered milk                         12
    hydrogen peroxide                     21
    mask                                   4
    sanitizer                              1
    toilet paper                           1
    disposable gloves                      4
    Name: 0, dtype: object
    >>> plot_google_trend_of_item(df, "US", "test")

    >>> plot_google_trend_of_item(df, "US", "test2", ['mask', 'disposable gloves'])

    """
    fig, ax = plt.subplots(nrows=5, ncols=2, figsize=(12, 10))
    x = df['date']

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
    >>> pytrend = TrendReq(hl='en-US', tz=360)
    >>> start_date = "2015-04-19"
    >>> end_date = "2020-04-22"
    >>> keyword_list = get_keyword_list(Constant.US)
    >>> US_df = create_google_trend_df(pytrend, keyword_list, Constant.US, start_date, end_date)
    >>> impacted_keyword_list = select_item_impacted_by_covid19(US_df)
    >>> print(len(impacted_keyword_list))
    9
    >>> impacted_keyword_list = select_item_impacted_by_covid19(None)
    Traceback (most recent call last):
    ValueError: Data frame not exist
    """
    if df is None:
        raise ValueError("Data frame not exist")

    kw_list = []
    for item in df.columns[1:]:
        skew = df[item].skew()
        past_max = df[df['date'].dt.date < datetime.date(2020, 1, 1)][item].max()
        if skew > 4 and past_max < 50:
            kw_list.append(item)
    return kw_list


def select_representative_kw(df: pd.DataFrame, impacted_item: list) -> (list, dict):
    """
    Select the representative items which has sharp increase due to COVID-19.
    The selection criteria:
    1. low max value of the trend 2 weeks before the peak
    2. high max value of the trend during COVID-19
    - Create a dictionary for record of items' max value date
    :param df: google trend dataframe of the items
    :param impacted_item: items list generated by select_item_impacted_by_covid19()
    :return: representative keywords list and dictionary of items' trend max date
    >>> pytrend = TrendReq(hl='en-US', tz=360)
    >>> start_date = "2015-04-19"
    >>> end_date = "2020-04-22"
    >>> keyword_list = get_keyword_list(Constant.US)
    >>> US_df = create_google_trend_df(pytrend, keyword_list, Constant.US, start_date, end_date)
    >>> impacted_keyword_list = select_item_impacted_by_covid19(US_df)
    >>> print(len(select_representative_kw(US_df, impacted_keyword_list)[0]))
    6
    >>> print(len(select_representative_kw(US_df, impacted_keyword_list)[1]))
    9
    >>> print(len(select_representative_kw(US_df, [])[0]))
    6
    >>> select_representative_kw(None, impacted_keyword_list)
    Traceback (most recent call last):
    ValueError: Data frame not exist
    """
    if df is None:
        raise ValueError("Data frame not exist")
    if impacted_item != []:
        df = pd.concat([df['date'], df[impacted_item]], sort=False, axis=1)
    kw_list = []
    keywords_maxdate_pairs = {}
    for item in df.columns[1:]:
        max_idx = df[item].idxmax()
        keywords_maxdate_pairs[item] = df['date'][max_idx]
        # Use two weeks as sharply increase time. So the local max value before global max value should be low.
        date_bound = df['date'][max_idx] - datetime.timedelta(days=14)
        past_max = df[df['date'] < date_bound][item].max()
        current_max = df[df['date'] > date_bound][item].max()
        if past_max < 30 and current_max > 90:
            kw_list.append(item)
    return kw_list, keywords_maxdate_pairs


def plot_items_with_confirmed_case(region_df: pd.DataFrame, item_name_list: list, first_confirmed_date: datetime,
                                   region: str):
    """
    Plot selective items' google trend and confirmed cases trend with 1st confirmed case date.
    :param first_confirmed_date: date of first confirmed
    :param region_df: combination dataframe of items google trend and confirmed number
    :param item_name_list: representative keywords list
    :param region: region of plot
    :return: None
    >>> pytrend = TrendReq(hl='en-US', tz=360)
    >>> start_date = "2015-04-19"
    >>> end_date = "2020-04-22"
    >>> keyword_list = get_keyword_list(Constant.US)
    >>> US_df = create_google_trend_df(pytrend, keyword_list, Constant.US, start_date, end_date)
    >>> representative_items = select_representative_kw(US_df, [])[0]
    >>> plot_items_with_confirmed_case(None, representative_items, datetime.date(2020, 1, 21), "US")
    Traceback (most recent call last):
    ValueError: Data frame not exist
    """
    if region_df is None:
        raise ValueError("Data frame not exist")

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
    ax2.legend(lines + lines2, labels + labels2, fontsize=8, loc='upper left')

    file_path = os.getcwd() + Constant.GT_FIGURE_NAME_PREFIX + region + '_' + \
                Constant.GT_FIGURE_WITH_COMFIRMED_CASE + '.png'
    fig.savefig(file_path, bbox_inches="tight")


def convert_country_abbreviation_to_fullname(abbreviation: str) -> str:
    """
    convert country's abbreviation to its full name
    :param abbreviation: country abbreviation
    :return: country full name
    >>> convert_country_abbreviation_to_fullname("TW")
    'Taiwan*'
    """
    if abbreviation == Constant.TW:
        return Constant.TAIWAN
    else:
        return None


def awareness_date_report(first_confirmed_date: datetime, keywords_max_dates_pairs: dict) -> dict:
    """
    Define the awareness date and report the first confirmed date, awareness date and time gap between first confirmed
    date and awareness date.
    The definition of awareness time gap is mean time interval between date of 1st confirmed case and date of max search
    volume of each item.
    The definition of awareness date the 1st confirmed case date + awareness time gap
    :param first_confirmed_date: date of first confirmed
    :param max_dates:of_keywords_dict_ dictionary of each item's google trend max date
    :return: dictionary that record the first confirmed date, awareness date and time gap between first confirmed
    date and awareness date
    >>> first_confirmed_date = datetime.date(2020, 1, 21)
    >>> pytrend = TrendReq(hl='en-US', tz=360)
    >>> start_date = "2015-04-19"
    >>> end_date = "2020-04-22"
    >>> keyword_list = get_keyword_list(Constant.US)
    >>> US_df = create_google_trend_df(pytrend, keyword_list, Constant.US, start_date, end_date)
    >>> impacted_keyword_list = select_item_impacted_by_covid19(US_df)
    >>> keywords_max_dates_pairs = select_representative_kw(US_df, impacted_keyword_list)[1]
    >>> awarness_report = awareness_date_report(first_confirmed_date, keywords_max_dates_pairs)
    >>> print(len(awarness_report))
    3
    >>> awarness_report['first_confirmed_date']
    datetime.date(2020, 1, 21)
    >>> awarness_report['mean_awareness_date'] - awarness_report['first_confirmed_date']
    datetime.timedelta(days=61)
    """
    report = {}
    report['first_confirmed_date'] = first_confirmed_date
    time_gap = {k: (v.date() - first_confirmed_date).days for k, v in keywords_max_dates_pairs.items()}
    report['awareness_time_gap(days)'] = int(sum([time_gap[key] for key in time_gap]) / float(len(time_gap)))
    report['mean_awareness_date'] = first_confirmed_date + datetime.timedelta(
        days=report['awareness_time_gap(days)'])
    return report


def plot_confirmed_number_and_awareness_comparison(data_manager: dict, region1: str, region2: str):
    """
    Plot confirmed number trend with first confirmed date and awareness date for two countries comparison.
    :param data_manager:
    :param region1: 1st country name
    :param region2: 2nd country name
    :return:
    >>> plot_confirmed_number_and_awareness_comparison({}, 'TW', 'US')
    Traceback (most recent call last):
    ValueError: Data manager is null
    """
    if data_manager == {}:
        raise ValueError("Data manager is null")

    # 1st country's merged data frame of items google trend and confirmed number
    region1_df = data_manager[region1]['COVID_19_with_google_trend']
    region1_awareness_report = data_manager[region1]['awareness_report']

    # 2nd country's merged data frame of items google trend and confirmed number
    region2_df = data_manager[region2]['COVID_19_with_google_trend']
    region2_awareness_report = data_manager[region2]['awareness_report']

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
        ax[i].set_ylabel('Google Trend', fontsize=18, color='blue')
        ax[i].legend()
    fig.tight_layout()
    fig.savefig('Confirmed_Number_Comparison.png', bbox_inches="tight")


if __name__ == '__main__':
    """
    Hypothesis 1:
    Steps:
    1) Pick 10 popular items in Google Trend during COVID-19 from Journals and other resources  
    2) In a macro viewpoint: Find the item which increase because of COVID-19 by examining each popular item in a 5-year trend
    3) In a micro viewpoint: Find representative item by filtering time interval
    
    Hypothesis 2:
    1) Plot to see the trend between COVID-19 and popular items
    2) Find the time interval between the time of the 1st confirmed case and the time of the max volume of each popular item
    3) Determine which country has better public awareness about the COVID-19 by comparing the time inteval in different region
    """
    # ------------------------------------------------------------------------------------------------------
    # Create COVID-19 data frame from start date to end date (default is 04-22-2020)
    create_data_folder(Constant.COVID_RAW_DATA_DIR)
    end_date = datetime.datetime.strptime("04-22-20", Constant.DATE_FORMAT)
    df = fetch_countries_COVID19_data_with_dates(end_date)

    # Establish the target countries in Abbreviation format
    selected_countries = [Constant.TW, Constant.US]

    """
    data_manager:{
        'TW': {'COVID_19_raw_data': COVID_df, 'GT_DF': GT_DF},
        'US': {'COVID_19_raw_data': COVID_df, 'GT_DF': GT_DF}
    }
    """
    data_manager = {}

    # ------------------------------------------------------------------------------------------------------
    # Store each country's COVID-19 data frame
    for country in selected_countries:
        country_raw_df = get_country_df(df, country)
        data_manager[country] = {}
        data_manager[country]["COVID_19_raw_data"] = country_raw_df
        # print("--------- country " + country + "---------------------------------")
        # print(country_raw_df.head(10))

    # ------------------------------------------------------------------------------------------------------
    # Plot the long-term(5 years) google trend of each item for observing the search trend.
    create_data_folder(Constant.GT_5_YR_DATA_DIR)
    pytrend = TrendReq(hl='en-US', tz=360)
    gt_start_date = "2015-04-19"
    gt_end_date = "2020-04-22"
    create_data_folder(Constant.GT_FIGURE_DIR)

    for country in selected_countries:
        keyword_list = get_keyword_list(country)

        # Create long-term(5 years) google trend for observation
        gt_country_raw_df = create_google_trend_df(pytrend, keyword_list, country, gt_start_date, gt_end_date, True)
        data_manager[country]["GT_DF"] = gt_country_raw_df

        # Plot the long-term(5 years) google trend of each item for observing the search trend.
        plot_google_trend_of_item(gt_country_raw_df, country, Constant.GT_FIGURE_5_YR)

    # ------------------------------------------------------------------------------------------------------
    # Select the items that impacted by COVID-19, then plot it
    # We assume that all items would have very low search volume before COVID-19
    # , but reach high search volume during the COVID-19 outbreak.
    # The selection criteria:
    # 1. high skew of the trend (extreme left skew)
    # 2. low max value of the search volume before COVID-19
    # Plot the long-term(5 years) google trend of the items which is highly impacted by COVID-19 (in red)
    for country in selected_countries:
        GT_df = data_manager[country]["GT_DF"]
        impacted_keyword_list = select_item_impacted_by_covid19(GT_df)
        data_manager[country]["impacted_keyword_list"] = impacted_keyword_list
        plot_google_trend_of_item(GT_df, country, Constant.GT_FIGURE_5_YR_SIGNIFICANT, impacted_keyword_list)

    # ------------------------------------------------------------------------------------------------------
    # Short-term google trend observation(this year)
    # From the long-term keyword selection, we then further select the representative items which has sharp increase
    # google trend during COVID-19 by observing short-term(this year) trend.
    # The selection criteria:
    # 1. low max value of the trend 2 weeks before the peak
    # 2. high max value of the trend during COVID-19
    # Plot the short-term(this year) google trend of each item for observing the search trend and make the selected
    # representative items drew by red line.
    create_data_folder(Constant.GT_RECENT_DATA_DIR)
    gt_start_date = "2020-01-01"
    for country in selected_countries:
        # Creat Google Trend data frame for each country
        keywords_list = get_keyword_list(country)

        # update google trend data frame from 5-yr to recent (2020-Present)
        GT_df = create_google_trend_df(pytrend, keywords_list, country, gt_start_date, gt_end_date, True)
        data_manager[country]["GT_DF"] = GT_df

        impacted_keyword_list = data_manager[country]["impacted_keyword_list"]
        representative_items, max_dates_of_keywords_pairs = select_representative_kw(GT_df, impacted_keyword_list)
        data_manager[country]['representative_items'] = representative_items
        data_manager[country]['max_dates_of_keywords_pairs'] = max_dates_of_keywords_pairs
        plot_google_trend_of_item(GT_df, country, 'representative', representative_items)

    # ------------------------------------------------------------------------------------------------------
    # Combind confirmed data and google trend data
    # Plot comparison between confirmed cases trend and google trend
    # Source: US: https://www.cdc.gov/coronavirus/2019-ncov/cases-updates/cases-in-us.html
    first_confirmed_date_dict = {Constant.TW: datetime.date(2020, 1, 21), Constant.US: datetime.date(2020, 1, 22)}

    for country in selected_countries:
        # Use final representative keywords of google trend
        country_GT_df = data_manager[country]["GT_DF"]
        representative_items = data_manager[country]['representative_items']
        country_GT_df = pd.concat([country_GT_df['date'], country_GT_df[representative_items]], sort=False, axis=1)
        country_COVID_19_df = data_manager[country]['COVID_19_raw_data']
        new_country_GT_df = country_GT_df.copy()

        # merge google trend and COVID-19 data frame
        new_country_GT_df = pd.merge(new_country_GT_df, country_COVID_19_df, left_on=['date'], right_on=['Date'], how='left').drop(['Date'], axis=1)
        country_full_name = country
        if country == Constant.TW:
            country_full_name = convert_country_abbreviation_to_fullname(Constant.TW)

        new_country_GT_df['Country'] = new_country_GT_df['Country'].fillna(country_full_name)
        new_country_GT_df = new_country_GT_df.fillna(0)
        data_manager[country]['COVID_19_with_google_trend'] = new_country_GT_df
        first_confirmed_date = first_confirmed_date_dict[country]
        plot_items_with_confirmed_case(new_country_GT_df, representative_items, first_confirmed_date, country)
        
    # ------------------------------------------------------------------------------------------------------
    # Determine which country has better public awareness about the COVID-19 by comparing the time interval
    # in different region by plotting the number of confirmed cases and awareness date of Taiwan and US
    for country in selected_countries:
        first_confirmed_date = first_confirmed_date_dict[country]
        max_dates_of_keywords_pairs = data_manager[country]['max_dates_of_keywords_pairs']

        # Use the average awareness date and its time interval
        # average awareness date: calculated from peak time of each items in Google Trend
        # time interval of each item: a period from the first confirmed date of COVID-19 to item's peak search time
        awareness_report = awareness_date_report(first_confirmed_date, max_dates_of_keywords_pairs)
        data_manager[country]['awareness_report'] = awareness_report

    # Plot confirmed number trend and time gap between first confirmed date and awareness date for two countries.
    plot_confirmed_number_and_awareness_comparison(data_manager, Constant.TW, Constant.US)
