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
    page_title="Airbnb Dash | Home",
    page_icon=":hut:",
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
            Cities.name.label("City"),
            func.count(ListingsCore.listing_id).label("Count"),
        )
        .join(ListingsLocation, ListingsLocation.listing_id == ListingsCore.listing_id)
        .join(
            Neighborhoods,
            Neighborhoods.neighborhood_id == ListingsLocation.neighborhood_id,
        )
        .join(Cities, Cities.city_id == Neighborhoods.city_id)
        .group_by(Cities.name)
    ).all()
)

listings_city_counts_chart = (
    alt.Chart(listings_city_counts, title="Listings by City")
    .mark_bar(
        opacity=0.7,
        color=COLORS["nature-green"],
    )
    .encode(
        x=alt.X("Count", sort="-x", axis=alt.Axis(title=None)),
        y=alt.Y("City", sort="-x", axis=alt.Axis(title=None)),
    )
)

# Generate room type counts by city chart --------------------------------------
# Define the room type counts SQL query
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

# Add an "All Cities" city which sums room type totals across cities
room_type_counts = pd.concat(
    [
        room_type_city_counts.groupby("Room Type")
        .agg({"Count": "sum"})
        .assign(City="All Cities")
        .reset_index(),
        room_type_city_counts,
    ],
    ignore_index=True,
)

# Pivot the room_type_counts DataFrame
pivot_room_type_counts = room_type_counts.pivot(
    index="Room Type", columns="City", values="Count"
)

# Fill NaN values with 0
pivot_room_type_counts.fillna(0, inplace=True)

# Get the room type counts filtered for the selected city
selected_city_room_type_counts = pivot_room_type_counts[
    st.session_state.selected_city
].reset_index()
selected_city_room_type_counts.columns = ["Room Type", "Count"]

# Set the chart title
title_text = f"Room Type Counts for {st.session_state.selected_city}"

# Create chart
room_type_counts_chart = (
    alt.Chart(
        selected_city_room_type_counts,
        title=title_text,
    )
    .mark_bar(
        opacity=0.7,
        color=COLORS["nature-green"],
    )
    .encode(
        x=alt.X("Count:Q", sort="-x", axis=alt.Axis(title=None)),
        y=alt.Y("Room Type:O", sort="-x", axis=alt.Axis(title=None)),
    )
)


# Generate active listings chart ------------------------------------------------
# Define the active listings SQL query
first_review_date_counts = pd.DataFrame(
    conn.session.query(
        Cities.name.label("City"),
        ListingsReviewsSummary.first_review.label("First Review Date"),
        func.count(ListingsReviewsSummary.listing_id).label("Count"),
    )
    .join(
        ListingsLocation,
        ListingsLocation.listing_id == ListingsReviewsSummary.listing_id,
    )
    .join(
        Neighborhoods,
        Neighborhoods.neighborhood_id == ListingsLocation.neighborhood_id,
    )
    .join(Cities, Cities.city_id == Neighborhoods.city_id)
    .filter(ListingsReviewsSummary.first_review.isnot(None))
    .group_by(ListingsReviewsSummary.first_review, Cities.name)
    .all()
)

# Convert 'First Review Date' to datetime and extract quarters
first_review_date_counts["First Review Date"] = pd.to_datetime(
    first_review_date_counts["First Review Date"]
)
first_review_date_counts["Quarter"] = first_review_date_counts[
    "First Review Date"
].dt.to_period("Q")

# Filter for city based on st.session_state.selected_city
if st.session_state.selected_city != "All Cities":
    first_review_date_counts = first_review_date_counts[
        first_review_date_counts["City"] == st.session_state.selected_city
    ]

# Group by quarter after filtering for the city and get counts
review_date_counts_grouped = (
    first_review_date_counts.groupby("Quarter").agg({"Count": "sum"}).reset_index()
)
review_date_counts_grouped["Quarter"] = review_date_counts_grouped[
    "Quarter"
].dt.to_timestamp()  # Convert back to timestamp for plotting

# Compute the cumulative sum for the 'Count' column
review_date_counts_grouped["Cumulative Count"] = review_date_counts_grouped[
    "Count"
].cumsum()

# Extend the dataframe for cumulative counts
cumulative_df = review_date_counts_grouped.copy()
cumulative_df["Value"] = cumulative_df["Count"].cumsum()  # Compute cumulative sum
cumulative_df["Type"] = "Cumulative Listings"

# Adjust the original dataframe for new listings
review_date_counts_grouped["Type"] = "New Listings"
review_date_counts_grouped.rename(columns={"Count": "Value"}, inplace=True)

# Combine the dataframes so that "Cumulative Listings" are first, ensuring they are plotted beneath "New Listings"
combined_df = pd.concat([cumulative_df, review_date_counts_grouped], ignore_index=True)

# Modify the subtitle of the chart properties
subtitle_text = (
    f"Filtered for Listings Active in Q1 2023 ({st.session_state.selected_city})"
)

# Altair chart with encoded color for the legend
active_listings_chart = (
    alt.Chart(combined_df)
    .mark_area(opacity=0.7)
    .encode(
        x=alt.X("Quarter:T", title=None),
        y=alt.Y("Value:Q", title=None, stack=None),
        color=alt.Color(
            "Type:N",
            scale=alt.Scale(
                domain=["New Listings", "Cumulative Listings"],
                range=[COLORS["nature-green"], COLORS["tiffany-blue"]],
            ),
            legend=alt.Legend(title=None, orient="top"),
        ),
        tooltip=["Quarter:T", "Value:Q"],
    )
    .properties(
        title={
            "text": "Listings by Quarter of First Review",
            "subtitle": subtitle_text,
        }
    )
    .configure_axis(
        domain=False,  # This removes the border around the chart
        ticks=False,  # This removes the ticks from the axes
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

    metric1, metric2, metric3, metric4 = st.columns(4)
    metric1.metric("Listings", millify(listings_count))
    metric2.metric("Cities", millify(cities_count))
    metric3.metric("Neighborhoods", millify(neighborhoods_count))
    metric4.metric("Amenities", millify(amenities_count))

    st.markdown(
        "First review was on **May 3, 2009** and data was last updated on **March 28, 2023**."
    )

    st.text("")

    st.altair_chart(listings_city_counts_chart, use_container_width=True)

    st.altair_chart(room_type_counts_chart, use_container_width=True)

    st.altair_chart(active_listings_chart, use_container_width=True)
