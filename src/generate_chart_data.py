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

    charts_data_values = {}
    for city in cities:
        chart = chart_active_listings_hosts_age(session, city)

        if chart is not None:
            chart_dict = chart.to_dict(format="vega")
            # Extracting the ["data"][0]["values"]
            chart_data_values = chart_dict.get("data", [{}])[0].get("values", {})
            charts_data_values[
                f"chart_active_listings_hosts_age_{city}"
            ] = chart_data_values
        else:
            print(
                f"No chart generated for city: {city}"
            )  # Logging which city didn’t generate a chart
            # You could also save a placeholder or message instead of the chart
            charts_data_values[
                f"chart_active_listings_hosts_age_{city}"
            ] = "No data available"

    # Saving all chart data values to a JSON file
    with open("data/charts_data.json", "w") as file:
        json.dump(charts_data_values, file)
