from matplotlib.pyplot import figure
import streamlit as st
from preprocessing import * 
from plots import * 

def app():
    st.title("Greece - Charts")
    # Get data:
    cases = cases_data()
    comple = tests_data()

    # Plot Charts
    fig_1 = figure_1(cases)
    st.plotly_chart(fig_1)

    fig_2 = figure_2(cases)
    st.plotly_chart(fig_2)

    fig_3 = figure_3(comple)
    st.plotly_chart(fig_3)

    fig_4 = figure_4(comple)
    st.plotly_chart(fig_4)

    fig_5 = figure_5(meth)
    st.plotly_chart(fig_5)
