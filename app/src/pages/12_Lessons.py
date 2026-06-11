import logging
logger = logging.getLogger(__name__)

import streamlit as st
import pandas as pd
import requests
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

if not st.session_state.get('authenticated'):
    st.switch_page('Home.py')

BASE_URL = "http://web-api:4000"
teacher_id = st.session_state['userID']

st.title("Lessons")

tab1, tab2, tab3 = st.tabs(["My Lessons", "All Lessons", "Create Lesson"])

# ── My Lessons ────────────────────────────────────────────────────────────────
with tab1:
    try:
        all_lessons = requests.get(f"{BASE_URL}/lessons").json()
        lessons = [l for l in all_lessons if l.get("teacherID") == teacher_id]
    except Exception:
        st.error("Could not load lessons.")
        st.stop()

    if not lessons:
        st.info("You have not created any lessons yet.")
    else:
        df = pd.DataFrame([{
            "Title":      l.get("title", ""),
            "Topic":      l.get("topicName", ""),
            "Difficulty": l.get("difficultyLevel", ""),
            "Status":     l.get("approvalStatus", ""),
            "Class ID":   l.get("classID", ""),
        } for l in lessons])

        df = df.sort_values("Status").reset_index(drop=True)
        df.index += 1

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Lessons", len(df))
        col2.metric("Approved", len(df[df["Status"] == "Approved"]))
        col3.metric("Pending", len(df[df["Status"] == "Pending"]))

        st.divider()
        st.dataframe(df, use_container_width=True)


# ── All Lessons ───────────────────────────────────────────────────────────────
with tab2:
    try:
        all_lessons = requests.get(f"{BASE_URL}/lessons").json()
    except Exception:
        st.error("Could not load lessons.")
        st.stop()

    if not all_lessons:
        st.info("No lessons available.")
    else:
        df_all = pd.DataFrame([{
            "Title":      l.get("title", ""),
            "Topic":      l.get("topicName", ""),
            "Difficulty": l.get("difficultyLevel", ""),
            "Status":     l.get("approvalStatus", ""),
            "Class ID":   l.get("classID", ""),
        } for l in all_lessons])

        df_all = df_all.sort_values("Status").reset_index(drop=True)
        df_all.index += 1

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Lessons", len(df_all))
        col2.metric("Approved", len(df_all[df_all["Status"] == "Approved"]))
        col3.metric("Pending", len(df_all[df_all["Status"] == "Pending"]))

        st.divider()
        st.dataframe(df_all, use_container_width=True)


# ── Create Lesson ─────────────────────────────────────────────────────────────
with tab3:
    st.subheader("Create a New Lesson")

    try:
        classes = requests.get(f"{BASE_URL}/classes/teacher/{teacher_id}").json()
    except Exception:
        st.error("Could not load your classes.")
        st.stop()

    if not classes:
        st.warning("You have no classes assigned. A lesson must be linked to a class.")
    else:
        class_options = {c["className"]: c["classID"] for c in classes}

        title      = st.text_input("Lesson Title")
        topic      = st.selectbox("Topic", [
            "European Institutions", "History", "Economics", "Public Policy",
            "Human Rights", "Governance", "Technology", "Migration",
            "International Relations", "Media", "Citizenship"
        ])
        difficulty      = st.selectbox("Difficulty", ["Beginner", "Intermediate", "Advanced"])
        selected_class  = st.selectbox("Class", list(class_options.keys()))
        content         = st.text_area("Lesson Content", height=200)

        if st.button("Submit Lesson", type="primary", use_container_width=True):
            if not title or not content:
                st.warning("Title and content are required.")
            else:
                payload = {
                    "teacherID":       teacher_id,
                    "classID":         class_options[selected_class],
                    "title":           title,
                    "topicName":       topic,
                    "difficultyLevel": difficulty,
                    "content":         content,
                    "approvalStatus":  "Pending",
                    "createdBy":       teacher_id,
                    "updatedBy":       teacher_id,
                }
                try:
                    response = requests.post(f"{BASE_URL}/lessons", json=payload)
                    if response.status_code == 201:
                        st.success("Lesson submitted for approval.")
                    else:
                        st.error("Something went wrong. Please try again.")
                except Exception as e:
                    st.error(f"Error: {e}")