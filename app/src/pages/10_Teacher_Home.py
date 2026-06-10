import logging
logger = logging.getLogger(__name__)

import streamlit as st
import plotly.express as px
import pandas as pd
import requests
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

# Show appropriate sidebar links for the role of the currently logged in user
SideBarLinks()

BASE_URL = "http://web-api:4000"
teacher_id = st.session_state['userID']

classes = requests.get(f"{BASE_URL}/classes/teacher/{teacher_id}").json()
class_ids = [c["classID"] for c in classes]
all_lessons = requests.get(f"{BASE_URL}/lessons").json()
lessons = [l for l in all_lessons if l.get("classID") in class_ids]

students = []
for class_id in class_ids:
    class_students = requests.get(f"{BASE_URL}/classes/{class_id}/students").json()
    students.extend(class_students)

student_progress = []
for s in students:
    progress = requests.get(f"{BASE_URL}/progress/{s['userID']}").json()
    completed = len([p for p in progress if p.get("completionStatus") == "Completed"])
    total = len(progress)
    pct = int((completed / total) * 100) if total > 0 else 0
    avg_engagement = (
        sum(float(p.get("avgEngagementTime", 0)) for p in progress) / total
        if total > 0 else 0
    )   
    student_progress.append({
        "name": f"{s['firstName']} {s['lastName']}",
        "score": pct,
        "engagement": round(avg_engagement, 1)
    })

student_progress.sort(key=lambda x: x["score"], reverse=True)

st.title(f"Welcome Teacher, {st.session_state['first_name']}.")

#all tabs need more revising to get mock data
tab1, tab2, tab3 = st.tabs(["Top Performing Students", "Recent Lessons", "Student Engagement"])

with tab1:
    if student_progress:
        for s in student_progress[:5]:
            col_name, col_pct, col_bar = st.columns([2, 1, 3])
            col_name.write(s["name"])
            col_pct.write(f"{s['score']}%")
            col_bar.progress(s["score"])
    else:
        st.write("No student data available.")

with tab2:
    h1, h2, h3 = st.columns([3, 2, 2])
    h1.write("**Lesson**")
    h2.write("**Assigned**")
    h3.write("**Completed**")

    if lessons:
        for lesson in lessons:
            c1, c2, c3 = st.columns([3, 2, 2])
            c1.write(lesson.get("title", "N/A"))
            c2.write(str(lesson.get("createdAt", "N/A"))[:10])
            c3.write(lesson.get("approvalStatus", "N/A"))
    else:
        st.write("No lessons available.")

with tab3:
    if student_progress:
        df = pd.DataFrame({
            "Student": [s["name"] for s in student_progress],
            "Engagement Time (min)": [s["engagement"] for s in student_progress]
        })
        df = df.sort_values("Engagement Time (min)", ascending=True)

        fig = px.bar(
            df,
            x="Engagement Time (min)",
            y="Student",
            orientation="h",
            title="Student Engagement",
            text="Engagement Time (min)",
        )
        fig.update_traces(
            marker_color="#2c7bb6",
            texttemplate="%{text:.0f} min",
            textposition="outside"
        )
        fig.update_layout(
            height=max(300, len(df) * 40),
            xaxis=dict(range=[0, df["Engagement Time (min)"].max() * 1.2]),
            plot_bgcolor="white",
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.write("No engagement data available.")