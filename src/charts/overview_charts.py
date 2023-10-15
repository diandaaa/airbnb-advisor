import altair as alt
from sqlalchemy import extract, func

from database.models import Cities, Hosts, ListingsCore, ListingsReviewsSummary


def chart_active_listings_hosts_age(session, city):
    # Querying active listings and hosts from the database
    query = (
        session.query(
            extract("year", ListingsReviewsSummary.first_review).label("year"),
            func.count(ListingsCore.listing_id).label("active_listings"),
            func.count(Hosts.host_id).label("active_hosts"),
        )
        .join(
            ListingsCore, ListingsCore.listing_id == ListingsReviewsSummary.listing_id
        )
        .join(Hosts, Hosts.host_id == ListingsCore.host_id)
        .filter(ListingsCore.was_active_most_recent_quarter == 1)
        .group_by("year")
        .order_by("year")
    )

    if city != "All Cities":
        query = query.join(Cities, Cities.city_id == ListingsCore.city_id).filter(
            Cities.city == city
        )

    results = query.all()

    # Creating a dataframe for Altair chart
    import pandas as pd

    df = pd.DataFrame(results)

    # Creating Altair bar chart
    chart = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            alt.X("year:O", title="Year"),
            alt.Y("active_listings:Q", title="Number of Active Listings"),
            alt.Y2("active_hosts:Q"),
            tooltip=["year:O", "active_listings:Q", "active_hosts:Q"],
        )
        .properties(title="Active Listings and Hosts by Year")
    )

    return chart
