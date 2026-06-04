import logging
logger = logging.getLogger(__name__)
import streamlit as st
import pandas as pd
import pydeck as pdk
from urllib.error import URLError
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

st.header('Welcome to the Diagnostic Survey')
st.write('### Take the survey to determine your trust in EU institutions')

st.number_input(
    label='Age:',
        value = 22,
        key="age"
)

st.selectbox(
    label="Level of Education:",
    options=["Middle School", "High School", "Bachelor's", "Master's", "Doctorate"],
    key="level_of_edu",
    index=None,
    placeholder="Select Education"
)

st.selectbox(
    label="Gender:",
    options=["Male", "Female", "Non-Binary", "Prefer Not to Say"],
    key="gender",
    index=None,
    placeholder="Select Gender"
)

st.write('### How would you rate your political interest?')
st.radio(
        label="",
        options= ["1 - Very Low", "2 - Low", "3 - Neutral", "4 - High", "5 - Very High"],
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
st.radio(
        label="",
        options= ["1 - Very Low", "2 - Low", "3 - Neutral", "4 - High", "5 - Very High"],
        key="politician_trust",
        label_visibility="collapsed"
)