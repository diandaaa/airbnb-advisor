import streamlit as st
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import sessionmaker

from database import models


def median_price_bar_chart(session, city):
    """
    Generate a bar chart displaying the median price across four room types.
    Filters by city if a specific city is selected.

    Parameters:
    session (Session): SQLAlchemy session object
    city (str): Selected city to filter by; 'All Cities' for no city filter
    """

    # Building the query to get the median price for each room type
    stmt = (
        select(
            [
                models.RoomTypes.room_type,
                func.median(models.ListingsCore.price).label("median_price"),
            ]
        )
        .join(
            models.ListingsCore,
            models.ListingsCore.room_type_id == models.RoomTypes.room_type_id,
        )
        .group_by(models.RoomTypes.room_type)
    )

    # Applying city filter if a specific city is selected
    if city != "All Cities":
        stmt = (
            stmt.where(
                models.ListingsLocation.neighborhood_id
                == models.Neighborhoods.neighborhood_id
            )
            .where(models.Neighborhoods.city_id == models.Cities.city_id)
            .where(models.Cities.city == city)
        )

    # Executing the query
    result = session.execute(stmt).fetchall()

    # Extracting room types and median prices from the query result
    room_types = [row[0] for row in result]
    median_prices = [row[1] for row in result]

    # Creating the bar chart using Streamlit
    st.bar_chart(data=median_prices, index=room_types, use_container_width=True)
