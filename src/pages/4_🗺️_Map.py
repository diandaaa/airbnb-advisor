import webbrowser

import altair as alt
import pandas as pd
import streamlit as st
from sqlalchemy import func, literal_column

from constants import CITIES
from database.models import Cities, Hosts, ListingsCore, Neighborhoods

# Set up streamlit page
st.set_page_config(
    page_title="Airbnb Advisor | Map",
    page_icon=":world_map:",
    layout="wide",
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

# Update the URL to include the selected city
geojson_url = f"https://raw.githubusercontent.com/benharmandev/airbnb-advisor/main/data/usa/{selected_city}/neighbourhoods.geojson"
geojson_data = alt.Data(url=geojson_url, format=alt.DataFormat(property="features"))


# Set the selected city to "Los Angeles" if "All Cities" is selected
if selected_city == "All Cities":
    selected_city = "Los Angeles"

# Query to get data from the database using conn.session
result = (
    conn.session.query(
        Neighborhoods.neighborhood,
        func.count(ListingsCore.listing_id).label("num_listings"),
        func.sum(Hosts.host_is_superhost).label("num_superhosts"),
    )
    .join(ListingsCore, ListingsCore.neighborhood_id == Neighborhoods.neighborhood_id)
    .join(Hosts, Hosts.host_id == ListingsCore.host_id)
    .filter(
        Neighborhoods.city_id
        == (conn.session.query(Cities.city_id).filter_by(city=selected_city).first()[0])
    )
    .group_by(Neighborhoods.neighborhood)
    .all()
)

# Process the result and pass it to the Altair chart for visualization
neighborhood_data = pd.DataFrame(result)


# Visualize the map
map_chart = (
    alt.Chart(geojson_data)
    .mark_geoshape(stroke="rgba(49, 51, 63, 0.2)", strokeWidth=1)
    .encode(
        color="num_listings:Q",
        tooltip=["properties.neighbourhood:N", "num_listings:Q", "num_superhosts:Q"],
    )
    .transform_lookup(
        lookup="properties.neighbourhood",
        from_=alt.LookupData(
            neighborhood_data, "neighborhood", ["num_listings", "num_superhosts"]
        ),
    )
    .properties(width="container", height=600)
)
st.altair_chart(map_chart, use_container_width=True)
