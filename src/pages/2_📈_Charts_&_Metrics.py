import altair as alt
import pandas as pd
import streamlit as st
from millify import millify
from sqlalchemy import func

import utilities
from charts import overview_charts, pricing_charts
from constants import BENS_COLORS as COLORS
from constants import CITIES
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

    st.altair_chart(
        overview_charts.chart_active_listings_hosts_age(
            conn.session, st.session_state.selected_city
        ),
        use_container_width=True,
    )

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

    st.altair_chart(
        pricing_charts.chart_price_dist_by_room_type(
            conn.session, st.session_state.selected_city
        )
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
