from sqlalchemy import and_, func

from database import models


def median_review_count(session, city):
    """
    Get the median number of reviews among active listings.

    Parameters:
    - session: SQLAlchemy session.
    - city: Selected city to filter by. If "All Cities", no city filter is applied.

    Returns:
    - Median review count.
    """
    # Base query
    query = (
        session.query(models.ListingsReviewsSummary.number_of_reviews)
        .join(
            models.ListingsCore,
            models.ListingsCore.listing_id == models.ListingsReviewsSummary.listing_id,
        )
        .filter(models.ListingsCore.was_active_most_recent_quarter == 1)
    )

    # Apply city filter if necessary
    if city != "All Cities":
        query = (
            query.join(models.ListingsLocation)
            .join(models.Neighborhoods)
            .filter(models.Neighborhoods.city_id == models.Cities.city_id)
            .filter(models.Cities.city == city)
        )

    # Get list of review counts and find the median
    review_counts = [r[0] for r in query.all()]
    sorted_counts = sorted(review_counts)
    median_count = sorted_counts[len(sorted_counts) // 2]

    return median_count


def median_review_count_delta(session, city):
    """
    Get the change in median review count from four quarters prior.

    Parameters:
    - session: SQLAlchemy session.
    - city: Selected city to filter by. If "All Cities", no city filter is applied.

    Returns:
    - Change in median review count from four quarters prior.
    """
    current_median = median_review_count(session, city)

    # Base query for four quarters prior
    query = (
        session.query(models.ListingsReviewsSummary.number_of_reviews)
        .join(
            models.ListingsCore,
            models.ListingsCore.listing_id == models.ListingsReviewsSummary.listing_id,
        )
        .filter(models.ListingsCore.was_active_four_quarters_prior == 1)
    )

    # Apply city filter if necessary
    if city != "All Cities":
        query = (
            query.join(models.ListingsLocation)
            .join(models.Neighborhoods)
            .filter(models.Neighborhoods.city_id == models.Cities.city_id)
            .filter(models.Cities.city == city)
        )

    # Get list of review counts from four quarters prior and find the median
    review_counts = [r[0] for r in query.all()]
    sorted_counts = sorted(review_counts)
    prior_median_count = sorted_counts[len(sorted_counts) // 2]

    return current_median - prior_median_count


def mean_reviews_score(session, city):
    """
    Fetches the mean reviews score for active listings.
    """
    # Base query
    query = (
        session.query(func.avg(models.ListingsReviewsSummary.review_scores_rating))
        .join(
            models.ListingsCore,
            models.ListingsReviewsSummary.listing_id == models.ListingsCore.listing_id,
        )
        .filter(models.ListingsCore.was_active_most_recent_quarter == 1)
    )

    # Apply city filter if city is not "All Cities"
    if city != "All Cities":
        query = (
            query.join(models.ListingsLocation)
            .join(models.Neighborhoods)
            .join(models.Cities)
            .filter(models.Cities.city == city)
        )

    return query.scalar()


def mean_reviews_score_delta(session, city):
    """
    Fetches the change in mean reviews score from four quarters prior for active listings.
    """
    # Mean reviews score for the most recent quarter
    current_score = mean_reviews_score(session, city)

    # Base query for score four quarters prior
    query = (
        session.query(func.avg(models.ListingsReviewsSummary.review_scores_rating))
        .join(
            models.ListingsCore,
            models.ListingsReviewsSummary.listing_id == models.ListingsCore.listing_id,
        )
        .filter(models.ListingsCore.was_active_four_quarters_prior == 1)
    )

    # Apply city filter if city is not "All Cities"
    if city != "All Cities":
        query = (
            query.join(models.ListingsLocation)
            .join(models.Neighborhoods)
            .join(models.Cities)
            .filter(models.Cities.city == city)
        )

    previous_score = query.scalar()

    # Calculate and return delta
    return current_score - previous_score if previous_score else None


def mean_superhost_reviews_score(session, city):
    """
    Fetches the mean reviews score for active listings hosted by superhosts.
    """
    # Base query
    query = (
        session.query(func.avg(models.ListingsReviewsSummary.review_scores_rating))
        .join(
            models.ListingsCore,
            models.ListingsReviewsSummary.listing_id == models.ListingsCore.listing_id,
        )
        .join(models.Hosts, models.ListingsCore.host_id == models.Hosts.host_id)
        .filter(
            models.ListingsCore.was_active_most_recent_quarter == 1,
            models.Hosts.host_is_superhost == 1,
        )
    )

    # Apply city filter if city is not "All Cities"
    if city != "All Cities":
        query = (
            query.join(models.ListingsLocation)
            .join(models.Neighborhoods)
            .join(models.Cities)
            .filter(models.Cities.city == city)
        )

    return query.scalar()


def mean_superhost_reviews_score_delta(session, city):
    """
    Fetches the change in mean reviews score from four quarters prior for active listings hosted by superhosts.
    """
    # Mean reviews score for the most recent quarter
    current_score = mean_superhost_reviews_score(session, city)

    # Base query for score four quarters prior
    query = (
        session.query(func.avg(models.ListingsReviewsSummary.review_scores_rating))
        .join(
            models.ListingsCore,
            models.ListingsReviewsSummary.listing_id == models.ListingsCore.listing_id,
        )
        .join(models.Hosts, models.ListingsCore.host_id == models.Hosts.host_id)
        .filter(
            models.ListingsCore.was_active_four_quarters_prior == 1,
            models.Hosts.host_is_superhost == 1,
        )
    )

    # Apply city filter if city is not "All Cities"
    if city != "All Cities":
        query = (
            query.join(models.ListingsLocation)
            .join(models.Neighborhoods)
            .join(models.Cities)
            .filter(models.Cities.city == city)
        )

    previous_score = query.scalar()

    # Calculate and return delta
    return current_score - previous_score if previous_score else None


def superhost_percent(session, city="All Cities"):
    # Base query to join ListingsCore with Hosts
    query = session.query(models.ListingsCore, models.Hosts).join(
        models.Hosts, models.Hosts.host_id == models.ListingsCore.host_id
    )

    # Filtering based on selected city if applicable
    if city != "All Cities":
        query = (
            query.join(models.ListingsLocation)
            .join(models.Neighborhoods)
            .join(models.Cities)
            .filter(models.Cities.city == city)
        )

    # Filter for active listings and those hosted by superhosts
    active_superhost_listings = query.filter(
        and_(
            models.ListingsCore.was_active_most_recent_quarter == 1,
            models.Hosts.host_is_superhost == 1,
        )
    ).count()

    # Filter just for active listings
    active_listings = query.filter(
        models.ListingsCore.was_active_most_recent_quarter == 1
    ).count()

    # Calculate percentage
    if active_listings == 0:  # Prevent division by zero
        return 0
    return (active_superhost_listings / active_listings) * 100


def superhost_percent_delta(session, city="All Cities"):
    # Current quarter percentage
    current_qtr_percent = superhost_percent(session, city)

    # Base query to join ListingsCore with Hosts
    query = session.query(models.ListingsCore, models.Hosts).join(
        models.Hosts, models.Hosts.host_id == models.ListingsCore.host_id
    )

    # Filtering based on selected city if applicable
    if city != "All Cities":
        query = (
            query.join(models.ListingsLocation)
            .join(models.Neighborhoods)
            .join(models.Cities)
            .filter(models.Cities.city == city)
        )

    # Filter for listings active in the quarter four quarters prior and hosted by superhosts
    active_superhost_listings_four_qtrs_prior = query.filter(
        and_(
            models.ListingsCore.was_active_four_quarters_prior == 1,
            models.Hosts.host_is_superhost == 1,
        )
    ).count()

    # Filter for listings active in the quarter four quarters prior
    active_listings_four_qtrs_prior = query.filter(
        models.ListingsCore.was_active_four_quarters_prior == 1
    ).count()

    # Calculate percentage four quarters prior
    if active_listings_four_qtrs_prior == 0:  # Prevent division by zero
        prior_qtr_percent = 0
    else:
        prior_qtr_percent = (
            active_superhost_listings_four_qtrs_prior / active_listings_four_qtrs_prior
        ) * 100

    # Calculate delta
    return current_qtr_percent - prior_qtr_percent
