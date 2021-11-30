from matplotlib.pyplot import figure
import streamlit as st
from preprocessing import * 
from plots import * 

def app():
    # Get Data
    global_pop = global_with_population()
    # write text:
    st.title("Worldwide - per 100,000 population")
    text_pop = """
    Differences in the population size between different countries are often large.
     To compare countries, it is insightful to look at the number of confirmed cases/deaths per 100,000 people.
    """
    st.write(text_pop)
    st.plotly_chart(figure_10(global_pop))
    st.plotly_chart(figure_11(global_pop))