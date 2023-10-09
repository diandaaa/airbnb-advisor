import constants
import data_cleaning
import data_reading
import db_populating
from database.db_session import init_db, SessionLocal

import os


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

    return listings_df


def main():
    # Delete database if it exists
    if os.path.exists(constants.DATABASE_PATH):
        os.remove(constants.DATABASE_PATH)

    # Initialize Database
    init_db()

    # Read and merge the listings file of the cities defined in constants.py
    listings_df_raw = data_reading.read_and_merge_csv_files(constants.CITIES)

    listings_df_clean = clean_listings_df(listings_df_raw)

    for col, dtype in listings_df_clean.dtypes.items():
        print(f"{col}: {dtype}")

    # Start a session
    session = SessionLocal()

    # Populate tables
    db_populating.populate_initial_tables(session, listings_df_clean)
    db_populating.populate_listings_tables(session, listings_df_clean)
    db_populating.populate_amenities_and_link(session, listings_df_clean)
    # db_initialization.populate_core_tables(session, listings_df)
    # db_initialization.populate_amenities(session, listings_df)
    # db_population.populate_tables_from_schema(session, listings_df)

    # Commit and Close Session
    session.commit()
    session.close()


if __name__ == "__main__":
    main()
