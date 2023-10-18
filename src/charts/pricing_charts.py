import altair as alt
import pandas as pd
from sqlalchemy import func

from constants import COLORS
from database.models import Cities, ListingsCore, Neighborhoods, RoomTypes
from utilities import load_chart_data_from_file


def chart_mean_room_type_prices(session, city):
    print(
        f"Processing price distribution by room types for city: {city}"
    )  # Logging the current city

    # Construct the chart name to match the JSON key
    chart_name = f"chart_price_dist_by_room_type_{city}"

    # Load chart data from JSON file
    data_values = load_chart_data_from_file(chart_name)

    # If data exists in the JSON file, use it
    if data_values:
        source = pd.DataFrame(data_values)
        print(f"Loaded data from JSON file for city: {city}")
    # Otherwise, perform the database query
    else:
        query = (
            session.query(RoomTypes.room_type, func.avg(ListingsCore.price))
            .join(RoomTypes, RoomTypes.room_type_id == ListingsCore.room_type_id)
            .group_by(RoomTypes.room_type)
        )

        if city != "All Cities":
            query = query.filter(ListingsCore.city_id == Cities.city_id).filter(
                Cities.city == city
            )

        data = [{"Room Type": rt, "Average Price": price} for rt, price in query]

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
            y=alt.Y(
                "Average Price:Q", axis=alt.Axis(tickCount=5, format="$~s", title=None)
            ),
            color=alt.Color(
                "Room Type:N",
                scale=alt.Scale(range=COLORS),
                legend=alt.Legend(title=None, orient="top"),
            ),
        )
    )

    return chart


def chart_median_neighborhood_prices(session, city):
    print(
        f"Processing price distribution by room types for city: {city}"
    )  # Logging the current city

    # Construct the chart name to match the JSON key
    chart_name = f"chart_median_neighborhood_prices_{city}"

    # Load chart data from JSON file
    data_values = load_chart_data_from_file(chart_name)

    # If data exists in the JSON file, use it
    if data_values:
        source = pd.DataFrame(data_values)
        print(f"Loaded data from JSON file for city: {city}")
    # Otherwise, perform the database query
    else:
        query = session.query(Neighborhoods.neighborhood, ListingsCore.price).join(
            Neighborhoods, Neighborhoods.neighborhood_id == ListingsCore.neighborhood_id
        )

        if city != "All Cities":
            query = query.filter(ListingsCore.city_id == Cities.city_id).filter(
                Cities.city == city
            )

        # Execute the query and get data
        data = query.all()

        # Processing the data to calculate medians
        neighborhoods = {}
        for neighborhood, price in data:
            if neighborhood not in neighborhoods:
                neighborhoods[neighborhood] = []
            neighborhoods[neighborhood].append(price)

        # Calculate median and sort by median price
        median_prices = []
        for neighborhood, prices in neighborhoods.items():
            prices.sort()
            n = len(prices)
            median = (
                prices[n // 2]
                if n % 2 != 0
                else (prices[n // 2 - 1] + prices[n // 2]) / 2
            )
            median_prices.append({"Neighborhood": neighborhood, "Median Price": median})

        # Sort neighborhoods by median price in descending order
        median_prices = sorted(
            median_prices, key=lambda x: x["Median Price"], reverse=True
        )

        source = pd.DataFrame(median_prices)

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
                "Median Price:Q",
                axis=alt.Axis(tickCount=5, format="$~s", title="Median Price"),
            ),
            color=alt.Color(
                "Neighborhood:N",
                legend=None,  # No legend due to a large number of neighborhoods
            ),
        )
    )

    return chart
