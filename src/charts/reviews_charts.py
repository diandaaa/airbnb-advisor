import altair as alt
import numpy as np
import pandas as pd
from sqlalchemy import and_, create_engine, func
from sqlalchemy.orm import aliased

from database.models import Cities, Hosts, ListingsCore, ListingsReviewsSummary
from utilities import load_chart_data_from_file


def chart_review_scores_superhost(session, city):
    print(f"Processing superhost review scores for city: {city}")

    chart_name = f"chart_review_scores_superhost_{city}"
    data_values = load_chart_data_from_file(chart_name)

    if data_values:
        source = pd.DataFrame(data_values)
        print(f"Loaded data from JSON file for city: {city}")
    else:
        query = (
            session.query(ListingsReviewsSummary, Hosts.host_is_superhost)
            .join(
                ListingsCore,
                ListingsReviewsSummary.listing_id == ListingsCore.listing_id,
            )
            .join(Hosts, ListingsCore.host_id == Hosts.host_id)
        )

        if city != "All Cities":
            query = query.filter(Cities.city == city)

        data = []
        for rs, host_is_superhost in query:
            data.append(
                {
                    "Superhost": host_is_superhost,
                    "Accuracy": rs.review_scores_accuracy,
                    "Cleanliness": rs.review_scores_cleanliness,
                    "Checkin": rs.review_scores_checkin,
                    "Communication": rs.review_scores_communication,
                    "Location": rs.review_scores_location,
                    "Value": rs.review_scores_value,
                }
            )

        source = pd.DataFrame(data)

        if source.empty:
            print(f"No data available for city: {city}")
            return None

        source["Superhost"] = source["Superhost"].apply(
            lambda x: "Superhost" if x == 1 else "Non-Superhost"
        )

        # Melting the DataFrame to have review types as a single column
        source = source.melt(
            id_vars=["Superhost"],
            value_vars=[
                "Accuracy",
                "Cleanliness",
                "Checkin",
                "Communication",
                "Location",
                "Value",
            ],
            var_name="review_type",
            value_name="score",
        )

        # Group by Superhost status and review type and then calculate the median
        source = source.groupby(["Superhost", "review_type"]).median().reset_index()

    # Calculate the minimum score to adjust y-axis
    min_score = source["score"].min() - 0.25

    # Altair grouped bar chart
    chart = (
        alt.Chart(source)
        .mark_circle(size=600, opacity=0.7)
        .encode(
            x=alt.X(
                "review_type:N", title="Review Type"
            ),  # x-axis shows the review types
            y=alt.Y(
                "score:Q", title="Median Score", scale=alt.Scale(domain=(min_score, 5))
            ),
            color=alt.Color("Superhost:N", legend=alt.Legend(title=None, orient="top")),
        )
    )

    return chart


def chart_review_scores_price_correlation(session, city):
    print(f"Processing review scores vs price correlation for city: {city}")

    chart_name = f"chart_review_scores_price_correlation_{city}"
    data_values = load_chart_data_from_file(chart_name)

    if data_values:
        source = pd.DataFrame(data_values)
        print(f"Loaded data from JSON file for city: {city}")
    else:
        # Perform a query to get all types of review scores and prices
        query = session.query(ListingsReviewsSummary, ListingsCore.price).join(
            ListingsCore,
            ListingsReviewsSummary.listing_id == ListingsCore.listing_id,
        )

        if city != "All Cities":
            query = query.filter(Cities.city == city)

        data = []
        for rs, price in query:
            data.append(
                {
                    "price": price,
                    "Accuracy": rs.review_scores_accuracy,
                    "Cleanliness": rs.review_scores_cleanliness,
                    "Checkin": rs.review_scores_checkin,
                    "Communication": rs.review_scores_communication,
                    "Location": rs.review_scores_location,
                    "Value": rs.review_scores_value,
                }
            )

        source = pd.DataFrame(data)

        if source.empty:
            print(f"No data available for city: {city}")
            return None

        # Assigning price percentiles
        source["price_percentile"] = pd.qcut(
            source["price"], 20, labels=False, duplicates="drop"
        )

        # Melting the DataFrame to have review types as a single column
        source = source.melt(
            id_vars=["price_percentile"],
            value_vars=[
                "Accuracy",
                "Cleanliness",
                "Checkin",
                "Communication",
                "Location",
                "Value",
            ],
            var_name="review_type",
            value_name="score",
        )

        # Group by price percentiles and review type and then calculate the median
        source = (
            source.groupby(["price_percentile", "review_type"]).median().reset_index()
        )

    # Calculate the 5th percentile value across all review groups
    min_score_percentile = source["score"].quantile(0.00)

    # Altair line chart
    chart = (
        alt.Chart(source)
        .transform_calculate(
            price_percentile_calculated="datum.price_percentile * 5 / 100"  # Calculate the new values
        )
        .mark_line(point=True)
        .encode(
            x=alt.X(
                "price_percentile_calculated:Q",
                title="Price Percentile",
                axis=alt.Axis(format=".0%", title="Price Percentile (%)"),
            ),
            y=alt.Y(
                "score:Q",
                title="Median Review Score",
                scale=alt.Scale(domain=(min_score_percentile, 5)),
            ),
            color=alt.Color(
                "review_type:N", legend=alt.Legend(title=None, orient="top")
            ),
            tooltip=["review_type", "score"],
        )
    )

    return chart
