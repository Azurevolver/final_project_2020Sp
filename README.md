# final_project
Each team creates a fork from this for their course project

# Team:
Yuan-Ching (Alan) Chen : @azurevolver
Jasmine Kuo : @wenyu125

# Contribution:
The following is a general division of work. Most of the content is discussed and revised together.

Yuan-Ching (Alan) Chen :
Data Collection (Google Trend & COVID19 dataset) and Data Preprocess
  create_data_folder()
  get_country_df()
  fetch_countries_COVID19_data_with_dates()
  get_keyword_list()
  create_google_trend_df()
  convert_country_abbreviation_to_fullname()
  
Jasmine Kuo :
Data Preprocess, Data Analysis and Data Visulization
  plot_google_trend_of_item()
  select_item_impacted_by_covid19()
  select_representative_kw()
  plot_items_with_confirmed_case()
  awareness_date_report()
  plot_confirmed_number_and_awareness_comparison()
  
# Introduction
Our team aims to find whether the search volume of specific products on Google Trend is positively related to the confirmed cases of COVID-19.
So we raise two research questions:
1) What kinds of products people tend to buy when they are aware of the pandemic?
2) After the announcement of the first confirmed case, will the domestic search for the panic-buying products affect the trend of diagnosed cases?

# Hypothesis 1
We hypothesize that the search volume of some medical and cleaning stuff such as ‘tissue,’ ‘surgical mask,’ and ‘hand sanitizer’ would increase because of the disease. We want to find out what are those items positively correlated with the outbreak of COVID19.
Steps:
1) Pick 10 panic-buying items during COVID-19 from Journals and Google Trend
2) Long-term observation: Limit the panic-buying items which increase because of COVID-19 by examining the search trend of those popular items in a 5-year period
3) Short-term observation: Determine the representative items by choosing items with a sharp increase in search trend during the outbreak of the disease

# Hypothesis 2
The time gap between the peak time of items' search volume and the time of the 1st confirmed case reflects people's response and awareness to the epidemic. We assume that shorter reaction times may indicate that the future outbreak will gradually slow down.
Steps:   
1) Plot to see the trend between COVID-19 and panic-buying items’ search volume
2) Find the time interval between the 1st confirmed case and the max search volume of each item
3) Determine which country has better public awareness about the COVID-19 by comparing the time interval in a different region

# Data Source
1. Americans Bought More Beans, Disinfectants and Oat Milk to Prepare for the Coronavirus Pandemic. (MARCH 26, 2020)  Retrived from https://time.com/5810811/coronavirus-shopping-data/

2. 2019 Novel Coronavirus COVID-19 (2019-nCoV) Data Repository by Johns Hopkins CSSE
https://github.com/CSSEGISandData/COVID-19

3. Taiwan CDC
https://sites.google.com/cdc.gov.tw/2019ncov/taiwan?authuser=0

4. US CDC
https://www.cdc.gov/coronavirus/2019-ncov/index.html

5. Google Trend
https://trends.google.com/trends/



# Methods
* Long term Google trend Observation:
![Alt text](https://github.com/Azurevolver/final_project_2020Sp/blob/master/GT_FIGURE/GoogleTrend_TW_5_yrs.png "GoogleTrend_TW_5_yrs")
We plot the 5-years google trend. Take the mask and disposable gloves in Taiwan as an example, and the mask is affected by COVID-19. You can see that there is a peak on the right side. However, disposable gloves are not a COVID-19 panic-buying item in Taiwan. Now let’s see ten items’ 5-year trend situation in the US and Taiwan.

![Alt text](https://github.com/Azurevolver/final_project_2020Sp/blob/master/GT_FIGURE/GoogleTrend_TW_5_yrs_significant.png "GoogleTrend_TW_5_yrs_significant")
![Alt text](https://github.com/Azurevolver/final_project_2020Sp/blob/master/GT_FIGURE/GoogleTrend_US_5_yrs_significant.png "GoogleTrend_US_5_yrs_significant")
The items in the red line were deeply affected by COVID-19. This charts ultimately confirm our first hypothesis, which is that the search volume of some things increased due to COVID-19. You may also find that Taiwan and the US COVID-19 panic-buying items are not the same. For example, Americans tend to buy gloves, but Taiwanese do not buy them. To find out which items were affected by COVID-19, that is the red line items. We used some statistical methods like calculating the skew and max value of a specific time interval to filter the keywords positively correlated with the outbreak of COVID19.

* Short term Google trend Observation:
![Alt text](https://github.com/Azurevolver/final_project_2020Sp/blob/master/GT_FIGURE/GoogleTrend_TW_representative.png "GoogleTrend_TW_representative")
![Alt text](https://github.com/Azurevolver/final_project_2020Sp/blob/master/GT_FIGURE/GoogleTrend_US_representative.png "GoogleTrend_US_representative")
Then, we further selected the representative items by observing short-term trends. We used this year’s google trend to identify those panic-buying items whose search volume sharply increased during the outbreak of COVID-19. As the figures show, the keywords in the red line significantly change from low to almost 100 over a short time. These kinds of items are defined as the country’s representative COVID19 panic-buying items for our analysis. We then used these keywords to determine the awareness date for further comparison.

* With confirmed cases in Taiwan and US
![Alt text](https://github.com/Azurevolver/final_project_2020Sp/blob/master/GT_FIGURE/GoogleTrend_TW_with_ConfirmedCases.png "GoogleTrend_TW_with_ConfirmedCases")
![Alt text](https://github.com/Azurevolver/final_project_2020Sp/blob/master/GT_FIGURE/GoogleTrend_US_with_ConfirmedCases.png "GoogleTrend_US_with_ConfirmedCases")
We plot the google trend of representative items and the number of confirmed cases for two countries and also add the first confirmed dates. You will see that even though the first confirmed dates are almost the same, the time when people start to search, the items are quite different in the comparison of the two countries. The search volume increasing time in Taiwan is earlier than the time in the US. We thought that searching panic-buying products indicate people's awareness of COVID-19. That is to say, based on our analysis, Taiwanese awareness of COVID-19 is relatively early.

* Comparison between Taiwan and US
![Alt text](https://github.com/Azurevolver/final_project_2020Sp/blob/master/Confirmed_Number_Comparison.png "Confirmed_Number_Comparison")
We define the awareness time gap as the average time gap between the max value date of representative items google trend and first confirmed date. So the awareness date would be the 1st confirmed case date plus awareness time gap. It can be clearly seen from the figure that the awareness time gap of Taiwan is 11 days which is significantly shorter than the time gap 55 days of the US.


# Result
Although the outcome supports our hypothesis, which is a shorter reaction times might indicate a gradually slow down in the trend of the confirmed case,  we believe there are other factors can influence the tendency of confirmed patients' number. In future research, we will make our hypothesis more tenable by including more countries' confirmed cases and Google Trend search data.


