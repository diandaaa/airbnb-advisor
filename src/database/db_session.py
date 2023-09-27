from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.models import Base
import constants

DATABASE_URI = "sqlite:///" + constants.DATABASE_PATH

engine = create_engine(DATABASE_URI, echo=False)  # echo=True will show generated SQL, remove in production
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    # Create tables
    Base.metadata.create_all(bind=engine)

if __name__ == '__main__':
    init_db()