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