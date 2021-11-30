from matplotlib.pyplot import figure
import streamlit as st
from preprocessing import * 
from plots import * 

def app():
    st.title("Greece - Regional Charts")
    regions = regions_data()
    geo = geo_data(regions)
    fig_9 = figure_9(regions,geo)
    st.pyplot(fig_9)
    fig_8 = figure_8(regions)
    st.plotly_chart(fig_8)


