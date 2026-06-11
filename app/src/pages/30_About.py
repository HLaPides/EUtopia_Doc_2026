import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

st.markdown("""
# 🌌 Welcome to EUtopia 🌌

## Summer 2026 Belgium DoC Project 🇧🇪


### Team Members 👩‍🚀
Sidra Ansari, Vineeth Kanpa, Bennett LaPides, & Meghan Paclob

EUtopia is an interactive civic education platform that helps people understand the European Union through personalized learning, simulations, quizzes, and real-world data. Rather than presenting long, text-heavy lessons, our platform makes EU education engaging, relevant, and accessible.

You can experience the platform from multiple perspectives:

**Login as a Student** to complete personalized lessons, track your progress, take assessments, and experiment with election turnout simulations.

**Login as a Teacher** to create educational content, manage learning experiences, and monitor student engagement and performance.

**Login as an EU Official/Moderator** to review submitted content, oversee platform quality, and analyze platform-wide learning trends and participation metrics.

Behind the scenes, EUtopia combines a relational database, REST APIs, interactive visualizations, and machine learning models that predict voter turnout using demographic and political indicators.

Our mission is simple: make civic education engaging, data-driven, and meaningful so that future European citizens feel informed, confident, and ready to participate in democracy.

*EUtopia: learn the EU by experiencing it.* 🇪🇺
""")



st.title("👩‍🚀 The Team")
st.write("Meet the people behind EUtopia.")

col1, col2 = st.columns(2)
col3, col4 = st.columns(2)

with col1:
    st.image("assets/sidra.png", width=250)
    st.subheader("Sidra Ansari")
    st.write("I am a rising fourth year studying electrical & computer engineering. I contributed to EUtopia through backend development, database design, API implementation, and user interface improvements.")

with col2:
    st.image("assets/vineeth.png", width=250)
    st.subheader("Vineeth Kanpa")
    st.write("Machine Learning & Backend")

with col3:
    st.image("assets/bennett.png", width=250)
    st.subheader("Bennett LaPides")
    st.write("\I am a rising second year studying computer science. I contributed to EUtopia through the voter turnout model and ui design")

with col4:
    st.image("assets/meghan.png", width=250)
    st.subheader("Meghan Paclob")
    st.write("Testing & Documentation")




if st.button("Return to Home", type="primary"):
    st.switch_page("Home.py")