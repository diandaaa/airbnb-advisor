import altair as alt
import streamlit as st
import pandas as pd
from constants import BENS_COLORS as COLORS
from millify import millify
from sqlalchemy import func, extract, text
from datetime import datetime
from database.models import (
    ListingsCore,
    RoomTypes,
    ListingsLocation,
    Neighborhoods,
    Cities,
    Amenities,
    ListingsReviewsSummary,
    Hosts,
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


# Generate overview metrics -----------------------------------------------------
# Get the two most recent quarters
quarters = (
    conn.session.query(
        extract("year", ListingsReviewsSummary.first_review).label("year"),
        extract("quarter", ListingsReviewsSummary.first_review).label("quarter"),
    )
    .distinct()
    .order_by(text("year desc"), text("quarter desc"))
    .limit(2)
    .all()
)

current_qtr = quarters[0]

# Calculate metrics for the current and the last quarter

# Total Listings
listings_current_qtr = (
    conn.session.query(func.count(ListingsCore.listing_id))
    .join(
        ListingsReviewsSummary,
        ListingsCore.listing_id == ListingsReviewsSummary.listing_id,
    )
    .filter(
        extract("year", ListingsReviewsSummary.first_review) == current_qtr.year,
        extract("quarter", ListingsReviewsSummary.first_review) == current_qtr.quarter,
    )
    .scalar()
)

all_time_listings = conn.session.query(func.count(ListingsCore.listing_id)).scalar()

hosts_current_qtr = (
    conn.session.query(func.count(Hosts.host_id))
    .filter(
        extract("year", Hosts.host_since) == current_qtr.year,
        extract("quarter", Hosts.host_since) == current_qtr.quarter,
    )
    .scalar()
)

all_time_hosts = conn.session.query(func.count(Hosts.host_id)).scalar()

review_scores_qtr = (
    conn.session.query(ListingsReviewsSummary.review_scores_rating)
    .join(
        ListingsCore,
        ListingsCore.listing_id == ListingsReviewsSummary.listing_id,
    )
    .filter(
        extract("year", ListingsReviewsSummary.first_review) == current_qtr.year,
        extract("quarter", ListingsReviewsSummary.first_review) == current_qtr.quarter,
    )
    .order_by(ListingsReviewsSummary.review_scores_rating)
    .all()
)

median_review_score_current_qtr = (
    review_scores_qtr[len(review_scores_qtr) // 2].review_scores_rating
    if len(review_scores_qtr) % 2 == 1
    else (
        review_scores_qtr[len(review_scores_qtr) // 2 - 1].review_scores_rating
        + review_scores_qtr[len(review_scores_qtr) // 2].review_scores_rating
    )
    / 2
)

all_review_scores = (
    conn.session.query(ListingsReviewsSummary.review_scores_rating)
    .order_by(ListingsReviewsSummary.review_scores_rating)
    .all()
)

all_time_median_review_score = (
    all_review_scores[len(all_review_scores) // 2].review_scores_rating
    if len(all_review_scores) % 2 == 1
    else (
        all_review_scores[len(all_review_scores) // 2 - 1].review_scores_rating
        + all_review_scores[len(all_review_scores) // 2].review_scores_rating
    )
    / 2
)

prices_qtr = (
    conn.session.query(ListingsCore.price)
    .join(
        ListingsReviewsSummary,
        ListingsCore.listing_id == ListingsReviewsSummary.listing_id,
    )  # replace 'some_id' with the actual join condition
    .filter(
        extract("year", ListingsReviewsSummary.first_review) == current_qtr.year,
        extract("quarter", ListingsReviewsSummary.first_review) == current_qtr.quarter,
    )
    .order_by(ListingsCore.price)
    .all()
)


median_price_current_qtr = (
    prices_qtr[len(prices_qtr) // 2].price
    if len(prices_qtr) % 2 == 1
    else (
        prices_qtr[len(prices_qtr) // 2 - 1].price
        + prices_qtr[len(prices_qtr) // 2].price
    )
    / 2
)

all_prices = conn.session.query(ListingsCore.price).order_by(ListingsCore.price).all()

all_time_median_price = (
    all_prices[len(all_prices) // 2].price
    if len(all_prices) % 2 == 1
    else (
        all_prices[len(all_prices) // 2 - 1].price
        + all_prices[len(all_prices) // 2].price
    )
    / 2
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
        title={"text": "Total Listings", "subtitle": "By Quarter of First Review"}
    )
    .configure_axis(
        domain=False,  # This removes the border around the chart
        ticks=False,  # This removes the ticks from the axes
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
).properties(width=300, height=200)


average_price_superhost = (
    conn.session.query(func.avg(ListingsCore.price))
    .join(Hosts, Hosts.host_id == ListingsCore.host_id)
    .filter(Hosts.host_is_superhost == 1)
    .scalar()
)

average_price_non_superhost = (
    conn.session.query(func.avg(ListingsCore.price))
    .join(Hosts, Hosts.host_id == ListingsCore.host_id)
    .filter(Hosts.host_is_superhost == 0)
    .scalar()
)

superhost_premium = average_price_superhost - average_price_non_superhost


st.title(f"📈 Charts & Metrics | {st.session_state.selected_city}")

st.markdown(
    "Note: The dataset is prefiltered for listings active in Q1 2023. Metrics deltas only reflect changes based on listings that were active both in the past and in Q1 2023."
)

overview_tab, pricing_tab, reviews_tab = st.tabs(["Overview", "Pricing", "Reviews"])

with overview_tab:
    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Listings",
        millify(all_time_listings),
        delta=f"{millify(listings_current_qtr)} New Listings",
        delta_color="off",
    )
    col2.metric(
        "Total Hosts",
        millify(all_time_hosts),
        delta=f"{millify(hosts_current_qtr)} New Hosts",
        delta_color="off",
    )
    col3.metric(
        "Median Review Score",
        f"{all_time_median_review_score}/5",
        delta=round(median_review_score_current_qtr - all_time_median_review_score, 2),
    )

    price_delta = median_price_current_qtr - all_time_median_price

    # Determine the prefix based on the sign of the delta
    prefix = "-" if price_delta < 0 else ""

    col4.metric(
        "Median Nightly Price",
        f"${millify(all_time_median_price)}",
        delta=f"{prefix}${millify(abs(price_delta))}",
    )

    st.altair_chart(active_listings_chart, use_container_width=True)

    chart1, chart2 = st.columns(2)

    chart1.altair_chart(room_type_counts_chart, use_container_width=False)
    chart2.altair_chart(room_type_counts_chart, use_container_width=False)

with pricing_tab:
    col1, col2, col3, col4 = st.columns(4)


with reviews_tab:
    st.header("Reviews")
