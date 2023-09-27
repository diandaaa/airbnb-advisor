from sqlalchemy import Column, Integer, String, ForeignKey, REAL
from sqlalchemy.orm import registry

mapper_registry = registry()
Base = mapper_registry.generate_base()

# Custom Base Class --------------------------------------------------------------------------------------------------
class CustomBase(Base):
    __abstract__ = True
    _table_type = None
    _description = None

    @classmethod
    def get_table_type(cls):
        return cls._table_type
    
    @classmethod
    def get_description(cls):
        return cls._description


# Simple Lookup Tables -----------------------------------------------------------------------------------------------
class HostResponseTimes(CustomBase):
    __tablename__ = 'HostResponseTimes'
    _table_type = 'lookup'
    _description = 'Simple lookup table for host response times'

    host_response_time_id = Column(Integer, primary_key=True, autoincrement=True)
    host_response_time = Column(String, unique=True)

class PropertyTypes(CustomBase):
    __tablename__ = 'PropertyTypes'
    _table_type = 'lookup'
    _description = 'Simple lookup table for listing property types'

    property_type_id = Column(Integer, primary_key=True, autoincrement=True)
    property_type = Column(String, unique=True)

class RoomTypes(CustomBase):
    __tablename__ = 'RoomTypes'
    _table_type = 'lookup'
    _description = 'Simple lookup table for listing room types'

    room_type_id = Column(Integer, primary_key=True, autoincrement=True)
    room_type = Column(String, unique=True)


# Heirarchical Lookup Tables (Level 1) -----------------------------------------------------------------------------
class Neighborhoods(CustomBase):
    __tablename__ = 'Neighborhoods'
    _table_type = 'heirarchical_lookup'
    _description = 'Heirarchical lookup table for listing neighborhoods; child to Cities'

    neighborhood_id = Column(Integer, primary_key=True, autoincrement=True)
    neighborhood = Column(String, unique=True)
    city_id = Column(Integer, ForeignKey('Cities.city_id'))

class Amenities(CustomBase):
    __tablename__ = 'Amenities'
    _table_type = 'heirarchical_lookup'
    _description = 'Heirarchical lookup table for listing amenities; child to AmenityTypes'

    amenity_id = Column(Integer, primary_key=True, autoincrement=True)
    amenity_name = Column(String, unique=True)
    amenity_type_id = Column(Integer, ForeignKey('AmenityTypes.amenity_category_id'))


# Heirarchical Lookup Tables (Level 2) -----------------------------------------------------------------------------
class Cities(CustomBase):
    __tablename__ = 'Cities'
    _table_type = 'heirarchical_lookup'
    _description = 'Heirarchical lookup table for listing cities; parent to Neighborhoods'

    city_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True)

class AmenityTypes(CustomBase):
    __tablename__ = 'AmenityTypes'
    _table_type = 'heirarchical_lookup'
    _description = 'Heirarchical lookup table for listing amenity types; parent to Amenities'

    amenity_category_id = Column(Integer, primary_key=True)
    amenity_category = Column(String, unique=True)


# Entity Tables ----------------------------------------------------------------------------------------------------
class Hosts(CustomBase):
    __tablename__ = 'Hosts'
    _table_type = 'entity'
    _description = 'Entity table for unique hosts'

    host_id = Column(Integer, primary_key=True)
    host_since = Column(String)
    host_response_time_id = Column(Integer, ForeignKey('HostResponseTimes.host_response_time_id'))
    host_response_rate = Column(REAL)
    host_acceptance_rate = Column(REAL)
    host_is_superhost = Column(Integer)
    host_listings_count = Column(Integer)
    host_total_listings_count = Column(Integer)
    host_has_profile_pic = Column(Integer)
    host_identity_verified = Column(Integer)

class ListingsCore(CustomBase):
    __tablename__ = 'ListingsCore'
    _table_type = 'entity'
    _description = 'Entity table for unique listings'

    listing_id = Column(Integer, primary_key=True)
    host_id = Column(Integer, ForeignKey('Hosts.host_id'))
    property_type_id = Column(Integer, ForeignKey('PropertyTypes.property_type_id'))
    room_type_id = Column(Integer, ForeignKey('RoomTypes.room_type_id'))
    accommodates = Column(Integer)
    bedrooms = Column(Integer)
    beds = Column(Integer)
    price = Column(Integer)
    minimum_nights = Column(Integer)
    maximum_nights = Column(Integer)
    has_availability = Column(Integer)
    instant_bookable = Column(Integer)
    license = Column(String)


# Listings Extension Tables ---------------------------------------------------------------------------------------
class ListingsAvailability(CustomBase):
    __tablename__ = 'ListingsAvailability'
    _table_type = 'extension'
    _description = 'Extension table for listing availability'

    listing_id = Column(Integer, ForeignKey('ListingsCore.listing_id') , primary_key=True)
    availability_30 = Column(Integer)
    availability_60 = Column(Integer)
    availability_90 = Column(Integer)
    availability_365 = Column(Integer)

class ListingsLocation(CustomBase):
    __tablename__ = 'ListingsLocation'
    _table_type = 'extension'
    _description = 'Extension table for listing location'

    listing_id = Column(Integer, ForeignKey('ListingsCore.listing_id') , primary_key=True)
    neighborhood_id = Column(Integer, ForeignKey('Neighborhoods.neighborhood_id'))
    latitude = Column(REAL)
    longitude = Column(REAL)

class ListingsReviewsSummary(CustomBase):
    __tablename__ = 'ListingsReviewsSummary'
    _table_type = 'extension'
    _description = 'Extension table for listing reviews summary'

    listing_id = Column(Integer, ForeignKey('ListingsCore.listing_id') , primary_key=True)
    number_of_reviews = Column(Integer)
    number_of_reviews_last_12m = Column(Integer)
    number_of_reviews_last_30d = Column(Integer)
    first_review = Column(String)
    last_review = Column(String)
    review_scores_rating = Column(Integer)
    review_scores_accuracy = Column(Integer)
    review_scores_cleanliness = Column(Integer)
    review_scores_checkin = Column(Integer)
    review_scores_communication = Column(Integer)
    review_scores_location = Column(Integer)
    review_scores_value = Column(Integer)


# Junction Tables -----------------------------------------------------------------------------------------------
class ListingsAmenities(CustomBase):
    __tablename__ = 'ListingsAmenities'
    _table_type = 'junction'
    _description = 'Junction table for listing amenities'

    listing_amenity_id = Column(Integer, primary_key=True, autoincrement=True)
    listing_id = Column(Integer, ForeignKey('ListingsCore.listing_id'))
    amenity_id = Column(Integer, ForeignKey('Amenities.amenity_id'))