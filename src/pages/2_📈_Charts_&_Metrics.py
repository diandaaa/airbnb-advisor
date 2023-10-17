import json

import streamlit as st
from millify import millify

import utilities
from charts import overview_charts, pricing_charts, reviews_charts
from constants import CITIES

# Load metrics data from the JSON file
with open("data/metrics.json", "r") as file:
    metrics_data = json.load(file)


# Function to determine the prefix
def get_prefix(value):
    return "-" if value < 0 else ""


# Configure the page
st.set_page_config(
    page_title="Airbnb Advisor | Charts",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="auto",
    menu_items=None,
)


# Configure the sidebar
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

selected_city = st.session_state.selected_city
selected_city_data = metrics_data.get(selected_city, metrics_data["All Cities"])

overview_tab, pricing_tab, reviews_tab = st.tabs(["Overview", "Pricing", "Reviews"])

with overview_tab:
    col1, col2, col3, col4 = st.columns(4)

    st.markdown("Note: Metrics are for Q1 2023 and are compared to Q1 2022.")

    col1.metric(
        "Active Listings",
        millify(selected_city_data["active_listings"]),
        delta=millify(selected_city_data["active_listings_delta"]),
    )

    col2.metric(
        "Active Hosts",
        millify(selected_city_data["active_hosts"]),
        delta=millify(selected_city_data["active_hosts_delta"]),
    )

    col3.metric(
        "Median Review Score",
        f"{selected_city_data['median_review_score']}/5",
        delta=round(selected_city_data["median_review_score_delta"], 2),
    )

    # Applying prefix logic for the overview metrics
    prefix_overview = get_prefix(selected_city_data["median_price"])
    formatted_delta = f"{prefix_overview}${millify(int(abs(selected_city_data['median_price_delta'])))}"

    col4.metric(
        "Median Nightly Price",
        f"${int(selected_city_data['median_price'])}",
        delta=formatted_delta,
    )

    st.altair_chart(
        overview_charts.chart_active_listings_hosts_age(conn.session, selected_city),
        use_container_width=True,
    )

    st.altair_chart(
        overview_charts.chart_room_types(conn.session, selected_city),
        use_container_width=True,
    )

with pricing_tab:
    col1, col2, col3, col4 = st.columns(4)

    # Access values directly from the selected city's data in the loaded JSON
    col1.metric(
        "Mean Price",
        f"${selected_city_data['mean_price']}",
        delta=f"${millify(abs(selected_city_data['mean_price_delta']))}",
    )

    col2.metric(
        "Mean New Listing Price",
        f"${selected_city_data['mean_new_listing_price']}",
        delta=f"${millify(abs(selected_city_data['mean_new_listing_price_delta']))}",
    )

    col3.metric(
        "Ninetieth Percentile Price",
        f"${selected_city_data['ninetieth_percentile_price']}",
        delta=f"${millify(abs(selected_city_data['ninetieth_percentile_price_delta']))}",
    )

    col4.metric(
        "Median Superhost Price",
        f"${selected_city_data['median_superhost_price']}",
        delta=f"${millify(abs(selected_city_data['median_superhost_price_delta']))}",
    )

    # Add any additional charts or elements here if needed


with reviews_tab:
    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Median Review Count",
        f"{selected_city_data['median_review_count']}",
        delta=f"{selected_city_data['median_review_count_delta']}",
    )

    col2.metric(
        "Mean Reviews Score",
        f"{selected_city_data['mean_reviews_score']}/5",
        delta=f"{selected_city_data['mean_reviews_score_delta']}",
    )

    col3.metric(
        "Mean Superhost Reviews Score",
        f"{selected_city_data['mean_superhost_reviews_score']}/5",
        delta=f"{selected_city_data['mean_superhost_reviews_score_delta']}",
    )

    col4.metric(
        "Superhost Percent",
        f"{selected_city_data['superhost_percent']}%",
        delta=f"{selected_city_data['superhost_percent_delta']}%",
    )
