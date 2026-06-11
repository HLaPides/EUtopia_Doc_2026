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
    .block-container { padding-left: 1rem !important; padding-right: 1rem !important; }
</style>
""", unsafe_allow_html=True)

# redirect if not logged in
if not st.session_state.get('authenticated'):
    st.switch_page('Home.py')

BASE_URL = "http://web-api:4000"
teacher_id = st.session_state['userID']

st.title(f"Analytics")
st.write(f"Student performance across your classes.")

# ── fetch data ────────────────────────────────────────────────────────────────
try:
    classes = requests.get(f"{BASE_URL}/classes/teacher/{teacher_id}").json()
    class_ids = [c["classID"] for c in classes]
except Exception as e:
    st.error("Could not load class data.")
    st.stop()

students = []
for class_id in class_ids:
    try:
        class_students = requests.get(f"{BASE_URL}/classes/{class_id}/students").json()
        students.extend(class_students)
    except Exception:
        continue

# deduplicate students in case they appear in multiple classes
seen = set()
unique_students = []
for s in students:
    if s['userID'] not in seen:
        seen.add(s['userID'])
        unique_students.append(s)

if not unique_students:
    st.info("No students found in your classes.")
    st.stop()

# ── build analytics rows ──────────────────────────────────────────────────────
rows = []
for s in unique_students:
    try:
        progress = requests.get(f"{BASE_URL}/progress/{s['userID']}").json()
    except Exception:
        progress = []

    total     = len(progress)
    completed = len([p for p in progress if p.get("completionStatus") == "Completed"])

    completion_pct = round((completed / total) * 100, 1) if total > 0 else 0
    avg_quiz       = round(
        sum(float(p.get("quizPerformance", 0)) for p in progress) / total, 1
    ) if total > 0 else 0

    rows.append({
        "Student":        f"{s['firstName']} {s['lastName']}",
        "Lessons Assigned": total,
        "Lessons Completed": completed,
        "Completion %":   completion_pct,
        "Avg Quiz Score": avg_quiz,
    })

df = pd.DataFrame(rows).sort_values("Completion %", ascending=False).reset_index(drop=True)
df.index += 1

# ── summary metrics ───────────────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)
col1.metric("Total Students", len(df))
col2.metric("Avg Completion %", f"{df['Completion %'].mean():.1f}%")
col3.metric("Avg Quiz Score", f"{df['Avg Quiz Score'].mean():.1f}")

st.divider()

# ── table ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    table { width: 100% !important; }
</style>
""", unsafe_allow_html=True)
st.subheader("Student Performance")
df["Completion %"]   = df["Completion %"].map("{:.1f}".format)
df["Avg Quiz Score"] = df["Avg Quiz Score"].map("{:.1f}".format)
st.markdown(
    '<div style="width:100%">' +
    df.style
    .set_properties(**{"text-align": "center"}, subset=["Lessons Assigned", "Lessons Completed", "Completion %", "Avg Quiz Score"])
    .set_properties(**{"text-align": "left"}, subset=["Student"])
    .set_table_styles([
        {"selector": "table", "props": [("width", "100%"), ("border-collapse", "collapse")]},
        {"selector": "th", "props": [("background-color", "#1a1a2e"), ("color", "white"), ("padding", "10px"), ("text-align", "center")]},
        {"selector": "td", "props": [("padding", "8px 12px")]},
        {"selector": "tr:nth-child(even)", "props": [("background-color", "#f5f5f5")]},
    ])
    .hide(axis="index")
    .to_html() +
    '</div>',
    unsafe_allow_html=True
)