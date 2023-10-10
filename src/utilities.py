import base64
from typing import List

from database.models import Cities


def load_city_names(conn) -> List[str]:
    """
    Loads unique city names from the Cities table in the database.

    Args:
    - conn: The database connection object.

    Returns:
    - A list of city names.
    """
    # Get unique cities from the Cities table
    cities_from_db = conn.session.query(Cities.city).distinct().all()

    # Return the list of cities with "All Cities" prepended
    return ["All Cities"] + [city[0] for city in cities_from_db]


def get_image_with_encoding(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")


def hex_to_rgba(hex_color, alpha=1.0):
    hex_color = hex_color.lstrip("#")
    rgb = tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
    return f"rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, {alpha})"
