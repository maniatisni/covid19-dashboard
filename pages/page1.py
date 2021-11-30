import streamlit as st
from preprocessing import * 
from plots import * 

def app():
    ### Set Title Page, Header and Subheader
    st.header('Coronavirus Pandemic Dashboard')
    st.markdown("by [Nikos Maniatis](https://github.com/maniatisni)")
    df = cases_data()
    current_date = datetime.datetime.strptime(str(df.iloc[-1].date).split()[0], '%Y-%m-%d').strftime('%A, %B %d, %Y')

    text = """
    Here is another Dashboard with some useful charts about the Coronavirus pandemic.
    Data regarding Greece are provided by the [Coronavirus Greek API](https://covid-19-greece.herokuapp.com/),
    while Global Data are provided by the [Johns Hopkins University](https://github.com/CSSEGISandData/COVID-19) and [Esri API](https://coronavirus-resources.esri.com/datasets/1cb306b5331945548745a5ccd290188e_1/api).
    """
    st.markdown(text)
    st.markdown("---")
    ##################################
    #### TEXT AND STATS###
    ##################################
    st.header("Daily Statistics for Greece")
    st.write(current_date)
    ## Create Useful Stats dashboard
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
    st.markdown("---")

