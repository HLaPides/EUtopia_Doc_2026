import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

# Show appropriate sidebar links for the role of the currently logged in user
SideBarLinks()

st.title(f"Welcome Student, {st.session_state['first_name']}.")

col1, col2 = st.columns(2)
col1.metric(label="Lesson Progress", value="50%")
col2.metric(label="Class Grade", value="80%")

st.header("Topic: Public Policy")
st.write('## Quizzes')
q1, q2, q3, q4 = st.columns(4)
q1.subheader("Quiz 1: Section 1")
q2.subheader("Quiz 2: Section 2")
q3.subheader("Quiz 3: Section 3")
q4.subheader("Quiz 4: Section 4")

st.write('## Content')
st.subheader("Section 1: Lorem Ipsum")
st.write("Lorem ipsum dolor sit amet, consectetur adipiscing elit. " \
"Nullam ante nulla, commodo in placerat eget, venenatis vitae lectus. Aenean ultrices enim turpis, " \
"at interdum mi placerat id. Sed at elementum quam. Duis euismod diam quis quam commodo, et accumsan " \
"lorem ornare. Cras sit amet sodales nibh. Duis nec nisl maximus, aliquam neque vel, efficitur velit.")

st.subheader("Section 2: Lorem Ipsum")
st.write("Lorem ipsum dolor sit amet, consectetur adipiscing elit. " \
"Nullam ante nulla, commodo in placerat eget, venenatis vitae lectus. Aenean ultrices enim turpis, " \
"at interdum mi placerat id. Sed at elementum quam. Duis euismod diam quis quam commodo, et accumsan " \
"lorem ornare. Cras sit amet sodales nibh. Duis nec nisl maximus, aliquam neque vel, efficitur velit.")

st.subheader("Section 3: Lorem Ipsum")
st.write("Lorem ipsum dolor sit amet, consectetur adipiscing elit. " \
"Nullam ante nulla, commodo in placerat eget, venenatis vitae lectus. Aenean ultrices enim turpis, " \
"at interdum mi placerat id. Sed at elementum quam. Duis euismod diam quis quam commodo, et accumsan " \
"lorem ornare. Cras sit amet sodales nibh. Duis nec nisl maximus, aliquam neque vel, efficitur velit.")
