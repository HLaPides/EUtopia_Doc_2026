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
teacher_id = st.session_state['userID']

st.title("My Lessons")

try:
    all_lessons = requests.get(f"{BASE_URL}/lessons").json()
    lessons = [l for l in all_lessons if l.get("teacherID") == teacher_id]
except Exception:
    st.error("Could not load lessons.")
    st.stop()

if not lessons:
    st.info("You have not created any lessons yet.")
    st.stop()

df = pd.DataFrame([{
    "Title":           l.get("title", ""),
    "Topic":           l.get("topicName", ""),
    "Difficulty":      l.get("difficultyLevel", ""),
    "Status":          l.get("approvalStatus", ""),
    "Class ID":        l.get("classID", ""),
} for l in lessons])

df = df.sort_values("Status").reset_index(drop=True)
df.index += 1

col1, col2, col3 = st.columns(3)
col1.metric("Total Lessons", len(df))
col2.metric("Approved", len(df[df["Status"] == "Approved"]))
col3.metric("Pending", len(df[df["Status"] == "Pending"]))

st.divider()

st.dataframe(df, use_container_width=True)