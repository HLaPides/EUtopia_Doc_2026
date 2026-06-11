import logging
logger = logging.getLogger(__name__)

import streamlit as st
import pandas as pd
import requests
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

st.markdown("""
<style>
    table { width: 100% !important; }
</style>
""", unsafe_allow_html=True)

if not st.session_state.get('authenticated'):
    st.switch_page('Home.py')

BASE_URL = "http://web-api:4000"
teacher_id = st.session_state['userID']

st.title("My Students")

try:
    classes = requests.get(f"{BASE_URL}/classes/teacher/{teacher_id}").json()
    class_ids = [c["classID"] for c in classes]
    class_names = {c["classID"]: c["className"] for c in classes}
except Exception:
    st.error("Could not load class data.")
    st.stop()

students = []
for class_id in class_ids:
    try:
        class_students = requests.get(f"{BASE_URL}/classes/{class_id}/students").json()
        for s in class_students:
            s["className"] = class_names.get(class_id, "")
        students.extend(class_students)
    except Exception:
        continue

seen = set()
unique_students = []
for s in students:
    if s['userID'] not in seen:
        seen.add(s['userID'])
        unique_students.append(s)

if not unique_students:
    st.info("No students found in your classes.")
    st.stop()

col1, col2 = st.columns(2)
col1.metric("Total Students", len(unique_students))
col2.metric("Classes", len(class_ids))

st.divider()

df = pd.DataFrame([{
    "Name":    f"{s['firstName']} {s['lastName']}",
    "Email":   s.get("email", ""),
    "Country": s.get("countryOrigin", ""),
    "Class":   s.get("className", ""),
} for s in unique_students])

df = df.sort_values("Class").reset_index(drop=True)
df.index += 1

st.markdown(
    df.style
    .set_properties(**{'text-align': 'left'})
    .set_table_styles([
    {'selector': 'table', 'props': [('width', '100%')]},
    {'selector': 'th', 'props': [('background-color', '#1a1a2e'), ('color', 'white'), ('padding', '10px'), ('text-align', 'center')]},
    {'selector': 'td', 'props': [('padding', '8px 12px')]},
    {'selector': 'tr:nth-child(even)', 'props': [('background-color', '#f5f5f5')]},
])
    .hide(axis='index')
    .to_html(),
    unsafe_allow_html=True
)