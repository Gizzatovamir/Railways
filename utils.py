import json
import numpy as np
import pymap3d as pm
from PointClass import Point

def get_json(path: str):
    with open(path, 'r') as f:
        data = json.load(f)
    return data

def find_l0_h0() -> (float, float, float):
    return 55,39,0


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


def find_sublist(to_find: int, original_list: list, condition: bool) -> dict:
    for i in range(len(original_list)):
        if to_find == original_list[i]:
            print(original_list)
            print(i)
            if condition:
                return original_list[i]
            else:
                return original_list[i-1]


def find_index(to_find: int, original_list: list) -> int:
    for i in range(len(original_list)):
        if to_find == original_list[i]:
            return i
