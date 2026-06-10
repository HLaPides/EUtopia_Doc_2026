import logging
logger = logging.getLogger(__name__)

import streamlit as st
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

# ── Test ─────────────────────────────────────────────────────────────────────
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
st.subheader("Model Features")
try:
    features = requests.get(f"{BASE_URL}/ml/voter-turnout/features").json().get("features", [])
    for f in features:
        st.write(f"• {f}")
except Exception as e:
    st.error(f"Could not load features: {e}")
st.divider()    