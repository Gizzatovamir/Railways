import json
import numpy as np
from src.PointClass import Point


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


def point_to_segment_projection(p: Point, line: list) -> Point:
    """ Finds point projection on a line segment.
        Args:
            points['gps_point']: point from projection is made
            points['line_p1']: start of the segment
            points['line_p2']: end of the segment
        Returns:
            Point: projection of p to line segment [a,b].
    """

    b = line[1]["coords"]
    a = line[0]["coords"]

    v = b - a
    res = a + v * (v.dot(p - a) / v.dot(v))
    return res


def find_cur_line_by_sin_of_angle(gps_points: list, observed_segment: list, i: int, **kwargs) -> float:
    return point_to_segment_distance(gps_points[i]['coords'], observed_segment)['dist'] / (
            gps_points[i]['coords'] - observed_segment[0]['coords']).norm


def find_cur_line_by_accum_dist(gps_points: list, observed_segment: list, i: int, **kwargs) -> float:
    return point_to_segment_distance(gps_points[i]['coords'], observed_segment)['dist']


def find_cur_line_min_by__last_point_min_dist(gps_point: dict, observed_segment: list, **kwargs) -> float:
    return point_to_segment_distance(gps_point['coords'], observed_segment)['dist']


def find_cur_line_min_by_multiply_dists(gps_points: list, observed_segment: list, i: int, **kwargs) -> float:
    return (point_to_segment_distance(gps_points[i]['coords'], observed_segment)['dist'] * (
            gps_points[i]['coords'] - observed_segment[0]['coords']).norm)


def find_cur_line_cos_beta_adjacent_angle(gps_points: list, observed_segment: list, i: int, **kwargs) -> float:
    return np.pi - (point_to_segment_distance(gps_points[i]['coords'], observed_segment)['dist'] / (
            gps_points[i]['coords'] - observed_segment[0]['coords']).norm)


def find_cur_line_by_min_dist_with_multiplier(gps_points: list, observed_segment: list, i: int, **kwargs) -> float:
    return point_to_segment_distance(gps_points[i]['coords'], observed_segment)['dist'] \
           * i


def find_cur_line_by_sin_of_angle_with_multiplier(gps_points: list, observed_segment: list, i: int, **kwargs) -> float:
    return point_to_segment_distance(gps_points[i]['coords'], observed_segment)['dist'] / ((
                                                                                                   gps_points[i][
                                                                                                       'coords'] -
                                                                                                   observed_segment[0][
                                                                                                       'coords']).norm * (
                                                                                                   i + 1))


def whole_radius_inclusion(gps_point, **kwargs) -> list:
    return gps_point


def segment_radius_inclusion(gps_points, **kwargs) -> list:
    return [gps_point for gps_point in gps_points if kwargs['r_start'] < (gps_point["coords"] - kwargs['line_point']['coords']).norm <= kwargs['r_end']]


def last_n_points(gps_points, **kwargs) -> list:
    return [gps_point for gps_point in gps_points[-kwargs["n"]:]]
