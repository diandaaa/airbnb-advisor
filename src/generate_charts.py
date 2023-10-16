import json

import altair as alt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import constants
from charts.overview_charts import *

alt.data_transformers.enable("vegafusion")

if __name__ == "__main__":
    DATABASE_URI = "sqlite:///" + constants.DATABASE_PATH

    engine = create_engine(
        DATABASE_URI, echo=False
    )  # echo=True will show generated SQL, remove in production
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Assuming session is already created and connected to your database
    session = SessionLocal()

    cities = constants.CITIES

    charts = {}
    for city in cities:
        chart = chart_active_listings_hosts_age(session, city)
        charts[f"chart_active_listings_hosts_age_{city}"] = chart.to_dict(
            format="vega"
        )  # specify format="vega"

    # Saving all charts to a JSON file
    with open("data/charts.json", "w") as file:
        json.dump(charts, file)
