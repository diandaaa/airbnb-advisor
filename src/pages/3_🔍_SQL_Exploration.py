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
if st.sidebar.button("🌐 benharman.dev"):
    webbrowser.open_new_tab("https://benharman.dev")

conn = st.experimental_connection("listings_sqlite", type="sql")

st.title("🔍 SQL Exploration")


def refresh_data():
    for query_info in queries:
        # Use the value from JSON if it exists, otherwise execute the query
        if "value" in query_info:
            value = query_info["value"]
        else:
            try:
                result = conn.query(query_info["query"])
                value = result.iloc[0, 0] if not result.empty else "No result"
            except Exception as e:
                value = f"Error: {e}"

        # Format the text with the retrieved or given value
        query_info["text"] = query_info["text"].format(value=value)


def display_query_info(query_info):
    with st.container():
        # Display the main text
        st.markdown(query_info["text"])
        st.code(query_info["query"])

        # Expander for the logic
        with st.expander("💡 See logical explanation of steps", expanded=False):
            # Displaying each step in the logic
            for step in query_info["logic"]["steps"]:
                st.markdown(f"**Step {step['step']}:** {step['description']}")

            # Displaying notes
            st.markdown("**Notes:**")
            for note_title, note_description in query_info["logic"]["notes"].items():
                # Removing underscores and capitalizing each word in the title
                note_title_formatted = " ".join(
                    word.capitalize() for word in note_title.replace("_", " ").split()
                )
                st.markdown(f"- **{note_title_formatted}:** {note_description}")

        st.text("")


refresh_data()


if st.button("Refresh Data"):
    refresh_data()

for query_info in queries:
    display_query_info(query_info)
