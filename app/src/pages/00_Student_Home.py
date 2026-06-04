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

lessons = requests.get(f"{BASE_URL}/lessons").json()
progress = requests.get(f"{BASE_URL}/progress/{student_id}").json()
assessments = requests.get(f"{BASE_URL}/assessments").json()

st.title(f"Welcome Student, {st.session_state['first_name']}.")

completed = len([p for p in progress if p.get("completionStatus") == "completed"])
total = len(progress)
lesson_pct = int((completed / total) * 100) if total > 0 else 0

col1, col2 = st.columns(2)
col1.metric(label="Lesson Progress", value=f"{lesson_pct}%")
col2.metric(label="Class Grade", value="80%")

st.header("Topic: Public Policy")

st.write("## Quizzes")
q1, q2, q3, q4 = st.columns(4)
q1.subheader("Quiz 1: Section 1")
q2.subheader("Quiz 2: Section 2")
q3.subheader("Quiz 3: Section 3")
q4.subheader("Quiz 4: Section 4")

#when class routes are implemented
# st.write("## Quizzes")
# if assessments:
#     cols = st.columns(4)
#     for i, assessment in enumerate(assessments):
#         cols[i % 4].write(assessment.get("assessmentName", f"Quiz {assessment['assessmentID']}"))
# else:
#     st.write("No quizzes available.")

st.write("## Content")
st.subheader("Section 1: Introduction to Public Policy")
st.write("Lorem ipsum dolor sit amet, consectetur adipiscing elit.")

st.subheader("Section 2: EU Institutions")
st.write("Lorem ipsum dolor sit amet, consectetur adipiscing elit.")

st.subheader("Section 3: Civic Engagement")
st.write("Lorem ipsum dolor sit amet, consectetur adipiscing elit.")

#when class routes are implemented
# st.write("## Content")
# if lessons:
#     for lesson in lessons:
#         st.subheader(lesson["title"])
#         st.caption(f"Topic: {lesson.get('topicName', 'N/A')} | Difficulty: {lesson.get('difficultyLevel', 'N/A')}")
#         st.write(lesson.get("content", "No content available."))
#         st.divider()
# else:
#     st.write("No lessons available.")