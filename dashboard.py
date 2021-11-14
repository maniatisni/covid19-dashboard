import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import requests
import datetime
from PIL import Image
import plotly.graph_objects as go
pd.options.plotting.backend = "plotly"

## This is a functions that gets the response from the Greek API and returns a pandas dataframe.
url = 'https://covid-19-greece.herokuapp.com/'
def request_to_pandas(url, endpoint):
    # Join url with endpoint
    full_url = str(url+endpoint)
    # Get Response
    response = requests.get(full_url)
    # Json
    jsondata = response.json()
    key = list(jsondata.keys())[0]
    columns = list(jsondata[key][0].keys())
    temp = []
    for k in jsondata[key]:
        temp.append([k[j] for j in columns])
    return pd.DataFrame(temp,columns=columns)


### Get "all" data from Coronavirus Greek API.
### It contains info about:
### 1. Confirmed Cases 2. Confirmed Deaths 3. Dates
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



############################
#TESTS AND POSITIVITY RATE#
############################

### Get info about the total tests from the same API.
tests = request_to_pandas(url, endpoint='total-tests')

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

############################
#CASES BY 100K PEOPLE BY REGION#
############################
#Get Data from API
regions = request_to_pandas(url, endpoint = 'regions')

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

figg['layout'].update(title='Cases per 100.000 people by Region - Color is total number of cases',
xaxis=dict(
      tickangle=-45
    ))


################################################
### GET DATA ABOUT CASES IN INTENSIVE CARE ###
################################################

### Get Data from same API.
meth = request_to_pandas(url, endpoint = 'intensive-care')
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



current_date = datetime.datetime.strptime(str(df.iloc[-1].date).split()[0], '%Y-%m-%d').strftime('%A, %B %d, %Y')
##################################
#### PAGE SETUP######
#################################

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
st.markdown("---")
##################################
#### TEXT AND STATS###
##################################
st.header("Daily Statistics")
st.write(current_date)
col1, col2, col3, col4 = st.columns(4)
col1.metric("Cases", int(df.iloc[-1].daily_cases), \
"{}%".format(round(100*(df.iloc[-1].daily_cases-df.iloc[-2].daily_cases)/df.iloc[-2].daily_cases,1)),delta_color="inverse")

col2.metric("Deaths", int(df.iloc[-1].daily_deaths),\
 "{}%".format(round(100*(df.iloc[-1].daily_deaths-df.iloc[-2].daily_deaths)/df.iloc[-2].daily_deaths,1)),delta_color="inverse")
col3.metric("Positivity Rate","{}%".format(round(comple['positivity'].iloc[-1],2)),\
"{}%".format(round(100*(comple.iloc[-1].positivity-comple.iloc[-2].positivity)/comple.iloc[-2].positivity,1)), delta_color = 'inverse')

total_tests = comple.iloc[-1].daily_tests + comple.iloc[-1].daily_rapid
total_tests_yesterday = comple.iloc[-2].daily_tests + comple.iloc[-2].daily_rapid
col4.metric("Total Tests (PCR + Rapid)", int(total_tests),\
"{}%".format(round(100*(total_tests - total_tests_yesterday)/total_tests_yesterday,1)),delta_color = 'off' )


#### NOW DEPLOY THE CHARTS IN WHATEVER ORDER WE PREFER
# DAILY CASES WITH MOVING AVERAGES
st.plotly_chart(fig,use_container_width=True)
# DAILY TEST POSITIVITY RATE
st.plotly_chart(fig5, use_container_width=True)
# TOTAL DAILY TESTS (PCR+RAPID)
st.plotly_chart(fig6, use_container_width=True)
# CASES PER 100K PEOPLE - BY Region
st.plotly_chart(figg, use_container_width = True)
note = """
NOTE: This is a plot showing cases per 100.000 people,
however, some regions have a population smaller than 100.000,
so the resulting "cases per 100k people" is calculated by estimating
the percentage of the population that has tested positive and then assuming that the population is 100.000.
The Color bar shows the absolute number of cases.
"""
st.caption(note)
# NUMBER OF CASES IN INTENSIVE CARE
st.plotly_chart(fig7, use_container_width=True)
# DAILY DEATHS WITH MOVING AVERAGES
st.plotly_chart(fig2,use_container_width=True)
# TOTAL CONFIRMED CASES
st.plotly_chart(fig3, use_container_width=True)
# TOTAL CONFIRMED DEATHS
st.plotly_chart(fig4, use_container_width=True)
