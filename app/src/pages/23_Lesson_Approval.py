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
    pending = requests.get(f"{BASE_URL}/lessons/pending").json()
except Exception as e:
    st.error(f"Could not load lessons: {e}")
    st.stop()

if not pending:
    st.info("No lessons pending approval.")
    st.stop()

# ── Filters ───────────────────────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)

teachers = sorted(set(l['teacherName'] for l in pending if l.get('teacherName')))
topics = [
    "Citizenship", "Economics", "European Institutions", "Governance",
    "History", "Human Rights", "International Relations", "Media",
    "Migration", "Public Policy", "Technology"
]

with col1:
    selected_teacher = st.selectbox("Filter by Teacher", ["All"] + teachers)
with col2:
    selected_topics = st.multiselect("Filter by Topic", topics)

filtered = pending
if selected_teacher != "All":
    filtered = [l for l in filtered if l.get('teacherName') == selected_teacher]
if selected_topics:
    filtered = [l for l in filtered if l.get('topicName') in selected_topics]

st.divider()
st.write(f"**{len(filtered)} lesson(s) pending review**")
st.divider()

for lesson in filtered:
    col1, col2, col3 = st.columns([4, 1, 1])

    with col1:
        st.write(f"**{lesson.get('title')}**")
        created = str(lesson.get('createdAt', ''))[:10]
        st.caption(
            f"{lesson.get('topicName')} | {lesson.get('difficultyLevel')} | "
            f"{lesson.get('teacherName')} (ID: {lesson.get('teacherID')}) | "
            f"Submitted {created}"
        )
        with st.expander("View content"):
            st.write(lesson.get("content", ""))

    with col2:
        if st.button("Approve", key=f"approve_{lesson['lessonID']}", type="primary", use_container_width=True):
            try:
                requests.put(
                    f"{BASE_URL}/lessons/{lesson['lessonID']}/approve",
                    json={"officialID": st.session_state['userID']}
                )
                st.success("Approved")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

    with col3:
        if st.button("Reject", key=f"reject_{lesson['lessonID']}", type="secondary", use_container_width=True):
            try:
                requests.put(
                    f"{BASE_URL}/lessons/{lesson['lessonID']}/reject",
                    json={"officialID": st.session_state['userID']}
                )
                st.warning("Rejected")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

    st.divider()