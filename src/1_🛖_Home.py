import streamlit as st
import pandas as pd
from constants import AIRBNB_COLORS as COLORS
from sqlalchemy import func, literal, union_all
from database.models import (
    ListingsCore,
    RoomTypes,
    ListingsLocation,
    Neighborhoods,
    Cities,
)
from constants import CITIES
import utilities

st.set_page_config(
    page_title="Airbnb Dash | Home",
    page_icon=":hut:",
    layout="wide",
    initial_sidebar_state="auto",
    menu_items=None,
)

profile_image = utilities.get_image_with_encoding("assets/profile-image.jpg")

cities = CITIES
if "All" not in cities:
    cities.insert(0, "All")

# Configure the sidebar
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

# Define the SQL query
room_type_city_counts = pd.DataFrame(
    (
        conn.session.query(
            Cities.name.label("City"),
            RoomTypes.room_type.label("Room Type"),
            func.count(ListingsCore.listing_id).label("Count"),
        )
        .join(RoomTypes, RoomTypes.room_type_id == ListingsCore.room_type_id)
        .join(ListingsLocation, ListingsLocation.listing_id == ListingsCore.listing_id)
        .join(
            Neighborhoods,
            Neighborhoods.neighborhood_id == ListingsLocation.neighborhood_id,
        )
        .join(Cities, Cities.city_id == Neighborhoods.city_id)
        .group_by(Cities.name, RoomTypes.room_type)
    ).all()
)


print(room_type_city_counts.__class__)

room_type_counts = pd.concat(
    [
        room_type_city_counts.groupby("Room Type")
        .agg({"Count": "sum"})
        .assign(City="All")
        .reset_index(),
        room_type_city_counts,
    ],
    ignore_index=True,
)

# Pivot the room_type_counts DataFrame
pivot_room_type_counts = room_type_counts.pivot(
    index="Room Type", columns="City", values="Count"
)
pivot_room_type_counts.fillna(0, inplace=True)

text_col, chart_col1, chart_col2 = st.columns(3)

with text_col:
    """
    # Airbnb Advisor

    Welcome to my **Airbnb Advirsor** project. This app aims to provide actionable insights for Airbnb hosts to improve their listings. Whether you're new to hosting or a seasoned veteran, explore select cities and find ways to maximize your profitability, ratings, and visibility.

    ### 📘 Pages at a Glance

    - **📊 Charts & Metrics**: View relevant visuals covering several topics including review scores, amenities, and pricing.
    - **🗺️ Map**: Get a spatial overview of a specific city's listings arranged by neighborhood and their respective metrics.
    - **💻 SQL Exploration**: Dive into the SQL queries and database model that fuel this app's analytics.
    - **🤖 AI Chat**: Got specific questions? My AI assistant is here to answer specific questions about the data.
    - **📖 About**: Background on the data source, methodology, and the person behind this app.

    ### 📚 Data Source

    This app utilizes data from [Inside Airbnb](http://insideairbnb.com/), a project that focuses on the impact of Airbnb on residential communities. The data was last updated on March 6, 2023. Future updates to the app will be contingent upon new, comparable data releases.

    ### ⚠️ Disclaimer
    This app is an independent project and serves as an exploratory tool. While it aims to provide valuable insights, it is not a substitute for professional advice and nuanced understanding of individual listings.
    """

with chart_col1:
    st.bar_chart(pivot_room_type_counts[st.session_state.selected_city])

with chart_col2:
    st.text("To do...")
