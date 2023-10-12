from datetime import datetime, timedelta

from sqlalchemy import and_, desc, func
from sqlalchemy.orm import Session

from database import models


def median_superhost_price(session: Session, city: str):
    """
    Calculate the median price for listings owned by superhosts.
    """
    query = session.query(models.ListingsCore.price).join(models.Hosts)

    if city != "All Cities":
        query = (
            query.join(models.ListingsLocation)
            .join(models.Neighborhoods)
            .join(models.Cities)
        )
        query = query.filter(models.Cities.city == city)

    prices = query.filter(
        models.Hosts.host_is_superhost == 1,
        models.ListingsCore.was_active_most_recent_quarter == 1,
    ).all()
    prices = [p[0] for p in prices]
    return sorted(prices)[len(prices) // 2] if prices else None


def mean_price(session: Session, city: str):
    """
    Calculate the mean price across all active listings.
    """
    query = session.query(func.avg(models.ListingsCore.price))

    if city != "All Cities":
        query = (
            query.join(models.ListingsLocation)
            .join(models.Neighborhoods)
            .join(models.Cities)
        )
        query = query.filter(models.Cities.city == city)

    return query.filter(
        models.ListingsCore.was_active_most_recent_quarter == 1
    ).scalar()


def ninetieth_percentile_price(session: Session, city: str):
    """
    Calculate the price which is higher than 90% of the listing prices.
    """
    query = session.query(models.ListingsCore.price)

    if city != "All Cities":
        query = (
            query.join(models.ListingsLocation)
            .join(models.Neighborhoods)
            .join(models.Cities)
        )
        query = query.filter(models.Cities.city == city)

    prices = query.filter(models.ListingsCore.was_active_most_recent_quarter == 1).all()
    prices = sorted([p[0] for p in prices])
    idx = int(0.9 * len(prices))
    return prices[idx] if prices else None


def median_superhost_price_delta(session: Session, city: str):
    """
    Calculate the change in median superhost price from four quarters ago.
    """
    current_price = median_superhost_price(session, city)

    query = session.query(models.ListingsCore.price).join(models.Hosts)
    if city != "All Cities":
        query = (
            query.join(models.ListingsLocation)
            .join(models.Neighborhoods)
            .join(models.Cities)
        )
        query = query.filter(models.Cities.city == city)

    prices = query.filter(
        models.Hosts.host_is_superhost == 1,
        models.ListingsCore.was_active_four_quarters_prior == 1,
    ).all()
    prices = [p[0] for p in prices]
    previous_price = sorted(prices)[len(prices) // 2] if prices else None

    return (current_price or 0) - (previous_price or 0)


def mean_price_delta(session: Session, city: str):
    """
    Calculate the change in mean price from four quarters ago.
    """
    current_mean = mean_price(session, city)
    query = session.query(func.avg(models.ListingsCore.price))

    if city != "All Cities":
        query = (
            query.join(models.ListingsLocation)
            .join(models.Neighborhoods)
            .join(models.Cities)
        )
        query = query.filter(models.Cities.city == city)

    previous_mean = query.filter(
        models.ListingsCore.was_active_four_quarters_prior == 1
    ).scalar()
    return (current_mean or 0) - (previous_mean or 0)


def mean_new_listing_price(session: Session, city: str):
    """
    Calculate the mean listing price of new listings in the most recent quarter.
    New listings are identified based on the first_review date from the ListingsReviewsSummary table.
    """
    query = (
        session.query(models.ListingsCore.price)
        .join(
            models.ListingsReviewsSummary,
            models.ListingsReviewsSummary.listing_id == models.ListingsCore.listing_id,
        )
        .filter(models.ListingsCore.was_active_most_recent_quarter == 1)
    )

    # Filter by city if "All Cities" is not selected
    if city != "All Cities":
        # Join with ListingsLocation to filter by city
        query = (
            query.join(models.ListingsLocation)
            .join(models.Neighborhoods)
            .join(models.Cities)
        )
        query = query.filter(models.Cities.city == city)

    new_listing_prices = query.filter(
        models.ListingsReviewsSummary.first_review.like("2023-%")
    ).all()
    new_listing_prices = [
        p[0] for p in new_listing_prices
    ]  # Extract prices from tuples

    return (
        sum(new_listing_prices) / len(new_listing_prices) if new_listing_prices else 0
    )


def mean_new_listing_price_delta(session: Session, city: str):
    """
    Calculate the change in the mean listing price for new listings from four quarters prior.
    """
    current_mean_price = mean_new_listing_price(session, city)

    query = (
        session.query(models.ListingsCore.price)
        .join(
            models.ListingsReviewsSummary,
            models.ListingsReviewsSummary.listing_id == models.ListingsCore.listing_id,
        )
        .filter(models.ListingsCore.was_active_four_quarters_prior == 1)
    )

    # Filter by city if "All Cities" is not selected
    if city != "All Cities":
        # Join with ListingsLocation to filter by city
        query = (
            query.join(models.ListingsLocation)
            .join(models.Neighborhoods)
            .join(models.Cities)
        )
        query = query.filter(models.Cities.city == city)

    previous_new_listing_prices = query.filter(
        models.ListingsReviewsSummary.first_review.like("2022-%")
    ).all()
    previous_new_listing_prices = [
        p[0] for p in previous_new_listing_prices
    ]  # Extract prices from tuples

    previous_mean_price = (
        sum(previous_new_listing_prices) / len(previous_new_listing_prices)
        if previous_new_listing_prices
        else 0
    )

    return current_mean_price - previous_mean_price


def ninetieth_percentile_price_delta(session: Session, city: str):
    """
    Calculate the change in 90th percentile price from four quarters ago.
    """
    current_90th = ninetieth_percentile_price(session, city)

    query = session.query(models.ListingsCore.price)
    if city != "All Cities":
        query = (
            query.join(models.ListingsLocation)
            .join(models.Neighborhoods)
            .join(models.Cities)
        )
        query = query.filter(models.Cities.city == city)

    prices = query.filter(models.ListingsCore.was_active_four_quarters_prior == 1).all()
    prices = sorted([p[0] for p in prices])
    idx = int(0.9 * len(prices))
    previous_90th = prices[idx] if prices else None

    return (current_90th or 0) - (previous_90th or 0)
