import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import requests
from PIL import Image
import plotly.graph_objects as go
pd.options.plotting.backend = "plotly"




st.set_page_config(page_title = "Greece Covid-19 Data Analysis")
st.header('Greece Covid-19 Data Analysis')
st.subheader("Nikos Maniatis")

url = "https://covid-19-greece.herokuapp.com/all"
response = requests.get(url)
jsondata = response.json()
columns=['confirmed','date','deaths']
df = pd.DataFrame.from_dict(jsondata['cases'])
data = []
for x in jsondata['cases']:
    data.append([x['confirmed'],x['date'],x['deaths']])

df = pd.DataFrame(data,columns=columns)
df['daily_cases'] = df['confirmed'] - df['confirmed'].shift(1)
df['daily_deaths'] = df['deaths'] - df['deaths'].shift(1)
df = df.dropna()
df['daily_cases'] = pd.to_numeric(df['daily_cases'],downcast='integer')
df['daily_deaths'] = pd.to_numeric(df['daily_deaths'],downcast='integer')
df['date'] = pd.to_datetime(df['date'],format='%Y-%m-%d')
##################################
#### DAILY CASES WITH M.A. PLOT###
##################################

x = df.copy()
x['SMA5'] = df['daily_cases'].rolling(window=5).mean()
x['SMA10']= df['daily_cases'].rolling(window=10).mean()
x = x.dropna(axis=0)
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

st.plotly_chart(fig,use_container_width=True)

##################################
#### DAILY DEATHS WITH M.A. PLOT###
##################################

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






############################
#TESTS AND POSITIVITY RATE#
############################

url = "https://covid-19-greece.herokuapp.com/total-tests"
response = requests.get(url)
jsondata = response.json()
columns=['date','rapid-tests','tests']
tests = pd.DataFrame.from_dict(jsondata['total_tests'])
data_ = []
for k in jsondata['total_tests']:
    data_.append([k['date'],k['rapid-tests'],k['tests']])

tests = pd.DataFrame(data_,columns=columns)
tests['tests'] = tests['tests'].replace(np.nan,0).astype(int)
tests['date'] = pd.to_datetime(tests['date'],format='%Y-%m-%d')

cases = df[df.date>= '2020-02-26']
comple = cases.merge(tests,how='left',on='date')
comple['daily_rapid'] = comple['rapid-tests'] - comple['rapid-tests'].shift(1)
comple['daily_tests'] = comple['tests'] - comple['tests'].shift(1)
comple = comple[comple['daily_tests'] >= 0]
comple = comple[comple['daily_rapid'] >= 0]
comple.dropna(inplace=True)

comple['positivity'] = comple['daily_cases']/(comple['daily_rapid'] + comple['daily_tests'])
comple['positivity'] = comple['positivity'].replace(np.nan,0)
comple['positivity'] = comple['positivity'].replace(np.inf,0)
comple['positivity'] = 100*comple['positivity']

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
