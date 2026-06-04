import logging
logger = logging.getLogger(__name__)
import pandas as pd
import streamlit as st
import world_bank_data as wb
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
import requests
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

# Call the SideBarLinks from the nav module in the modules directory
SideBarLinks()

BASE_URL = "http://web-api:4000"

# set the header of the page
st.header('Build Your Own Country')

# You can access the session state to make a more customized/personalized app experience
st.write('### Fill in the values to predict EU Election Turnout for your created country')

col1, col2 = st.columns(2)

with col1:
    country_name = st.text_input(
        label='Name your Country:',
        type = "default",
        placeholder = "Country Name",
        key="country_name",
        help="Give your made up country a unique name."
    )

with col2:
    corruption_index = st.slider(
        label='Corruption Index:',
        min_value=0,
        max_value=100,
        value=35,
        step=1,
        format="%.1f",
        key="corruption_index",
        help="Corruption in politicians, or other related political institutions."
    )

col3, col4 = st.columns(2)

with col3:
     #maybe a better way to input this than increment by 1
    population = st.number_input(
        label='Population:',
        value = 5000000,
        key="population",
        help="The total population of the country."
    )

with col4:
    urbanization_rate = st.slider(
        label='Urbanization Rate:',
        min_value=0,
        max_value=100,
        value=60,
        step=1,
        format="%.1f",
        key="urbanization_rate",
        help="The rate of urbanization of the country."
    )

col5, col6 = st.columns(2)

with col5:
    #maybe a better way to input this than increment by 1
    gdp = st.number_input(
        label='GDP Per Capita (in euros):',
        value = 340000,
        key="gdp",
        help="GDP Per Capita of the country"
    )

with col6:
    median_age = st.number_input(
        label='Median Age:',
        value = 46,
        key="median_age",
        help="Median age of the country's population"
    )

col7, col8 = st.columns(2)

with col7:
    unemployment_rate = st.slider(
        label='Unemployment Rate:',
        min_value=0,
        max_value=100,
        value=24,
        step=1,
        format="%.1f",
        key="unemployment_rate",
        help="Rate of unemployment"
    )

with col8:
    net_beneficiary = st.radio(
        label='Net Beneficiary:',
        options= ["Yes", "No"],
        key="net_beneficiary",
        help="Does the country receive more benefit from being in the EU than it contributes?"
    )

col9, col10 = st.columns(2)

with col9:
    compulsory_voting = st.radio(
        label='Compulsory Voting:',
        options= ["Yes", "No"],
        key="compulsory_voting",
        help="Is voting mandatory for eligible citizens in the country?"
    )

with col10:
    weekend_voting = st.radio(
        label='Weekend Voting: ',
        options= ["Yes", "No"],
        key="weekend_voting",
        help="Are citizens able to vote on the weekends?"
    )

col11, col12 = st.columns(2)

with col11:
    years_in_eu = st.number_input(
        label='Years in EU:',
        value = 10,
        key="years_in_eu",
        help="How long the country has been part of the EU."
    )

with col12:
    nat_election_turnout = st.slider(
        label='National Election Turnout:',
        min_value=0,
        max_value=100,
        value=45,
        step=1,
        format="%.1f",
        key="nat_election_turnout",
        help="The election turnout of voters for national votes."
    )

if st.button("Predict EU Election Turnout", type='primary', use_container_width=True):
    payload = {
        "compulsory_voting": 1 if compulsory_voting == "Yes" else 0,
        "median_age": median_age,
        "national_turnout": nat_election_turnout,
        "unemployment_rate": unemployment_rate,
        "population": population,
        "region_northern": 0,
        "region_southern": 0,
        "region_western": 0,
    }

    response = requests.post(f"{BASE_URL}/ml/turnout-prediction", json=payload)

    if response.status_code == 200:
        result = response.json()
        predicted = result.get("predictedTurnout")
        st.success(f"Predicted EU Election Turnout for **{country_name}**: **{predicted:.1f}%**")
    else:
        st.error("Something went wrong with the prediction. Please try again.")
