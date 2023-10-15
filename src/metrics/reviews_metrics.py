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
            query.join(models.Cities)
            .filter(models.Cities.city_id == models.ListingsCore.city_id)
            .filter(models.Cities.city == city)
        )

    # Get list of review counts and find the median
    review_counts = [r[0] for r in query.all()]
    sorted_counts = sorted(review_counts)
    median_count = sorted_counts[len(sorted_counts) // 2]

    return median_count


# You can modify other functions similarly. I will show you one more as an example:


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
            query.join(models.Cities)
            .filter(models.Cities.city_id == models.ListingsCore.city_id)
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
            query.join(models.Cities)
            .filter(models.Cities.city_id == models.ListingsCore.city_id)
            .filter(models.Cities.city == city)
        )

    previous_score = query.scalar()

    # Calculate and return delta
    return current_score - previous_score if previous_score else None


def superhost_percent(session, city="All Cities"):
    """
    Calculate the percentage of active listings that are hosted by superhosts.
    """
    # Base query
    query = (
        session.query(models.ListingsCore)
        .join(models.Hosts, models.ListingsCore.host_id == models.Hosts.host_id)
        .filter(models.ListingsCore.was_active_most_recent_quarter == 1)
    )

    # Apply city filter if necessary
    if city != "All Cities":
        query = (
            query.join(models.Cities)
            .filter(models.Cities.city_id == models.ListingsCore.city_id)
            .filter(models.Cities.city == city)
        )

    # Count superhost listings
    superhost_listings = query.filter(models.Hosts.host_is_superhost == 1).count()

    # Count all listings
    all_listings = query.count()

    # Calculate percentage
    return (superhost_listings / all_listings) * 100 if all_listings else 0


def superhost_percent_delta(session, city="All Cities"):
    """
    Calculate the change in the superhost percentage from four quarters prior.
    """
    current_percent = superhost_percent(session, city)

    # Base query for listings from four quarters prior
    query = (
        session.query(models.ListingsCore)
        .join(models.Hosts, models.ListingsCore.host_id == models.Hosts.host_id)
        .filter(models.ListingsCore.was_active_four_quarters_prior == 1)
    )

    # Apply city filter if necessary
    if city != "All Cities":
        query = (
            query.join(models.Cities)
            .filter(models.Cities.city_id == models.ListingsCore.city_id)
            .filter(models.Cities.city == city)
        )

    # Count superhost listings from four quarters prior
    superhost_listings_prior = query.filter(models.Hosts.host_is_superhost == 1).count()

    # Count all listings from four quarters prior
    all_listings_prior = query.count()

    # Calculate prior percentage
    prior_percent = (
        (superhost_listings_prior / all_listings_prior) * 100
        if all_listings_prior
        else 0
    )

    # Calculate and return the delta
    return current_percent - prior_percent


def mean_superhost_reviews_score(session, city):
    """
    Fetches the mean reviews score for active listings hosted by superhosts.
    """
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

    if city != "All Cities":
        query = (
            query.join(models.Cities)
            .filter(models.Cities.city_id == models.ListingsCore.city_id)
            .filter(models.Cities.city == city)
        )

    return query.scalar()


def mean_superhost_reviews_score_delta(session, city):
    """
    Fetches the change in mean reviews score from four quarters prior for active listings hosted by superhosts.
    """
    current_score = mean_superhost_reviews_score(session, city)

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

    if city != "All Cities":
        query = (
            query.join(models.Cities)
            .filter(models.Cities.city_id == models.ListingsCore.city_id)
            .filter(models.Cities.city == city)
        )

    previous_score = query.scalar()

    return current_score - previous_score if previous_score else None


def median_review_count_delta(session, city):
    """
    Get the change in median review count from four quarters prior.

    Parameters:
    - session: SQLAlchemy session.
    - city: Selected city to filter by. If "All Cities", no city filter is applied.

    Returns:
    - Change in median review count from four quarters prior.
    """
    # Current median
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
            query.join(models.Cities)
            .filter(models.Cities.city_id == models.ListingsCore.city_id)
            .filter(models.Cities.city == city)
        )

    # Get list of review counts from four quarters prior and find the median
    review_counts = [r[0] for r in query.all()]
    sorted_counts = sorted(review_counts)
    len_counts = len(sorted_counts)

    if len_counts == 0:
        prior_median_count = 0
    elif len_counts % 2 == 0:
        prior_median_count = (
            sorted_counts[len_counts // 2 - 1] + sorted_counts[len_counts // 2]
        ) / 2
    else:
        prior_median_count = sorted_counts[len_counts // 2]

    return current_median - prior_median_count
