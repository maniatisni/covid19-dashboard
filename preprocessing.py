########## IMPORTS ##########
import pandas as pd
import numpy as np
import plotly.express as px
import requests
import datetime
from PIL import Image
import geopandas as gpd

##################################################
# API URL
url = 'https://covid-19-greece.herokuapp.com/'
##################################################
def request_to_pandas(url, endpoint):
    """
    This is a function that gets the response
    from the Greek API and returns a pandas dataframe.

    """
    # Join url with endpoint
    full_url = str(url+endpoint)
    # Get Response
    response = requests.get(full_url)
    # JSON
    jsondata = response.json()
    key = list(jsondata.keys())[0]
    columns = list(jsondata[key][0].keys())
    temp = []
    for k in jsondata[key]:
        temp.append([k[j] for j in columns])
    return pd.DataFrame(temp,columns=columns)

##################################################
# CASES AND DEATHS DATA #
##################################################
def cases_data():
    """
     Get "all" data from Coronavirus Greek API.
     It contains info about:
     1. Confirmed Cases
     2. Confirmed Deaths
     3. Dates
     """
    df = request_to_pandas(url, endpoint='all')

    ### Calculate Daily cases/deaths from cumulative data.
    df['daily_cases'] = df['confirmed'] - df['confirmed'].shift(1)
    df['daily_deaths'] = df['deaths'] - df['deaths'].shift(1)
    df = df.dropna()
    ### Convert daily data to integers
    df['daily_cases'] = pd.to_numeric(df['daily_cases'],downcast='integer')
    df['daily_deaths'] = pd.to_numeric(df['daily_deaths'],downcast='integer')
    ### Convert Date column to datetime.
    df['date'] = pd.to_datetime(df['date'],format='%Y-%m-%d')
    # Create Moving Averages for 5 and 10 days window. (For Cases)
    df['SMA5'] = df['daily_cases'].rolling(window=5).mean()
    df['SMA10']= df['daily_cases'].rolling(window=10).mean()
    # Create Moving Averages for 5 and 10 days window. (For Deaths)
    df['DSMA5'] = df['daily_deaths'].rolling(window=5).mean()
    df['DSMA10']= df['daily_deaths'].rolling(window=10).mean()
    df = df.dropna(axis=0)
    return df

##################################################
# TESTS DATA #
##################################################
def tests_data():
    ### Get info about the total tests from the same API.
    tests = request_to_pandas(url, endpoint='total-tests')

    # Remove NaNs.
    tests['tests'] = tests['tests'].replace(np.nan,0).astype(int)
    tests['date'] = pd.to_datetime(tests['date'],format='%Y-%m-%d')

    # Get previous data
    cases = cases_data()
    # Choose cases after 26/2 because prior to that we didn't have data about tests.
    cases = cases[cases.date>= '2020-02-26']

    # MERGE the test data with the rest of our data on the 'date' column.
    comple = cases.merge(tests,how='left',on='date')

    # Calculate daily rapid tests and daily PCR tests
    comple['daily_rapid'] = comple['rapid-tests'] - comple['rapid-tests'].shift(1)
    comple['daily_tests'] = comple['tests'] - comple['tests'].shift(1)

    # Filter out the days with negative number of tests and drop NaNs.
    comple = comple[comple['daily_tests'] >= 0]
    comple = comple[comple['daily_rapid'] >= 0]
    comple.dropna(inplace=True)

    # Calculate Test Positivity Rate --> PR = 100*cases/total_tests
    comple['positivity'] = comple['daily_cases']/(comple['daily_rapid'] + comple['daily_tests'])
    # Replace NaNs and infinite positivity rates due to zero testing, with zero.
    comple['positivity'] = comple['positivity'].replace(np.nan,0)
    comple['positivity'] = comple['positivity'].replace(np.inf,0)
    comple['positivity'] = 100*comple['positivity']

    return comple

##################################################
# REGIONS DATA #
##################################################
def regions_data():
    regions = request_to_pandas(url, endpoint = 'regions')
    return regions



################################################
# CASES IN INTENSIVE CARE DATA #
################################################

def intensive_care_data():
    meth = request_to_pandas(url, endpoint = 'intensive-care')
    return meth

def geo_data(regions):
    ###################
    ####### MAP #######
    ###################
    gr = gpd.read_file("gadm36_GRC_shp/gadm36_GRC_2.shp")
    gdf_points = gpd.GeoDataFrame(regions, geometry=gpd.points_from_xy(regions.longtitude, regions.latitude))

    gr['NAME_2'] = gr['NAME_2'].replace({'Athos':'Mount Athos',
                    'West Macedonia':'Western Macedonia',
                    'East Macedonia and Thrace':'Eastern Macedonia and Thrace',
                    'West Greece':'Western Greece',
                    })


    mee = gdf_points.merge(gr, left_on='region_en', right_on ='NAME_2')
    mee = gpd.GeoDataFrame(mee,geometry='geometry_y')
    mee['casesper100k'] = 1e5*mee['total_cases']/mee['population']
    return mee


################################################
# GLOBAL DATA FROM JOHN HOPKINS UNIVERSITY #
################################################

def get_global_timeseries():
    # URLs
    url_1 = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'
    url_2 = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv'
    # Read Data
    cases = pd.read_csv(url_1)
    deaths = pd.read_csv(url_2)
    # Convert from wide to long format
    cases = pd.melt(cases, id_vars=['Province/State','Country/Region'], value_vars = list(cases.iloc[:,4:].columns),
               value_name = 'Confirmed',var_name = 'Date')
    deaths = pd.melt(deaths, id_vars=['Province/State','Country/Region'], value_vars = list(deaths.iloc[:,4:].columns),
               value_name = 'Deaths',var_name = 'Date')
    # Merge
    total = cases.merge(deaths, how = 'left', on = ['Date', 'Province/State','Country/Region'])
    # to DateTime
    total['Date'] = pd.to_datetime(total['Date'],format='%m/%d/%y')
    # group by date and country
    total = total.groupby(by=['Date','Country/Region'],as_index=False).sum()
    return total

def country_daily(data, country):
    """
    Helper function, to pick a country and calc daily stats
    """
    country_df = data.loc[data['Country/Region'] == country]
    country_df['Daily-Cases'] = country_df['Confirmed'] - country_df['Confirmed'].shift(1)
    country_df['Daily-Deaths'] = country_df['Deaths'] - country_df['Deaths'].shift(1)
    country_df.loc[country_df.Date == '2020-01-22','Daily-Cases'] = 0
    country_df.loc[country_df.Date == '2020-01-22','Daily-Deaths'] = 0
    return country_df

################################################
# GLOBAL DATA FROM API WITH POPULATION DATA #
################################################

def global_with_population():
    # Get first dataset:
    url = "https://services1.arcgis.com/0MSEUqKaxRlEPj5g/arcgis/rest/services/ncov_cases2_v1/FeatureServer/2/query?where=1%3D1&outFields=*&outSR=4326&f=json"
    response = requests.get(url)
    jsondata = response.json()
    # do it
    columns = ['Country_Region','Last_Update','Lat','Long_','Confirmed','Deaths','Recovered','Active','Incident_Rate',
          'People_Tested','People_Hospitalized','Mortality_Rate','UID','ISO3']
    data = []
    df = pd.DataFrame.from_dict(jsondata['features'][0])
    for x in jsondata['features']:
        x = x['attributes']
        data.append([x['Country_Region'], x['Last_Update'],x['Lat'],x['Long_'],x['Confirmed'],
                    x['Deaths'],x['Recovered'],x['Active'],x['Incident_Rate'],x['People_Tested'],
                    x['People_Hospitalized'],x['Mortality_Rate'],x['UID'],x['ISO3']] )
    df = pd.DataFrame(data,columns=columns)
    df = df.drop(columns=['Recovered', 'Active','People_Tested','People_Hospitalized','Last_Update'],axis=1)
    # convert to gpd dataframe
    df_gpd = gpd.GeoDataFrame(df,geometry=gpd.points_from_xy(df.Long_, df.Lat))
    # Get World Data
    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
    # MERGE
    merged = df_gpd.merge(world, left_on = 'ISO3',right_on='iso_a3')
    merged = gpd.GeoDataFrame(merged,geometry='geometry_y')
    # Data per 100K pop
    merged['Cases-per-100k'] = 100000*merged['Confirmed']/merged['pop_est']
    merged['Deaths-per-100k'] = 100000*merged['Deaths']/merged['pop_est']

    return merged