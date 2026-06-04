# Idea borrowed from https://github.com/fsmosca/sample-streamlit-authenticator

# This file has functions to add links to the left sidebar based on the user's role.

import streamlit as st


# ---- General ----------------------------------------------------------------

def home_nav():
    st.sidebar.page_link("Home.py", label="Home", icon="🏠")


def about_page_nav():
    st.sidebar.page_link("pages/30_About.py", label="About", icon="🧠")


# ---- Role: student ------------------------------------------------

def student_home_nav():
    st.sidebar.page_link(
        "pages/00_Student_Home.py", label="Dashboard", icon="👤"
    )


def country_simulation_nav():
    st.sidebar.page_link(
        "pages/01_Country_Simulation.py", label="Country Simulation", icon="📍"
    )


def diagnostic_survey_nav():
    st.sidebar.page_link("pages/02_Diagnostic_Survey.py", label="Diagnostic Survey", icon="📋")


# ---- Role: teacher -----------------------------------------------------

def teacher_home_nav():
    st.sidebar.page_link(
        "pages/10_Teacher_Home.py", label="Dashboard", icon="👤"
    )

#make page that gets students in class
def my_students_nav():
    st.sidebar.page_link("pages/11_My_Students.py", label="My Students", icon="📋")

#make page for lessons
def lessons_nav():
    st.sidebar.page_link("pages/12_Lessons.py", label="Lessons", icon="📚")

#make page for analytics
def analytics_nav():
    st.sidebar.page_link(
        "pages/13_Analytics.py", label="Analytics", icon="📈"
    )


# ---- Role: administrator ----------------------------------------------------

def admin_home_nav():
    st.sidebar.page_link("pages/20_Admin_Home.py", label="System Admin", icon="🖥️")


def ml_model_mgmt_nav():
    st.sidebar.page_link(
        "pages/21_ML_Model_Mgmt.py", label="ML Model Management", icon="🏢"
    )

def new_ml_model_nav():
    st.sidebar.page_link(
        "pages/22_Prettier_ML.py", label="New ML Model", icon="📈"
    )

# ---- Sidebar assembly -------------------------------------------------------

def SideBarLinks(show_home=False):
    """
    Renders sidebar navigation links based on the logged-in user's role.
    The role is stored in st.session_state when the user logs in on Home.py.
    """

    # Logo appears at the top of the sidebar on every page
    st.sidebar.image("assets/logo.png", width=150)

    # If no one is logged in, send them to the Home (login) page
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.switch_page("Home.py")

    if show_home:
        home_nav()

    if st.session_state["authenticated"]:

        if st.session_state["role"] == "student":
            student_home_nav()
            country_simulation_nav()
            diagnostic_survey_nav()

        if st.session_state["role"] == "teacher":
            teacher_home_nav()
            my_students_nav()
            lessons_nav()
            analytics_nav()

        if st.session_state["role"] == "administrator":
            admin_home_nav()
            ml_model_mgmt_nav()
            new_ml_model_nav()
            
    # About link appears at the bottom for all roles
    about_page_nav()

    if st.session_state["authenticated"]:
        if st.sidebar.button("Logout"):
            del st.session_state["role"]
            del st.session_state["authenticated"]
            st.switch_page("Home.py")
