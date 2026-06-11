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
        if col == "Country" or col == "Compulsory Voting":
            continue
        elif col == "Population":
            df[col] = df[col].apply(lambda x: f"{int(float(x)):,}" if x not in ("nan", "") else x)
        elif col == "National Turnout":
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


def show_turnout_heatmap():
    turnout_2024 = {
        'Belgium':     89.0, 'Luxembourg':  84.1, 'Malta':       72.8,
        'Italy':       49.7, 'Denmark':     58.7, 'Germany':     64.8,
        'Austria':     59.6, 'Sweden':      54.5, 'Ireland':     50.0,
        'Netherlands': 46.0, 'France':      51.5, 'Spain':       49.2,
        'Portugal':    36.4, 'Greece':      41.8, 'Finland':     40.0,
        'Czechia':     36.5, 'Romania':     32.4, 'Hungary':     43.0,
        'Poland':      40.7, 'Slovakia':    27.2, 'Bulgaria':    33.7,
        'Croatia':     21.4, 'Slovenia':    42.6, 'Estonia':     37.6,
        'Latvia':      33.4, 'Lithuania':   28.3, 'Cyprus':      44.9,
    }
    df_map = px.data.gapminder().query("year == 2007 and continent == 'Europe'")[['country', 'iso_alpha']].copy()
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
    import pandas as pd
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
    st.plotly_chart(fig, use_container_width=True)

# ── Tab 1: Guided Simulation ──────────────────────────────────────────────────
with tab1:
    if "guided_step" not in st.session_state:
        st.session_state["guided_step"] = 0

    if st.session_state.get("guided_prediction"):
        p = st.session_state["guided_prediction"]

        st.write(f"### Results for **{p['country']}**")
        st.divider()

        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Predicted EU Turnout", f"{p['predicted']:.1f}%")
        col_b.metric("Most Similar Country", p['similar'])
        col_c.metric("Their Turnout", f"{p['similar_turnout']}%", delta=f"{p['predicted'] - p['similar_turnout']:.1f}%")

        st.divider()
        show_comparison(p.get("comparison"), p.get("country", "Your Country"))
        st.divider()
        show_turnout_heatmap()
        st.divider()

        if st.button("← Try Again", type="primary"):
            st.session_state["guided_prediction"] = None
            st.session_state["guided_step"] = 0
            st.rerun()
    else:
        steps = [
            {
                "key": "g_country_name",
                "label": "Name your Country",
                "description": "Every country needs a name! This is your chance to get creative. The name won't affect the prediction, it's just how your simulation will be saved and identified.",
                "type": "text"
            },
            {
                "key": "g_population",
                "label": "Population",
                "description": "Population size shapes how electoral systems are designed and how voter turnout is measured. Larger countries often have more diverse populations and complex political landscapes, which can affect how engaged citizens feel. In the EU, populations range from about 500,000 in Malta to over 80 million in Germany.",
                "type": "number",
                "default": 5000000,
                "step": 1000
            },
            {
                "key": "g_median_age",
                "label": "Median Age",
                "description": "The median age of a population is one of the strongest predictors of voter turnout. Older populations tend to vote at significantly higher rates than younger ones, older citizens often feel more invested in political outcomes and have more stable voting habits. The EU average median age is around 44 years.",
                "type": "number",
                "default": 40,
                "min": 0
            },
            {
                "key": "g_unemployment_rate",
                "label": "Unemployment Rate (%)",
                "description": "Economic conditions have a complex relationship with political participation. High unemployment can discourage civic engagement when people feel the system isn't working for them, but it can also mobilize voters who want change. The EU average unemployment rate has historically ranged between 5% and 12%.",
                "type": "slider",
                "default": 10,
                "min": 0,
                "max": 100
            },
            {
                "key": "g_compulsory_voting",
                "label": "Compulsory Voting",
                "description": "In some countries, voting is legally required for eligible citizens. Belgium and Luxembourg are the only EU countries that meaningfully enforce compulsory voting laws, and both consistently have some of the highest turnout rates in Europe, often above 85%. Making voting optional tends to lower participation significantly.",
                "type": "radio",
                "options": ["Yes", "No"]
            },
            {
                "key": "g_region",
                "label": "Region",
                "description": "Where a country is located in Europe has a strong effect on EU election turnout, even after accounting for other factors. Western European countries average around 20 percentage points higher turnout than Eastern European ones.",
                "type": "selectbox",
                "options": ["Northern", "Southern", "Western", "Eastern"]
            },
            {
                "key": "g_nat_election_turnout",
                "label": "National Election Turnout (%)",
                "description": "Countries where citizens regularly participate in national elections also tend to vote more in EU elections. National turnout in EU countries ranges widely, from around 35% in some Eastern European countries to over 90% in Belgium.",
                "type": "slider",
                "default": 60,
                "min": 0,
                "max": 100
            },
        ]

        step = st.session_state["guided_step"]
        total_steps = len(steps)
        current = steps[step]

        st.progress((step) / total_steps, text=f"Step {step + 1} of {total_steps}")
        st.write(f"### {current['label']}")
        st.write(current["description"])

        key = current["key"]
        if current["type"] == "text":
            st.text_input(label=current["label"], placeholder="Enter name...", key=key, label_visibility="collapsed")
        elif current["type"] == "number":
            st.number_input(label=current["label"], value=current.get("default", 0), min_value=current.get("min", 0), step=current.get("step", 1), key=key, label_visibility="collapsed")
        elif current["type"] == "slider":
            st.slider(label=current["label"], min_value=current.get("min", 0), max_value=current.get("max", 100), value=current.get("default", 50), key=key, label_visibility="collapsed")
        elif current["type"] == "radio":
            st.radio(label=current["label"], options=current["options"], key=key, label_visibility="collapsed")
        elif current["type"] == "selectbox":
            st.selectbox(label=current["label"], options=current["options"], key=key, label_visibility="collapsed")

        col_back, col_spacer, col_next = st.columns([1, 4, 1])

        with col_back:
            if step > 0:
                if st.button("← Back", use_container_width=True):
                    st.session_state["guided_step"] -= 1
                    st.rerun()

        with col_next:
            if step < total_steps - 1:
                if st.button("Next →", type="primary", use_container_width=True):
                    valid = True
                    if current["key"] == "g_median_age" and st.session_state.get("g_median_age", 0) < 18:
                        st.error("Median age must be at least 18.")
                        valid = False
                    if current["key"] == "g_population" and st.session_state.get("g_population", 0) <= 0:
                        st.error("Population must be greater than 0.")
                        valid = False
                    if current["key"] == "g_country_name" and not st.session_state.get("g_country_name", "").strip():
                        st.error("Please enter a country name.")
                        valid = False
                    if valid:
                        if current["key"] == "g_country_name":
                            st.session_state["_saved_country_name"] = st.session_state.get("g_country_name", "")
                        st.session_state["guided_step"] += 1
                        st.rerun()
            else:
                if st.button("Predict EU Election Turnout", type="primary"):
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
                        st.session_state["guided_prediction"] = {
                            "predicted": result.get("predicted_turnout"),
                            "similar": result.get("similar_country"),
                            "similar_turnout": result.get("similar_country_turnout"),
                            "country": st.session_state.get("_saved_country_name", "Your Country"),
                            "comparison": result.get("comparison"),
                        }
                        sim_payload = {
                            "studentID": student_id,
                            "countryName": st.session_state.get("_saved_country_name", "Your Country"),
                            "population": st.session_state.get("g_population"),
                            "unemploymentRate": st.session_state.get("g_unemployment_rate"),
                            "compulsoryVoting": st.session_state.get("g_compulsory_voting") == "Yes",
                            "medianAge": st.session_state.get("g_median_age"),
                            "region": region_val,
                            "nationalTurnout": st.session_state.get("g_nat_election_turnout"),
                            "predicted_turnout": result.get("predicted_turnout"),
                        }
                        requests.post(f"{BASE_URL}/simulations", json=sim_payload)
                        st.rerun()
                    else:
                        st.error("Something went wrong. Please try again.")


# ── Tab 2: Custom Simulation ──────────────────────────────────────────────────
with tab2:
    if "tab2_mode" not in st.session_state:
        st.session_state["tab2_mode"] = None
        st.session_state["_last_profile"] = None

    if st.session_state["tab2_mode"] is None:
        st.write("### How would you like to start?")
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("🌍\n\n**Start from a Real Country**\n\nPick a real EU country and year as your starting point, then customize from there.", use_container_width=True, type="primary", key="btn_profile"):
                st.session_state["tab2_mode"] = "profile"
                st.rerun()
        with col_b:
            if st.button("✏️\n\n**Build from Scratch**\n\nSet every value yourself and create a completely custom country.", use_container_width=True, type="primary", key="btn_custom"):
                st.session_state["tab2_mode"] = "custom"
                st.session_state["population"] = 5000000
                st.session_state["median_age"] = 46
                st.session_state["unemployment_rate"] = 24
                st.session_state["compulsory_voting"] = "No"
                st.session_state["region"] = "Eastern"
                st.session_state["nat_election_turnout"] = 45
                st.rerun()
    else:
        if st.button("← Start Over", key="tab2_reset"):
            st.session_state["tab2_mode"] = None
            st.session_state["_last_profile"] = None
            st.rerun()

        if st.session_state["tab2_mode"] == "profile":
            dataset = requests.get(f"{BASE_URL}/turnout-dataset").json()
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
            country_profiles = {}
            for row in dataset:
                country_full = COUNTRY_NAMES.get(row['country'], row['country'])
                label = f"{country_full} {row['year']}"
                country_profiles[label] = {
                    "country_name": country_full,
                    "population": row["population"],
                    "median_age": float(row["median_age"]),
                    "unemployment_rate": round(float(row["unemployment_rate"])),
                    "compulsory_voting": "Yes" if row["compulsory_voting"] == 1 else "No",
                    "region": (
                        "Northern" if row["region_northern"] == 1 else
                        "Southern" if row["region_southern"] == 1 else
                        "Western"  if row["region_western"]  == 1 else
                        "Eastern"
                    ),
                    "nat_election_turnout": round(float(row["national_turnout"])),
                }
            selected_profile = st.selectbox("Select a country profile:", options=["— Select —"] + list(country_profiles.keys()), key="country_profile")
            if selected_profile != "— Select —":
                if st.session_state.get("_last_profile") != selected_profile:
                    p = country_profiles[selected_profile]
                    st.session_state["_last_profile"] = selected_profile
                    st.session_state["country_name"] = p["country_name"]
                    st.session_state["population"] = p["population"]
                    st.session_state["median_age"] = int(p["median_age"])
                    st.session_state["unemployment_rate"] = p["unemployment_rate"]
                    st.session_state["compulsory_voting"] = p["compulsory_voting"]
                    st.session_state["region"] = p["region"]
                    st.session_state["nat_election_turnout"] = p["nat_election_turnout"]
                    st.rerun()

        show_inputs = (
            st.session_state["tab2_mode"] == "custom" or
            (st.session_state["tab2_mode"] == "profile" and st.session_state.get("_last_profile") is not None)
        )

        if show_inputs:
            st.divider()
            col1, col2 = st.columns(2)
            with col1:
                country_name = st.text_input(label='Name your Country:', placeholder="Country Name", key="country_name", help="Give your made up country a unique name.")
            with col2:
                population = st.number_input(label='Population:', step=1000, value=5000000, key="population", help="The total population of the country.")

            col3, col4 = st.columns(2)
            with col3:
                median_age = st.number_input(label='Median Age:', min_value=18, value=46, key="median_age", help="Median age of the country's population")
            with col4:
                unemployment_rate = st.slider(label='Unemployment Rate:', min_value=0, max_value=100, value=24, step=1, key="unemployment_rate", help="Rate of unemployment")

            col5, col6 = st.columns(2)
            with col5:
                compulsory_voting = st.radio(label='Compulsory Voting:', options=["Yes", "No"], index=1, key="compulsory_voting", help="Is voting mandatory for eligible citizens?")
            with col6:
                region = st.selectbox(label="Country Region:", options=["Northern", "Southern", "Western", "Eastern"], index=3, key="region", help="What region in Europe is your country located?")

            nat_election_turnout = st.slider(label='National Election Turnout:', min_value=0, max_value=100, value=45, step=1, key="nat_election_turnout", help="The election turnout of voters for national votes.")

            if st.button("Predict EU Election Turnout", type='primary', use_container_width=True):
                payload = {
                    "compulsory_voting": 1 if compulsory_voting == "Yes" else 0,
                    "median_age": median_age,
                    "national_turnout": nat_election_turnout,
                    "unemployment_rate": unemployment_rate,
                    "population": population,
                    "region_northern": 1 if region == "Northern" else 0,
                    "region_southern": 1 if region == "Southern" else 0,
                    "region_western":  1 if region == "Western"  else 0,
                }
                response = requests.post(f"{BASE_URL}/ml/turnout-prediction", json=payload)
                if response.status_code == 200:
                    result = response.json()
                    st.session_state["tab2_prediction"] = {
                        "predicted": result.get("predicted_turnout"),
                        "similar": result.get("similar_country"),
                        "similar_turnout": result.get("similar_country_turnout"),
                        "country": country_name or st.session_state.get("_last_profile", "Your Country"),
                        "comparison": result.get("comparison"),
                    }
                    sim_payload = {
                        "studentID": student_id,
                        "countryName": country_name or st.session_state.get("_last_profile", "Custom"),
                        "population": population,
                        "unemploymentRate": unemployment_rate,
                        "compulsoryVoting": compulsory_voting == "Yes",
                        "medianAge": median_age,
                        "region": region,
                        "nationalTurnout": nat_election_turnout,
                        "predicted_turnout": result.get("predicted_turnout"),
                    }
                    requests.post(f"{BASE_URL}/simulations", json=sim_payload)
                else:
                    st.session_state["tab2_prediction"] = None
                    st.error("Something went wrong. Please try again.")

            if st.session_state.get("tab2_prediction"):
                p = st.session_state["tab2_prediction"]
                st.divider()
                st.write(f"### Results for **{p['country']}**")
                col_a, col_b, col_c = st.columns(3)
                col_a.metric("Predicted EU Turnout", f"{p['predicted']:.1f}%")
                col_b.metric("Most Similar Country", p['similar'])
                col_c.metric("Their Turnout", f"{p['similar_turnout']}%", delta=f"{p['predicted'] - p['similar_turnout']:.1f}%")
                st.divider()
                show_comparison(p.get("comparison"), p.get("country", "Your Country"))
                st.divider()
                show_turnout_heatmap()


# ── Tab 3: Your Simulations ───────────────────────────────────────────────────
with tab3:
    if simulations:
        st.write("### Your Past Simulations")
        for sim in simulations:
            with st.expander(f"🌍 {sim.get('countryName', 'Unknown')}"):
                col1, col2, col3 = st.columns(3)
                col1.metric("Predicted Turnout", f"{sim.get('predicted_turnout', 'N/A')}%")
                col2.metric("National Turnout", f"{sim.get('nationalTurnout', 'N/A')}%")
                col3.metric("Unemployment Rate", f"{sim.get('unemploymentRate', 'N/A')}%")

                col4, col5, col6 = st.columns(3)
                col4.metric("Population", f"{sim.get('population', 'N/A'):,}")
                col5.metric("Median Age", sim.get('medianAge', 'N/A'))
                col6.metric("Region", sim.get('region', 'N/A'))

                st.write(f"**Compulsory Voting:** {'Yes' if sim.get('compulsoryVoting') else 'No'}")
    else:
        st.write("You haven't run any simulations yet. Try the Custom Simulation tab!")