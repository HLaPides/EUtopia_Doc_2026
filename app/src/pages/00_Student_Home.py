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

col1, col2 = st.columns(2)
col1.metric(label="Lesson Progress", value=f"{lesson_pct}%")
col2.metric(label="Class Grade", value="80%")

st.header(f"Class: {class_name}")

st.write("## Quizzes")
if assessments:
    cards_html = """
    <div style="display: flex; overflow-x: auto; gap: 16px; padding-bottom: 12px;">
    """
    for assessment in assessments:
        name = assessment.get("assessmentName", f"Quiz {assessment['assessmentID']}")
        a_type = assessment.get("assessmentType", "")
        cards_html += f"""
        <div style="
            min-width: 200px;
            background-color: #1e1e2e;
            border-radius: 12px;
            padding: 20px;
            flex-shrink: 0;
            border: 1px solid #444;
        ">
            <div style="color: #ffffff; font-weight: bold; font-size: 16px; margin-bottom: 8px;">{name}</div>
            <div style="color: #ffffff; font-size: 13px;">{a_type}</div>
        </div>
        """
    cards_html += "</div>"
    st.html(cards_html)
else:
    st.write("No quizzes available.")

st.write("## Content")
if lessons:
    for lesson in lessons:
        st.subheader(lesson["title"])
        st.caption(f"Topic: {lesson.get('topicName', 'N/A')} | Difficulty: {lesson.get('difficultyLevel', 'N/A')}")
        st.write(lesson.get("content", "No content available."))
        st.divider()
else:
    st.write("No lessons available.")