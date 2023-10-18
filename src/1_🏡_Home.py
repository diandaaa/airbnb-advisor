import webbrowser

import altair as alt
import pandas as pd
import streamlit as st
from millify import millify
from sqlalchemy import func

from constants import COLORS
from database.models import Amenities, Cities, ListingsCore, Neighborhoods

# Configure the page -----------------------------------------------------------
st.set_page_config(
    page_title="Airbnb Dash | Home",
    page_icon="🏡",
    layout="wide",
    initial_sidebar_state="auto",
    menu_items=None,
)


# Configure the sidebar --------------------------------------------------------
st.sidebar.text("")
st.sidebar.text("")
st.sidebar.markdown("Developed by Ben Harman and powered by Streamlit.")
if st.sidebar.button("🌐 benharman.dev"):
    webbrowser.open_new_tab("https://benharman.dev")

# Establish a connection to the SQLite database
conn = st.experimental_connection(
    "listings_db",
    type="sql",
    url="sqlite:///data/listings.sqlite",  # SQLite connection URL
)


# Generate metrics--------------------------------------------------------------
listings_count = conn.session.query(func.count(ListingsCore.listing_id)).scalar()
amenities_count = conn.session.query(func.count(Amenities.amenity_id)).scalar()
cities_count = conn.session.query(func.count(Cities.city_id)).scalar()
neighborhoods_count = conn.session.query(
    func.count(Neighborhoods.neighborhood_id)
).scalar()


# Generate listings count by city chart ----------------------------------------
# Define the listings count SQL query
listings_city_counts = pd.DataFrame(
    (
        conn.session.query(
            Cities.city.label("City"),
            func.count(ListingsCore.listing_id).label("Count"),
        )
        .join(
            Neighborhoods, Neighborhoods.neighborhood_id == ListingsCore.neighborhood_id
        )
        .join(Cities, Cities.city_id == ListingsCore.city_id)
        .group_by(Cities.city)
    ).all()
)


listings_city_counts_chart = (
    alt.Chart(listings_city_counts, title="Listings by City")
    .mark_bar(
        opacity=0.7,
        color=COLORS[0],
    )
    .encode(
        x=alt.X("Count", sort="-x", axis=alt.Axis(title=None)),
        y=alt.Y("City", sort="-x", axis=alt.Axis(title=None)),
    )
)


# Generate page content --------------------------------------------------------
st.title("Airbnb Advisor")

text_col, padding, chart_col = st.columns((10, 2, 10))

with text_col:
    """
    Welcome to my **Airbnb Advisor** project. This app explores a huge set of Airbnb listings and aims to provide actionable insights for hosts. Whether you're new to hosting or a seasoned veteran, explore select cities and find ways to maximize your profitability, ratings, and visibility.

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

with chart_col:
    st.markdown("### 🗃️ Dataset Overview")

    metric1, metric2, metric3 = st.columns(3)
    metric1.metric("Unique Areas", cities_count)
    metric2.metric("Neighborhoods", neighborhoods_count)
    metric3.metric("Listings", millify(listings_count))

    st.markdown(
        "First review was on **May 3, 2009** and data was last updated on **March 31, 2023**. Some cities had data up to May 17th but were excluded to only keep complete quarters. Listings with no reviews in or after 2022 were deemed inactive and removed. Because I am primarily interested in studying short term rentals (STRs), listings with 7+ nights required for a booking were also filtered out. Host and listing IDs were anonymized and listing geocoordinates removed for privacy."
    )

    st.altair_chart(listings_city_counts_chart, use_container_width=True)
