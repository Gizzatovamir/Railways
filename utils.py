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

def point_to_segment_distance(p: Point, line: list) -> dict:
    try:
        a = line[0]["coords"]
        b = line[1]["coords"]
    except TypeError:
        return {"dist": -1, "break": True}
    ab = b - a
    ap = p - a

    if ap.dot(ab) <= 0.0:  # Point is lagging behind start of the segment, so perpendicular distance is not viable.
        return {"dist": ap.norm, "flag": False, "line_point": True,
                'cur_line': line, "break": False}  # Use distance to start of segment instead.

    bp = p - b

    if bp.dot(ab) >= 0.0:  # Point is advanced past the end of the segment, so perpendicular distance is not viable.
        return {"dist": bp.norm, "flag": False, "line_point": False,
                'cur_line': line, "break": False}  # Use distance to end of the segment instead.

    # Perpendicular distance of point to segment. Use distance to start of segment instead.
    return {"dist": (ab.cross(ap)).norm / ab.norm, "flag": True, 'cur_line': line, "break": False}


def point_to_segment_projection(points: dict) -> Point:
    """ Finds point projection on a line segment.
        Args:
            points['gps_point']: point from projection is made
            points['line_p1']: start of the segment
            points['line_p2']: end of the segment
        Returns:
            Point: projection of p to line segment [a,b].
    """

    p = points['gps_point']['coords']
    b = points['cur_line'][0]["coords"]
    a = points['cur_line'][1]["coords"]

    v = b - a
    res = a + v * (v.dot(p - a) / v.dot(v))
    return res


def find_cur_line_by_sin_of_angle(gps_points: list, observed_segments: list) -> list:
    angle_1 = 0
    angle_2 = 0
    for point in gps_points:
        angle_1 += point_to_segment_distance(point['coords'], observed_segments[0])['dist'] / (
                point['coords'] - observed_segments[0][0]['coords']).norm
        angle_2 += point_to_segment_distance(point['coords'], observed_segments[1])['dist'] / (
                point['coords'] - observed_segments[0][0]['coords']).norm
    if angle_2 > angle_1:
        cur_line = observed_segments[0]
    else:
        cur_line = observed_segments[1]
    return cur_line


def find_cur_line_by_accum_dist(gps_points: list, observed_segments: list) -> list:
    dist_1 = 0
    dist_2 = 0
    for point in gps_points:
        dist_1 += point_to_segment_distance(point['coords'], observed_segments[0])['dist']
        dist_2 += point_to_segment_distance(point['coords'], observed_segments[1])['dist']
    if dist_2 > dist_1:
        cur_line = observed_segments[0]
    else:
        cur_line = observed_segments[1]
    return cur_line


def find_cur_line_min_by__last_point_min_dist(gps_points: list, observed_segments: list) -> list:
    dist_1 = point_to_segment_distance(gps_points[-1]['coords'],
                                             observed_segments[0])['dist']
    dist_2 = point_to_segment_distance(gps_points[-1]['coords'],
                                             observed_segments[1])['dist']
    if dist_2 > dist_1:
        cur_line = observed_segments[0]
    else:
        cur_line = observed_segments[1]
    return cur_line

def find_cur_line_min_by_multiply_dists(gps_points: list, observed_segments: list) -> list:
    dist_1 = 0
    dist_2 = 0
    for point in gps_points:
        dist_1 += 1 / (point_to_segment_distance(point['coords'], observed_segments[0])['dist'] * (
                point['coords'] - observed_segments[0][0]['coords']).norm)
        dist_2 += 1 / (point_to_segment_distance(point['coords'], observed_segments[1])['dist'] * (
                point['coords'] - observed_segments[0][0]['coords']).norm)
    if dist_2 > dist_1:
        cur_line = observed_segments[0]
    else:
        cur_line = observed_segments[1]
    return cur_line


def find_cur_line_cos_beta(gps_points: list, observed_segments: list) -> list:
    dist_1 = 0
    dist_2 = 0
    for point in gps_points:
        dist_1 += np.pi - (point_to_segment_distance(point['coords'], observed_segments[0])['dist'] / (
                point['coords'] - observed_segments[0][0]['coords']).norm)
        dist_2 += np.pi - (point_to_segment_distance(point['coords'], observed_segments[1])['dist'] / (
                point['coords'] - observed_segments[0][0]['coords']).norm)
    if dist_2 < dist_1:
        cur_line = observed_segments[0]
    else:
        cur_line = observed_segments[1]
    return cur_line


def find_cur_line_by_min_dist_with_multiplier(gps_points: list, observed_segments: list) -> list:
    dist_1 = 0
    dist_2 = 0
    for multiplier in range(len(gps_points)):
        dist_1 += point_to_segment_distance(gps_points[multiplier]['coords'], observed_segments[0])['dist'] * multiplier
        dist_2 += point_to_segment_distance(gps_points[multiplier]['coords'], observed_segments[1])['dist'] * multiplier
    if dist_2 > dist_1:
        cur_line = observed_segments[0]
    else:
        cur_line = observed_segments[1]
    return cur_line


def find_cur_line_by_sin_of_angle_with_multiplier(gps_points: list, observed_segments: list) -> list:
    angle_1 = 0
    angle_2 = 0
    for multiplier in range(len(gps_points)):
        angle_1 += point_to_segment_distance(gps_points[multiplier]['coords'], observed_segments[0])['dist'] / ((
                gps_points[multiplier]['coords'] - observed_segments[0][0]['coords']).norm * (multiplier+1))
        angle_2 += point_to_segment_distance(gps_points[multiplier]['coords'], observed_segments[1])['dist'] / ((
                gps_points[multiplier]['coords'] - observed_segments[0][0]['coords']).norm * (multiplier+1))
    [print(point['id'], end=' ') for point in gps_points]
    print()
    print(observed_segments[0][0]['id'], ' start id of the switch')
    print(observed_segments[1][0]['id'], ' start id of the switch')
    [print(x['id'], end=' ') for x in observed_segments[0]]
    print()
    [print(x['id'], end=' ') for x in observed_segments[1]]
    print()
    print(angle_1, ' angle 1')
    print(angle_2, ' angle 2')
    if angle_2 > angle_1:
        cur_line = observed_segments[0]
    else:
        cur_line = observed_segments[1]
    return cur_line
