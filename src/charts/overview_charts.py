from datetime import datetime

import altair as alt

alt.data_transformers.enable("vegafusion")

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
                data.append({"id": lc.host_id, "age": host_age, "type": "Hosts"})

            if listing_age is not None:
                data.append(
                    {"id": lc.listing_id, "age": listing_age, "type": "Listings"}
                )

        source = pd.DataFrame(data)

        if source.empty:
            print(f"No data available for city: {city}")
            return None

        # Grouping by 'age' and 'type' and counting the occurrences
        source = source.groupby(["age", "type"]).size().reset_index(name="count")

    # Check if DataFrame is empty and log it
    if source.empty:
        print(f"No data available for city: {city}")
        return None

    # Altair area chart
    chart = (
        alt.Chart(source)
        .mark_line()
        .encode(
            x=alt.X("age:O", title=None),
            y=alt.Y("count:Q", title=None),
            color=alt.Color(
                "type:N",
                scale=alt.Scale(domain=["Hosts", "Listings"], range=COLORS),
                legend=alt.Legend(title=None, orient="top"),
            ),
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
        .mark_bar(opacity=0.7)
        .encode(
            x=alt.X("Room Type", title=None),
            y=alt.Y("Count:Q", axis=alt.Axis(tickCount=5, format=",.0f", title=None)),
            color=alt.Color(
                "Room Type:N",
                scale=alt.Scale(range=COLORS),
                legend=alt.Legend(title=None, orient="top"),
            ),
        )
    )

    return chart


def chart_neighborhood_listings_count(session, city):
    print(f"Processing listing counts by neighborhoods for city: {city}")

    # Construct the chart name to match the JSON key
    chart_name = f"chart_neighborhood_listings_count_{city}"

    # Load chart data from JSON file
    data_values = load_chart_data_from_file(chart_name)

    # If data exists in the JSON file, use it
    if data_values:
        source = pd.DataFrame(data_values)
        print(f"Loaded data from JSON file for city: {city}")
    else:
        query = (
            session.query(
                Neighborhoods.neighborhood, func.count(ListingsCore.listing_id)
            )
            .join(
                ListingsCore,
                ListingsCore.neighborhood_id == Neighborhoods.neighborhood_id,
            )
            .group_by(Neighborhoods.neighborhood)
        )

        if city != "All Cities":
            query = query.filter(ListingsCore.city_id == Cities.city_id).filter(
                Cities.city == city
            )

        listing_counts = [
            {"Neighborhood": n, "Listing Count": count} for n, count in query
        ]

        source = pd.DataFrame(listing_counts)

        # Optionally: Save the new data to a JSON file here

    # Check if DataFrame is empty and log it
    if source.empty:
        print(f"No data available for city: {city}")
        return None  # You might want to return None or some default chart here

    # Altair bar chart
    chart = (
        alt.Chart(source)
        .mark_bar(opacity=0.7)
        .encode(
            x=alt.X(
                "Neighborhood:N", axis=alt.Axis(labelAngle=-90), title=None, sort="-y"
            ),  # Explicitly sort bars based on the y-value
            y=alt.Y(
                "Listing Count:Q", axis=alt.Axis(tickCount=5, title="Listing Count")
            ),
            color=alt.Color(
                "Neighborhood:N",
                legend=None,  # No legend due to a large number of neighborhoods
            ),
        )
        .properties(
            width=600,
            height=400,
        )
    )

    return chart
