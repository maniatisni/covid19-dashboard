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