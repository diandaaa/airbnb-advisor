from sqlalchemy import and_, extract, func, or_, text

from database.models import (
    Cities,
    Hosts,
    ListingsCore,
    ListingsLocation,
    ListingsReviewsSummary,
    Neighborhoods,
)


def get_current_quarter(conn):
    """Get the most recent quarter from the database."""
    quarter = (
        conn.session.query(
            extract("year", ListingsReviewsSummary.first_review).label("year"),
            extract("quarter", ListingsReviewsSummary.first_review).label("quarter"),
        )
        .distinct()
        .order_by(text("year desc"), text("quarter desc"))
        .first()
    )

    return (quarter.year, quarter.quarter)


def get_overview_metrics(conn, selected_city):
    current_qtr = get_current_quarter(conn)

    metrics = {}

    # Metrics for current quarter
    metrics["active_listings"] = fetch_listings_count(
        conn, current_qtr, selected_city, "last_review"
    )
    metrics["listings_gained"] = fetch_listings_count(
        conn, current_qtr, selected_city, "first_review"
    )
    metrics["listings_lost"] = fetch_listings_lost(conn, current_qtr, selected_city)
    metrics["active_listings_delta"] = (
        metrics["listings_gained"] - metrics["listings_lost"]
    )
    metrics["active_hosts"] = fetch_host_count(conn, current_qtr, selected_city)
    metrics["median_review_score"] = calculate_median_review_score(
        conn, current_qtr, selected_city
    )
    metrics["median_price"] = calculate_median_price(conn, current_qtr, selected_city)

    # Metrics for last year's quarter
    last_year_qtr = (current_qtr[0] - 1, current_qtr[1])
    metrics["active_hosts_last_year"] = fetch_host_count(
        conn, last_year_qtr, selected_city
    )
    metrics["median_review_score_last_year"] = calculate_median_review_score(
        conn, last_year_qtr, selected_city
    )
    metrics["median_price_last_year"] = calculate_median_price(
        conn, last_year_qtr, selected_city
    )

    # Calculate deltas
    metrics["active_hosts_delta"] = (
        metrics["active_hosts"] - metrics["active_hosts_last_year"]
    )
    metrics["median_review_score_delta"] = (
        metrics["median_review_score"] - metrics["median_review_score_last_year"]
    )
    metrics["median_price_delta"] = (
        metrics["median_price"] - metrics["median_price_last_year"]
    )

    return metrics


def fetch_listings_count(conn, qtr, city, review_type):
    year, quarter = qtr
    filter_conditions = [
        extract("year", getattr(ListingsReviewsSummary, review_type)) == year,
        extract("quarter", getattr(ListingsReviewsSummary, review_type)) == quarter,
    ]

    if city != "All Cities":
        city_join_condition = Cities.city == city
        filter_conditions.append(city_join_condition)

    return (
        conn.session.query(func.count(ListingsCore.listing_id))
        .join(
            ListingsReviewsSummary,
            ListingsCore.listing_id == ListingsReviewsSummary.listing_id,
        )
        .filter(*filter_conditions)
        .scalar()
    )


def fetch_listings_lost(conn, current_qtr, city):
    current_year, current_quarter = current_qtr
    last_year_qtr = (current_year - 1, current_quarter)

    # Listings that had a last_review in the 4 quarters before the current
    last_review_conditions = [
        extract("year", ListingsReviewsSummary.last_review) < current_year,
        or_(
            extract("year", ListingsReviewsSummary.last_review) == current_year,
            extract("quarter", ListingsReviewsSummary.last_review) < current_quarter,
        ),
    ]

    # Listings that did not have a review in the current quarter
    no_review_current_qtr = (
        ~conn.session.query(ListingsReviewsSummary.listing_id)
        .filter(
            extract("year", ListingsReviewsSummary.last_review) == current_year,
            extract("quarter", ListingsReviewsSummary.last_review) == current_quarter,
        )
        .exists()
    )

    # Listings that had their first review during or before the last_year_qtr
    first_review_conditions = [
        or_(
            extract("year", ListingsReviewsSummary.first_review) < last_year_qtr[0],
            and_(
                extract("year", ListingsReviewsSummary.first_review)
                == last_year_qtr[0],
                extract("quarter", ListingsReviewsSummary.first_review)
                <= last_year_qtr[1],
            ),
        )
    ]

    # Consider the selected city if not "All Cities"
    if city != "All Cities":
        city_condition = Cities.city == city
        last_review_conditions.append(city_condition)
        first_review_conditions.append(city_condition)

    return (
        conn.session.query(func.count(ListingsCore.listing_id.distinct()))
        .join(
            ListingsReviewsSummary,
            ListingsCore.listing_id == ListingsReviewsSummary.listing_id,
        )
        .join(ListingsLocation, ListingsLocation.listing_id == ListingsCore.listing_id)
        .join(
            Neighborhoods,
            Neighborhoods.neighborhood_id == ListingsLocation.neighborhood_id,
        )
        .join(Cities, Cities.city_id == Neighborhoods.city_id)
        .filter(
            *last_review_conditions, no_review_current_qtr, *first_review_conditions
        )
        .scalar()
    )


def fetch_host_count(conn, qtr, city):
    year, quarter = qtr
    filter_conditions = [
        extract("year", Hosts.host_since) == year,
        extract("quarter", Hosts.host_since) == quarter,
    ]

    if city != "All Cities":
        city_join_condition = Cities.city == city
        filter_conditions.append(city_join_condition)

    return (
        conn.session.query(func.count(Hosts.host_id))
        .filter(*filter_conditions)
        .scalar()
    )


def calculate_median_review_score(conn, qtr, city):
    year, quarter = qtr
    filter_conditions = [
        extract("year", ListingsReviewsSummary.first_review) == year,
        extract("quarter", ListingsReviewsSummary.first_review) == quarter,
    ]

    if city != "All Cities":
        city_join_condition = Cities.city == city
        filter_conditions.append(city_join_condition)

    review_scores = (
        conn.session.query(ListingsReviewsSummary.review_scores_rating)
        .join(
            ListingsCore,
            ListingsCore.listing_id == ListingsReviewsSummary.listing_id,
        )
        .join(ListingsLocation, ListingsLocation.listing_id == ListingsCore.listing_id)
        .join(
            Neighborhoods,
            Neighborhoods.neighborhood_id == ListingsLocation.neighborhood_id,
        )
        .join(Cities, Cities.city_id == Neighborhoods.city_id)
        .filter(*filter_conditions)
        .order_by(ListingsReviewsSummary.review_scores_rating)
        .all()
    )

    median_review_score = (
        review_scores[len(review_scores) // 2].review_scores_rating
        if len(review_scores) % 2 == 1
        else (
            review_scores[len(review_scores) // 2 - 1].review_scores_rating
            + review_scores[len(review_scores) // 2].review_scores_rating
        )
        / 2
    )

    return median_review_score


def calculate_median_price(conn, qtr, city):
    year, quarter = qtr
    filter_conditions = [
        extract("year", ListingsReviewsSummary.first_review) == year,
        extract("quarter", ListingsReviewsSummary.first_review) == quarter,
    ]

    if city != "All Cities":
        city_join_condition = Cities.city == city
        filter_conditions.append(city_join_condition)

    prices = (
        conn.session.query(ListingsCore.price)
        .join(
            ListingsReviewsSummary,
            ListingsCore.listing_id == ListingsReviewsSummary.listing_id,
        )
        .join(ListingsLocation, ListingsLocation.listing_id == ListingsCore.listing_id)
        .join(
            Neighborhoods,
            Neighborhoods.neighborhood_id == ListingsLocation.neighborhood_id,
        )
        .join(Cities, Cities.city_id == Neighborhoods.city_id)
        .filter(*filter_conditions)
        .order_by(ListingsCore.price)
        .all()
    )

    median_price = (
        prices[len(prices) // 2].price
        if len(prices) % 2 == 1
        else (prices[len(prices) // 2 - 1].price + prices[len(prices) // 2].price) / 2
    )

    return median_price
