from database.session import SessionLocal
from setup.generate_amenity_impacts import generate_amenity_impacts

session = SessionLocal()

generate_amenity_impacts(session)
