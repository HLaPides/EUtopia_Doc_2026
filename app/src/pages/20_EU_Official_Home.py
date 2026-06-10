import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

if not st.session_state.get('authenticated'):
    st.switch_page('Home.py')

st.title('EU Official Dashboard')
st.write('### What would you like to do today?')

btn1 = st.button('Manage Voter Turnout Model', type='primary', use_container_width=True)
btn2 = st.button('Manage EU Trust Model', type='primary', use_container_width=True)
btn3 = st.button('Lesson Approval', type='primary', use_container_width=True)

if btn1:
    st.switch_page('pages/21_Voter_Turnout_Admin.py')
if btn2:
    st.switch_page('pages/22_EU_Trust_Admin.py')
if btn3:
    st.switch_page('pages/23_Lesson_Approval.py')
