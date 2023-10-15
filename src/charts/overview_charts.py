from datetime import datetime

import altair as alt
import pandas as pd
from dateutil.relativedelta import relativedelta
from sqlalchemy.orm import joinedload

from constants import BENS_COLORS
from database.models import (
    Cities,
    Hosts,
    ListingsCore,
    ListingsReviewsSummary,
    Neighborhoods,
)


def calculate_age(start_date_str, end_date_str="2023-10-01"):
    if start_date_str is None:
        return None

    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
    delta = relativedelta(end_date, start_date)
    return delta.years


def chart_active_listings_hosts_age(session, city):
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
            Neighborhoods, Neighborhoods.neighborhood_id == ListingsCore.neighborhood_id
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
            data.append({"id": lc.listing_id, "age": listing_age, "type": "Listing"})

    source = pd.DataFrame(data)

    # Altair area chart
    chart = (
        alt.Chart(source)
        .transform_aggregate(count="count()", groupby=["age", "type"])
        .mark_area(opacity=0.7)
        .encode(
            x=alt.X("age:O", title="Age"),
            y=alt.Y("count:Q", title="Count"),
            color=alt.Color(
                "type:N",
                legend=alt.Legend(title="Type"),
                scale=alt.Scale(domain=["Host", "Listing"]),
            ),
        )
    )

    return chart
