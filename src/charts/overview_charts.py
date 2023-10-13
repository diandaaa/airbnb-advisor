import altair as alt
import pandas as pd
from sqlalchemy import func

from constants import BENS_COLORS
from database.models import (
    Cities,
    ListingsCore,
    ListingsLocation,
    ListingsReviewsSummary,
    Neighborhoods,
    RoomTypes,
)


def chart_active_listings(session, selected_city):
    query = (
        session.query(
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
    )

    data = pd.read_sql(query.statement, session.bind)

    # ... (your existing DataFrame processing code here, but try to utilize SQL queries more)

    colors_to_use = list(BENS_COLORS.values())[:2]

    chart = (
        alt.Chart(data)
        .mark_area(opacity=0.7)
        .encode(
            x=alt.X("Quarter:T", title=None),
            y=alt.Y("Value:Q", title=None, stack=None),
            color=alt.Color(
                "Type:N",
                scale=alt.Scale(
                    domain=["New Listings", "Cumulative Listings"], range=colors_to_use
                ),
                legend=alt.Legend(title=None, orient="top"),
            ),
            tooltip=["Quarter:T", "Value:Q"],
        )
        .properties(
            title={"text": "Total Listings", "subtitle": "By Quarter of First Review"},
            width=600,
            height=400,
        )
        .configure_axis(
            domain=False,
            ticks=False,
        )
    )

    return chart


def chart_room_type_counts(session, selected_city):
    query = (
        session.query(
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
    )

    data = pd.read_sql(query.statement, session.bind)

    # ... (your existing DataFrame processing code here, but try to utilize SQL queries more)

    color_to_use = list(BENS_COLORS.values())[0]

    chart = (
        alt.Chart(data)
        .mark_bar(opacity=0.7, color=color_to_use)
        .encode(
            x=alt.X("Count:Q", sort="-x", axis=alt.Axis(title=None)),
            y=alt.Y("Room Type:O", sort="-x", axis=alt.Axis(title=None)),
        )
        .properties(
            title=f"Room Type Counts for {selected_city}",
            width=300,
            height=200,
        )
    )

    return chart
