import logging
logger = logging.getLogger(__name__)

import pandas as pd
import streamlit as st
import requests
import plotly.express as px
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


def show_comparison(comparison: dict, country_name: str = "Your Country"):
    if not comparison:
        return
    st.subheader("Feature Comparison")
    df = pd.DataFrame(comparison).T.copy()
    df.index = df.index.map(lambda x: country_name if x == "input" else x)
    df.index.name = "Country"
    df = df.reset_index()
    df = df.astype(str)
    for col in df.columns:
        if col in ("Country", "Compulsory Voting"):
            continue
        elif col == "Population":
            df[col] = df[col].apply(lambda x: f"{int(float(x)):,}" if x not in ("nan", "") else x)
        elif col == "National Turnout %":
            df[col] = df[col].apply(lambda x: f"{float(x):.2f}%" if x not in ("nan", "") else x)
        else:
            df[col] = df[col].apply(lambda x: f"{float(x):.2f}" if x not in ("nan", "") else x)
    st.markdown(
        df.style
        .set_table_styles(TABLE_STYLES)
        .hide(axis='index')
        .to_html(),
        unsafe_allow_html=True
    )


def show_turnout_heatmap(key: str = "heatmap"):
    turnout_2024 = {
        'Belgium': 89.0, 'Luxembourg': 84.1, 'Malta': 72.8,
        'Italy': 49.7, 'Denmark': 58.7, 'Germany': 64.8,
        'Austria': 59.6, 'Sweden': 54.5, 'Ireland': 50.0,
        'Netherlands': 46.0, 'France': 51.5, 'Spain': 49.2,
        'Portugal': 36.4, 'Greece': 41.8, 'Finland': 40.0,
        'Czechia': 36.5, 'Romania': 32.4, 'Hungary': 43.0,
        'Poland': 40.7, 'Slovakia': 27.2, 'Bulgaria': 33.7,
        'Croatia': 21.4, 'Slovenia': 42.6, 'Estonia': 37.6,
        'Latvia': 33.4, 'Lithuania': 28.3, 'Cyprus': 44.9,
    }
    country_to_iso = {
        'Belgium': 'BEL', 'Luxembourg': 'LUX', 'Malta': 'MLT',
        'Italy': 'ITA', 'Denmark': 'DNK', 'Germany': 'DEU',
        'Austria': 'AUT', 'Sweden': 'SWE', 'Ireland': 'IRL',
        'Netherlands': 'NLD', 'France': 'FRA', 'Spain': 'ESP',
        'Portugal': 'PRT', 'Greece': 'GRC', 'Finland': 'FIN',
        'Czechia': 'CZE', 'Romania': 'ROU', 'Hungary': 'HUN',
        'Poland': 'POL', 'Slovakia': 'SVK', 'Bulgaria': 'BGR',
        'Croatia': 'HRV', 'Slovenia': 'SVN', 'Estonia': 'EST',
        'Latvia': 'LVA', 'Lithuania': 'LTU', 'Cyprus': 'CYP',
    }
    df_map = pd.DataFrame([
        {'country': k, 'iso_alpha': country_to_iso[k], 'turnout': v}
        for k, v in turnout_2024.items()
    ])
    fig = px.choropleth(
        df_map,
        locations='iso_alpha',
        color='turnout',
        hover_name='country',
        hover_data={'turnout': ':.1f', 'iso_alpha': False},
        color_continuous_scale='Blues',
        range_color=[20, 90],
        scope='europe',
        title='2024 EU Parliamentary Election Voter Turnout (%)',
        labels={'turnout': 'Turnout (%)'},
    )
    fig.update_layout(
        margin=dict(l=0, r=0, t=40, b=0),
        height=600,
        coloraxis_colorbar=dict(title='Turnout %'),
        geo=dict(
            showcoastlines=True,
            coastlinecolor='white',
            showland=True,
            landcolor='lightgray',
            showframe=False,
            lonaxis=dict(range=[-25, 45]),
            lataxis=dict(range=[34, 72]),
        )
    )
    st.plotly_chart(fig, use_container_width=True, key=key)


def make_steps(prefix):
    return [
        {
            "key": f"{prefix}_country_name",
            "label": "Name your Country",
            "description": "Every country needs a name! This is your chance to get creative. The name won't affect the prediction, it's just how your simulation will be saved and identified.",
            "type": "text"
        },
        {
            "key": f"{prefix}_population",
            "label": "Population",
            "description": "Population size shapes how electoral systems are designed and how voter turnout is measured. Larger countries often have more diverse populations and complex political landscapes, which can affect how engaged citizens feel. In the EU, populations range from about 500,000 in Malta to over 80 million in Germany.",
            "type": "number",
            "default": 5000000,
            "min": 1,
            "step": 1000
        },
        {
            "key": f"{prefix}_median_age",
            "label": "Median Age",
            "description": "The median age of a population is one of the strongest predictors of voter turnout. Older populations tend to vote at significantly higher rates than younger ones, older citizens often feel more invested in political outcomes and have more stable voting habits. The EU average median age is around 44 years.",
            "type": "number",
            "default": 40,
            "min": 0,
            "step": 1
        },
        {
            "key": f"{prefix}_unemployment_rate",
            "label": "Unemployment Rate (%)",
            "description": "Economic conditions have a complex relationship with political participation. High unemployment can discourage civic engagement when people feel the system isn't working for them, but it can also mobilize voters who want change. The EU average unemployment rate has historically ranged between 5% and 12%.",
            "type": "slider",
            "default": 10,
            "min": 0,
            "max": 100
        },
        {
            "key": f"{prefix}_compulsory_voting",
            "label": "Compulsory Voting",
            "description": "In some countries, voting is legally required for eligible citizens. Belgium and Luxembourg are the only EU countries that meaningfully enforce compulsory voting laws, and both consistently have some of the highest turnout rates in Europe, often above 85%. Making voting optional tends to lower participation significantly.",
            "type": "radio",
            "options": ["Yes", "No"]
        },
        {
            "key": f"{prefix}_region",
            "label": "Region",
            "description": "Where a country is located in Europe has a strong effect on EU election turnout, even after accounting for other factors. Western European countries average around 20 percentage points higher turnout than Eastern European ones. This reflects differences in how long countries have been EU members, historical relationships with democratic institutions, and levels of trust in the European project.",
            "type": "selectbox",
            "options": ["Northern", "Southern", "Western", "Eastern"]
        },
        {
            "key": f"{prefix}_nat_election_turnout",
            "label": "National Election Turnout (%)",
            "description": "Countries where citizens regularly participate in national elections also tend to vote more in EU elections. If people are in the habit of voting domestically, they are more likely to show up for European elections too. National turnout in EU countries ranges widely, from around 35% in some Eastern European countries to over 90% in Belgium.",
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
            if st.button("Next →", type="primary", use_container_width=True):
                # validate current input before moving on
                valid = True
                if current["key"] == "g_median_age":
                    if st.session_state.get("g_median_age", 0) < 18:
                        st.error("Median age must be at least 18.")
                        valid = False
                if current["key"] == "g_population":
                    if st.session_state.get("g_population", 0) <= 0:
                        st.error("Population must be greater than 0.")
                        valid = False
                if current["key"] == "g_country_name":
                    if not st.session_state.get("g_country_name", "").strip():
                        st.error("Please enter a country name.")
                        valid = False
                if valid:
                    st.session_state["guided_step"] += 1
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
                        "comparison": result.get("comparison"),
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
        show_comparison(p.get("comparison"), country)
        st.divider()
        show_turnout_heatmap(key=f"{prefix}_heatmap")
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