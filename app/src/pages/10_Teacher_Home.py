import logging
logger = logging.getLogger(__name__)

import streamlit as st
import plotly.express as px
import pandas as pd
import requests
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

# Show appropriate sidebar links for the role of the currently logged in user
SideBarLinks()

BASE_URL = "http://web-api:4000"

lessons_resp = requests.get(f"{BASE_URL}/lessons").json()

st.title(f"Welcome Teacher, {st.session_state['first_name']}.")

#all tabs need more revising to get mock data
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

    if lessons_resp:
        for lesson in lessons_resp:
            c1, c2, c3 = st.columns([3, 2, 2])
            c1.write(lesson.get("title", "N/A"))
            c2.write(str(lesson.get("createdAt", "N/A"))[:10])
            c3.write(lesson.get("approvalStatus", "N/A"))
    else:
        st.write("No lessons available.")

with tab3:
    df = pd.DataFrame({
        "Student": ["Emma Johns", "Lucas Miller", "Sofia Rose", "Elena Garcia", "John Doe"],
        "Engagement (%)": [95, 82, 78, 91, 70]
    })
    
    fig = px.bar(df, x="Student", y="Engagement (%)", title="Student Engagement",
                 color="Engagement (%)", color_continuous_scale="blues")
    st.plotly_chart(fig, use_container_width=True)