import logging
logger = logging.getLogger(__name__)

import streamlit as st
import requests
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

if not st.session_state.get('authenticated'):
    st.switch_page('Home.py')

BASE_URL = "http://web-api:4000"

st.title("Lesson Approval")
st.write("Review and approve or reject lessons submitted by teachers.")

st.divider()

try:
    all_lessons = requests.get(f"{BASE_URL}/lessons").json()
    pending = [l for l in all_lessons if l.get("approvalStatus") == "Pending"]
except Exception as e:
    st.error(f"Could not load lessons: {e}")
    st.stop()

if not pending:
    st.info("No lessons pending approval.")
    st.stop()

st.write(f"**{len(pending)} lesson(s) pending review**")
st.divider()

for lesson in pending:
    col1, col2, col3 = st.columns([4, 1, 1])

    with col1:
        st.write(f"**{lesson.get('title')}**")
        st.caption(f"{lesson.get('topicName')} · {lesson.get('difficultyLevel')} · Teacher ID {lesson.get('teacherID')}")
        with st.expander("View content"):
            st.write(lesson.get("content", ""))

    with col2:
        if st.button("Approve", key=f"approve_{lesson['lessonID']}", type="primary", use_container_width=True):
            try:
                requests.put(
                    f"{BASE_URL}/lessons/{lesson['lessonID']}/status",
                    json={"approvalStatus": "Approved"}
                )
                st.success("Approved")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

    with col3:
        if st.button("Reject", key=f"reject_{lesson['lessonID']}", type="secondary", use_container_width=True):
            try:
                requests.put(
                    f"{BASE_URL}/lessons/{lesson['lessonID']}/status",
                    json={"approvalStatus": "Rejected"}
                )
                st.warning("Rejected")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

    st.divider()