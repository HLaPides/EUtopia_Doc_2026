import streamlit as st
import requests
from modules.nav import SideBarLinks

st.set_page_config(layout="wide")
SideBarLinks()

if not st.session_state.get("authenticated"):
    st.switch_page("Home.py")

BASE_URL = "http://web-api:4000"
official_id = st.session_state["userID"]

st.title("Lesson Approval")
st.write("Review teacher-submitted lessons and approve or reject them.")

lessons = requests.get(f"{BASE_URL}/lessons/pending").json()
pending_lessons = lessons

if not pending_lessons:
    st.success("No pending lessons right now.")
    st.stop()

for lesson in pending_lessons:
    with st.container(border=True):
        st.subheader(lesson["title"])
        st.write(f"**Topic:** {lesson.get('topicName', 'N/A')}")
        st.write(f"**Difficulty:** {lesson.get('difficultyLevel', 'N/A')}")
        teacher_name = lesson.get("teacherName") or "Unknown teacher"
        st.write(f"**Teacher:** {teacher_name}")
        st.write("**Lesson Content:**")
        st.write(lesson.get("content", ""))

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Approve", key=f"approve_{lesson['lessonID']}"):
                requests.put(
                    f"{BASE_URL}/lessons/{lesson['lessonID']}",
                    json={
                        "title": lesson["title"],
                        "topicName": lesson.get("topicName"),
                        "content": lesson["content"],
                        "difficultyLevel": lesson.get("difficultyLevel"),
                        "approvalStatus": "Approved",
                        "updatedBy": official_id
                    }
                )
                st.success("Lesson approved.")
                st.rerun()

        with col2:
            if st.button("Reject", key=f"reject_{lesson['lessonID']}"):
                requests.put(
                    f"{BASE_URL}/lessons/{lesson['lessonID']}",
                    json={
                        "title": lesson["title"],
                        "topicName": lesson.get("topicName"),
                        "content": lesson["content"],
                        "difficultyLevel": lesson.get("difficultyLevel"),
                        "approvalStatus": "Rejected",
                        "updatedBy": official_id
                    }
                )
                st.error("Lesson rejected.")
                st.rerun()
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

teachers = sorted(set(f"{l['firstName']} {l['lastName']}" for l in pending))
topics   = sorted(set(l['topicName'] for l in pending if l.get('topicName')))
classes  = sorted(set(l['className'] for l in pending if l.get('className')))

with col1:
    selected_teacher = st.selectbox("Filter by Teacher", ["All"] + teachers)
with col2:
    selected_topic = st.selectbox("Filter by Topic", ["All"] + topics)
with col3:
    selected_class = st.selectbox("Filter by Class", ["All"] + classes)

filtered = pending
if selected_teacher != "All":
    filtered = [l for l in filtered if f"{l['firstName']} {l['lastName']}" == selected_teacher]
if selected_topic != "All":
    filtered = [l for l in filtered if l.get('topicName') == selected_topic]
if selected_class != "All":
    filtered = [l for l in filtered if l.get('className') == selected_class]

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
        f"{lesson.get('className')} | "
        f"{lesson.get('firstName')} {lesson.get('lastName')} (ID: {lesson.get('teacherID')}) | "
        f"Submitted {created}"
    )
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