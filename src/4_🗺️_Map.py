import webbrowser

import streamlit as st

st.set_page_config(
    page_title="Airbnb Advisor | Map",
    page_icon=":world_map:",
    layout="centered",
    initial_sidebar_state="auto",
    menu_items=None,
)

# Configure the sidebar
st.sidebar.text("")
st.sidebar.text("")
st.sidebar.markdown("Developed by Ben Harman and powered by Streamlit.")
if st.sidebar.button("🧪 Source Code"):
    webbrowser.open_new_tab("https://github.com/benharmandev/airbnb-advisor")
if st.sidebar.button("🌐 BenHarman.dev"):
    webbrowser.open_new_tab("https://benharman.dev")
