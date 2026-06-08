import logging
logger = logging.getLogger(__name__)

import streamlit as st
import pandas as pd
import requests
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

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
st.subheader("Student Performance")
st.dataframe(
    df,
    use_container_width=True,
    column_config={
        "Completion %": st.column_config.ProgressColumn(
            "Completion %",
            min_value=0,
            max_value=100,
            format="%d%%",
        ),
        "Avg Quiz Score": st.column_config.NumberColumn(
            "Avg Quiz Score",
            format="%.1f",
        ),
    }
)