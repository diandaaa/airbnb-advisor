import json
import os
import webbrowser

import altair as alt
import geopandas as gpd
import shapely.geometry as sg
import shapely.ops as so
import sqlalchemy
import streamlit as st

from constants import CITIES
from database.models import Cities, ListingsCore

# Set up streamlit page
st.set_page_config(
    page_title="Airbnb Advisor | Map",
    page_icon=":world_map:",
    layout="centered",
    initial_sidebar_state="auto",
    menu_items=None,
)

conn = st.experimental_connection("listings_sqlite", type="sql")

# Configure the sidebar
st.sidebar.text("")
st.sidebar.text("")
st.sidebar.markdown("Developed by Ben Harman and powered by Streamlit.")
if st.sidebar.button("🌐 benharman.dev"):
    webbrowser.open_new_tab("https://benharman.dev")


st.title("🗺️ Airbnb Advisor | Map")

# Add session state variable for city selection
selected_city = st.selectbox("Which city would you like to explore?", CITIES)

# Set the selected city to "Los Angeles" if "All Cities" is selected
if selected_city == "All Cities":
    selected_city = "Los Angeles"

# Update the URL to include the selected city
geojson_url = f"https://raw.githubusercontent.com/benharmandev/airbnb-advisor/main/data/usa/{selected_city}/neighbourhoods.geojson"

geojson_data = alt.Data(url=geojson_url, format=alt.DataFormat(property="features"))

map = alt.Chart(geojson_data).mark_geoshape().encode(color="properties.neighbourhood:N")
st.altair_chart(map, use_container_width=True, theme="streamlit")
