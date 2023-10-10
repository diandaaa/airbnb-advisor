import os

import constants
import data_cleaning
import data_reading
import db_populating
from amenity_processing import process_amenities
from database import models
from database.db_session import SessionLocal, init_db


def clean_listings_df(listings_df):
    # Convert true/false columns to boolean values
    data_cleaning.convert_tf_columns_to_bool(listings_df)

    # Convert percentages to floats
    data_cleaning.convert_percent_columns_to_float(listings_df)

    # Rename columns
    listings_df.rename(
        columns={
            "neighbourhood_cleansed": "neighborhood",
            "id": "listing_id",
            "number_of_reviews_ltm": "number_of_reviews_last_12m",
            "number_of_reviews_l30d": "number_of_reviews_last_30d",
        },
        inplace=True,
    )

    # Remove duplicate listings
    listings_df.drop_duplicates(subset=["listing_id"], keep="first", inplace=True)

    # Convert price to integers
    listings_df["price"] = (
        listings_df["price"]
        .replace({"\$": "", ",": ""}, regex=True)
        .astype(float)
        .astype(int)
    )

    # Round review scores to 2 decimal places
    listings_df[constants.REVIEW_SCORES_COLUMNS] = listings_df[
        constants.REVIEW_SCORES_COLUMNS
    ].round(2)

    # Remove listings with no reviews in 2023 (the scrape year) or later
    listings_df = listings_df[listings_df["last_review"].str[:4] >= "2023"].copy()

    # Restart ordering of listing_id and host_id at 1 to anonymize the data
    listings_df["listing_id"] = (
        listings_df["listing_id"].rank(method="first").astype(int)
    )
    listings_df["host_id"] = listings_df["host_id"].rank(method="first").astype(int)

    return listings_df


def list_subfolders(path):
    return [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]


def update_cities_from_db(session):
    if not constants.CITIES:
        # Get unique cities from the Cities table
        cities_from_db = session.query(models.Cities.city).distinct().all()
        city_list = [city[0] for city in cities_from_db]

        # Add 'All Cities' to the beginning
        city_list.insert(0, "All Cities")

        # Update the CITIES constant
        constants.CITIES.extend(city_list)


def main():
    # Delete database if it exists
    if os.path.exists(constants.DATABASE_PATH):
        os.remove(constants.DATABASE_PATH)

    # Initialize Database
    init_db()

    # Read and merge the listings file of the cities defined in constants.py
    listings_df_raw = data_reading.read_and_merge_csv_files(list_subfolders("data/usa"))

    listings_df_clean = clean_listings_df(listings_df_raw)

    # Print the data types of the columns
    # for col, dtype in listings_df_clean.dtypes.items():
    #     print(f"{col}: {dtype}")

    # Start a session
    session = SessionLocal()

    # Populate tables
    db_populating.populate_initial_tables(session, listings_df_clean)
    db_populating.populate_listings_tables(session, listings_df_clean)
    db_populating.populate_amenity_tables(session)

    # Map amenities to listings through the ListingsAmenities table
    process_amenities(session, listings_df_clean)

    # Update CITIES from the database
    update_cities_from_db(session)

    # Commit and Close Session
    session.commit()
    session.close()


if __name__ == "__main__":
    main()
