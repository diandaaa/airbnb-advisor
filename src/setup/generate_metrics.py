import json
import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

import constants
from src.metrics.overview_metrics import *
from src.metrics.pricing_metrics import *
from src.metrics.reviews_metrics import *


def calculate_city_metrics(session: Session, city: str):
    return {
        "active_listings": active_listings(session, city),
        "active_listings_delta": active_listings_delta(session, city),
        "active_hosts": active_hosts(session, city),
        "active_hosts_delta": active_hosts_delta(session, city),
        "median_price": median_price(session, city),
        "median_review_score": median_review_score(session, city),
        "median_price_delta": median_price_delta(session, city),
        "median_review_score_delta": median_review_score_delta(session, city),
        "mean_price": mean_price(session, city),
        "mean_price_delta": mean_price_delta(session, city),
        "ninetieth_percentile_price": ninetieth_percentile_price(session, city),
        "ninetieth_percentile_price_delta": ninetieth_percentile_price_delta(
            session, city
        ),
        "median_superhost_price": median_superhost_price(session, city),
        "median_superhost_price_delta": median_superhost_price_delta(session, city),
        "mean_new_listing_price": mean_new_listing_price(session, city),
        "mean_new_listing_price_delta": mean_new_listing_price_delta(session, city),
        "mean_reviews_score": mean_reviews_score(session, city),
        "mean_reviews_score_delta": mean_reviews_score_delta(session, city),
        "median_review_count": median_review_count(session, city),
        "median_review_count_delta": median_review_count_delta(session, city),
        "mean_superhost_reviews_score": mean_superhost_reviews_score(session, city),
        "mean_superhost_reviews_score_delta": mean_superhost_reviews_score_delta(
            session, city
        ),
        "superhost_percent": superhost_percent(session, city),
        "superhost_percent_delta": superhost_percent_delta(session, city),
    }


def save_metrics_to_json(cities_metrics: dict, filename="metrics.json"):
    # Get the current script's directory
    current_dir = Path(os.path.dirname(os.path.abspath(__file__)))

    # Navigate up one directory and then into the data directory
    data_dir = current_dir.parent / "data"

    # Create the full path to the metrics.json file
    filepath = data_dir / filename

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(cities_metrics, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    DATABASE_URI = "sqlite:///" + constants.DATABASE_PATH

    engine = create_engine(
        DATABASE_URI, echo=False
    )  # echo=True will show generated SQL, remove in production
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Assuming session is already created and connected to your database
    session = SessionLocal()

    cities = constants.CITIES

    cities_metrics = {}
    for city in cities:
        cities_metrics[city] = calculate_city_metrics(session, city)

    save_metrics_to_json(cities_metrics)
