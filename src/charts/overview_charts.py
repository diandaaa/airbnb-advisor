import altair as alt
from sqlalchemy.orm import joinedload

from database.models import (
    Cities,
    ListingsCore,
    ListingsLocation,
    Neighborhoods,
    RoomTypes,
)


def chart_price_dist_by_room_type(session, city_name):
    # Query the necessary data
    listings_query = (
        session.query(ListingsCore.price, RoomTypes.room_type)
        .join(RoomTypes, RoomTypes.room_type_id == ListingsCore.room_type_id)
        .join(ListingsLocation, ListingsLocation.listing_id == ListingsCore.listing_id)
        .join(
            Neighborhoods,
            Neighborhoods.neighborhood_id == ListingsLocation.neighborhood_id,
        )
        .join(Cities, Cities.city_id == Neighborhoods.city_id)
        .filter(Cities.city == city_name)
    )

    # Execute the query
    results = listings_query.all()

    # Prepare the data for visualization
    data = [
        {"room_type": result.room_type, "price": result.price} for result in results
    ]

    # Define the Altair chart
    chart = (
        alt.Chart(alt.Data(values=data))
        .mark_boxplot()
        .encode(x="room_type:N", y="price:Q", tooltip=["room_type:N", "price:Q"])
        .properties(title=f"Price Distribution by Room Type in {city_name}", width=400)
    )

    return chart
