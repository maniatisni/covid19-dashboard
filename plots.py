from preprocessing import *
import plotly.express as px
import plotly.graph_objects as go
import geopandas as gpd
import matplotlib.pyplot as plt
pd.options.plotting.backend = "plotly"

################################
# Call functions and get data #
################################

# cases and deaths base dataframe
cases = cases_data()
# tests data merged with cases df
comple = tests_data()
# regions data
regions = regions_data()
# intensive care data (ΜΕΘ)
meth = intensive_care_data()
# geographic data
mee = geo_data(regions)

################################
# Cases with Moving Averages Plot #
################################

def figure_1(cases):

    ### Make the plot with PlotLy.
    fig_1 = go.Figure()
    fig_1.add_trace(
        go.Line(
            x=cases['date'],
            y=cases['daily_cases'],
            name='Daily Cases'
        ))
    fig_1.add_trace(
        go.Line(
            x=cases['date'],
            y=cases['SMA5'],
            name='5 Day Moving Average'
        ))
    fig_1.add_trace(
        go.Line(
            x=cases['date'],
            y=cases['SMA10'],
            name='10 Day Moving Average'
        ))
    fig_1['layout'].update(title='Daily Cases in Greece\n with Moving Averages',xaxis=dict(
        tickangle=-30),
        legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01
))

    return fig_1

def figure_2(cases):

    ### Make the plot with PlotLy.
    fig_2 = go.Figure()
    fig_2.add_trace(
        go.Line(
            x=cases['date'],
            y=cases['daily_deaths'],
            name='Daily Deaths'
        ))
    fig_2.add_trace(
        go.Line(
            x=cases['date'],
            y=cases['DSMA5'],
            name='5 Day Moving Average'
        ))
    fig_2.add_trace(
        go.Line(
            x=cases['date'],
            y=cases['DSMA10'],
            name='10 Day Moving Average'
        ))
    fig_2['layout'].update(title='Daily Deaths in Greece\n with Moving Averages',xaxis=dict(
        tickangle=-30),
        legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01
))

    return fig_2


def figure_3(comple):
# Make the plot.
    fig_3 = go.Figure()

    fig_3.add_trace(
        go.Scatter(
            x=comple['date'],
            y=comple['positivity'],
            name='Positivity Rate'
        ))
    fig_3['layout'].update(title='Daily Test Positivity Rate (%)',xaxis=dict(
        tickangle=-30
        ))
    return fig_3

def figure_4(comple):
    fig_4 = go.Figure()

    fig_4.add_trace(
        go.Scatter(
            x=comple['date'],
            y=comple['daily_rapid']+comple['daily_tests'],
            name='Total Daily Tests (PCR + Rapid)'
        ))
    fig_4['layout'].update(title='Total Daily Tests (PCR + Rapid)',xaxis=dict(
        tickangle=-30
        ))
    return fig_4

def figure_5(meth):
    fig_5 = go.Figure()
    fig_5.add_trace(
        go.Scatter(
            x=meth['date'],
            y=meth['intensive_care'],
            name='Number of Cases in Intensive Care'
        ))
    fig_5['layout'].update(title='Number of Cases in Intensive Care',xaxis=dict(
        tickangle=-30
        ))
    return fig_5

def figure_6(cases):
    fig_6 = go.Figure()

    fig_6.add_trace(
        go.Scatter(
            x=cases['date'],
            y=cases['confirmed'],
            name='Cases'
        ))
    fig_6['layout'].update(title='Total Confirmed Cases in Greece',xaxis=dict(
        tickangle=-30
        ))
    return fig_6

def figure_7(cases):
    fig_7 = go.Figure()
    fig_7.add_trace(
    go.Scatter(
        x=cases['date'],
        y=cases['deaths'],
        name='Cases'
    ))
    fig_7['layout'].update(title='Total Confirmed Deaths in Greece',xaxis=dict(
        tickangle=-30
        ))
    return fig_7

def figure_8(regions):
        # Barplot
    fig_8 = px.bar(regions.sort_values(by='cases_per_100000_people',ascending = False),
                x='area_en', y='cases_per_100000_people',
                hover_data=['area_gr', 'cases_per_100000_people','last_updated_at','total_cases','population'],
                color='total_cases',
                labels={
                        "area_en": "District",
                        "cases_per_100000_people": "Cases per 100.000 People",
                        "last_updated_at": "Data Last Updated at",
                        "population": "Population",
                        "total_cases": "Total Cases",
                        "area_gr": "ΝΟΜΟΣ"
                    },)

    fig_8['layout'].update(title='Cases per 100.000 people by District (Νομοί) - Color is total number of cases',
    xaxis=dict(
        tickangle=-45
        ))
    return fig_8

plt.style.use('default')
plt.rcParams.update({"figure.facecolor":"#0E1117",
                    "axes.edgecolor":"#0E1117",
                    "axes.facecolor":"#0E1117",
                    "text.color":"white",
                    "axes.labelcolor":"white",
                    "xtick.color":"white",
                    "ytick.color":"white"
                    })

def figure_9(regions,mee):
    fig_9,base = plt.subplots(dpi=200)
    base.set_aspect('equal')
    mee.plot(color='white',edgecolor='#0E1117',figsize=(10, 10),ax=base)
    mee.plot(column='casesper100k',legend=True,cmap='inferno',ax=base,\
        legend_kwds={'label':"Cases per 100K Population - by Region (Περιφέρεια)",'orientation':'horizontal'})
    base.axis('off')
    base.set_title("Last Updated on: {}".format(regions.iloc[-1].last_updated_at),fontsize=5,fontdict={"color":"white"})
    return fig_9