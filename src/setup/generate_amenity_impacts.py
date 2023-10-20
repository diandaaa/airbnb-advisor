import numpy as np

from database.models import (
    Amenities,
    AmenityPriceImpacts,
    Cities,
    ListingsAmenities,
    ListingsCore,
    Neighborhoods,
)


def generate_amenity_impacts(session):
    amenities = session.query(Amenities).all()
    cities = session.query(Cities).all()  # Query all cities

    for amenity in amenities:
        # Query for price data on listings with the amenity
        listings_with_amenity = (
            session.query(ListingsCore.price)
            .join(
                ListingsAmenities,
                ListingsAmenities.listing_id == ListingsCore.listing_id,
            )
            .filter(ListingsAmenities.amenity_id == amenity.amenity_id)
            .all()
        )

        listings_with_amenity_prices = [x.price for x in listings_with_amenity]

        # Query for price data on listings without the amenity
        listings_without_amenity = (
            session.query(ListingsCore.price)
            .outerjoin(
                ListingsAmenities,
                (ListingsAmenities.listing_id == ListingsCore.listing_id)
                & (ListingsAmenities.amenity_id == amenity.amenity_id),
            )
            .filter(ListingsAmenities.amenity_id == None)
            .all()
        )

        listings_without_amenity_prices = [x.price for x in listings_without_amenity]

        # Check if the price lists are empty, and skip the iteration if they are.
        if not listings_with_amenity_prices or not listings_without_amenity_prices:
            continue  # Skip this iteration if any price list is empty

        # Calculating median price differences
        median_with_amenity = np.median(listings_with_amenity_prices)
        median_without_amenity = np.median(listings_without_amenity_prices)

        if np.isnan(median_with_amenity) or np.isnan(median_without_amenity):
            continue  # skip this iteration if either median is NaN

        median_difference = round(median_with_amenity - median_without_amenity)

        # Inserting the overall impact
        overall_impact = AmenityPriceImpacts(
            amenity_id=amenity.amenity_id,
            median_price_difference=median_difference,
            amenity_count=len(listings_with_amenity_prices),
        )

        session.add(overall_impact)

        # You can repeat a similar process for each city and neighborhood by adding city_id and neighborhood_id
        # to the queries and iterating over each city and neighborhood

        # Committing after processing each amenity
        session.commit()


def generate_amenity_impacts(session):
    def calculate_impact(scope=None, location_id=None):
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

            session.add(impact)

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
