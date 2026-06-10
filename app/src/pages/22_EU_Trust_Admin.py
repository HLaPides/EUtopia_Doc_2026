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

st.title("EU Trust Model")
st.write("Retrain or evaluate the logistic regression model that predicts whether an individual trusts the EU.")

st.divider()

# ── Test ─────────────────────────────────────────────────────────────────────
st.subheader("Evaluate Model")
st.write("Evaluates the model on an 80/20 train/test split.")

if st.button("Run Test", type="secondary", use_container_width=True):
    with st.spinner("Evaluating..."):
        try:
            response = requests.get(f"{BASE_URL}/ml/eu-trust/test")
            result   = response.json()
            col1, col2, col3 = st.columns(3)
            col1.metric("Train Accuracy", f"{result.get('train_accuracy') * 100:.1f}%")
            col2.metric("Test Accuracy",  f"{result.get('test_accuracy') * 100:.1f}%")
            col3.metric("N",              result.get("n"))
        except Exception as e:
            st.error(f"Error: {e}")

st.divider()
st.subheader("Model Features")
try:
    features = requests.get(f"{BASE_URL}/ml/eu-trust/features").json().get("features", [])
    for f in features:
        st.write(f"• {f}")
except Exception as e:
    st.error(f"Could not load features: {e}")