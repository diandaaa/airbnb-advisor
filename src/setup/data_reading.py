import os
import pandas as pd

import constants

def read_and_merge_csv_files(cities):
    """Reads and merges multiple city-specific CSV files into a single DataFrame.
    
    Parameters:
        cities (list): A list of city names for which data needs to be read.
    
    Returns:
        pd.DataFrame: A DataFrame containing the merged data for all cities.
    """
    all_frames = []
    for city in cities:
        city_path = os.path.join("data/usa", city, "listings_detailed.csv")
        if os.path.exists(city_path):
            df = pd.read_csv(
                city_path,
                dtype=constants.COLUMN_IMPORT_TYPES,
                na_values=["N/A", "NA", "na", "", "NaN"],
                keep_default_na=False,
            )
            df["city"] = city
            all_frames.append(df)
        else:
            print(f"File for {city} does not exist. Skipping.")
    merged_df = pd.concat(all_frames, ignore_index=True)

    return merged_df