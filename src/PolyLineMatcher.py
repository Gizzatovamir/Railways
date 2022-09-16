from utils.constants import MIN_DIST
import utils.utils as utils
from utils.utils import point_to_segment_distance
from src.PolyLine import PolyLine
from src.StateMatcher import StateMatcher
from src.MakeCSV import MakeCSV
from typing import Dict, List, Tuple, Set


class PolyLineMatcher(StateMatcher):
    def __init__(self, kwargs: Dict):
        super(PolyLineMatcher, self).__init__(kwargs)
        self.result_path = []
        print(kwargs["result_csv_path"])
        self.make_csv = MakeCSV(
            kwargs["result_csv_path"]
            + kwargs["path"].split("/")[-1].split(".")[0]
            + "/"
        )
        self.make_csv.raw_dict_list_to_data_frame(self.gps_points)

    def find_init_direction(self, points: Dict, index: int) -> str:
        distances = []
        start = points["cur_line"].start
        for point in self.gps_points[index : index + 3]:
            distances.append((start["coords"] - point["coords"]).norm)
        return "start" if distances[0] > distances[-1] else "end"

    def get_initial_points(self, index: int, min_dist=MIN_DIST) -> Dict:
        points = None
        for i in range(len(self.lines)):
            for j in range(len(self.lines[i]["points"]) - 1):
                line_points = [
                    utils.find_dict(self.points, self.lines[i]["points"][j]),
                    utils.find_dict(self.points, self.lines[i]["points"][j + 1]),
                ]
                current_dict = point_to_segment_distance(
                    self.gps_points[index]["coords"], line_points
                )
                if current_dict["dist"] < min_dist and current_dict["is_ortho"]:
                    min_dist = current_dict["dist"]
                    poly_line = PolyLine(
                        self.lines[i]["line_id"], self.lines[i]["points"], self.points
                    )
                    self.gps_points[index]["poly_line"] = poly_line
                    points = {
                        "gps_point": self.gps_points[index],
                        "cur_line": poly_line,
                    }
        return points

    def find_initial_state(self, index: int) -> Dict:
        points = self.get_initial_points(index)
        if points:
            current_line = points["cur_line"].point_to_poly_line_dist(
                self.gps_points[index]["coords"]
            )["line"]
            if all([not line_point["cross"] for line_point in current_line]):
                points["gps_point"] = points["cur_line"].point_to_poly_line_projection(
                    points["gps_point"]["coords"]
                )["ortho_point"]
                # self.result_path.append(points["cur_line"].get_id)
                points["direction"] = self.find_init_direction(points, index)
            for point in current_line:
                if point["cross"]:
                    if (
                        self.gps_points[index]["coords"] - point["coords"]
                    ).norm <= self.end_r:
                        self.point_buffer.append(self.gps_points[index])
                        self.gps_points[index]["is_on_switch"] = True
                        points = None

        return points

    def get_line_without_chain(
        self,
        next_poly_lines: List[PolyLine],
        last_segment: List[Dict],
        i: int,
        **kwargs
    ) -> Tuple[PolyLine, int]:
        points = []
        for line in next_poly_lines:
            norm = (
                line.points_dict_list[-1]["coords"] - line.points_dict_list[0]["coords"]
            ).norm
            if norm < self.end_r:
                self.end_r = norm

        is_valid_condition = utils.is_switch_valid_poly_line(
            last_segment, next_poly_lines, **kwargs
        )
        print(last_segment[1])
        print(last_segment[0])
        print(" Last segment")
        print("len of all gps points", len(self.gps_points))
        print("__________")
        while (
            last_segment[1]["coords"] - self.gps_points[i]["coords"]
        ).norm <= self.end_r and i < len(self.gps_points) - 1:
            print(self.gps_points[i])
            points.append(self.gps_points[i])
            self.gps_points[i]["is_on_switch"] = is_valid_condition["is_valid"]
            i += 1
        if is_valid_condition["is_valid"]:
            cur_poly_line = self.find_path_class.find_cur_poly_line(
                points,
                next_poly_lines,
                line_point=last_segment[1],
                constants=self.switch_information["constants"],
            )
        else:
            cur_poly_line = is_valid_condition["line"]
        self.link_points_to_poly_line_on_switch(points, cur_poly_line)
        return cur_poly_line, len(points) if points != [] else 1

    def choose_line_on_cross(
        self, i: int, last_poly_line: PolyLine, **kwargs
    ) -> Tuple[PolyLine, int]:
        last_segment = (
            last_poly_line.points_dict_list[:2][::-1]
            if kwargs["direction"] == "start"
            else last_poly_line.points_dict_list[-2:]
        )
        next_poly_lines = utils.find_next_poly_lines_on_switch(
            self.lines, last_segment, **kwargs
        )
        return self.get_line_without_chain(next_poly_lines, last_segment, i, **kwargs)

    def match_all_gps_points(self) -> None:
        for point in self.gps_points:
            try:
                print(point["poly_line"].id_list, " - ", point["id"])
                print("__________")
                point_projection = point["poly_line"].point_to_poly_line_projection(
                    point["coords"]
                )["ortho_point"]
                self.result.append([point, point_projection])
            except Exception as e:
                pass

    @staticmethod
    def link_points_to_poly_line_on_switch(
        gps_points: List[Dict], poly_line: PolyLine
    ) -> None:
        for point in gps_points:
            # cur_point_to_dist = poly_line.point_to_poly_line_dist(point["coords"])
            point["poly_line"] = poly_line

    def link_points_to_paths(self, i: int) -> None:
        # print(self.initial_dict["cur_line"])
        cur_point_to_dist = self.initial_dict["cur_line"].point_to_poly_line_dist(
            self.gps_points[i]["coords"], direction=self.initial_dict["direction"]
        )
        try:
            print(cur_point_to_dist["is_valid"])
            if cur_point_to_dist["is_valid"]:
                self.gps_points[i]["poly_line"] = self.initial_dict["cur_line"]
                print(self.initial_dict["cur_line"].print_poly_line())
                i += 1
            else:
                result_poly_line, step = self.choose_line_on_cross(
                    i,
                    self.initial_dict["cur_line"],
                    direction=self.initial_dict["direction"],
                    points=self.points,
                )
                self.initial_dict["cur_line"] = result_poly_line
                print(i, "current point")
                i += step
        except Exception as e:
            print("Exception", e)
            return
        if i < len(self.gps_points) and self.initial_dict["cur_line"]:
            self.link_points_to_paths(i)

    def match(self) -> None:
        # self.gps_points = self.gps_points[::-1]
        self.initial_dict, i = self.initialize()
        self.gps_points[i - 1]["poly_line"] = self.initial_dict["cur_line"]
        self.link_points_to_paths(i)
        self.match_all_gps_points()
        self.make_csv.matched_dict_list_to_data_frame(self.result)
