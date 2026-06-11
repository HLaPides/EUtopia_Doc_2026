import logging
logger = logging.getLogger(__name__)

import streamlit as st
import pandas as pd
import requests
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

if not st.session_state.get('authenticated'):
    st.switch_page('Home.py')

BASE_URL = "http://web-api:4000"

st.title("Voter Turnout Model")
st.write("Retrain or evaluate the OLS linear regression model that predicts EU parliamentary election voter turnout.")

st.divider()

# ── Test ──────────────────────────────────────────────────────────────────────
st.subheader("Evaluate Model (LOO-CV)")
st.write("Runs leave-one-out cross validation on the full training dataset.")

if st.button("Run LOO-CV Test", type="secondary", use_container_width=True):
    with st.spinner("Running LOO-CV on 184 observations..."):
        try:
            response = requests.get(f"{BASE_URL}/ml/voter-turnout/test")
            result   = response.json()
            col1, col2, col3 = st.columns(3)
            col1.metric("LOO-CV R²",  result.get("loo_cv_r2"))
            col2.metric("LOO-CV MSE", result.get("loo_cv_mse"))
            col3.metric("N",          result.get("n"))
        except Exception as e:
            st.error(f"Error: {e}")

st.divider()

# ── Features ──────────────────────────────────────────────────────────────────
st.subheader("Model Features")

features_info = [
    {
        "Feature":     "Compulsory Voting",
        "Description": "Adds roughly 7 percentage points to predicted turnout.",
    },
    {
        "Feature":     "Median Age",
        "Description": "Older populations vote more, but only up to a point. Turnout rises with age then levels off.",
    },
    {
        "Feature":     "National Turnout",
        "Description": "The strongest predictor in the model. High turnout in national elections carries over to EU elections.",
    },
    {
        "Feature":     "Unemployment Rate",
        "Description": "Higher unemployment reduces voter turnout.",
    },
    {
        "Feature":     "Population",
        "Description": "Larger countries show slightly higher turnout.",
    },
    {
        "Feature":     "Northern Europe",
        "Description": "Northern European countries average about 10 percentage points higher turnout than Eastern Europe.",
    },
    {
        "Feature":     "Southern Europe",
        "Description": "Southern European countries average about 5 percentage points higher turnout than Eastern Europe.",
    },
    {
        "Feature":     "Western Europe",
        "Description": "Western European countries average about 20 percentage points higher turnout than Eastern Europe — the largest regional gap in the model.",
    },
]

df = pd.DataFrame(features_info)

TABLE_STYLES = [
    {'selector': 'table', 'props': [('width', '100%'), ('border-collapse', 'collapse')]},
    {'selector': 'th', 'props': [('background-color', '#1a1a2e'), ('color', 'white'), ('padding', '10px'), ('text-align', 'left')]},
    {'selector': 'td', 'props': [('padding', '8px 12px'), ('text-align', 'left')]},
    {'selector': 'tr:nth-child(even)', 'props': [('background-color', '#f5f5f5')]},
]

st.markdown("""
<style>
    table { width: 100% !important; }
</style>
""", unsafe_allow_html=True)

st.markdown(
    df.style
    .set_table_styles(TABLE_STYLES)
    .hide(axis='index')
    .to_html(),
    unsafe_allow_html=True
)

st.divider()

# ── 2029 Baseline Predictions ─────────────────────────────────────────────────
st.subheader("2029 Baseline Predictions")
st.write("Predicted EU election turnout for all 27 member states using their most recent feature values.")

try:
    dataset = requests.get(f"{BASE_URL}/turnout-dataset").json()

    COUNTRY_NAMES = {
        'AT': 'Austria', 'BE': 'Belgium', 'BG': 'Bulgaria',
        'CY': 'Cyprus', 'CZ': 'Czechia', 'DE': 'Germany',
        'DK': 'Denmark', 'EE': 'Estonia', 'ES': 'Spain',
        'FI': 'Finland', 'FR': 'France', 'GR': 'Greece',
        'HR': 'Croatia', 'HU': 'Hungary', 'IE': 'Ireland',
        'IT': 'Italy', 'LT': 'Lithuania', 'LU': 'Luxembourg',
        'LV': 'Latvia', 'MT': 'Malta', 'NL': 'Netherlands',
        'PL': 'Poland', 'PT': 'Portugal', 'RO': 'Romania',
        'SE': 'Sweden', 'SI': 'Slovenia', 'SK': 'Slovakia',
        'EL': 'Greece',
    }

    # get most recent row per country
    df_all = pd.DataFrame(dataset)
    df_all['year'] = df_all['year'].astype(int)
    df_latest = df_all.sort_values('year', ascending=False).groupby('country').first().reset_index()

    rows = []
    for _, row in df_latest.iterrows():
        payload = {
            "compulsory_voting": int(row['compulsory_voting']),
            "median_age":        float(row['median_age']),
            "national_turnout":  float(row['national_turnout']),
            "unemployment_rate": float(row['unemployment_rate']),
            "population":        float(row['population']),
            "region_northern":   int(row['region_northern']),
            "region_southern":   int(row['region_southern']),
            "region_western":    int(row['region_western']),
        }
        resp = requests.post(f"{BASE_URL}/ml/turnout-prediction", json=payload)
        if resp.status_code == 200:
            predicted = resp.json().get("predicted_turnout")
            rows.append({
                "Country":            COUNTRY_NAMES.get(row['country'], row['country']),
                "Region":             ("Northern" if row['region_northern'] == 1 else
                                        "Southern" if row['region_southern'] == 1 else
                                        "Western"  if row['region_western']  == 1 else
                                        "Eastern"),
                "Predicted Turnout":  f"{predicted:.1f}%",
            })

    df_pred = pd.DataFrame(rows).sort_values("Predicted Turnout", ascending=False).reset_index(drop=True)
    df_pred.index += 1

    st.markdown(
        df_pred.style
        .set_table_styles(TABLE_STYLES)
        .hide(axis='index')
        .to_html(),
        unsafe_allow_html=True
    )

except Exception as e:
    st.error(f"Could not generate predictions: {e}")

st.divider()