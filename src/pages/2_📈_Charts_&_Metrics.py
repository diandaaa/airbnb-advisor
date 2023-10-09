import altair as alt
import streamlit as st
import pandas as pd
from constants import BENS_COLORS as COLORS
from millify import millify
from sqlalchemy import func
from database.models import (
    ListingsCore,
    RoomTypes,
    ListingsLocation,
    Neighborhoods,
    Cities,
    Amenities,
    ListingsReviewsSummary,
)
from constants import CITIES
import utilities


# Configure the page -----------------------------------------------------------
st.set_page_config(
    page_title="Airbnb Advisor | Charts",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="auto",
    menu_items=None,
)


cities = CITIES
if "All Cities" not in cities:
    cities.insert(0, "All Cities")


# Configure the sidebar --------------------------------------------------------
# Add session state variable for city selection
st.session_state.selected_city = st.sidebar.selectbox(
    "Which city will we explore?", cities
)

st.sidebar.text("")
st.sidebar.text("")
st.sidebar.markdown("Developed by Ben Harman and powered by Streamlit.")
st.sidebar.markdown("Visit my [website](https://benharman.dev/) for more!")
st.sidebar.text("")
st.sidebar.markdown(
    f"[![LinkedIn](data:image/png;base64,{utilities.get_image_with_encoding('assets/linkedin.png')})](https://github.com/benharmandev) &nbsp;&nbsp;&nbsp; [![GitHub](data:image/png;base64,{utilities.get_image_with_encoding('assets/github.png')})](https://github.com/benharmandev)",
    unsafe_allow_html=True,
)


# Establish a connection to the SQLite database
conn = st.experimental_connection(
    "listings_db",
    type="sql",
    url="sqlite:///data/listings.sqlite",  # SQLite connection URL
)
