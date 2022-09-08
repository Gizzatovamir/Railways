import utils.utils as utils
from src.RailMap import RailLines
from utils.constants import POINTS_PATH, LINES_PATH
from src.PointClass import Point


class PolyLine:
    __slots__ = ("_line_id", "_point_id_list", "map_points", "points_dict_list")

    def __init__(self, line_id: int, point_ids: list):
        self._line_id = line_id
        self._point_id_list = point_ids
        self.map_points = RailLines(
            path_to_lines=LINES_PATH, path_to_points=POINTS_PATH
        )
        self.points_dict_list = self.get_poly_line_list_by_id()

    def get_poly_line_list_by_id(self) -> list:
        return [
            utils.find_dict(self.map_points.points, point_id)
            for point_id in self._point_id_list
        ]

    def point_to_poly_line_dist(self, p: Point) -> dict:
        result = []
        last_info = []
        for i in range(len(self.points_dict_list) - 1):
            current_segment = self.points_dict_list[i : i + 2]
            distance_to_segment = utils.point_to_segment_distance(p, current_segment)
            ortho_point = utils.point_to_segment_projection(p, current_segment)
            if distance_to_segment["is_ortho"]:
                result.append([distance_to_segment, ortho_point, current_segment])
            else:
                last_info = [distance_to_segment, ortho_point, current_segment]
        try:
            res = min(result, key=lambda x: x[0]["dist"])
            return {
                "dist": res[0],
                "ortho_point": res[1],
                "line": res[2],
                "is_valid": True,
            }
        except ValueError:
            print("there is no suitable segment in the poly line")
            return {
                "dist": last_info[0],
                "ortho_point": last_info[1],
                "line": last_info[2],
                "is_valid": False,
            }

    def point_to_poly_line_projection(self, p: Point) -> dict:
        res = []
        last_info = []
        for i in range(len(self.points_dict_list) - 1):
            dist = utils.point_to_segment_distance(p, self.points_dict_list[i : i + 2])
            projection = utils.point_to_segment_projection(
                p, self.points_dict_list[i : i + 2]
            )
            if dist["is_ortho"]:
                res.append([dist, projection])
            else:
                last_info = projection
        try:
            return {
                "ortho_point": min(res, key=lambda x: x[0]["dist"])[1],
                "is_valid": True,
            }
        except ValueError:
            print("there is no suitable segment in the poly line")
            return {"ortho_point": last_info, "is_valid": False}

    def get_next_segment(self, segment: list) -> list:
        index = self.points_dict_list.index(segment[1])
        return self.points_dict_list[index : index + 2]

    def print_poly_line(self) -> None:
        print(self._point_id_list, " - list of points in poly line")
