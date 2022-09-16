import utils.utils as utils
from utils.utils import point_to_segment_projection, point_to_segment_distance
from src.PolyLine import PolyLine
from typing import Dict, List, Tuple, Set


class SwitchClass:
    def __init__(self, method_id, selection_mode):
        self.method_id = method_id
        self.selection_mode = selection_mode
        self.methods_segments_list = [
            utils.find_cur_line_by_sin_of_angle,
            utils.find_cur_line_by_accum_dist,
            utils.find_cur_line_cos_beta_adjacent_angle,
            utils.find_cur_line_min_by_multiply_dists,
            utils.find_cur_line_by_sin_of_angle_with_multiplier,
            utils.find_cur_line_by_min_dist_with_multiplier,
            utils.find_cur_line_min_by__last_point_min_dist,
            utils.find_cur_line_by_sin_of_angle_multiplied,
        ]
        self.method_point_connection = [
            self.multiple_points_method,
            self.multiple_points_method,
            self.multiple_points_method,
            self.multiple_points_method,
            self.multiple_points_method,
            self.multiple_points_method,
            self.single_point_method,
            self.multiple_points_method,
        ]
        self.poly_line_method_list = [
            utils.method_1_poly_line,
            utils.method_2_poly_line,
            utils.method_3_poly_line,
            utils.method_4_poly_line,
            utils.method_5_poly_line,
            utils.method_6_poly_line,
            utils.method_7_poly_line,
        ]
        self.selection_list = {
            "whole": utils.whole_radius_inclusion,
            "interval": utils.segment_radius_inclusion,
            "last_n": utils.last_n_points,
        }
        self.method_poly_line_connection = [
            self.single_point_poly_line_method,
            self.multiple_point_poly_line_method,
            self.multiple_point_poly_line_method,
            self.multiple_point_poly_line_method,
            self.multiple_point_poly_line_method,
            self.multiple_point_poly_line_method,
            self.multiple_point_poly_line_method,
        ]

    def multiple_points_method(
        self, gps_points: List[Dict], observed_segments: List[List[Dict]], **kwargs
    ) -> List[Dict]:
        criteria = []
        for segment in observed_segments:
            tmp_criterion = 0
            for i in range(len(gps_points)):
                tmp_criterion += self.methods_segments_list[self.method_id](
                    gps_points, segment, i, **kwargs
                )
            criteria.append([tmp_criterion, segment])
        return min(criteria, key=lambda x: x[0])[1]

    def single_point_method(
        self, gps_points: List[Dict], observed_segments: List[List[Dict]], **kwargs
    ) -> List[Dict]:
        criteria = []
        for segment in observed_segments:
            criteria.append(
                [
                    self.methods_segments_list[self.method_id](
                        gps_points[-1], segment, **kwargs
                    ),
                    segment,
                ]
            )
        return min(criteria, key=lambda x: x[0])[1]

    def multiple_point_poly_line_method(
        self, gps_points: List[Dict], poly_lines: List[PolyLine], **kwargs
    ) -> PolyLine:
        criteria = []
        for poly_line in poly_lines:
            tmp_criterion = 0
            for i in range(len(gps_points)):
                tmp_criterion += self.poly_line_method_list[self.method_id](
                    gps_points[i], poly_line, i, **kwargs
                )
            criteria.append([tmp_criterion, poly_line])
        return min(criteria, key=lambda x: x[0])[1]

    def single_point_poly_line_method(
        self, gps_points: List[Dict], poly_lines: List[PolyLine], **kwargs
    ) -> PolyLine:
        [print(poly_line.id_list, end=" | ") for poly_line in poly_lines]
        print("Poly lines to choose")
        criteria = []
        # [print(poly_line.get_id, " Line id") for poly_line in poly_lines]
        for poly_line in poly_lines:
            criteria.append(
                [
                    self.poly_line_method_list[self.method_id](
                        gps_points[-1], poly_line
                    ),
                    poly_line,
                ]
            )
        if criteria:
            return min(criteria, key=lambda x: x[0])[1]
        else:
            return None

    def change_config(self, **kwargs) -> None:
        self.method_id = kwargs["method"]
        self.selection_mode = kwargs["mode"]

    def find_cur_line(
        self, gps_points: List[dict], segments: List[Dict], **kwargs
    ) -> List[Dict]:
        selected_gps_points = self.selection_list[self.selection_mode](
            gps_points, **kwargs
        )
        result_segment = self.method_point_connection[self.method_id](
            selected_gps_points, segments, **kwargs
        )
        return result_segment

    def find_cur_poly_line(
        self, gps_points: List[Dict], poly_lines: List[PolyLine], **kwargs
    ) -> PolyLine:
        selected_gps_points = self.selection_list[self.selection_mode](
            gps_points, **kwargs
        )
        result_poly_line = self.method_poly_line_connection[self.method_id](
            selected_gps_points, poly_lines, **kwargs
        )
        return result_poly_line

    def find_cur_switch(
        self, gps_point: Dict, graph: Dict, leaves: Set, **kwargs
    ) -> PolyLine:
        result_poly_line = self.method_poly_line_connection[0](
            [gps_point], leaves, **kwargs
        )
        for key, value in graph.items():
            if result_poly_line in value and len(graph.items()) > 1:
                return key
            else:
                return None
