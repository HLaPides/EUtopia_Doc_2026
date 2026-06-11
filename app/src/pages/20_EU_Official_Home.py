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
st.title(f"Welcome back, {st.session_state.get('first_name', 'Official')}")

st.divider()

try:
    pending = requests.get(f"{BASE_URL}/lessons/pending").json()
    n_pending = len(pending)
except Exception:
    n_pending = "—"

st.subheader("Lessons")
col1, col2 = st.columns(2)
col1.metric("Pending Approval", n_pending)
col2.metric("Action Required", "Yes" if n_pending and n_pending != "—" and n_pending > 0 else "No")

st.divider()

st.write("### What would you like to do today?")

btn1 = st.button("Lesson Approval", type="primary", use_container_width=True)
btn2 = st.button("Voter Turnout Model", type="primary", use_container_width=True)
btn3 = st.button("EU Trust Model", type="primary", use_container_width=True)

if btn1:
    st.switch_page("pages/23_Lesson_Approval.py")
if btn2:
    st.switch_page("pages/21_Voter_Turnout_Admin.py")
if btn3:
    st.switch_page("pages/22_EU_Trust_Admin.py")