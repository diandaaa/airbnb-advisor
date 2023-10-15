import altair as alt
import pandas as pd

from constants import BENS_COLORS
from database.models import Cities, ListingsCore, Neighborhoods, RoomTypes


def chart_price_dist_by_room_type(session, city):
    query = (
        session.query(ListingsCore.price, RoomTypes.room_type)
        .join(RoomTypes, RoomTypes.room_type_id == ListingsCore.room_type_id)
        .join(
            Neighborhoods, Neighborhoods.neighborhood_id == ListingsCore.neighborhood_id
        )
        .join(Cities, Cities.city_id == ListingsCore.city_id)
    )

    if city != "All Cities":
        query = query.filter(Cities.city == city)

    results = query.all()

    # Convert results to a pandas DataFrame
    data = pd.DataFrame(results, columns=["price", "room_type"])

    # Removing outliers: keeping only data below the 99th percentile
    p99 = data["price"].quantile(0.99)
    data = data[data["price"] < p99]

    # Picking the first four colors from BENS_COLORS
    colors_to_use = list(BENS_COLORS.values())[:4]

    # Creating an Altair chart
    chart = (
        alt.Chart(data)
        .mark_area(opacity=0.7)
        .encode(
            x=alt.X("price:Q", bin=alt.Bin(maxbins=100), title="Price"),
            y="count():Q",
            color=alt.Color(
                "room_type:N",
                scale=alt.Scale(range=colors_to_use),
                legend=alt.Legend(title=None),
            ),  # Customizing legend
            tooltip=["room_type", "count()", "mean(price)"],
        )
        .properties(
            title="Price Distribution by Room Type",
            width=600,
            height=400,
        )
        .configure_legend(orient="top")
    )

    return chart
