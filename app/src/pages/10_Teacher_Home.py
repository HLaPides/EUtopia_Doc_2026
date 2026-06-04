import logging
logger = logging.getLogger(__name__)

import streamlit as st
import plotly.express as px
import pandas as pd
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

# Show appropriate sidebar links for the role of the currently logged in user
SideBarLinks()

st.title(f"Welcome Teacher, {st.session_state['first_name']}.")

tab1, tab2, tab3 = st.tabs(["Top Performing Students", "Recent Lessons", "Student Engagement"])

with tab1:
    for name, score in [("Emma Johns", 92), ("Lucas Miller", 88), ("Sofia Rose", 84), ("Elena Garcia", 80), ("John Doe", 78)]:
        col_name, col_pct, col_bar = st.columns([2, 1, 3])
        col_name.write(name)
        col_pct.write(f"{score}%")
        col_bar.progress(score)

with tab2:
    h1, h2, h3 = st.columns([3, 2, 2])
    h1.write("**Lesson**")
    h2.write("**Assigned**")
    h3.write("**Completed**")
    
    lessons = [
        ("Algebra Basics", "Jan 10", "24/30"),
        ("Fractions", "Jan 15", "18/30"),
        ("Geometry Intro", "Jan 20", "30/30"),
    ]
    
    for name, assigned, completed in lessons:
        c1, c2, c3 = st.columns([3, 2, 2])
        c1.write(name)
        c2.write(assigned)
        c3.write(completed)

with tab3:
    df = pd.DataFrame({
        "Student": ["Emma Johns", "Lucas Miller", "Sofia Rose", "Elena Garcia", "John Doe"],
        "Engagement (%)": [95, 82, 78, 91, 70]
    })
    
    fig = px.bar(df, x="Student", y="Engagement (%)", title="Student Engagement",
                 color="Engagement (%)", color_continuous_scale="blues")
    st.plotly_chart(fig, use_container_width=True)