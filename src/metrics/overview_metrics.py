from sqlalchemy.orm import Session

from database import models


def active_listings(session: Session, city: str):
    query = session.query(models.ListingsCore)

    if city != "All Cities":
        query = query.join(
            models.Cities, models.Cities.city_id == models.ListingsCore.city_id
        )
        query = query.filter(models.Cities.city == city)

    return query.filter(models.ListingsCore.was_active_most_recent_quarter == 1).count()


def active_listings_delta(session: Session, city: str):
    current_active = active_listings(session, city)

    query = session.query(models.ListingsCore)

    if city != "All Cities":
        query = query.join(
            models.Cities, models.Cities.city_id == models.ListingsCore.city_id
        )
        query = query.filter(models.Cities.city == city)

    previous_active = query.filter(
        models.ListingsCore.was_active_four_quarters_prior == 1
    ).count()

    return current_active - previous_active


def active_hosts(session: Session, city: str):
    query = session.query(models.ListingsCore.host_id.distinct())

    if city != "All Cities":
        query = query.join(
            models.Cities, models.Cities.city_id == models.ListingsCore.city_id
        )
        query = query.filter(models.Cities.city == city)

    return query.filter(models.ListingsCore.was_active_most_recent_quarter == 1).count()


def median_price(session: Session, city: str):
    query = session.query(models.ListingsCore.price)

    if city != "All Cities":
        query = query.join(
            models.Cities, models.Cities.city_id == models.ListingsCore.city_id
        )
        query = query.filter(models.Cities.city == city)

    prices = query.filter(models.ListingsCore.was_active_most_recent_quarter == 1).all()
    prices = [p[0] for p in prices]

    return sorted(prices)[len(prices) // 2] if prices else None


def median_review_score(session: Session, city: str):
    query = session.query(models.ListingsReviewsSummary.review_scores_rating).join(
        models.ListingsCore
    )

    if city != "All Cities":
        query = query.join(
            models.Cities, models.Cities.city_id == models.ListingsCore.city_id
        )
        query = query.filter(models.Cities.city == city)

    scores = query.filter(models.ListingsCore.was_active_most_recent_quarter == 1).all()
    scores = [s[0] for s in scores]

    return sorted(scores)[len(scores) // 2] if scores else None


def median_price_delta(session: Session, city: str):
    current_median_price = median_price(session, city)

    query = session.query(models.ListingsCore.price)

    if city != "All Cities":
        query = query.join(
            models.Cities, models.Cities.city_id == models.ListingsCore.city_id
        )
        query = query.filter(models.Cities.city == city)

    previous_prices = query.filter(
        models.ListingsCore.was_active_four_quarters_prior == 1
    ).all()
    previous_prices = [p[0] for p in previous_prices]

    previous_median_price = (
        sorted(previous_prices)[len(previous_prices) // 2] if previous_prices else None
    )

    return (current_median_price or 0) - (previous_median_price or 0)


def median_review_score_delta(session: Session, city: str):
    current_median_score = median_review_score(session, city)

    query = session.query(models.ListingsReviewsSummary.review_scores_rating).join(
        models.ListingsCore
    )

    if city != "All Cities":
        query = query.join(
            models.Cities, models.Cities.city_id == models.ListingsCore.city_id
        )
        query = query.filter(models.Cities.city == city)

    previous_scores = query.filter(
        models.ListingsCore.was_active_four_quarters_prior == 1
    ).all()
    previous_scores = [s[0] for s in previous_scores]

    previous_median_score = (
        sorted(previous_scores)[len(previous_scores) // 2] if previous_scores else None
    )

    return (current_median_score or 0) - (previous_median_score or 0)


def active_hosts_delta(session: Session, city: str):
    """
    Calculate the change in the number of unique hosts with an active listing from four quarters prior.
    """
    current_active_hosts = active_hosts(session, city)

    query = session.query(models.ListingsCore.host_id.distinct())

    # Filter by city if "All Cities" is not selected
    if city != "All Cities":
        query = query.join(
            models.Cities, models.Cities.city_id == models.ListingsCore.city_id
        )
        query = query.filter(models.Cities.city == city)

    previous_active_hosts = query.filter(
        models.ListingsCore.was_active_four_quarters_prior == 1
    ).count()

    return current_active_hosts - previous_active_hosts
