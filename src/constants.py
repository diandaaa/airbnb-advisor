import json

# Read the schema.json to get table definitions
SCHEMA = None


def load_schema():
    global SCHEMA
    if SCHEMA is None:
        with open("data/schema.json", "r") as f:
            SCHEMA = json.load(f)
    return SCHEMA


# Specify the cities list
CITIES = [
    "Los Angeles",
    "San Francisco",
    "Seattle",
    "Chicago",
    "Cambridge",
    "San Mateo County",
    "Santa Clara County",
    "Santa Cruz County",
    "Oakland",
]

AIRBNB_COLORS = {
    "main": "#FF5A5F",  # Rausch
    "green": "#00A699",  # Babu
    "orange": "#FC642D",  # Arches
    "darkgrey": "#484848",  # Hof
    "lightgrey": "#767676",  # Foggy
}


# Specify the database path
DATABASE_PATH = "data/listings.sqlite"

# Specify tables that can be directly loaded from the pandas dataframe without additional operations
CORE_TABLES = [
    "ListingBasicInfo",
    "ListingLocation",
    "ListingAvailability",
    "ListingReviewScores",
    "ListingReviewsSummary",
]

# Set the types of columns for reading from CSV using pandas
COLUMN_IMPORT_TYPES = {
    "id": "int64",
    "listing_url": "str",
    "scrape_id": "float32",
    "last_scraped": "str",
    "scrape_name": "str",
    "name": "str",
    "description": "str",
    "picture_url": "str",
    "host_id": "float32",
    "host_url": "str",
    "host_name": "str",
    "host_since": "str",
    "host_location": "str",
    "host_about": "str",
    "host_response_time": "str",
    "host_response_rate": "str",
    "host_acceptance_rate": "str",
    "host_is_superhost": "str",
    "host_thumbnail_url": "str",
    "host_picture_url": "str",
    "host_neighbourhood": "str",
    "host_listings_count": "float32",
    "host_total_listings_count": "float32",
    "host_verifications": "str",
    "host_has_profile_pic": "str",
    "host_identity_verified": "str",
    "neighbourhood": "str",
    "neighbourhood_cleansed": "str",
    "latitude": "float32",
    "longitude": "float32",
    "property_type": "str",
    "room_type": "str",
    "accommodates": "float32",
    "bathrooms": "float32",
    "bathroom_text": "str",
    "bedrooms": "float32",
    "amenities": "str",
    "price": "str",
    "minimum_nights": "float32",
    "maximum_nights": "float32",
    "minimum_minimum_nights": "float32",
    "maximum_minimum_nights": "float32",
    "minimum_maximum_nights": "float32",
    "maximum_maximum_nights": "float32",
    "minimum_nights_avg_ntm": "float32",
    "maximum_nights_avg_ntm": "float32",
    "has_availability": "str",
    "availability_30": "float32",
    "availability_60": "float32",
    "availability_90": "float32",
    "availability_365": "float32",
    "calendar_last_scraped": "str",
    "number_of_reviews": "float32",
    "number_of_reviews_ltm": "float32",
    "first_review": "str",
    "last_review": "str",
    "review_scores_rating": "float64",
    "review_scores_accuracy": "float64",
    "review_scores_cleanliness": "float64",
    "review_scores_checkin": "float64",
    "review_scores_communication": "float64",
    "review_scores_location": "float64",
    "review_scores_value": "float64",
    "license": "str",
    "instant_bookable": "str",
    "reviews_per_month": "float32",
    "calculated_host_listings_count": "float32",
    "calculated_host_listings_count_entire_homes": "float32",
    "calculated_host_listings_count_private_rooms": "float32",
    "calculated_host_listings_count_shared_rooms": "float32",
}

# Specify the columns that need to be rounded as part of the review scores table
REVIEW_SCORES_COLUMNS = [
    "review_scores_rating",
    "review_scores_accuracy",
    "review_scores_cleanliness",
    "review_scores_checkin",
    "review_scores_communication",
    "review_scores_location",
    "review_scores_value",
]

# Mapping from DataFrame columns to corresponding database table names for base lookup tables
COLUMN_TO_TABLE_MAP = {
    "city": "Cities",
    "neighborhood": "Neighborhoods",
    "property_type": "PropertyTypes",
    "room_type": "RoomTypes",
    "host_response_time": "HostResponseTime",
}

LOOKUP_TABLES = [
    "Cities",
    "Neighborhoods",
    "PropertyTypes",
    "RoomTypes",
    "HostResponseTime",
]

EXTENSION_TABLES = [
    "ListingAvailability",
    "ListingLocation",
    "ListingReviewsSummary",
    "ListingReviewScores",
]
