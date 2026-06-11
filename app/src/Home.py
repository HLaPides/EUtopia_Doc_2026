##################################################
# This is the main/entry-point file for the
# sample application for your project
##################################################

# Set up basic logging infrastructure
import logging
logging.basicConfig(format='%(filename)s:%(lineno)s:%(levelname)s -- %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# import the main streamlit library as well
# as SideBarLinks function from src/modules folder
import streamlit as st
import requests
from modules.nav import SideBarLinks

# streamlit supports regular and wide layout (how the controls
# are organized/displayed on the screen).
st.set_page_config(layout='wide')

# If a user is at this page, we assume they are not
# authenticated.  So we change the 'authenticated' value
# in the streamlit session_state to false.
st.session_state['authenticated'] = False

# Use the SideBarLinks function from src/modules/nav.py to control
# the links displayed on the left-side panel.
# IMPORTANT: ensure src/.streamlit/config.toml sets
# showSidebarNavigation = false in the [client] section
SideBarLinks(show_home=True)

# ***************************************************
#    The major content of this page
# ***************************************************

BASE_URL = "http://web-api:4000"

users = requests.get(f"{BASE_URL}/users").json()
user_map = {u["userID"]: u for u in users}

students = requests.get(f"{BASE_URL}/users/by-role/student").json()
teachers = requests.get(f"{BASE_URL}/users/by-role/teacher").json()
officials = requests.get(f"{BASE_URL}/users/by-role/eu_official").json()


def user_label(user):
    return f"{user['firstName']} {user['lastName']}"

logger.info("Loading the Home page of the app")
#st.title('EUtopia')
#here
st.markdown("""
<style>
.eutopia-hero {
    text-align: center;
    margin-top: 10px;
    margin-bottom: 20px;
}

.eutopia-orbit {
    position: relative;
    width: 170px;
    height: 170px;
    margin: auto;
    border: 2px solid rgba(80, 100, 255, 0.35);
    border-radius: 50%;
    animation: spin 7s linear infinite;
}

.eutopia-planet {
    position: absolute;
    width: 18px;
    height: 18px;
    top: -9px;
    left: 75px;
    background: #6C63FF;
    border-radius: 50%;
    box-shadow: 0 0 18px #6C63FF;
}

.eutopia-word {
    margin-top: -110px;
    font-size: 64px;
    font-weight: 800;
    color: #202033;
    animation: float 3s ease-in-out infinite;
}

@keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}

@keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-10px); }
}
</style>

<div class="eutopia-hero">
    <div class="eutopia-orbit">
        <div class="eutopia-planet"></div>
    </div>
    <div class="eutopia-word">EUtopia</div>
</div>
""", unsafe_allow_html=True)
#tohere
##st.write('## Learn Europe. Shape Tomorrow.')
st.markdown(
    "<h2 style='text-align: center;'>Learn Europe. Shape Tomorrow.</h2>",
    unsafe_allow_html=True
)
st.write('### As which user would you like to log in?')

# For each of the user personas for which we are implementing
# functionality, we put a button on the screen that the user
# can click to MIMIC logging in as that mock user.


col1, col2 = st.columns([4, 1])
with col1:
    selected_student = st.selectbox(
        "Student",
        options=students,
        format_func=user_label,
        index=None,
        placeholder="Select a student..."
    )
with col2:
    st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
    if st.button("Log in as Student", type='primary', use_container_width=True):
        if selected_student:
            st.session_state['authenticated'] = True
            st.session_state['role'] = 'student'
            st.session_state['first_name'] = selected_student['firstName']
            st.session_state['userID'] = selected_student['userID']
            logger.info("Logging in as a Student")
            st.switch_page('pages/00_Student_Home.py')
        else:
            st.warning("Please select a student first.")

col1, col2 = st.columns([4, 1])
with col1:
    selected_teacher = st.selectbox(
        "Teacher",
        options=teachers,
        format_func=user_label,
        index=None,
        placeholder="Select a teacher..."
    )
with col2:
    st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
    if st.button("Log in as Teacher", type='primary', use_container_width=True):
        if selected_teacher:
            st.session_state['authenticated'] = True
            st.session_state['role'] = 'teacher'
            st.session_state['first_name'] = selected_teacher['firstName']
            st.session_state['userID'] = selected_teacher['userID']
            st.switch_page('pages/10_Teacher_Home.py')
        else:
            st.warning("Please select a teacher first.")

col1, col2 = st.columns([4, 1])
with col1:
    selected_official = st.selectbox(
        "EU Official",
        options=officials,
        format_func=user_label,
        index=None,
        placeholder="Select an EU official..."
    )
with col2:
    st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
    if st.button("Log in as EU Official", type='primary', use_container_width=True):
        if selected_official:
            st.session_state['authenticated'] = True
            st.session_state['role'] = 'eu_official'
            st.session_state['first_name'] = selected_official['firstName']
            st.session_state['userID'] = selected_official['userID']
            st.switch_page('pages/20_EU_Official_Home.py')
        else:
            st.warning("Please select an EU official first.")