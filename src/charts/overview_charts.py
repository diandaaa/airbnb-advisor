from datetime import datetime

import altair as alt
import pandas as pd
from dateutil.relativedelta import relativedelta
from sqlalchemy import func

from constants import COLORS
from database.models import (
    Cities,
    Hosts,
    ListingsCore,
    ListingsReviewsSummary,
    Neighborhoods,
    RoomTypes,
)
from utilities import load_chart_data_from_file


def calculate_age(start_date_str, end_date_str="2023-10-01"):
    if start_date_str is None:
        return None

    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
    delta = relativedelta(end_date, start_date)
    return delta.years


def chart_active_listings_hosts_age(session, city):
    print(f"Processing city: {city}")  # Logging the current city

    # Construct the chart name to match the JSON key
    chart_name = f"chart_active_listings_hosts_age_{city}"

    # Load chart data from JSON file
    data_values = load_chart_data_from_file(chart_name)

    # If data exists in the JSON file, use it
    if data_values:
        source = pd.DataFrame(data_values)
        print(f"Loaded data from JSON file for city: {city}")
    # Otherwise, perform the database query
    else:
        query = (
            session.query(
                ListingsCore, ListingsReviewsSummary, Hosts, Neighborhoods, Cities
            )
            .join(
                ListingsReviewsSummary,
                ListingsReviewsSummary.listing_id == ListingsCore.listing_id,
            )
            .join(Hosts, Hosts.host_id == ListingsCore.host_id)
            .join(
                Neighborhoods,
                Neighborhoods.neighborhood_id == ListingsCore.neighborhood_id,
            )
            .join(Cities, Cities.city_id == ListingsCore.city_id)
            .filter(ListingsCore.was_active_most_recent_quarter == 1)
        )

        if city != "All Cities":
            query = query.filter(Cities.city == city)

        data = []
        for lc, lrs, h, n, c in query:
            host_age = calculate_age(h.host_since)
            listing_age = calculate_age(lrs.first_review)

            if host_age is not None:
                data.append({"id": lc.host_id, "age": host_age, "type": "Host"})

            if listing_age is not None:
                data.append(
                    {"id": lc.listing_id, "age": listing_age, "type": "Listing"}
                )

        source = pd.DataFrame(data)

    # Check if DataFrame is empty and log it
    if source.empty:
        print(f"No data available for city: {city}")
        return None  # You might want to return None or some default chart here

    # Altair area chart
    chart = (
        alt.Chart(source)
        .mark_area(opacity=0.7)
        .encode(
            x=alt.X("age:O", title="Age"),
            y=alt.Y("count:Q", title="Count"),
            color=alt.Color(
                "type:N",
                scale=alt.Scale(domain=["Host", "Listing"], range=COLORS),
                legend=alt.Legend(title="Type", orient="top"),
            ),
        )
        .properties(
            title="Count of Active Listings and Hosts by Age",
        )
    )

    return chart


def chart_room_types(session, city):
    print(f"Processing room types for city: {city}")  # Logging the current city

    # Construct the chart name to match the JSON key
    chart_name = f"chart_room_types_{city}"

    # Load chart data from JSON file
    data_values = load_chart_data_from_file(chart_name)

    # If data exists in the JSON file, use it
    if data_values:
        source = pd.DataFrame(data_values)
        print(f"Loaded data from JSON file for city: {city}")
    # Otherwise, perform the database query
    else:
        query = (
            session.query(RoomTypes.room_type, func.count(ListingsCore.listing_id))
            .join(RoomTypes, RoomTypes.room_type_id == ListingsCore.room_type_id)
            .group_by(RoomTypes.room_type)
        )

        if city != "All Cities":
            query = query.filter(ListingsCore.city_id == Cities.city_id).filter(
                Cities.city == city
            )

        data = [{"Room Type": rt, "Count": count} for rt, count in query]

        source = pd.DataFrame(data)

    # Check if DataFrame is empty and log it
    if source.empty:
        print(f"No data available for city: {city}")
        return None  # You might want to return None or some default chart here

    # Altair bar chart
    chart = (
        alt.Chart(source)
        .mark_bar()
        .encode(
            x="Room Type",
            y="Count",
            color=alt.Color("Room Type:N", legend=alt.Legend(title="Room Type")),
        )
        .properties(
            title=f"Count of Listings by Room Type in {city}",
        )
    )

    return chart
