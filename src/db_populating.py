from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy import inspect
from database import models
import pandas as pd


def populate_initial_tables(session: Session, df: pd.DataFrame):
    def populate_neighborhoods(city_col: str, neighborhood_col: str):
        unique_neighborhoods = df.dropna(subset=[neighborhood_col]).drop_duplicates(subset=[neighborhood_col])

        for _, record in unique_neighborhoods.iterrows():
            city_name = record[city_col]
            neighborhood_name = record[neighborhood_col]

            # Try to find the city first, if not exist then create a new one
            city = session.query(models.Cities).filter_by(name=city_name).first()
            if city is None:
                city = models.Cities(name=city_name)
                session.add(city)
                session.flush()  # to get the new city_id
                
            # Add the neighborhood record with the associated city_id
            neighborhood = models.Neighborhoods(neighborhood=neighborhood_name, city_id=city.city_id)
            session.add(neighborhood)
        
        session.commit()

    def populate_hosts():
        # Create an auxiliary column representing the number of filled (non-NaN) values
        df['filled_count'] = df.notna().sum(axis=1)

        # Sort the DataFrame based on the auxiliary column
        sorted_df = df.sort_values(by='filled_count', ascending=False).drop(columns='filled_count')

        
        # Drop duplicate host IDs, keeping the first occurrence (which has the most filled columns after sorting)
        unique_hosts = sorted_df.drop_duplicates(subset='host_id')
        
        for _, record in unique_hosts.iterrows():
            response_time = record.get('host_response_time', None)
            if response_time:
                host_response_time_obj = session.query(models.HostResponseTimes).filter_by(host_response_time=response_time).first()
                if not host_response_time_obj:
                    host_response_time_obj = models.HostResponseTimes(host_response_time=response_time)
                    session.add(host_response_time_obj)
                    session.flush()  # to get the new host_response_time_id
                host_response_time_id = host_response_time_obj.host_response_time_id
            else:
                host_response_time_id = None
            
            host = models.Hosts(
                host_id=record['host_id'],
                host_since=record.get('host_since', None),
                host_response_time_id=host_response_time_id,
                host_response_rate=record.get('host_response_rate', None),
                host_acceptance_rate=record.get('host_acceptance_rate', None),
                host_is_superhost=record.get('host_is_superhost', None),
                host_listings_count=record.get('host_listings_count', None),
                host_total_listings_count=record.get('host_total_listings_count', None),
                host_has_profile_pic=record.get('host_has_profile_pic', None),
                host_identity_verified=record.get('host_identity_verified', None)
            )
            session.add(host)
        
        session.commit()

    
    # Loop through all SQLAlchemy subclasses to find tables with _table_type as 'lookup'
    for cls in models.CustomBase.__subclasses__():
        if cls.get_table_type() == 'lookup':
            column_name_to_populate = None
            for column in cls.__table__.columns:
                if column.name.endswith('_id'):
                    continue
                if column.name in df.columns:
                    column_name_to_populate = column.name
                    break
            
            if column_name_to_populate:
                unique_values = df[column_name_to_populate].dropna().drop_duplicates().unique()
                existing_values = {x[0] for x in session.query(getattr(cls, column_name_to_populate)).all()}
                
                for value in unique_values:
                    if value not in existing_values:
                        new_row = cls(**{column_name_to_populate: value})
                        session.add(new_row)
                        existing_values.add(value)
                
                session.commit()
                
    # For Neighborhoods, assume the DataFrame has 'city' and 'neighborhood' columns
    if 'city' in df.columns and 'neighborhood' in df.columns:
        try:
            populate_neighborhoods('city', 'neighborhood')
        except IntegrityError:
            session.rollback()
            print("Integrity error: Skipping duplicate neighborhoods or other constraint violations.")
    
    try:
        populate_hosts()
    except IntegrityError:
        session.rollback()
        print("Integrity error: Skipping duplicate hosts or other constraint violations.")








# def populate_core_tables(session: Session, listings_df):
    # Existing SQLAlchemy function to populate core tables

# def populate_amenities(session: Session, listings_df):
    # Existing SQLAlchemy function to populate amenities

# def populate_lookup_tables(session, df, models):
#     """
#     Populate lookup tables first so we can map the values later.
#     This function assumes you have a __tablegroup__ attribute set to 'Lookup'
#     in your lookup table classes.
#     """
#     for model in models:
#         if hasattr(model, '__tablegroup__') and model.__tablegroup__ == 'Lookup':
#             unique_values = df[model.__tablename__.lower()].drop_duplicates()
#             for value in unique_values:
#                 record = model(name=value)
#                 session.add(record)
#     session.commit()

# def populate_core_tables(session, listings_df, models):
#     """
#     Populate main tables, replace categories with their IDs
#     and exclude auto-incrementing ID columns.
#     """
#     # Filter models to exclude lookup tables
#     core_models = [model for model in models if not (hasattr(model, '__tablegroup__') and model.__tablegroup__ == 'Lookup')]

#     for model in core_models:
#         mapper = inspect(model)
#         columns = [column.key for column in mapper.attrs]
        
#         # Remove the first column assuming it's always the auto-incrementing ID
#         if len(columns) > 1:
#             columns = columns[1:]

#         for _, row in listings_df.iterrows():
#             try:
#                 attributes = {col: row[col] for col in columns if col in row.index and col not in ['host_id', 'listing_id']}
#                 record = model(**attributes)
#                 session.add(record)
#             except IntegrityError:
#                 session.rollback()
#     session.commit()  # Note: More efficient than committing in loop, but uses lots of memory


# def populate_amenities(session, listings_df):
#     for index, row in listings_df.iterrows():
#         amenities = row['amenities']
#         listing_id = row['listing_id']

#         # Assuming 'amenities' column is a list of amenity names
#         for amenity in amenities:
#             amenity_record = session.query(models.Amenities).filter_by(amenity_name=amenity).first()
#             if amenity_record is None:
#                 amenity_record = models.Amenities(amenity_name=amenity)
#                 session.add(amenity_record)
#                 session.flush()  # To get the newly created amenity_id
            
#             listing_amenity = models.ListingAmenities(listing_id=listing_id, amenity_id=amenity_record.amenity_id)
#             session.add(listing_amenity)

#     session.commit()


# def populate_tables_from_schema(session, df):
#     inspector = inspect(session.get_bind())

#     # Fill lookup tables first
#     for table_name in constants.LOOKUP_TABLES:
#         columns = [col['name'] for col in inspector.get_columns(table_name)]
#         df_column_name = columns[0][:-3]  # Remove "_id" suffix to match df columns
        
#         if df_column_name in df.columns:
#             unique_values = set(df[df_column_name].drop_duplicates().dropna())
            
#             # Get unique values already in the table
#             table_class = getattr(models, table_name)
#             existing_values = {x[0] for x in session.query(table_class).with_entities(getattr(table_class, columns[0])).all()}
            
#             # Find new unique values
#             new_values = unique_values - existing_values
            
#             # Bulk insert new unique values
#             bulk_data = [{df_column_name: val} for val in new_values]
#             session.bulk_insert_mappings(table_class, bulk_data)
#             session.commit()

#     for table_name in constants.EXTENSION_TABLES:
#         # Get DataFrame columns that match the table columns
#         table_columns = [col['name'] for col in inspector.get_columns(table_name)]
#         common_columns = [col for col in table_columns if col in df.columns]
        
#         if common_columns:
#             table_data = df[common_columns].to_dict(orient='records')
            
#             # Bulk insert
#             table_class = getattr(models, table_name)
#             session.bulk_insert_mappings(table_class, table_data)
#             session.commit()