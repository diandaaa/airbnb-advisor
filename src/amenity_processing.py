from fuzzywuzzy import fuzz
from sqlalchemy.orm import Session

from database.models import Amenities, ListingsAmenities


def sanitize_string(input_str: str) -> str:
    """Sanitize the string by replacing surrogate characters."""
    return input_str.encode("utf-16", "surrogatepass").decode("utf-16")


def find_amenity_id(session: Session, amenity_str: str):
    """Find the amenity's ID based on its name. If not found, use NLP or string comparison."""
    sanitized_amenity = sanitize_string(amenity_str)

    amenity_obj = session.query(Amenities).filter_by(amenity=sanitized_amenity).first()
    if amenity_obj:
        return amenity_obj.amenity_id

    # No exact match found, search for the closest match using string comparison
    all_amenities = session.query(Amenities).all()
    highest_ratio = 0
    matched_amenity_id = None
    for existing_amenity in all_amenities:
        ratio = fuzz.ratio(sanitized_amenity, existing_amenity.amenity)
        if ratio > highest_ratio:
            highest_ratio = ratio
            matched_amenity_id = existing_amenity.amenity_id

    if highest_ratio > 80:  # Assuming 80 as the threshold for similarity
        return matched_amenity_id
    return None


def get_unique_amenities_from_listings(listings_df_clean):
    """Extract all unique amenities from the dataframe."""
    unique_amenities = set()
    for amenities in listings_df_clean["amenities"]:
        unique_amenities.update(eval(amenities))
    return unique_amenities


def match_unique_amenities(session, unique_amenities):
    """Match unique amenities to predefined list. Return a dict of matches."""
    matched_ids = {}
    for amenity in unique_amenities:
        amenity_id = find_amenity_id(session, amenity)
        if amenity_id:
            matched_ids[amenity] = amenity_id
    return matched_ids


def bulk_insert_matched_amenities(session, listings_df_clean, matched_amenities):
    """Bulk insert matched amenities into ListingsAmenities."""
    insert_list = []
    for _, row in listings_df_clean.iterrows():
        listing_amenities = eval(row["amenities"])
        for amenity in listing_amenities:
            amenity_id = matched_amenities.get(amenity)
            if amenity_id:
                insert_list.append(
                    {"listing_id": row["listing_id"], "amenity_id": amenity_id}
                )
    session.bulk_insert_mappings(ListingsAmenities, insert_list)
    session.commit()


def process_amenities(session, listings_df_clean):
    unique_amenities = get_unique_amenities_from_listings(listings_df_clean)
    matched_amenities = match_unique_amenities(session, unique_amenities)
    bulk_insert_matched_amenities(session, listings_df_clean, matched_amenities)
