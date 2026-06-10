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


col1, col2 = st.columns(2)
col1.metric(label="Lesson Progress", value=f"{lesson_pct}%")
col2.metric(label="Class Grade", value=f"{avg_grade}%" if avg_grade is not None else "N/A")

st.header(f"Class: {class_name}")

st.write("## Quizzes")
if assessments:
    st.markdown("""
    <style>
    section[data-testid="stMain"] div[data-testid="stButton"] > button {
        background-color: #B3B5D0;
        color: #1e1e2e;
        border-radius: 12px;
        border: 1px solid #444;
        padding: 20px;
        height: 100px;
        text-align: left;
        white-space: normal;
    }
    section[data-testid="stMain"] div[data-testid="stButton"] > button:hover {
        background-color: #9799ba;
        border: 1px solid #444;
        color: #1e1e2e;
    }
    </style>
    """, unsafe_allow_html=True)

    cols = st.columns(min(len(assessments), 4))
    for i, assessment in enumerate(assessments):
        name = assessment.get("assessmentName", f"Quiz {assessment['assessmentID']}")
        a_type = assessment.get("assessmentType", "")
        col = cols[i % 4]
        with col:
            if st.button(
                f"**{name}**\n\n{a_type}",
                key=f"assessment_{assessment['assessmentID']}",
                use_container_width=True
            ):
                st.session_state['selected_assessment'] = assessment
                st.switch_page("pages/03_Student_Assessment.py")
else:
    st.write("No quizzes available.")

st.write("## Content")
if lessons:
    for lesson in sorted_lessons:
        st.subheader(lesson["title"])
        st.caption(f"Topic: {lesson.get('topicName', 'N/A')} | Difficulty: {lesson.get('difficultyLevel', 'N/A')}")
        st.write(lesson.get("content", "No content available."))
        st.divider()
else:
    st.write("No lessons available.")