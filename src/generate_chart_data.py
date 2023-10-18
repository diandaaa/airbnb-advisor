import json
import os  # Import the os module to use file deletion function

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import constants
from charts.overview_charts import *
from charts.pricing_charts import *
from charts.reviews_charts import *


def main(charts):
    # File path to the JSON file
    file_path = "data/charts_data.json"

    # Checking if the file exists, and if it does, deleting it
    if os.path.exists(file_path):
        os.remove(file_path)

    DATABASE_URI = "sqlite:///" + constants.DATABASE_PATH

    engine = create_engine(
        DATABASE_URI, echo=False
    )  # echo=True will show generated SQL, remove in production
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Assuming session is already created and connected to your database
    session = SessionLocal()

    cities = constants.CITIES

    charts_data_values = {}
    for chart_func in charts:
        for city in cities:
            chart = chart_func(session, city)

            chart_func_name = chart_func.__name__
            if chart is not None:
                chart_dict = chart.to_dict(format="vega")
                # Extracting the ["data"][0]["values"]
                chart_data_values = chart_dict.get("data", [{}])[0].get("values", {})
                charts_data_values[f"{chart_func_name}_{city}"] = chart_data_values
            else:
                print(f"No chart generated for city: {city}")
                charts_data_values[f"{chart_func_name}_{city}"] = None

    # Saving all chart data values to a JSON file
    with open(file_path, "w") as file:
        json.dump(charts_data_values, file)


if __name__ == "__main__":
    charts = [
        chart_active_listings_hosts_age,
        chart_room_types,
        chart_neighborhood_listings_count,
        chart_median_neighborhood_prices,
        chart_mean_room_type_prices,
        chart_review_scores_price_correlation,
        chart_review_scores_superhost,
    ]
    main(charts)
