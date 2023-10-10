import pandas as pd
from sqlalchemy import inspect
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from constants import AMENITY_CATEGORIES
from database import models


def populate_initial_tables(session: Session, df: pd.DataFrame):
    def populate_neighborhoods(city_col: str, neighborhood_col: str):
        unique_neighborhoods = df.dropna(subset=[neighborhood_col]).drop_duplicates(
            subset=[neighborhood_col]
        )

        for _, record in unique_neighborhoods.iterrows():
            city_name = record[city_col]
            neighborhood_name = record[neighborhood_col]

            # Try to find the city first, if not exist then create a new one
            city = session.query(models.Cities).filter_by(city=city_name).first()
            if city is None:
                city = models.Cities(city=city_name)
                session.add(city)
                session.flush()  # to get the new city_id

            # Add the neighborhood record with the associated city_id
            neighborhood = models.Neighborhoods(
                neighborhood=neighborhood_name, city_id=city.city_id
            )
            session.add(neighborhood)

        session.commit()

    def populate_host_response_times(session: Session, df: pd.DataFrame):
        unique_response_times = df["host_response_time"].dropna().drop_duplicates()

        for response_time in unique_response_times:
            host_response_time_obj = (
                session.query(models.HostResponseTimes)
                .filter_by(host_response_time=response_time)
                .first()
            )
            if not host_response_time_obj:
                host_response_time_obj = models.HostResponseTimes(
                    host_response_time=response_time
                )
                session.add(host_response_time_obj)

    session.commit()

    def populate_hosts(session: Session, df: pd.DataFrame):
        # Create an auxiliary column representing the number of filled (non-NaN) values
        df = df.copy()
        df["filled_count"] = df.notna().sum(axis=1)

        # Sort the DataFrame based on the auxiliary column
        sorted_df = df.sort_values(by="filled_count", ascending=False).drop(
            columns="filled_count"
        )

        # We can now drop duplicate host IDs from the DataFrame
        sorted_df = sorted_df.drop_duplicates(subset="host_id")

        # Keep track of host response times we've processed
        processed_response_times = set()

        for _, record in sorted_df.iterrows():
            response_time = record.get("host_response_time", None)
            if response_time:
                host_response_time_obj = (
                    session.query(models.HostResponseTimes)
                    .filter_by(host_response_time=response_time)
                    .first()
                )
                if host_response_time_obj:
                    host_response_time_id = host_response_time_obj.host_response_time_id
                else:
                    host_response_time_id = None
            else:
                host_response_time_id = None

            existing_host = (
                session.query(models.Hosts).filter_by(host_id=record["host_id"]).first()
            )
            if not existing_host:
                host = models.Hosts(
                    host_id=record["host_id"],  # Adding back host_id assignment
                    host_since=record.get("host_since", None),
                    host_response_time_id=host_response_time_id,
                    host_response_rate=record.get("host_response_rate", None),
                    host_acceptance_rate=record.get("host_acceptance_rate", None),
                    host_is_superhost=record.get("host_is_superhost", None),
                    host_listings_count=record.get("host_listings_count", None),
                    host_total_listings_count=record.get(
                        "host_total_listings_count", None
                    ),
                    host_has_profile_pic=record.get("host_has_profile_pic", None),
                    host_identity_verified=record.get("host_identity_verified", None),
                )
                session.add(host)

        session.commit()

    # Loop through all SQLAlchemy subclasses to find tables with _table_type as 'lookup'
    for cls in models.CustomBase.__subclasses__():
        if cls.get_table_type() == "lookup":
            column_name_to_populate = None
            for column in cls.__table__.columns:
                if column.name.endswith("_id"):
                    continue
                if column.name in df.columns:
                    column_name_to_populate = column.name
                    break

            if column_name_to_populate:
                unique_values = (
                    df[column_name_to_populate].dropna().drop_duplicates().unique()
                )
                existing_values = {
                    x[0]
                    for x in session.query(getattr(cls, column_name_to_populate)).all()
                }

                for value in unique_values:
                    if value not in existing_values:
                        new_row = cls(**{column_name_to_populate: value})
                        session.add(new_row)
                        existing_values.add(value)

                session.commit()

    # For Neighborhoods, assume the DataFrame has 'city' and 'neighborhood' columns
    if "city" in df.columns and "neighborhood" in df.columns:
        try:
            populate_neighborhoods("city", "neighborhood")
        except IntegrityError:
            session.rollback()
            print(
                "Integrity error: Skipping duplicate neighborhoods or other constraint violations."
            )

    try:
        populate_host_response_times(session, df)
    except IntegrityError:
        session.rollback()
        print(
            "Integrity error: Skipping duplicate host response times or other constraint violations."
        )

    try:
        populate_hosts(session, df)
    except IntegrityError:
        session.rollback()
        print(
            "Integrity error: Skipping duplicate hosts or other constraint violations."
        )


def get_neighborhood_id(session, neighborhood_name):
    neighborhood = (
        session.query(models.Neighborhoods)
        .filter_by(neighborhood=neighborhood_name)
        .first()
    )
    return neighborhood.neighborhood_id if neighborhood else None


def get_property_type_id(session, property_type_name):
    property_type = (
        session.query(models.PropertyTypes)
        .filter_by(property_type=property_type_name)
        .first()
    )
    return property_type.property_type_id if property_type else None


def get_room_type_id(session, room_type_name):
    room_type = (
        session.query(models.RoomTypes).filter_by(room_type=room_type_name).first()
    )
    return room_type.room_type_id if room_type else None


def populate_listings_core(session, df):
    for _, row in df.iterrows():
        listing = models.ListingsCore(
            listing_id=row["listing_id"],
            host_id=row["host_id"],
            property_type_id=get_property_type_id(session, row["property_type"]),
            room_type_id=get_room_type_id(session, row["room_type"]),
            accommodates=row["accommodates"],
            bedrooms=row["bedrooms"],
            beds=row["beds"],
            price=row["price"],
            minimum_nights=row["minimum_nights"],
            maximum_nights=row["maximum_nights"],
            has_availability=row["has_availability"],
            instant_bookable=row["instant_bookable"],
            # license=row["license"],
        )
        session.add(listing)


def populate_listings_availability(session, df):
    for _, row in df.iterrows():
        availability = models.ListingsAvailability(
            listing_id=row["listing_id"],
            availability_30=row["availability_30"],
            availability_60=row["availability_60"],
            availability_90=row["availability_90"],
            availability_365=row["availability_365"],
        )
        session.add(availability)


def populate_listings_location(session, df):
    for _, row in df.iterrows():
        location = models.ListingsLocation(
            listing_id=row["listing_id"],
            neighborhood_id=get_neighborhood_id(session, row["neighborhood"]),
            # latitude=row["latitude"],  # not used in the app (makes DB too large for GitHub)
            # longitude=row["longitude"],  # not used in the app (makes DB too large for GitHub)
        )
        session.add(location)


def populate_listings_reviews_summary(session, df):
    for _, row in df.iterrows():
        review = models.ListingsReviewsSummary(
            listing_id=row["listing_id"],
            number_of_reviews=row["number_of_reviews"],
            number_of_reviews_last_12m=row["number_of_reviews_last_12m"],
            number_of_reviews_last_30d=row["number_of_reviews_last_30d"],
            first_review=row["first_review"],
            last_review=row["last_review"],
            review_scores_rating=row["review_scores_rating"],
            review_scores_accuracy=row["review_scores_accuracy"],
            review_scores_cleanliness=row["review_scores_cleanliness"],
            review_scores_checkin=row["review_scores_checkin"],
            review_scores_communication=row["review_scores_communication"],
            review_scores_location=row["review_scores_location"],
            review_scores_value=row["review_scores_value"],
        )
        session.add(review)


def populate_listings_tables(session, df):
    populate_listings_core(session, df)
    # populate_listings_availability(session, df) # not used in the app (makes DB too large for GitHub)
    populate_listings_location(session, df)
    populate_listings_reviews_summary(session, df)

    session.commit()


def populate_amenity_tables(session: Session):
    """Populate Amenities and AmenityCategories tables with predefined data."""
    for category, amenities_list in AMENITY_CATEGORIES.items():
        # Create or find the category in the AmenityCategories table
        amenity_category = (
            session.query(models.AmenityCategories)
            .filter_by(amenity_category=category)
            .first()
        )
        if not amenity_category:
            amenity_category = models.AmenityCategories(amenity_category=category)
            session.add(amenity_category)
            session.commit()

        # Create the amenities associated with this category
        for amenity_name in amenities_list:
            existing_amenity = (
                session.query(models.Amenities).filter_by(amenity=amenity_name).first()
            )
            if not existing_amenity:
                new_amenity = models.Amenities(
                    amenity=amenity_name,
                    amenity_category_id=amenity_category.amenity_category_id,
                )
                session.add(new_amenity)
        session.commit()
