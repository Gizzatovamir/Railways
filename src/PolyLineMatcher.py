from utils.constants import MIN_DIST
from src.RailMap import RailLines
from src.GPSPoints import GPSPoints
import matplotlib.pyplot as plt
import utils.utils as utils
from src.SwitchClass import SwitchClass
from utils.utils import point_to_segment_distance, point_to_segment_projection
import itertools
from src.PolyLine import PolyLine
from src.StateMatcher import StateMatcher
from src.MakeCSV import MakeCSV


class PolyLineMatcher(StateMatcher):
    def get_initial_points(self, index: int, min_dist=MIN_DIST) -> dict:
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
                        self.lines[i]["line_id"], self.lines[i]["points"]
                    )
                    self.gps_points[index]['poly_line_id'] = self.lines[i]["line_id"]
                    points = {
                        "gps_point": self.gps_points[index],
                        "cur_line": poly_line,
                    }
        self.result_path.append(points["cur_line"].get_id())
        return points

    def find_initial_state(self, index: int) -> dict:
        points = self.get_initial_points(index)
        if points:
            current_line = points["cur_line"].point_to_poly_line_dist(
                self.gps_points[index]["coords"]
            )["line"]
            if all([not line_point["cross"] for line_point in current_line]):
                points["gps_point"] = points["cur_line"].point_to_poly_line_projection(
                    points["gps_point"]["coords"]
                )
            for point in current_line:
                if point["cross"]:
                    if (
                        self.gps_points[index]["coords"] - point["coords"]
                    ).norm <= self.end_r:
                        self.point_buffer.append(self.gps_points[index])
                        self.gps_points[index]["is_on_switch"] = True
                        points = None
        return points

    # def add_point_to_result(
    #     self, point: dict, line_point: dict, ortho_point_dist: dict, condition: bool
    # ) -> (list, bool):

    def find_next_poly_lines_on_switch(self, last_segment: list, **kwargs) -> list:
        result = []
        for line in self.lines:
            if (
                last_segment[1]["id"] in line["points"]
                and last_segment[0]["id"] not in line["points"]
            ):
                result.append(PolyLine(line["line_id"], line["points"]))
        return result

    def choose_line_on_cross(self, i: int, last_segment: list, **kwargs) -> tuple:
        points = []
        next_poly_lines = self.find_next_poly_lines_on_switch(last_segment, **kwargs)
        is_valid_condition = utils.is_switch_valid_poly_line(
            last_segment, next_poly_lines, **kwargs
        )
        while (
            last_segment[1]["coords"] - self.gps_points[i]["coords"]
        ).norm <= self.end_r:
            points.append(self.gps_points[i])
            self.gps_points[i]["is_on_switch"] = is_valid_condition["is_valid"]
            i += 1
        print(is_valid_condition, " is valid condition")
        if is_valid_condition["is_valid"]:
            print(last_segment[1], " last segment")
            print(next_poly_lines)
            [next_poly_line.print_poly_line() for next_poly_line in next_poly_lines]
            cur_poly_line = self.find_path_class.find_cur_poly_line(
                points,
                next_poly_lines,
                line_point=last_segment[1],
                constants=self.switch_information["constants"],
            )
        else:
            cur_poly_line = is_valid_condition["line"]
        self.link_points_to_poly_line_on_switch(points, cur_poly_line)
        self.result_path.append(cur_poly_line.get_id())
        return cur_poly_line, len(points) if points != [] else 1

    def link_points_to_poly_line_on_switch(
        self, gps_points: list, poly_line: PolyLine
    ) -> None:
        for point in gps_points:
            cur_point_to_dist = poly_line.point_to_poly_line_dist(point["coords"])
            point['poly_line_id'] = poly_line.get_id()
            self.result.append(
                [
                    point,
                    cur_point_to_dist["ortho_point"],
                ]
            )

    def link_points_to_paths(self, i: int):
        cur_point_to_dist = self.initial_dict["cur_line"].point_to_poly_line_dist(
            self.gps_points[i]["coords"]
        )
        if cur_point_to_dist["is_valid"]:
            self.result.append(
                [
                    self.gps_points[i],
                    cur_point_to_dist["ortho_point"],
                ]
            )
            self.gps_points[i]['poly_line_id'] = self.initial_dict["cur_line"].get_id()
            i += 1
        else:
            last_segment = (
                self.initial_dict["cur_line"].points_dict_list[:2][::-1]
                if cur_point_to_dist["dist"]["line_point"] == "start"
                else self.initial_dict["cur_line"].points_dict_list[-2:]
            )
            result_poly_line, step = self.choose_line_on_cross(
                i, last_segment, direction=cur_point_to_dist["dist"]["line_point"]
            )
            self.initial_dict["cur_line"] = result_poly_line
            i += step
        if i < len(self.gps_points):
            self.link_points_to_paths(i)

    def match(self) -> None:
        # self.gps_points = self.gps_points[::-1]
        self.initial_dict, i = self.initialize()
        self.result.append(
            [self.gps_points[i - 1], self.initial_dict["gps_point"]["ortho_point"]]
        )
        self.link_points_to_paths(i)
        print(self.result_path, " result path that train has passed")
        make_csv = MakeCSV("result_df")
        make_csv.linked_dict_list_to_data_frame(self.result)
