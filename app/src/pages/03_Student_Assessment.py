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
submission_key = f"submitted_{assessment_id}"


if st.session_state.get(submission_key):
    st.title(name)
    st.divider()
    if st.session_state.pop(f"show_balloons_{assessment_id}", False):
        st.balloons()
    st.success("You have already submitted this assessment.")
    st.write("Your responses have been recorded. Return to your homepage to continue.")
    if st.button("← Back to Home", type="primary"):
        st.switch_page("pages/00_Student_Home.py")
else:
    st.title(name)
    st.caption(f"Type: {a_type} | Max Score: {max_score}")
    st.divider()


#questions
    if not questions:
        st.write("No questions available for this assessment.")
    else:
        with st.form(key=f"assessment_form_{assessment_id}"):
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

            submitted = st.form_submit_button("Submit Assessment", type="primary", use_container_width=True)

        if submitted:
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

            st.balloons()
            st.session_state[submission_key] = True
            st.rerun()