import logging
logger = logging.getLogger(__name__)

import streamlit as st
import requests
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')
SideBarLinks()

BASE_URL = "http://web-api:4000"
student_id = st.session_state['userID']

if 'selected_assessment' not in st.session_state:
    st.error("No assessment selected.")
    st.stop()

assessment = st.session_state['selected_assessment']
assessment_id = assessment['assessmentID']
name = assessment.get("assessmentName", "Assessment")
a_type = assessment.get("assessmentType", "")
max_score = assessment.get("maxScore", 100)
questions = requests.get(f"{BASE_URL}/questions/{assessment_id}").json()


#Quiz title
st.title(name)
st.caption(f"Type: {a_type} | Max Score: {max_score}")
st.divider()

#questions
if not questions:
    st.write("No questions available for this assessment.")
else:
    answers = {}
    for q in questions:
        qid = q["questionID"]
        qtext = q.get("questionText", "")
        qtype = q.get("questionType", "Short Answer")

        st.write(f"**{qtext}**")

        if qtype == "True/False":
            answers[qid] = st.radio(
                label="",
                options=["True", "False"],
                key=f"q_{qid}",
                label_visibility="collapsed"
            )
        elif qtype == "Multiple Choice":
            answers[qid] = st.radio(
                label="",
                options=["A", "B", "C", "D"],
                key=f"q_{qid}",
                label_visibility="collapsed"
            )
        else:
            answers[qid] = st.text_input(
                label="",
                key=f"q_{qid}",
                placeholder="Your answer...",
                label_visibility="collapsed"
            )
        st.divider()

#submit button
if st.button("Submit Assessment", type="primary", use_container_width=True):
        for qid, input_val in answers.items():
            payload = {
                "studentID": student_id,
                "questionID": qid,
                "input": input_val,
                "score": None,
                "createdBy": student_id,
                "updatedBy": student_id
            }
            requests.post(f"{BASE_URL}/responses", json=payload)

        st.success("Assessment submitted successfully!")
        st.balloons()