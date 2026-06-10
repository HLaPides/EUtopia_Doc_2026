import logging
logger = logging.getLogger(__name__)
import streamlit as st
import pandas as pd
import pydeck as pdk
from urllib.error import URLError
import requests
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

BASE_URL = "http://web-api:4000"

st.header('Welcome to the Diagnostic Survey')
st.write('### Take the survey to determine your trust in EU institutions')

level_of_edu = st.selectbox(
    label="Level of Education:",
    options=["Middle School", "High School", "Bachelor's", "Master's", "Doctorate"],
    key="level_of_edu",
    index=None,
    placeholder="Select Education"
)

political_affiliation = st.selectbox(
    label="Political Affiliation:",
    options=["Liberal", "Conservative", "Socialist", "Green", "Nationalist"],
    key="political_affiliation",
    index=None,
    placeholder="Select Affiliation"
)

st.write('### How would you rate your trust in the European Parliament?')
euro_parliament_trust = st.radio(
        label="",
        options= ["1 - Very Low", "2 - Low - Neutral", "3 - Neutral - High", "4 - Very High"],
        key="pol_interest",
        label_visibility="collapsed"
)

st.write('### How would you rate your trust in your national parliament?')
st.radio(
        label="",
        options= ["1 - Very Low", "2 - Low", "3 - Neutral", "4 - High", "5 - Very High"],
        key="nat_parliament_trust",
        label_visibility="collapsed"
)

st.write('### How would you rate your trust in politicians?')
politician_trust = st.radio(
        label="",
        options= ["1 - Very Low", "2 - Low", "3 - Neutral", "4 - High", "5 - Very High"],
        key="politician_trust",
        label_visibility="collapsed"
)

st.write('#### How satisfied are you with democracy?')
democracy_satisfaction = st.radio(
    label="",
    options= ["1 - Very Low", "2 - Low", "3 - Neutral", "4 - High", "5 - Very High"],
    key="democracy_satisfaction",
    label_visibility="collapsed"
)

if st.button("Submit Survey", type="primary", use_container_width=True):
    if not level_of_edu or not political_affiliation:
        st.warning("Please fill in all fields before submitting.")
    else:
        payload = {
            "studentID": st.session_state['userID'],
            "educationLevel": level_of_edu,
            "politicalAffiliation": political_affiliation,
            "trustEuroParliament": int(euro_parliament_trust[0]),
            "trustPoliticians": int(politician_trust[0]),
            "democracySatisfaction": int(democracy_satisfaction[0]),
        }

        response = requests.post(f"{BASE_URL}/survey", json=payload)

        if response.status_code == 201:
            st.success("Survey submitted successfully!")
        else:
            st.error("Something went wrong. Please try again.")