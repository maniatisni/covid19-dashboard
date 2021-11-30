# Global TimeSeries Data
from matplotlib.pyplot import figure
import streamlit as st
from preprocessing import * 
from plots import * 

def app():
    # Get Data
    total = get_global_timeseries()
    # Get available countries list
    countries = list(total['Country/Region'].unique())
    # title
    st.title("Worldwide - Absolute Numbers")
    # Default countries to show 
    defaults = ['Greece', 'Switzerland', 'Slovenia', 'Portugal','Netherlands']
    # Multi Select
    options = st.multiselect("Choose Countries to visualize:", countries, default = defaults)
    # Do plot

    fig = go.Figure()
    fig2 = go.Figure()
    fig3 = go.Figure()
    fig4 = go.Figure()
    for country in options:
        df = country_daily(total,country)
        fig.add_trace(
            go.Line(
                x=df['Date'],
                y=df['Confirmed'],
                name=country
            ))
        
        fig2.add_trace(
            go.Line(
                x=df['Date'],
                y=df['Deaths'],
                name=country
            ))
        fig3.add_trace(
            go.Line(
                x=df['Date'],
                y=df['Daily-Cases'],
                name=country
            ))
        
        fig4.add_trace(
            go.Line(
                x=df['Date'],
                y=df['Daily-Deaths'],
                name=country
            ))
    fig['layout'].update(title='Confirmed Cases for selected Countries',xaxis=dict(
    tickangle=-30),
    legend=dict(
    yanchor="top",
    y=0.99,
    xanchor="left",
    x=0.01))
    st.plotly_chart(fig) 

    fig2['layout'].update(title='Confirmed Deaths for selected Countries',xaxis=dict(
    tickangle=-30),
    legend=dict(
    yanchor="top",
    y=0.99,
    xanchor="left",
    x=0.01))
    st.plotly_chart(fig2)

    fig3['layout'].update(title='Daily Confirmed Cases for selected Countries',xaxis=dict(
    tickangle=-30),
    legend=dict(
    yanchor="top",
    y=0.99,
    xanchor="left",
    x=0.01))

    st.plotly_chart(fig3)

    fig4['layout'].update(title='Daily Confirmed Deaths for selected Countries',xaxis=dict(
    tickangle=-30),
    legend=dict(
    yanchor="top",
    y=0.99,
    xanchor="left",
    x=0.01))
    st.plotly_chart(fig4)
