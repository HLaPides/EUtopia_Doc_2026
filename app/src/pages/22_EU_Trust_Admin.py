import logging
logger = logging.getLogger(__name__)

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')
SideBarLinks()

if not st.session_state.get('authenticated'):
    st.switch_page('Home.py')

BASE_URL = "http://web-api:4000"

st.title("EU Trust Survey Results")
st.write("Most recent survey response per student.")

try:
    surveys = requests.get(f"{BASE_URL}/surveys").json()
except Exception as e:
    st.error(f"Could not load surveys: {e}")
    st.stop()

if not surveys:
    st.info("No survey responses yet.")
    st.stop()

df = pd.DataFrame(surveys)
df['predictedTrust'] = pd.to_numeric(df['predictedTrust'], errors='coerce').fillna(0).round().astype(int)
df = df[df['predictedTrust'].isin([0, 1])]
df['Predicted EU Trust'] = df['predictedTrust'].map({0: '✅ Trusts EU', 1: '❌ Does Not Trust EU'})
st.dataframe(df[['firstName', 'lastName', 'Predicted EU Trust']], use_container_width=True)

# metrics
total = len(df)
trusting = int((df['predictedTrust'] == 1).sum())
not_trusting = int((df['predictedTrust'] == 0).sum())
percent = (trusting / total) * 100 if total > 0 else 0

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Students Surveyed", total)
with col2:
    st.metric("Trust EU", f"{trusting} ({percent:.1f}%)")
with col3:
    st.metric("Do Not Trust EU", f"{not_trusting} ({100 - percent:.1f}%)")

st.divider()

# pie chart
import plotly.graph_objects as go

fig = go.Figure(go.Indicator(
    mode="gauge+number",
    value=percent,
    title={'text': "% of Students Who Trust the EU"},
    gauge={
        'axis': {'range': [0, 100]},
        'bar': {'color': "#1a7a3c"},
        'steps': [
            {'range': [0, 33], 'color': "#e74c3c"},
            {'range': [33, 66], 'color': "#f39c12"},
            {'range': [66, 100], 'color': "#2ecc71"}
        ],
        'threshold': {
            'line': {'color': "black", 'width': 4},
            'thickness': 0.75,
            'value': percent
        }
    }
))

st.plotly_chart(fig, use_container_width=True, key="gauge")


st.divider()

# bar chart by education level
if 'educationLevel' in df.columns:
    all_edu = ['Middle School', 'High School', "Bachelor's", "Master's", 'Doctorate']
    edu_trust = df.groupby('educationLevel')['predictedTrust'].apply(lambda x: (x == 0).mean() * 100).reset_index()
    edu_trust.columns = ['Education Level', 'Trust Rate']
    edu_trust['Trust Rate'] = edu_trust['Trust Rate'].round(1)
    edu_display = edu_trust.copy()
    edu_display['Trust Rate Display'] = edu_display['Trust Rate'].apply(lambda x: max(x, 2) if x == 0 else x)
    fig2 = px.bar(
        edu_display,
        x='Education Level',
        y='Trust Rate Display',
        title='EU Trust Rate by Education Level (%)',
        color='Trust Rate',
        color_continuous_scale='RdYlGn',
        range_y=[0, 100],
        range_color=[0, 100],
        category_orders={'Education Level': all_edu}
)
    st.plotly_chart(fig2, use_container_width=True, key="edu_chart")

st.divider()

if 'politicalAffiliation' in df.columns:
    pol_trust = df.groupby('politicalAffiliation')['predictedTrust'].apply(lambda x: (x == 0).mean() * 100).reset_index()
    pol_trust.columns = ['Left-Right (1-10)', 'Trust Rate']
    pol_trust['Trust Rate'] = pol_trust['Trust Rate'].round(1)
    
pol_display = pol_trust.copy()
pol_display['Trust Rate Display'] = pol_display['Trust Rate'].apply(lambda x: 2 if x == 0 else x)

fig3 = px.bar(
    pol_display,
    x='Left-Right (1-10)',
    y='Trust Rate Display',
    title='EU Trust Rate by Political Orientation (%)',
    color='Trust Rate',
    color_continuous_scale='RdYlGn',
    range_x=[0.5, 10.5],
    range_y=[0, 100],
    range_color=[0, 100]
)
st.plotly_chart(fig3, use_container_width=True, key="pol_chart")

st.divider()

# raw table
st.subheader("Individual Responses")
df['Predicted EU Trust'] = df['predictedTrust'].map({0: '✅ Trusts EU', 1: '❌ Does Not Trust EU'})
display_cols = ['firstName', 'lastName', 'educationLevel', 'politicalAffiliation',
                'trustPoliticians', 'satisfactionDemocracy', 'Predicted EU Trust', 'createdAt']
available_cols = [c for c in display_cols if c in df.columns]
st.dataframe(df[available_cols], use_container_width=True)