import logging
logger = logging.getLogger(__name__)

import pandas as pd
import streamlit as st
import requests
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

BASE_URL = "http://web-api:4000"
student_id = st.session_state['userID']
simulations = requests.get(f"{BASE_URL}/simulations/{student_id}").json()

st.header('Build Your Own Country')
st.write('### Fill in the values to predict EU Election Turnout for your created country')

TABLE_STYLES = [
    {'selector': 'table', 'props': [('width', '100%'), ('border-collapse', 'collapse')]},
    {'selector': 'th', 'props': [('background-color', '#1a1a2e'), ('color', 'white'), ('padding', '10px'), ('text-align', 'center')]},
    {'selector': 'td', 'props': [('padding', '8px 12px'), ('text-align', 'center')]},
    {'selector': 'tr:nth-child(even)', 'props': [('background-color', '#f5f5f5')]},
]

st.markdown("""
<style>
    table { width: 100% !important; }
</style>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["Guided Simulation", "Custom Simulation", "Your Simulations"])


COUNTRY_NAMES = {
    'AT': 'Austria', 'BE': 'Belgium', 'BG': 'Bulgaria',
    'CY': 'Cyprus', 'CZ': 'Czechia', 'DE': 'Germany',
    'DK': 'Denmark', 'EE': 'Estonia', 'ES': 'Spain',
    'FI': 'Finland', 'FR': 'France', 'HR': 'Croatia',
    'HU': 'Hungary', 'IE': 'Ireland', 'IT': 'Italy',
    'LT': 'Lithuania', 'LU': 'Luxembourg', 'LV': 'Latvia',
    'MT': 'Malta', 'NL': 'Netherlands', 'PL': 'Poland',
    'PT': 'Portugal', 'RO': 'Romania', 'SE': 'Sweden',
    'SI': 'Slovenia', 'SK': 'Slovakia', 'EL': 'Greece',
}


def make_steps(prefix):
    return [
        {
            "key": f"{prefix}_country_name",
            "label": "Name your Country",
            "description": "Every country needs a name. This is how your simulation will be saved.",
            "type": "text"
        },
        {
            "key": f"{prefix}_population",
            "label": "Population",
            "description": "Population size shapes how electoral systems are designed and how turnout is measured.",
            "type": "number",
            "default": 5000000,
            "min": 1,
            "step": 1000
        },
        {
            "key": f"{prefix}_median_age",
            "label": "Median Age",
            "description": "Older populations often vote at higher rates than younger populations.",
            "type": "number",
            "default": 40,
            "min": 18,
            "step": 1
        },
        {
            "key": f"{prefix}_unemployment_rate",
            "label": "Unemployment Rate (%)",
            "description": "Economic conditions can affect political participation and trust.",
            "type": "slider",
            "default": 10,
            "min": 0,
            "max": 100
        },
        {
            "key": f"{prefix}_compulsory_voting",
            "label": "Compulsory Voting",
            "description": "Countries with mandatory voting often have higher turnout.",
            "type": "radio",
            "options": ["Yes", "No"]
        },
        {
            "key": f"{prefix}_region",
            "label": "Region",
            "description": "Region helps the model account for broad voting patterns across Europe.",
            "type": "selectbox",
            "options": ["Northern", "Southern", "Western", "Eastern"]
        },
        {
            "key": f"{prefix}_nat_election_turnout",
            "label": "National Election Turnout (%)",
            "description": "Countries with higher national election turnout often have higher EU election turnout too.",
            "type": "slider",
            "default": 60,
            "min": 0,
            "max": 100
        },
    ]


def run_step_simulation(prefix, step_key):
    steps = make_steps(prefix)

    if step_key not in st.session_state:
        st.session_state[step_key] = 0

    step = st.session_state[step_key]
    total_steps = len(steps)
    current = steps[step]
    key = current["key"]

    if key not in st.session_state and "default" in current:
        st.session_state[key] = current["default"]

    st.progress((step + 1) / total_steps, text=f"Step {step + 1} of {total_steps}")
    st.write(f"### {current['label']}")
    st.write(current["description"])

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
            min_value=current.get("min", 0),
            step=current.get("step", 1),
            value=int(st.session_state.get(key, current.get("default", 0))),
            key=key,
            label_visibility="collapsed"
        )

    elif current["type"] == "slider":
        st.slider(
            label=current["label"],
            min_value=current.get("min", 0),
            max_value=current.get("max", 100),
            value=int(st.session_state.get(key, current.get("default", 50))),
            key=key,
            label_visibility="collapsed"
        )

    elif current["type"] == "radio":
        options = current["options"]
        current_value = st.session_state.get(key, options[0])
        st.radio(
            label=current["label"],
            options=options,
            index=options.index(current_value),
            key=key,
            label_visibility="collapsed"
        )

    elif current["type"] == "selectbox":
        options = current["options"]
        current_value = st.session_state.get(key, options[0])
        st.selectbox(
            label=current["label"],
            options=options,
            index=options.index(current_value),
            key=key,
            label_visibility="collapsed"
        )

    col_back, col_spacer, col_next = st.columns([1, 4, 1])

    with col_back:
        if step > 0:
            if st.button("← Back", use_container_width=True, key=f"{prefix}_back"):
                st.session_state[step_key] -= 1
                st.rerun()

    with col_next:
        if step < total_steps - 1:
            if st.button("Next →", type="primary", use_container_width=True, key=f"{prefix}_next"):
                if key == f"{prefix}_country_name":
                    typed_name = st.session_state.get(key, "").strip()

                    if not typed_name:
                        st.error("Please enter a country name.")
                    else:
                        st.session_state[f"{prefix}_saved_country_name"] = typed_name
                        st.session_state[step_key] += 1
                        st.rerun()
                else:
                    st.session_state[step_key] += 1
                    st.rerun()
        else:
            if st.button("Predict EU Election Turnout", type="primary", use_container_width=True, key=f"{prefix}_predict"):
                region_val = st.session_state.get(f"{prefix}_region", "Eastern")

                payload = {
                    "compulsory_voting": 1 if st.session_state.get(f"{prefix}_compulsory_voting") == "Yes" else 0,
                    "median_age": st.session_state.get(f"{prefix}_median_age"),
                    "national_turnout": st.session_state.get(f"{prefix}_nat_election_turnout"),
                    "unemployment_rate": st.session_state.get(f"{prefix}_unemployment_rate"),
                    "population": st.session_state.get(f"{prefix}_population"),
                    "region_northern": 1 if region_val == "Northern" else 0,
                    "region_southern": 1 if region_val == "Southern" else 0,
                    "region_western": 1 if region_val == "Western" else 0,
                }

                response = requests.post(f"{BASE_URL}/ml/turnout-prediction", json=payload)

                if response.status_code == 200:
                    result = response.json()
                    predicted = result.get("predicted_turnout")
                    similar = result.get("similar_country")
                    similar_turnout = result.get("similar_country_turnout")
                    country = st.session_state.get(f"{prefix}_saved_country_name", "").strip() or st.session_state.get(f"{prefix}_country_name", "").strip() or "Your Country"

                    st.session_state[f"{prefix}_prediction"] = {
                        "predicted": predicted,
                        "similar": similar,
                        "similar_turnout": similar_turnout,
                        "country": country,
                    }

                    sim_payload = {
                        "studentID": student_id,
                        "countryName": country,
                        "population": st.session_state.get(f"{prefix}_population"),
                        "unemploymentRate": st.session_state.get(f"{prefix}_unemployment_rate"),
                        "compulsoryVoting": st.session_state.get(f"{prefix}_compulsory_voting") == "Yes",
                        "medianAge": st.session_state.get(f"{prefix}_median_age"),
                        "region": region_val,
                        "nationalTurnout": st.session_state.get(f"{prefix}_nat_election_turnout"),
                        "predicted_turnout": predicted,
                    }

                    save_response = requests.post(f"{BASE_URL}/simulations", json=sim_payload)

                    if save_response.status_code != 201:
                        st.error("Simulation did not save.")
                        st.write(save_response.status_code)
                        st.write(save_response.text)
                    else:
                        st.success("Simulation saved.")
                    st.rerun()
                else:
                    st.error("Something went wrong. Please try again.")
                    st.write(response.status_code)
                    st.write(response.text)


def show_prediction(prefix, step_key):
    p = st.session_state.get(f"{prefix}_prediction")

    if p:
        predicted = p["predicted"]
        similar = p["similar"]
        similar_turnout = p["similar_turnout"]
        country = p["country"]

        st.write(f"### Results for **{country}**")
        st.divider()

        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Predicted EU Turnout", f"{predicted:.1f}%")
        col_b.metric("Most Similar Country", similar)
        col_c.metric("Their Turnout", f"{similar_turnout}%", delta=f"{predicted - similar_turnout:.1f}%")

        st.divider()

        if st.button("← Try Again", type="primary", key=f"{prefix}_try_again"):
            st.session_state[f"{prefix}_prediction"] = None
            st.session_state[step_key] = 0
            st.rerun()

        return True

    return False


with tab1:
    st.write("### Guided Simulation")
    st.write("Start from a real country profile, then adjust each value one question at a time. Use the default or make your own name!")

    if not show_prediction("g", "guided_step"):
        dataset = requests.get(f"{BASE_URL}/turnout-dataset").json()

        country_profiles = {}
        for row in dataset:
            country_full = COUNTRY_NAMES.get(row["country"], row["country"])
            label = f"{country_full} {row['year']}"

            country_profiles[label] = {
                "country_name": country_full,
                "population": row["population"],
                "median_age": int(float(row["median_age"])),
                "unemployment_rate": round(float(row["unemployment_rate"])),
                "compulsory_voting": "Yes" if row["compulsory_voting"] == 1 else "No",
                "region": (
                    "Northern" if row["region_northern"] == 1 else
                    "Southern" if row["region_southern"] == 1 else
                    "Western" if row["region_western"] == 1 else
                    "Eastern"
                ),
                "nat_election_turnout": round(float(row["national_turnout"])),
            }

        if "guided_profile_loaded" not in st.session_state:
            st.session_state["guided_profile_loaded"] = None

        selected_profile = st.selectbox(
            "Select a country profile:",
            options=["— Select —"] + list(country_profiles.keys()),
            key="guided_country_profile"
        )

        if selected_profile == "— Select —":
            st.info("Choose a country profile to begin.")
        else:
            if st.session_state["guided_profile_loaded"] != selected_profile:
                p = country_profiles[selected_profile]

                if "g_country_name" not in st.session_state:
                    st.session_state["g_country_name"] = p["country_name"]
                st.session_state["g_population"] = int(float(p["population"]))
                st.session_state["g_median_age"] = int(float(p["median_age"]))
                st.session_state["g_unemployment_rate"] = int(round(float(p["unemployment_rate"])))
                st.session_state["g_compulsory_voting"] = p["compulsory_voting"]
                st.session_state["g_region"] = p["region"]
                st.session_state["g_nat_election_turnout"] = int(round(float(p["nat_election_turnout"])))

                st.session_state["guided_step"] = 0
                st.session_state["guided_profile_loaded"] = selected_profile
                st.rerun()

            st.divider()
            run_step_simulation("g", "guided_step")


with tab2:
    st.write("### Custom Simulation")
    st.write("Start from scratch and build your country one question at a time. View your creations in 'Your Simulations.'")

    if "custom_defaults_loaded" not in st.session_state:
        st.session_state["c_country_name"] = ""
        st.session_state["c_population"] = 5000000
        st.session_state["c_median_age"] = 40
        st.session_state["c_unemployment_rate"] = 10
        st.session_state["c_compulsory_voting"] = "No"
        st.session_state["c_region"] = "Eastern"
        st.session_state["c_nat_election_turnout"] = 60
        st.session_state["custom_step"] = 0
        st.session_state["custom_defaults_loaded"] = True

    if not show_prediction("c", "custom_step"):
        run_step_simulation("c", "custom_step")


with tab3:
    simulations = requests.get(f"{BASE_URL}/simulations/{student_id}").json()

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