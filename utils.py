import json
import numpy as np
import pymap3d as pm
from PointClass import Point

def get_json(path: str):
    with open(path, 'r') as f:
        data = json.load(f)
    return data

def find_l0_h0(points: list) -> (float, float, float):
    res_lat = []
    res_lon = []
    res_h = []
    for point in points:
        lat, lon, h = pm.ecef2geodetic(*point['coords'].vector)
        res_lat.append(lat)
        res_lon.append(lon)
        res_h.append(h)

    return np.average(res_lat).astype(float), np.average(res_lon).astype(float), np.average(res_h).astype(float)

def find_min_by_x(line: list) -> Point:
    return line[0]['coords'] if line[0]['coords'].x < line[1]['coords'].x else line[1]['coords']

def find_min_by_y(line: list) -> Point:
    return line[0]['coords'] if line[0]['coords'].y < line[1]['coords'].y else line[1]['coords']

def find_max_by_x(line: list) -> Point:
    return line[0]['coords'] if line[0]['coords'].x > line[1]['coords'].x else line[1]['coords']

def find_max_by_y(line: list) -> Point:
    return line[0]['coords'] if line[0]['coords'].y > line[1]['coords'].y else line[1]['coords']
