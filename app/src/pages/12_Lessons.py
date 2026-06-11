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

st.title("Lessons")

try:
    all_lessons = requests.get(f"{BASE_URL}/lessons").json()
except Exception:
    st.error("Could not load lessons.")
    st.stop()

my_lessons = [l for l in all_lessons if l.get("teacherID") == teacher_id]

tab1, tab2 = st.tabs(["My Lessons", "All Lessons"])

def show_lessons(lessons):
    if not lessons:
        st.info("No lessons found.")
        return

    df = pd.DataFrame([{
        "Title":      l.get("title", ""),
        "Topic":      l.get("topicName", ""),
        "Difficulty": l.get("difficultyLevel", ""),
        "Status":     l.get("approvalStatus", ""),
    } for l in lessons])

    df = df.sort_values("Status").reset_index(drop=True)
    df.index += 1

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Lessons", len(df))
    col2.metric("Approved", len(df[df["Status"] == "Approved"]))
    col3.metric("Pending", len(df[df["Status"] == "Pending"]))

    st.divider()
    st.dataframe(df, use_container_width=True)

with tab1:
    st.subheader("My Lessons")
    show_lessons(my_lessons)

with tab2:
    st.subheader("All Lessons")
    show_lessons(all_lessons)