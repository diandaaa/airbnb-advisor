import json
import os
import webbrowser

import altair as alt
import geopandas as gpd
import shapely.geometry as sg
import shapely.ops as so
import sqlalchemy
import streamlit as st

import constants
from database.models import Cities, ListingsCore

# Set up streamlit page
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
if st.sidebar.button("🌐 benharman.dev"):
    webbrowser.open_new_tab("https://benharman.dev")

st.title("🗺️ Airbnb Advisor | Map")

conn = st.experimental_connection("listings_sqlite", type="sql")


import json

import geopandas as gpd
import plotly.express as px
import streamlit as st

# # Load the GeoJSON file into a GeoDataFrame
# geojson_file_path = "data/usa/Cambridge/neighbourhoods.geojson"
# gdf = gpd.read_file(geojson_file_path)

# # Creating the choropleth map using Plotly
# fig = px.choropleth_mapbox(
#     gdf,
#     geojson=gdf.geometry,
#     locations=gdf.index,
#     color="neighbourhood",  # Assuming you want to color by neighbourhood
#     hover_name="neighbourhood",
#     mapbox_style="carto-positron",
#     center={"lat": 42.373611, "lon": -71.109733},
#     zoom=12,
#     title="Neighbourhoods in Cambridge",
# )


# # Display the map in Streamlit
# st.plotly_chart(fig, use_container_width=True)
