import streamlit as st
from pages import page1,page2,page3
# Custom imports 
from multipage import MultiPage

# Create an instance of the app 
app = MultiPage()

# Title of the main page
st.set_page_config(page_title = "Coronavirus Data Charts - Greece")
# Add all your applications (pages) here
app.add_page("Daily Stats", page1.app)
app.add_page("Charts", page2.app)
app.add_page("Regional Charts", page3.app)

# The main app
app.run()