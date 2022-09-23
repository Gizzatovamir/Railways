import utils.utils as utils
from utils.constants import POINTS_PATH, LINES_PATH
from src.PointClass import Point
from typing import TYPE_CHECKING, Dict, List, Set, Tuple
from copy import deepcopy

if TYPE_CHECKING:
    from src.RailMap import RailLines


class PolyLine:
    __slots__ = ("_line_id", "_point_id_list", "map_points", "_points_dict_list")

    def __init__(self, line_id: int, point_ids: List[int], map_points: "RailLines"):
        self._line_id = line_id
        self._point_id_list = point_ids
        self.map_points = map_points
        self._points_dict_list = self.get_poly_line_list_by_id()

    def get_poly_line_list_by_id(self) -> List[Dict]:
        return [
            utils.find_dict(self.map_points, point_id)
            for point_id in self._point_id_list
        ]

    def point_to_poly_line_dist(self, p: Point, **kwargs) -> Dict:
        result: List = []
        for i in range(len(self._points_dict_list) - 1):
            current_segment = self._points_dict_list[i : i + 2]
            distance_to_segment = utils.point_to_segment_distance(p, current_segment)
            ortho_point = utils.point_to_segment_projection(p, current_segment)
            result.append([distance_to_segment, ortho_point, current_segment])
        try:
            res = min(result, key=lambda x: x[0]["dist"])

            if not res[0]["is_ortho"]:
                if any(
                    [
                        # если расстояние не ортогонально и проекция находится на начале или конце геолинии, то True
                        res[0]["end_point"]["id"] == last_point["id"]
                        for last_point in [self.start, self.end]
                    ]
                ):
                    # если точка гоелинии является концом карты и движемся в конец линии, то True
                    if (self.start["end"] and kwargs["direction"] == "start") or (
                        self.end["end"] and kwargs["direction"] == "end"
                    ):
                        return {"is_valid": False, "is_breakable": True}
                    else:
                        return {
                            "dist": res[0],
                            "ortho_point": res[1],
                            "line": res[2],
                            "is_valid": False,
                            "is_breakable": False,
                        }
                else:
                    return {
                        "dist": res[0],
                        "ortho_point": res[1],
                        "line": res[2],
                        "is_valid": True,
                        "is_breakable": False,
                    }
            else:
                return {
                    "dist": res[0],
                    "ortho_point": res[1],
                    "line": res[2],
                    "is_valid": True,
                    "is_breakable": False,
                }
        except ValueError:
            return {"is_valid": False, "is_breakable": False}

    def point_to_poly_line_projection(self, p: Point) -> Dict:
        res = []
        last_info = []
        for i in range(len(self._points_dict_list) - 1):
            dist = utils.point_to_segment_distance(p, self._points_dict_list[i : i + 2])
            projection = utils.point_to_segment_projection(
                p, self._points_dict_list[i : i + 2]
            )
            res.append([dist, projection])
        try:
            return {
                "ortho_point": min(res, key=lambda x: x[0]["dist"])[1],
                "is_valid": True,
            }
        except ValueError:
            return {"ortho_point": last_info, "is_valid": False}

    def get_next_segment(self, segment: List[Dict]) -> List[Dict]:
        index = self._points_dict_list.index(segment[1])
        return self._points_dict_list[index : index + 2]

    def print_poly_line(self) -> None:
        print(self._point_id_list, " - list of points in poly line")

    def print_poly_line_silent(self) -> None:
        print(self._point_id_list, end=" ")

    @property
    def id(self):
        return deepcopy(self._line_id)

    @property
    def start(self):
        return deepcopy(self._points_dict_list[0])

    @property
    def end(self):
        return deepcopy(self._points_dict_list[-1])

    @property
    def start_ids(self):
        return deepcopy(self._point_id_list[:2])

    @property
    def end_ids(self):
        return deepcopy(self._point_id_list[-2:])

    def last_segment(self, direction: str):
        return self._points_dict_list[: 2 if direction == "start" else -2 :]

    @property
    def points_dict_list(self):
        return deepcopy(self._points_dict_list)

    @property
    def id_list(self):
        return deepcopy(self._point_id_list)
