import numpy as np

from database.models import (
    Amenities,
    AmenityPriceImpacts,
    Cities,
    ListingsAmenities,
    ListingsCore,
    Neighborhoods,
)

BATCH_SIZE = 100


def generate_amenity_impacts(session):
    # Clearing all records from AmenityPriceImpacts table
    session.query(AmenityPriceImpacts).delete()
    session.commit()
    print("All existing records in AmenityPriceImpacts have been deleted.")

    def calculate_impact(scope=None, location_id=None):
        if scope == "overall":
            print(f"Processing overall totals.")
        elif scope == "cities":
            print(f"Processing City ID: {location_id}")
        elif scope == "neighborhoods":
            print(f"Processing Neighborhood ID: {location_id}")

        impacts_to_insert = []  # A list to store the impacts

        for amenity in amenities:
            base_query = (
                session.query(ListingsCore.price)
                .join(
                    ListingsAmenities,
                    ListingsAmenities.listing_id == ListingsCore.listing_id,
                )
                .filter(ListingsAmenities.amenity_id == amenity.amenity_id)
            )

            if scope == "cities":
                base_query = base_query.filter(ListingsCore.city_id == location_id)
            elif scope == "neighborhoods":
                base_query = base_query.filter(
                    ListingsCore.neighborhood_id == location_id
                )

            listings_with_amenity = base_query.all()
            listings_with_amenity_prices = [x.price for x in listings_with_amenity]

            # Listings without the amenity
            base_query_without_amenity = (
                session.query(ListingsCore.price)
                .outerjoin(
                    ListingsAmenities,
                    (ListingsAmenities.listing_id == ListingsCore.listing_id)
                    & (ListingsAmenities.amenity_id == amenity.amenity_id),
                )
                .filter(ListingsAmenities.amenity_id == None)
            )

            if scope == "cities":
                base_query_without_amenity = base_query_without_amenity.filter(
                    ListingsCore.city_id == location_id
                )
            elif scope == "neighborhoods":
                base_query_without_amenity = base_query_without_amenity.filter(
                    ListingsCore.neighborhood_id == location_id
                )

            listings_without_amenity = base_query_without_amenity.all()
            listings_without_amenity_prices = [
                x.price for x in listings_without_amenity
            ]

            # Check if the price lists are empty, and skip the iteration if they are.
            if not listings_with_amenity_prices or not listings_without_amenity_prices:
                continue  # Skip this iteration if any price list is empty

            # Calculating median price differences
            median_with_amenity = np.median(listings_with_amenity_prices)
            median_without_amenity = np.median(listings_without_amenity_prices)

            if np.isnan(median_with_amenity) or np.isnan(median_without_amenity):
                continue  # skip this iteration if either median is NaN

            median_difference = round(median_with_amenity - median_without_amenity)

            # Inserting the impact
            impact = AmenityPriceImpacts(
                amenity_id=amenity.amenity_id,
                median_price_difference=median_difference,
                amenity_count=len(listings_with_amenity_prices),
            )

            if scope == "cities":
                impact.city_id = location_id
            elif scope == "neighborhoods":
                impact.neighborhood_id = location_id

            # Inserting the impact
            impact = AmenityPriceImpacts(
                amenity_id=amenity.amenity_id,
                median_price_difference=median_difference,
                amenity_count=len(listings_with_amenity_prices),
            )

            if scope == "cities":
                impact.city_id = location_id
            elif scope == "neighborhoods":
                impact.neighborhood_id = location_id

            impacts_to_insert.append(impact)  # Add impact to the list

            # Check if we reached the batch size limit
            if len(impacts_to_insert) >= 100:
                session.bulk_save_objects(impacts_to_insert)
                session.commit()  # Commit after each batch
                impacts_to_insert.clear()  # Clear the list after saving

        # Insert remaining impacts that didn't reach the batch size limit
        if impacts_to_insert:
            session.bulk_save_objects(impacts_to_insert)
            session.commit()

    amenities = session.query(Amenities).all()

    calculate_impact("overall")  # For overall

    cities = session.query(Cities).all()
    for city in cities:
        calculate_impact("cities", city.city_id)  # For each city

    neighborhoods = session.query(Neighborhoods).all()
    for neighborhood in neighborhoods:
        calculate_impact(
            "neighborhoods", neighborhood.neighborhood_id
        )  # For each neighborhood
