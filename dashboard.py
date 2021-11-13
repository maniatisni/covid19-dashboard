import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import requests
from PIL import Image
import plotly.graph_objects as go
pd.options.plotting.backend = "plotly"


### Set Title Page, Header and Subheader
st.set_page_config(page_title = "Coronavirus Data Charts - Greece")
st.header('Coronavirus Data Charts - Greece')
st.markdown("by [Nikos Maniatis](https://github.com/maniatisni)")


text = """
Here is another Dashboard with some useful charts about the Coronavirus pandemic in Greece.
Data provided by the [Coronavirus Greek API](https://covid-19-greece.herokuapp.com/), which is updated daily.
All charts are interactive and can be enlarged.
"""
st.markdown(text)

### Get "all" data from Coronavirus Greek API.
### It contains info about:
### 1. Confirmed Cases 2. Confirmed Deaths 3. Dates
url = "https://covid-19-greece.herokuapp.com/all"
response = requests.get(url)
jsondata = response.json()

### Read the JSON data into a pandas dataframe.
columns=['confirmed','date','deaths']
df = pd.DataFrame.from_dict(jsondata['cases'])
data = []
for x in jsondata['cases']:
    data.append([x['confirmed'],x['date'],x['deaths']])
df = pd.DataFrame(data,columns=columns)

### Calculate Daily cases/deaths from cumulative data.
df['daily_cases'] = df['confirmed'] - df['confirmed'].shift(1)
df['daily_deaths'] = df['deaths'] - df['deaths'].shift(1)
df = df.dropna()
### Convert daily data to integers
df['daily_cases'] = pd.to_numeric(df['daily_cases'],downcast='integer')
df['daily_deaths'] = pd.to_numeric(df['daily_deaths'],downcast='integer')
### Convert Date column to datetime.
df['date'] = pd.to_datetime(df['date'],format='%Y-%m-%d')

##################################
#### DAILY CASES WITH M.A. PLOT###
##################################

#make a copy of the dataframe and calculate moving average for 5 and 10 days.
x = df.copy()
x['SMA5'] = df['daily_cases'].rolling(window=5).mean()
x['SMA10']= df['daily_cases'].rolling(window=10).mean()
x = x.dropna(axis=0)

### Make the plot with PlotLy.
fig = go.Figure()
fig.add_trace(
    go.Line(
        x=x['date'],
        y=x['daily_cases'],
        name='Daily Cases'
    ))
fig.add_trace(
    go.Line(
        x=x['date'],
        y=x['SMA5'],
        name='5 Day Moving Average'
    ))
fig.add_trace(
    go.Line(
        x=x['date'],
        y=x['SMA10'],
        name='10 Day Moving Average'
    ))
fig['layout'].update(title='Daily Cases in Greece\n with Moving Averages',xaxis=dict(
      tickangle=-30
    ))

# Put the chart on the dashboard.
st.plotly_chart(fig,use_container_width=True)

############################
#TESTS AND POSITIVITY RATE#
############################

### Get info about the total tests from the same API.
url = "https://covid-19-greece.herokuapp.com/total-tests"
response = requests.get(url)
jsondata = response.json()
### Convert the JSON data to pandas dataframe.
columns=['date','rapid-tests','tests']
tests = pd.DataFrame.from_dict(jsondata['total_tests'])
data_ = []
for k in jsondata['total_tests']:
    data_.append([k['date'],k['rapid-tests'],k['tests']])
tests = pd.DataFrame(data_,columns=columns)
# Remove NaNs.
tests['tests'] = tests['tests'].replace(np.nan,0).astype(int)
tests['date'] = pd.to_datetime(tests['date'],format='%Y-%m-%d')

# Choose cases after 26/2 because prior to that we didn't have data about tests.
cases = df[df.date>= '2020-02-26']

# MERGE the test data with the rest of our data on the 'date' column.
comple = cases.merge(tests,how='left',on='date')
# Calculate daily rapid tests and daily PCR tests
comple['daily_rapid'] = comple['rapid-tests'] - comple['rapid-tests'].shift(1)
comple['daily_tests'] = comple['tests'] - comple['tests'].shift(1)

# Filter out the days with negative number of tests and drop NaNs.
comple = comple[comple['daily_tests'] >= 0]
comple = comple[comple['daily_rapid'] >= 0]
comple.dropna(inplace=True)

# Calculate Test Positivity Rate.
# PR = 100*cases/total_tests
comple['positivity'] = comple['daily_cases']/(comple['daily_rapid'] + comple['daily_tests'])
# Replace NaNs and infinite positivity rates due to zero testing, with zero.
comple['positivity'] = comple['positivity'].replace(np.nan,0)
comple['positivity'] = comple['positivity'].replace(np.inf,0)
comple['positivity'] = 100*comple['positivity']

# Make the plot.
fig5 = go.Figure()

fig5.add_trace(
    go.Scatter(
        x=comple['date'],
        y=comple['positivity'],
        name='Positivity Rate'
    ))
fig5['layout'].update(title='Daily Test Positivity Rate (%)',xaxis=dict(
      tickangle=-30
    ))

st.plotly_chart(fig5, use_container_width=True)

fig6 = go.Figure()

fig6.add_trace(
    go.Scatter(
        x=comple['date'],
        y=comple['daily_rapid']+comple['daily_tests'],
        name='Total Daily Tests (PCR + Rapid)'
    ))
fig6['layout'].update(title='Total Daily Tests (PCR + Rapid)',xaxis=dict(
      tickangle=-30
    ))

st.plotly_chart(fig6, use_container_width=True)
############################
#CASES BY 100K PEOPLE BY REGION#
############################
#Get Data from API
url = 'https://covid-19-greece.herokuapp.com/regions'
response = requests.get(url)
jsondata = response.json()

#Prepare columns to read with pandas
regions = pd.DataFrame.from_dict(jsondata['regions'])
columns=['area_en','area_gr','cases_per_100000_people',
                 'geo_department_en','geo_department_gr','last_updated_at',
                 'latitude','longitude','population','region_en',
                 'region_gr','total_cases']
# read with pandas
data = []
for k in jsondata['regions']:
    data.append([k['area_en'],k['area_gr'],k['cases_per_100000_people'],
                 k['geo_department_en'],k['geo_department_gr'],k['last_updated_at'],
                 k['latitude'],k['longtitude'],k['population'],k['region_en'],
                 k['region_gr'],k['total_cases']])

regions = pd.DataFrame(data,columns=columns)

# Barplot
figg = px.bar(regions.sort_values(by='cases_per_100000_people',ascending = False),
             x='area_en', y='cases_per_100000_people',
            hover_data=['area_gr', 'cases_per_100000_people','last_updated_at','total_cases','population'],
            color='total_cases',
            labels={
                     "area_en": "Region",
                     "cases_per_100000_people": "Cases per 100.000 People",
                     "last_updated_at": "Data Last Updated at",
                     "population": "Population",
                     "total_cases": "Total Cases",
                     "area_gr": "ΝΟΜΟΣ"
                 },)
note = """
NOTE: This is a plot showing cases per 100.000 people,
however, some regions have a population smaller than 100.000,
so the resulting "cases per 100k people" is calculated by estimating
the percentage of the population that has tested positive and then assuming that the population is 100.000.
The Color bar shows the absolute number of cases.
"""
figg['layout'].update(title='Cases per 100.000 people by Region - Color is total number of cases',
xaxis=dict(
      tickangle=-45
    ))
st.plotly_chart(figg, use_container_width = True)
st.caption(note)

################################################
### GET DATA ABOUT CASES IN INTENSIVE CARE ###
################################################

### Get Data from same API.
url = "https://covid-19-greece.herokuapp.com/intensive-care"
response = requests.get(url)
jsondata = response.json()

### Convert JSON data to pandas dataframe.
columns=['date','intensive_care']
meth = pd.DataFrame.from_dict(jsondata['cases'])
data_ = []
for k in jsondata['cases']:
    data_.append([k['date'],k['intensive_care']])
meth = pd.DataFrame(data_,columns=columns)


### Make the Plot.

fig7 = go.Figure()

fig7.add_trace(
    go.Scatter(
        x=meth['date'],
        y=meth['intensive_care'],
        name='Number of Cases in Intensive Care'
    ))
fig7['layout'].update(title='Number of Cases in Intensive Care',xaxis=dict(
      tickangle=-30
    ))

st.plotly_chart(fig7, use_container_width=True)


##################################
#### DAILY DEATHS WITH M.A. PLOT###
##################################

# Same as above, with the moving average, just with the deaths data.
y = df.copy()
y['SMA5'] = df['daily_deaths'].rolling(window=5).mean()
y['SMA10']= df['daily_deaths'].rolling(window=10).mean()
y = y.dropna(axis=0)
fig2 = go.Figure()

fig2.add_trace(
    go.Line(
        x=y['date'],
        y=y['daily_deaths'],
        name='Daily Deaths'
    ))

fig2.add_trace(
    go.Line(
        x=y['date'],
        y=y['SMA5'],
        name='5 Day Moving Average'
    ))

fig2.add_trace(
    go.Line(
        x=y['date'],
        y=y['SMA10'],
        name='10 Day Moving Average'
    ))
fig2['layout'].update(title='Daily Deaths in Greece\n with Moving Averages',xaxis=dict(
      tickangle=-30
    ))

st.plotly_chart(fig2,use_container_width=True)

##################################
#### TOTAL CONFIRMED CASES PLOT###
##################################

fig3 = go.Figure()

fig3.add_trace(
    go.Scatter(
        x=x['date'],
        y=x['confirmed'],
        name='Cases'
    ))
fig3['layout'].update(title='Total Confirmed Cases in Greece',xaxis=dict(
      tickangle=-30
    ))

st.plotly_chart(fig3, use_container_width=True)


##################################
#### TOTAL CONFIRMED DEATHS PLOT#
#################################

fig4 = go.Figure()

fig4.add_trace(
    go.Scatter(
        x=x['date'],
        y=x['deaths'],
        name='Cases'
    ))
fig4['layout'].update(title='Total Confirmed Deaths in Greece',xaxis=dict(
      tickangle=-30
    ))

st.plotly_chart(fig4, use_container_width=True)
