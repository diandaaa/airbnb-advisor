import base64
import json


def load_chart_data_from_file(chart_name):
    try:
        with open("data/charts_data.json", "r") as file:
            charts_data_values = json.load(file)
            return charts_data_values.get(chart_name, None)
    except FileNotFoundError:
        return None


def get_image_with_encoding(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")


def hex_to_rgba(hex_color, alpha=1.0):
    hex_color = hex_color.lstrip("#")
    rgb = tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
    return f"rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, {alpha})"
