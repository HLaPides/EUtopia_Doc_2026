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

student_id = st.session_state['userID']
simulations = requests.get(f"{BASE_URL}/simulations/{student_id}").json()


# set the header of the page
st.header('Build Your Own Country')

# You can access the session state to make a more customized/personalized app experience
st.write('### Fill in the values to predict EU Election Turnout for your created country')

tab1, tab2, tab3 = st.tabs(["Guided Simulation", "Custom Simulation", "Your Simulations"])

#tab1 will be what Gerber said where each input is presented one at a time, more teaching than exploration
with tab1:
    steps = [
        {
            "key": "g_country_name",
            "label": "Name your Country",
            "description": "placeholder",
            "type": "text"
        },
        {
            "key": "g_population",
            "label": "Population",
            "description": "placeholder",
            "type": "number",
            "default": 5000000,
            "step": 1000
        },
        {
            "key": "g_median_age",
            "label": "Median Age",
            "description": "placeholder",
            "type": "number",
            "default": 40,
            "min": 18
        },
        {
            "key": "g_unemployment_rate",
            "label": "Unemployment Rate (%)",
            "description": "placeholder",
            "type": "slider",
            "default": 10,
            "min": 0,
            "max": 100
        },
        {
            "key": "g_compulsory_voting",
            "label": "Compulsory Voting",
            "description": "placeholder",
            "type": "radio",
            "options": ["Yes", "No"]
        },
        {
            "key": "g_region",
            "label": "Region",
            "description": "placeholder",
            "type": "selectbox",
            "options": ["Northern", "Southern", "Western", "Eastern"]
        },
        {
            "key": "g_nat_election_turnout",
            "label": "National Election Turnout (%)",
            "description": "placeholder",
            "type": "slider",
            "default": 60,
            "min": 0,
            "max": 100
        },
    ]

    if "guided_step" not in st.session_state:
        st.session_state["guided_step"] = 0

    step = st.session_state["guided_step"]
    total_steps = len(steps)
    current = steps[step]

    st.progress((step) / total_steps, text=f"Step {step + 1} of {total_steps}")
    st.write(f"### {current['label']}")
    st.write(current["description"])

    key = current["key"]
    if current["type"] == "text":
        st.text_input(
            label=current["label"],
            placeholder="Enter name...",
            key=key,
            label_visibility="collapsed"
        )
    elif current["type"] == "number":
        st.number_input(
            label=current["label"],
            value=current.get("default", 0),
            min_value=current.get("min", 0),
            step=current.get("step", 1),
            key=key,
            label_visibility="collapsed"
        )
    elif current["type"] == "slider":
        st.slider(
            label=current["label"],
            min_value=current.get("min", 0),
            max_value=current.get("max", 100),
            value=current.get("default", 50),
            key=key,
            label_visibility="collapsed"
        )
    elif current["type"] == "radio":
        st.radio(
            label=current["label"],
            options=current["options"],
            key=key,
            label_visibility="collapsed"
        )
    elif current["type"] == "selectbox":
        st.selectbox(
            label=current["label"],
            options=current["options"],
            key=key,
            label_visibility="collapsed"
        )

    col_back, col_spacer, col_next = st.columns([1, 4, 1])

    with col_back:
        if step > 0:
            if st.button("← Back", use_container_width=True):
                st.session_state["guided_step"] -= 1
                st.rerun()

    with col_next:
        if step < total_steps - 1:
            if st.button("Next →", type="primary", use_container_width=True):
                st.session_state["guided_step"] += 1
                st.rerun()
        else:
            if st.button("Predict →", type="primary", use_container_width=True):
                region_val = st.session_state.get("g_region", "Eastern")
                payload = {
                    "compulsory_voting": 1 if st.session_state.get("g_compulsory_voting") == "Yes" else 0,
                    "median_age": st.session_state.get("g_median_age", 40),
                    "national_turnout": st.session_state.get("g_nat_election_turnout", 60),
                    "unemployment_rate": st.session_state.get("g_unemployment_rate", 10),
                    "population": st.session_state.get("g_population", 5000000),
                    "region_northern": 1 if region_val == "Northern" else 0,
                    "region_southern": 1 if region_val == "Southern" else 0,
                    "region_western": 1 if region_val == "Western" else 0,
                }

                response = requests.post(f"{BASE_URL}/ml/turnout-prediction", json=payload)

                if response.status_code == 200:
                    result = response.json()
                    predicted = result.get("predictedTurnout")
                    country = st.session_state.get("g_country_name", "Your Country")
                    st.success(f"Predicted EU Election Turnout for **{country}**: **{predicted:.1f}%**")

                    sim_payload = {
                        "studentID": student_id,
                        "countryName": country,
                        "population": st.session_state.get("g_population"),
                        "unemploymentRate": st.session_state.get("g_unemployment_rate"),
                        "compulsoryVoting": st.session_state.get("g_compulsory_voting") == "Yes",
                        "medianAge": st.session_state.get("g_median_age"),
                        "region": region_val,
                        "nationalTurnout": st.session_state.get("g_nat_election_turnout"),
                        "predictedTurnout": predicted,
                    }
                    requests.post(f"{BASE_URL}/simulations", json=sim_payload)
                    st.session_state["guided_step"] = 0
                else:
                    st.error("Something went wrong. Please try again.")

#User can fill in all values in a single screen (selecting a country profile to use as base w.i.p)
with tab2:
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
        population = st.number_input(
            label='Population:',
            value = 5000000,
            step=1000,
            key="population",
            help="The total population of the country."
        )

    col5, col6 = st.columns(2)

    with col5:
        median_age = st.number_input(
            label='Median Age:',
            min_value = 18,
            value = 46,
            key="median_age",
            help="Median age of the country's population"
        )

    with col6:
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

    col9, col10 = st.columns(2)

    with col9:
        compulsory_voting = st.radio(
            label='Compulsory Voting:',
            options= ["Yes", "No"],
            key="compulsory_voting",
            help="Is voting mandatory for eligible citizens in the country?"
        )

    with col10:
        region = st.selectbox(
            label="Country Region",
            options=["Northern", "Southern", "Western", "Eastern"],
            key="region",
            help="What region in Europe is your country located?"
        )

    col11, col12 = st.columns(2)

    with col11:
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
            "region_northern": 1 if region == "Northern" else 0,
            "region_southern": 1 if region == "Southern" else 0,
            "region_western": 1 if region == "Western" else 0,
        }

        response = requests.post(f"{BASE_URL}/ml/turnout-prediction", json=payload)

        if response.status_code == 200:
            result = response.json()
            predicted = result.get("predicted_turnout")
            similar = result.get("similar_country")
            similar_turnout = result.get("similar_country_turnout")
        
            st.success(f"Predicted EU Election Turnout for **{country_name}**: **{predicted:.1f}%**")
            st.info(f"Your country most closely resembles **{similar}**, which had a voter turnout of **{similar_turnout}%**")
        else:
            st.error("Something went wrong with the prediction. Please try again.")
            st.write(response.status_code)
            st.write(response.text)

#User can see their past simulations
with tab3:
    if simulations:
        st.write("### Your Past Simulations")
        for sim in simulations:
            with st.expander(f"🌍 {sim.get('countryName', 'Unknown')}"):
                col1, col2, col3 = st.columns(3)
                col1.metric("Predicted Turnout", f"{sim.get('predictedTurnout', 'N/A')}%")
                col2.metric("National Turnout", f"{sim.get('nationalTurnout', 'N/A')}%")
                col3.metric("Unemployment Rate", f"{sim.get('unemploymentRate', 'N/A')}%")

                col4, col5, col6 = st.columns(3)
                col4.metric("Population", f"{sim.get('population', 'N/A'):,}")
                col5.metric("Median Age", sim.get('medianAge', 'N/A'))
                col6.metric("Region", sim.get('region', 'N/A'))

                st.write(f"**Compulsory Voting:** {'Yes' if sim.get('compulsoryVoting') else 'No'}")
    else:
        st.write("You haven't run any simulations yet. Try the Custom Simulation tab!")