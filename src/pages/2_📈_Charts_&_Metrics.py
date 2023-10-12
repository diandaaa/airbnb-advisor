import altair as alt
import pandas as pd
import streamlit as st
from millify import millify
from sqlalchemy import func

import utilities
from charts import overview_charts
from constants import BENS_COLORS as COLORS
from constants import CITIES
from database.models import (
    Cities,
    Hosts,
    ListingsCore,
    ListingsLocation,
    ListingsReviewsSummary,
    Neighborhoods,
    RoomTypes,
)
from metrics import overview_metrics, pricing_metrics, reviews_metrics


# Function to determine the prefix
def get_prefix(value):
    return "-" if value < 0 else ""


# Configure the page -----------------------------------------------------------
st.set_page_config(
    page_title="Airbnb Advisor | Charts",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="auto",
    menu_items=None,
)


# Configure the sidebar --------------------------------------------------------
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

st.title(f"📈 Charts & Metrics")

# Add session state variable for city selection
st.session_state.selected_city = st.selectbox(
    "Which city would you like to explore?", CITIES
)


# Generate active listings chart ------------------------------------------------
# Define the active listings SQL query
first_review_date_counts = pd.DataFrame(
    conn.session.query(
        Cities.city.label("City"),
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
    .group_by(ListingsReviewsSummary.first_review, Cities.city)
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
            Cities.city.label("City"),
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
        .group_by(Cities.city, RoomTypes.room_type)
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

overview_tab, pricing_tab, reviews_tab = st.tabs(["Overview", "Pricing", "Reviews"])

with overview_tab:
    col1, col2, col3, col4 = st.columns(4)

    st.markdown("Note: Metrics are for Q1 2023 and are compared to Q1 2022.")

    col1.metric(
        "Active Listings",
        millify(
            overview_metrics.active_listings(
                conn.session, st.session_state.selected_city
            )
        ),
        delta=f"{millify(overview_metrics.active_listings_delta(conn.session, st.session_state.selected_city))}",
    )
    col2.metric(
        "Active Hosts",
        millify(
            overview_metrics.active_hosts(conn.session, st.session_state.selected_city)
        ),
        delta=f"{millify(overview_metrics.active_hosts_delta(conn.session, st.session_state.selected_city))}",
    )
    col3.metric(
        "Median Review Score",
        f"{overview_metrics.median_review_score(conn.session, st.session_state.selected_city)}/5",
        delta=round(
            overview_metrics.median_review_score_delta(
                conn.session, st.session_state.selected_city
            ),
            0,
        ),
    )

    # Applying prefix logic for the overview metrics
    prefix_overview = get_prefix(
        overview_metrics.median_price(conn.session, st.session_state.selected_city)
    )
    delta_value = overview_metrics.median_price_delta(
        conn.session, st.session_state.selected_city
    )
    formatted_delta = f"{prefix_overview}${millify(int(abs(delta_value)))}"

    col4.metric(
        "Median Nightly Price",
        f"${int(overview_metrics.median_price(conn.session, st.session_state.selected_city))}",
        delta=formatted_delta,
    )

    st.altair_chart(active_listings_chart, use_container_width=True)
    st.altair_chart(room_type_counts_chart, use_container_width=True)

# Applying prefix logic for the pricing tab metrics
with pricing_tab:
    col1, col2, col3, col4 = st.columns(4)
    prefix_mean_price = get_prefix(
        pricing_metrics.mean_price_delta(conn.session, st.session_state.selected_city)
    )
    mean_price_value = int(
        pricing_metrics.mean_price(conn.session, st.session_state.selected_city)
    )
    mean_price_delta_value = int(
        pricing_metrics.mean_price_delta(conn.session, st.session_state.selected_city)
    )

    col1.metric(
        "Mean Price",
        f"${mean_price_value}",
        delta=f"{prefix_mean_price}${millify(abs(mean_price_delta_value))}",
    )

    prefix_new_listing_price = get_prefix(
        pricing_metrics.mean_new_listing_price_delta(
            conn.session, st.session_state.selected_city
        )
    )
    new_listing_price_value = int(
        pricing_metrics.mean_new_listing_price(
            conn.session, st.session_state.selected_city
        )
    )
    new_listing_price_delta_value = int(
        pricing_metrics.mean_new_listing_price_delta(
            conn.session, st.session_state.selected_city
        )
    )

    col2.metric(
        "Mean New Listing Price",
        f"${new_listing_price_value}",
        delta=f"{prefix_new_listing_price}${millify(abs(new_listing_price_delta_value))}",
    )

    prefix_ninetieth_percentile = get_prefix(
        pricing_metrics.ninetieth_percentile_price_delta(
            conn.session, st.session_state.selected_city
        )
    )
    ninetieth_percentile_price_value = int(
        pricing_metrics.ninetieth_percentile_price(
            conn.session, st.session_state.selected_city
        )
    )
    ninetieth_percentile_price_delta_value = int(
        pricing_metrics.ninetieth_percentile_price_delta(
            conn.session, st.session_state.selected_city
        )
    )

    col3.metric(
        "Ninetieth Percentile Price",
        f"${ninetieth_percentile_price_value}",
        delta=f"{prefix_ninetieth_percentile}${millify(abs(ninetieth_percentile_price_delta_value))}",
    )

    prefix_superhost = get_prefix(
        pricing_metrics.median_superhost_price_delta(
            conn.session, st.session_state.selected_city
        )
    )
    median_superhost_price_value = int(
        pricing_metrics.median_superhost_price(
            conn.session, st.session_state.selected_city
        )
    )
    median_superhost_price_delta_value = int(
        pricing_metrics.median_superhost_price_delta(
            conn.session, st.session_state.selected_city
        )
    )

    col4.metric(
        "Median Superhost Price",
        f"${median_superhost_price_value}",
        delta=f"{prefix_superhost}${millify(abs(median_superhost_price_delta_value))}",
    )

    overview_charts.chart_price_dist_by_room_type(
        conn.session, st.session_state.selected_city
    )


with reviews_tab:
    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Median Review Count",
        f"{round(reviews_metrics.median_review_count(conn.session, st.session_state.selected_city), 2)}",
        delta=f"{round(reviews_metrics.median_review_count_delta(conn.session, st.session_state.selected_city), 2)}",
    )

    col2.metric(
        "Mean Reviews Score",
        f"{round(reviews_metrics.mean_reviews_score(conn.session, st.session_state.selected_city), 2)}/5",
        delta=f"{round(reviews_metrics.mean_reviews_score_delta(conn.session, st.session_state.selected_city), 2)}",
    )

    col3.metric(
        "Mean Superhost Reviews Score",
        f"{round(reviews_metrics.mean_superhost_reviews_score(conn.session, st.session_state.selected_city), 2)}/5",
        delta=f"{round(reviews_metrics.mean_superhost_reviews_score_delta(conn.session, st.session_state.selected_city), 2)}",
    )

    col4.metric(
        "Superhost Percent",
        f"{round(reviews_metrics.superhost_percent(conn.session, st.session_state.selected_city))}%",
        delta=f"{round(reviews_metrics.superhost_percent_delta(conn.session, st.session_state.selected_city))}%",
    )
