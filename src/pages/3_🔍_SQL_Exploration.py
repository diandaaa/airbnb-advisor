import json
import webbrowser

import pandas as pd
import streamlit as st

# Load queries from JSON file
with open("data/exploration_queries.json", "r") as file:
    queries = json.load(file)

st.set_page_config(
    page_title="Airbnb Advisor | SQL Exploration",
    page_icon="🔍",
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

conn = st.experimental_connection("listings_sqlite", type="sql")

st.title("🔍 SQL Exploration")


if st.button("Refresh Data"):
    for query_info in queries:
        try:
            result = conn.query(query_info["query"])
            value = result.iloc[0, 0] if not result.empty else "No result"
            query_info["text"] = query_info["text"].format(value=value)
        except Exception as e:
            query_info["text"] = f"Error: {e}"

for query_info in queries:
    with st.container():
        st.markdown(query_info["text"])
        st.code(query_info["query"], language="sql")
