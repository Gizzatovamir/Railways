import json
import numpy as np
import pymap3d as pm
from PointClass import Point


def get_json(path: str):
    with open(path, 'r') as f:
        data = json.load(f)
    return data


def find_l0_h0() -> (float, float, float):
    return 59.62569003, 28.55332764, 0


def find_min_by_x(line: list) -> Point:
    return line[0]['coords'] if line[0]['coords'].x < line[1]['coords'].x else line[1]['coords']


def find_min_by_y(line: list) -> Point:
    return line[0]['coords'] if line[0]['coords'].y < line[1]['coords'].y else line[1]['coords']


def find_max_by_x(line: list) -> Point:
    return line[0]['coords'] if line[0]['coords'].x > line[1]['coords'].x else line[1]['coords']


def find_max_by_y(line: list) -> Point:
    return line[0]['coords'] if line[0]['coords'].y > line[1]['coords'].y else line[1]['coords']


def find_min_dict_x(line: list) -> dict:
    return line[0] if line[0]['coords'].x < line[1]['coords'].x else line[1]


def find_min_dict_y(line: list) -> dict:
    return line[0] if line[0]['coords'].y < line[1]['coords'].y else line[1]


def find_max_dict_x(line: list) -> dict:
    return line[0] if line[0]['coords'].x > line[1]['coords'].x else line[1]


def find_max_dict_y(line: list) -> dict:
    return line[0] if line[0]['coords'].y < line[1]['coords'].y else line[1]

def find_index(to_find: dict, original_list: list) -> int:
    for i in range(len(original_list)):
        if to_find['id'] == original_list[i]:
            return i


def find_dict(points, point_id) -> dict:
    return next(item for item in points if item["id"] == point_id)


def print_dict(to_print: dict) -> None:
    [print(el) for el in to_print]


def find_line_from_start_point(start_point: dict, lines: list) -> dict:
    for line in lines:
        if line['points'][0] == start_point['id']:
            return line


def find_line_from_end_point(end_point: dict, lines: list) -> dict:
    for line in lines:
        if line['points'][-1] == end_point['id']:
            return line
