from database.session import SessionLocal
from setup.generate_amenity_impacts import generate_amenity_impacts

session = SessionLocal()

try:
    generate_amenity_impacts(session)
    session.commit()  # commit here if there’s no exception
except Exception as e:
    session.rollback()  # rollback in case of an exception
    print(f"An error occurred: {e}")
finally:
    session.close()  # ensure that session is closed in any case
