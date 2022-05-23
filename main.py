import matplotlib.pyplot as plt
import json
import os

MAP_PATH = "map_lines.json"
MAP_LINES = "map_points.json"

def get_json(path):
    with open(path, 'r') as f:
        data = json.load(f)
    return data
