from src.PolyLineMatcher import PolyLineMatcher
import utils.utils as utils
from src.ChainSwitch import ChainSwitch
from src.PolyLine import PolyLine
from typing import List, Dict, Tuple


class GroundTruthMatcher(PolyLineMatcher):
    __slots__ = "switch_chain_class"

    def __init__(self, kwargs: Dict):
        super(GroundTruthMatcher, self).__init__(kwargs)
        self.switch_chain_class = ChainSwitch(lines=self.lines, end_r=self.end_r)

    def choose_line_on_cross(
        self, i: int, last_poly_line: PolyLine, **kwargs
    ) -> Tuple[PolyLine, int]:
        path_on_chain_of_switches = []
        last_segment = (
            last_poly_line.points_dict_list[:2][::-1]
            if kwargs["direction"] == "start"
            else last_poly_line.points_dict_list[-2:]
        )
        next_poly_lines = utils.find_next_poly_lines_on_switch(
            self.lines, last_segment, **kwargs
        )
        is_valid_condition = utils.is_switch_valid_poly_line(
            last_segment, next_poly_lines, **kwargs
        )
        if is_valid_condition["is_valid"]:
            while utils.switch_adding_condition(
                last_poly_line, next_poly_lines, self.end_r, **kwargs
            ):
                points = []
                graph = self.switch_chain_class.create_graph_on_switch_chain(
                    last_poly_line, next_poly_lines, None, **kwargs
                )
                tmp_i = i
                try:
                    while (
                        list(graph.keys())[0].end["coords"]
                        - self.gps_points[tmp_i]["coords"]
                    ).norm <= self.end_r:
                        tmp_i += 1
                except IndexError:
                    break
                print("old graph")
                ChainSwitch.print_graph(graph)
                leaves = self.switch_chain_class.dfs(graph)
                if len(graph) > 2:
                    root = self.find_path_class.find_cur_switch(
                        self.gps_points[tmp_i], graph, leaves, **kwargs
                    )
                    while (
                        root.start["coords"] - self.gps_points[i]["coords"]
                    ).norm <= (root.end["coords"] - root.start["coords"]).norm:
                        points.append(self.gps_points[i])
                        self.gps_points[i]["is_on_switch"] = is_valid_condition[
                            "is_valid"
                        ]
                        i += 1
                    path_on_chain_of_switches.append(root)
                    last_poly_line = root
                    self.link_points_to_poly_line_on_switch(points, last_poly_line)
                    last_segment = (
                        last_poly_line.points_dict_list[:2][::-1]
                        if kwargs["direction"] == "start"
                        else last_poly_line.points_dict_list[-2:]
                    )
                    next_poly_lines = utils.find_next_poly_lines_on_switch(
                        self.lines, last_segment, **kwargs
                    )
                else:
                    break
            print("Result path on chain of switches ", end=": ")
            ChainSwitch.print_path(path_on_chain_of_switches)
            return self.get_line_without_chain(
                next_poly_lines, last_segment, i, **kwargs
            )
        else:
            return is_valid_condition["line"], 1
