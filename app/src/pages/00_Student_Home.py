import logging
logger = logging.getLogger(__name__)

import streamlit as st
import requests
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

# Show appropriate sidebar links for the role of the currently logged in user
SideBarLinks()

BASE_URL = "http://web-api:4000"
student_id = st.session_state['userID']

profile = requests.get(f"{BASE_URL}/students/{student_id}/profile").json()
class_id = profile.get("classID")
class_info = requests.get(f"{BASE_URL}/classes/{class_id}").json()
class_name = class_info.get("className", "Your Class")
lessons = requests.get(f"{BASE_URL}/lessons/class/{class_id}").json()
progress = requests.get(f"{BASE_URL}/progress/{student_id}").json()
all_assessments = requests.get(f"{BASE_URL}/assessments").json()
lesson_ids = {l["lessonID"] for l in lessons}
assessments = [a for a in all_assessments if a.get("lessonID") in lesson_ids]

st.title(f"Welcome Student, {st.session_state['first_name']}.")

completed = len([p for p in progress if p.get("completionStatus") == "Completed"])
total = len(progress)
lesson_pct = int((completed / total) * 100) if total > 0 else 0
difficulty_order = {"Beginner": 0, "Intermediate": 1, "Advanced": 2}
sorted_lessons = sorted(lessons, key=lambda l: difficulty_order.get(l.get("difficultyLevel", ""), 99))
quiz_scores = [p.get("quizPerformance") for p in progress if p.get("quizPerformance") is not None]
avg_grade = round(sum(float(s) for s in quiz_scores) / len(quiz_scores), 1) if quiz_scores else None


col1, col2, col3 = st.columns(3)
col1.metric(label="Class", value=f"{class_name}", border=True)
col2.metric(label="Lesson Progress", value=f"{lesson_pct}%", border=True)
col3.metric(label="Class Grade", value=f"{avg_grade}%" if avg_grade is not None else "N/A", border=True)
st.divider()

btn1, btn2 = st.columns(2)
with btn1:
    if st.button("🌍\n\n**Run a country simulation to predict EU Election Turnout.**\n\n Take a guided lesson, start from an existing country profile, create a completely custom country, or view past simulations.", 
                 use_container_width=True,
                 type="primary",
                 key="nav_simulation"):
        st.switch_page("pages/01_Country_Simulation.py")
with btn2:
    if st.button("📋\n\n**Take Diagnostic Survey**\n\n Answer a few questions about your trust in the EU parliament, trust in politicians, satisfaction with democracy, etc.",
                 use_container_width=True,
                 type="primary",
                 key="nav_survey"):
        st.switch_page("pages/02_Diagnostic_Survey.py")
st.divider()

st.write("## Lessons")
if lessons:
    assessments_by_lesson = {}
    for a in assessments:
        lid = a.get("lessonID")
        if lid not in assessments_by_lesson:
            assessments_by_lesson[lid] = []
        assessments_by_lesson[lid].append(a)

    st.markdown("""
    <style>
    section[data-testid="stMain"] div[data-testid="stButton"] > button:not([kind="primary"]) {
        background-color: #B3B5D0;
        color: #1e1e2e;
        border-radius: 12px;
        border: 1px solid #444;
        padding: 20px;
        height: 80px;
        text-align: left;
        justify-content: flex-start;
        white-space: normal;
    }
    section[data-testid="stMain"] div[data-testid="stButton"] > button:not([kind="primary"]):hover {
        background-color: #9799ba;
        border: 1px solid #444;
        color: #1e1e2e;
    }
    div[data-testid="stButton"]:has(button[kind="primary"]) > button {
        height: 175px !important;
        white-space: normal !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    for lesson in sorted_lessons:
        st.subheader(lesson["title"])
        st.caption(f"Topic: {lesson.get('topicName', 'N/A')} | Difficulty: {lesson.get('difficultyLevel', 'N/A')}")
        st.write(lesson.get("content", "No content available."))

        lesson_assessments = assessments_by_lesson.get(lesson["lessonID"], [])
        if lesson_assessments:
            st.write("### Quizzes")
            num_cols = min(len(lesson_assessments), 4)
            cols = st.columns(num_cols)
            for i, assessment in enumerate(lesson_assessments):
                name = assessment.get("assessmentName", f"Quiz {assessment['assessmentID']}")
                a_type = assessment.get("assessmentType", "")
                with cols[i % num_cols]:
                    if st.button(
                        f"**{name}**\n\n{a_type}",
                        key=f"assessment_{assessment['assessmentID']}",
                        use_container_width=True
                    ):
                        st.session_state['selected_assessment'] = assessment
                        st.switch_page("pages/03_Student_Assessment.py")
        st.divider()
else:
    st.write("No lessons available.")