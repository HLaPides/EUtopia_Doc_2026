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

st.write('### How would you rate your trust in your national parliament?')
nat_parliament_trust = st.radio(
        label="",
        options= ["1 - Very Low", "2 - Low-Neutral", "3 - Neutral-High", "4 - Very High"],
        key="nat_parliament_trust",
        label_visibility="collapsed"
)

st.write('### How would you rate your trust in politicians?')
politician_trust = st.radio(
        label="",
        options= ["1 - Very Low", "2 - Low-Neutral", "3 - Neutral-High", "4 - Very High"],
        key="politician_trust",
        label_visibility="collapsed"
)

st.write('#### How satisfied are you with democracy?')
democracy_satisfaction = st.radio(
    label="",
    options= ["1 - Very Low", "2 - Low-Neutral", "3 - Neutral-High", "4 - Very High"],
    key="democracy_satisfaction",
    label_visibility="collapsed"
)

st.write('### Where do you place yourself on the political spectrum?')
political_affiliation = st.slider(
    label="Political Orientation:",
    min_value=1,
    max_value=10,
    value=5,
    step=1,
    format="%d",
    key="political_affiliation",
    help="1 = Far Left, 10 = Far Right"
)
st.caption("1 = Far Left | 10 = Far Right")


if st.button("Submit Survey", type="primary", use_container_width=True):
    if not level_of_edu:
        st.warning("Please fill in all fields before submitting.")
    else:
        trust_politicians_converted = 1 if int(politician_trust[0]) <= 2 else 2
        democracy_converted = 1 if int(democracy_satisfaction[0]) <= 2 else 2
        trust_national_parliament_converted = 1 if int(nat_parliament_trust[0]) <= 2 else 2

        # map education to numeric
        edu_map = {"Middle School": 1, "High School": 2, "Bachelor's": 3, "Master's": 4, "Doctorate": 5}
        edu_numeric = edu_map.get(level_of_edu, 2)

        # call model
        ml_payload = {
            "education": edu_numeric,
            "trust_parliament": trust_national_parliament_converted,
            "trust_politicians": trust_politicians_converted,
            "satisfaction_democracy": democracy_converted,
            "left_right": political_affiliation
        }
        ml_response = requests.post(f"{BASE_URL}/ml/trust-prediction", json=ml_payload)
        predicted_trust = ml_response.json().get("prediction") if ml_response.status_code == 200 else None

        # save survey
        payload = {
            "studentID": st.session_state['userID'],
            "educationLevel": level_of_edu,
            "leftRight": political_affiliation,
            "trustPoliticians": trust_politicians_converted,
            "democracySatisfaction": democracy_converted,
            "predictedTrust": predicted_trust
        }

        response = requests.post(f"{BASE_URL}/surveys", json=payload)

        if response.status_code == 201:
            if predicted_trust == 0:
                st.success("✅ Based on your responses, you are predicted to **trust** the EU.")
            else:
                st.error("❌ Based on your responses, you are predicted to **not trust** the EU.")
        else:
            st.error("Something went wrong. Please try again.") 