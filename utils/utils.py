import json
import numpy as np
from src.PointClass import Point
from typing import Dict, List, Tuple, Set

import yaml
from src.PolyLine import PolyLine
import pymap3d as pm


def get_json(path: str):
    with open(path, "r") as f:
        data = json.load(f)
    return data


def find_l0_h0() -> (float, float, float):
    return 59.62569003, 28.55332764, 0


def find_min_by_x(line: List[Dict]) -> Point:
    return (
        line[0]["coords"]
        if line[0]["coords"].x < line[1]["coords"].x
        else line[1]["coords"]
    )


def find_min_by_y(line: List[Dict]) -> Point:
    return (
        line[0]["coords"]
        if line[0]["coords"].y < line[1]["coords"].y
        else line[1]["coords"]
    )


def find_max_by_x(line: List[Dict]) -> Point:
    return (
        line[0]["coords"]
        if line[0]["coords"].x > line[1]["coords"].x
        else line[1]["coords"]
    )


def find_max_by_y(line: List[Dict]) -> Point:
    return (
        line[0]["coords"]
        if line[0]["coords"].y > line[1]["coords"].y
        else line[1]["coords"]
    )


def find_min_dict_x(line: List[Dict]) -> Dict:
    return line[0] if line[0]["coords"].x < line[1]["coords"].x else line[1]


def find_min_dict_y(line: List[Dict]) -> Dict:
    return line[0] if line[0]["coords"].y < line[1]["coords"].y else line[1]


def find_max_dict_x(line: List[Dict]) -> Dict:
    return line[0] if line[0]["coords"].x > line[1]["coords"].x else line[1]


def find_max_dict_y(line: List[Dict]) -> Dict:
    return line[0] if line[0]["coords"].y < line[1]["coords"].y else line[1]


def find_index(to_find: Dict, original_list: List[Dict]) -> int:
    for i in range(len(original_list)):
        if to_find["id"] == original_list[i]:
            return i


def find_dict(points, point_id) -> dict:
    return next(item for item in points if item["id"] == point_id)


def print_dict(to_print: dict) -> None:
    [print(el) for el in to_print]


def find_line_from_start_point(start_point: dict, lines: list) -> dict:
    for line in lines:
        if line["points"][0] == start_point["id"]:
            return line


def find_line_from_end_point(end_point: dict, lines: list) -> dict:
    for line in lines:
        if line["points"][-1] == end_point["id"]:
            return line


def point_to_segment_distance(p: Point, line: list) -> dict:
    try:
        a = line[0]["coords"]
        b = line[1]["coords"]
    except TypeError:
        return {"dist": -1, "break": True}
    except IndexError:
        return {"dist": -1, "break": True}
    ab = b - a
    ap = p - a

    if (
        ap.dot(ab) <= 0.0
    ):  # Point is lagging behind start of the segment, so perpendicular distance is not viable.
        return {
            "dist": ap.norm,
            "is_ortho": False,
            "line_point": "start",
            "cur_line": line,
            "break": False,
            "end_point": line[0],
        }  # Use distance to start of segment instead.
    #  Return True if function returns distance to the start and False if it returns to the end of segment
    bp = p - b

    if (
        bp.dot(ab) >= 0.0
    ):  # Point is advanced past the end of the segment, so perpendicular distance is not viable.
        return {
            "dist": bp.norm,
            "is_ortho": False,
            "line_point": "end",
            "cur_line": line,
            "break": False,
            "end_point": line[1],
        }  # Use distance to end of the segment instead.

    # Perpendicular distance of point to segment. Use distance to start of segment instead.
    return {
        "dist": (ab.cross(ap)).norm / ab.norm,
        "is_ortho": True,
        "cur_line": line,
        "break": False,
        "end_point": None,
    }


def point_to_segment_projection(p: Point, line: list) -> Point:
    """Finds point projection on a line segment.
    Args:
        points['gps_point']: point from projection is made
        points['line_p1']: start of the segment
        points['line_p2']: end of the segment
    Returns:
        Point: projection of p to line segment [a,b].
    """
    a = line[0]["coords"]
    b = line[1]["coords"]

    v = b - a
    res = a + v * (v.dot(p - a) / v.dot(v))
    return res


def find_cur_line_by_sin_of_angle(
    gps_points: list, observed_segment: list, i: int, **kwargs
) -> float:
    return (
        point_to_segment_distance(gps_points[i]["coords"], observed_segment)["dist"]
        / (gps_points[i]["coords"] - observed_segment[0]["coords"]).norm
    )


def find_cur_line_by_accum_dist(
    gps_points: list, observed_segment: list, i: int, **kwargs
) -> float:
    return point_to_segment_distance(gps_points[i]["coords"], observed_segment)["dist"]


def find_cur_line_min_by__last_point_min_dist(
    gps_point: dict, observed_segment: list, **kwargs
) -> float:
    return point_to_segment_distance(gps_point["coords"], observed_segment)["dist"]


def find_cur_line_min_by_multiply_dists(
    gps_points: list, observed_segment: list, i: int, **kwargs
) -> float:
    return (
        point_to_segment_distance(gps_points[i]["coords"], observed_segment)["dist"]
        * (gps_points[i]["coords"] - observed_segment[0]["coords"]).norm
    )


def find_cur_line_cos_beta_adjacent_angle(
    gps_points: list, observed_segment: list, i: int, **kwargs
) -> float:
    return np.pi - (
        point_to_segment_distance(gps_points[i]["coords"], observed_segment)["dist"]
        / (gps_points[i]["coords"] - observed_segment[0]["coords"]).norm
    )


def find_cur_line_by_min_dist_with_multiplier(
    gps_points: list, observed_segment: list, i: int, **kwargs
) -> float:
    return (
        point_to_segment_distance(gps_points[i]["coords"], observed_segment)["dist"] * i
    )


def find_cur_line_by_sin_of_angle_with_multiplier(
    gps_points: list, observed_segment: list, i: int, **kwargs
) -> float:
    return point_to_segment_distance(gps_points[i]["coords"], observed_segment)[
        "dist"
    ] / ((gps_points[i]["coords"] - observed_segment[0]["coords"]).norm * (i + 1))


def find_cur_line_by_sin_of_angle_multiplied(
    gps_points: list, observed_segment: list, i: int, **kwargs
) -> float:
    return (
        point_to_segment_distance(gps_points[i]["coords"], observed_segment)["dist"]
        * (i + 1)
        / (gps_points[i]["coords"] - observed_segment[0]["coords"]).norm
    )


def whole_radius_inclusion(gps_point: list, **kwargs) -> list:
    return gps_point


def segment_radius_inclusion(gps_points: list, **kwargs) -> list:
    return [
        gps_point
        for gps_point in gps_points
        if kwargs["constants"]["start_r"]
        < (gps_point["coords"] - kwargs["line_point"]["coords"]).norm
        <= kwargs["constants"]["end_r"]
    ]


def last_n_points(gps_points: list, **kwargs) -> list:
    return [gps_point for gps_point in gps_points[-kwargs["constants"]["n"] :]]


def dist_to_switch_segment(
    gps_point: dict, line_point: dict, segments: list, condition: bool
) -> int:
    try:
        if condition:
            return point_to_segment_distance(
                gps_point["coords"], [line_point, segments[0]]
            )["dist"]
        else:
            return point_to_segment_distance(
                gps_point["coords"], [line_point, segments[1]]
            )["dist"]
    except:
        return 10000


def get_angle(line_1, line_2, **kwargs) -> float:
    vec_1 = line_1[1]["coords"] - line_1[0]["coords"]
    if line_1[1]["id"] == line_2[0]["id"]:
        vec_2 = line_2[1]["coords"] - line_2[0]["coords"]
    else:
        vec_2 = line_2[-2]["coords"] - line_2[-1]["coords"]

    cos_alpha = (float(np.dot(vec_1.vector, np.reshape(vec_2.vector, (3, 1))))) / (
        vec_1.norm * vec_2.norm
    )
    return 0 < np.arccos(cos_alpha) < np.pi / 2


def is_switch_valid(cur_line: list, segments: list) -> dict:
    if all([get_angle(cur_line, segment) for segment in segments]):
        return {"is_valid": True}
    if get_angle(cur_line, segments[0]):
        return {"is_valid": False, "line": segments[0][0:2]}
    else:
        return {"is_valid": False, "line": segments[1][0:2]}


def is_switch_valid_poly_line(cur_line: list, poly_lines: list, **kwargs) -> dict:
    # [line.print_poly_line() for line in poly_lines]
    if all(
        [get_angle(cur_line, line.points_dict_list, **kwargs) for line in poly_lines]
    ):
        return {"is_valid": True}
    try:
        if get_angle(cur_line, poly_lines[0].points_dict_list):
            return {"is_valid": False, "line": poly_lines[0]}
        else:
            return {"is_valid": False, "line": poly_lines[1]}
    except Exception as e:
        # print(e)
        # [line.print_poly_line() for line in poly_lines]
        return {"is_valid": False, "line": poly_lines[0]}


def get_arg_list(args) -> dict:
    if args.cfg:
        with open(args.cfg, "r") as cfg:
            try:
                arg_list = yaml.load(cfg, Loader=yaml.FullLoader)["matching_config"]
                for el in args.__dict__:
                    if args.__dict__[el] and el != "cfg":
                        arg_list[el] = args.__dict__[el]
                print(arg_list)
            except yaml.YAMLError as exc:
                print(exc)
    else:
        arg_list = vars(args)
    return arg_list


def method_1_poly_line(gps_point: dict, poly_line: "PolyLine", **kwargs) -> float:
    return poly_line.point_to_poly_line_dist(gps_point["coords"])["dist"]["dist"]


def method_2_poly_line(
    gps_points: dict, poly_line: "PolyLine", i: int, **kwargs
) -> float:
    return (
        poly_line.point_to_poly_line_dist(gps_points[i]["coords"])["dist"]["dist"]
        / (gps_points[i]["coords"] - kwargs["line_point"]["coords"]).norm
    )


def method_3_poly_line(
    gps_points: dict, poly_line: "PolyLine", i: int, **kwargs
) -> float:
    return np.cos(
        np.pi
        - np.arccos(
            poly_line.point_to_poly_line_dist(gps_points[i]["coords"])["dist"]["dist"]
            / (gps_points[i]["coords"] - kwargs["line_point"]["coords"]).norm
        )
    )


def method_4_poly_line(
    gps_points: dict, poly_line: "PolyLine", i: int, **kwargs
) -> float:
    return (
        poly_line.point_to_poly_line_dist(gps_points[i]["coords"])["dist"]["dist"]
        * (gps_points[i]["coords"] - kwargs["line_point"]["coords"]).norm
    )


def method_5_poly_line(
    gps_points: dict, poly_line: "PolyLine", i: int, **kwargs
) -> float:
    return poly_line.point_to_poly_line_dist(gps_points[i]["coords"])["dist"][
        "dist"
    ] / ((gps_points[i]["coords"] - kwargs["line_point"]["coords"]).norm * (i + 1))


def method_6_poly_line(
    gps_points: dict, poly_line: "PolyLine", i: int, **kwargs
) -> float:
    return (
        poly_line.point_to_poly_line_dist(gps_points[i]["coords"])["dist"]["dist"] * i
    )


def method_7_poly_line(
    gps_points: dict, poly_line: "PolyLine", i: int, **kwargs
) -> float:
    return (
        poly_line.point_to_poly_line_dist(gps_points[i]["coords"])["dist"]["dist"]
        * (i + 1)
        / (gps_points[i]["coords"] - kwargs["line_point"]["coords"]).norm
    )


def find_next_poly_lines_on_switch(lines: list, last_segment: list, **kwargs) -> list:
    result = []
    try:
        for line in lines:
            if (
                last_segment[1]["id"] in line["points"]
                and last_segment[0]["id"] not in line["points"]
            ):
                result.append(
                    PolyLine(line["line_id"], line["points"], kwargs["points"])
                )
    except IndexError:
        return None
    return result


def switch_adding_condition(
    last_poly_line: PolyLine, poly_lines: list, end_r: int, **kwargs
) -> bool:
    conditions = []
    try:
        # print("____________")
        # print(last_poly_line.id_list, "start line on switch")
        for line in poly_lines:
            norm = (line.start["coords"] - line.end["coords"]).norm
            # print(norm, " norm between start and end of line on switch")
            conditions.append(
                norm <= end_r and (not line.start["end"] or not line.end["end"])
            )
        # print("____________")
    except TypeError:
        return False
    return any(conditions)


def transform_ecef_to_geodetic(point) -> (float, float, float):
    try:
        return pm.ecef2geodetic(*point["coords"].vector, deg=True)
    except AttributeError:
        return pm.ecef2geodetic(*point["coords"]["coords"].vector, deg=True)


def is_in_decision_area(poly_line: PolyLine, end_r: float) -> bool:
    return (poly_line.start["coords"] - poly_line.end["coords"]).norm <= end_r
