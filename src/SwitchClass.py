import utils.utils as utils
from utils.utils import point_to_segment_projection, point_to_segment_distance


class SwitchClass:
    def __init__(self, method_id, selection_mode):
        self.method_id = method_id
        self.selection_mode = selection_mode
        self.methods_list = [
            utils.find_cur_line_by_sin_of_angle,
            utils.find_cur_line_by_accum_dist,
            utils.find_cur_line_cos_beta_adjacent_angle,
            utils.find_cur_line_min_by_multiply_dists,
            utils.find_cur_line_by_sin_of_angle_with_multiplier,
            utils.find_cur_line_by_min_dist_with_multiplier,
            utils.find_cur_line_min_by__last_point_min_dist,
            utils.find_cur_line_by_sin_of_angle_multiplied
        ]
        self.method_point_connection = [
            self.multiple_points_method,
            self.multiple_points_method,
            self.multiple_points_method,
            self.multiple_points_method,
            self.multiple_points_method,
            self.multiple_points_method,
            self.single_point_method,
            self.multiple_points_method
        ]
        self.selection_list = {
            "whole": utils.whole_radius_inclusion,
            "interval": utils.segment_radius_inclusion,
            "last_n": utils.last_n_points
        }

    def multiple_points_method(self, gps_points: list, observed_segments: dict, **kwargs) -> tuple:
        criterion_1, criterion_2 = 0.0, 0.0
        for i in range(len(gps_points)):
            criterion_1 += self.methods_list[self.method_id](gps_points, observed_segments[0], i, **kwargs)
            criterion_2 += self.methods_list[self.method_id](gps_points, observed_segments[1], i, **kwargs)
        return criterion_1, criterion_2

    def single_point_method(self, gps_points: list, observed_segments: dict, **kwargs) -> tuple:
        criterion_1, criterion_2 = self.methods_list[self.method_id](gps_points[-1], observed_segments[0]), \
               self.methods_list[self.method_id](gps_points[-1], observed_segments[1])
        print(criterion_1, " criterion 1")
        print(criterion_2, " criterion 2")
        return criterion_1, criterion_2

    def change_config(self, **kwargs):
        self.method_id = kwargs['method']
        self.selection_mode = kwargs['mode']

    def find_cur_line(self, gps_points: list, segments: list, **kwargs):
        selected_gps_points = self.selection_list[self.selection_mode](gps_points, **kwargs)
        criterion_1, criterion_2 = self.method_point_connection[self.method_id](selected_gps_points, segments, **kwargs)
        # print(gps_points[-1]['id'])
        # print(segments[0], " segment 1")
        # print(segments[1], " segment 2")
        # print(point_to_segment_distance(gps_points[-1]['coords'], segments[0])['dist'])
        # print(point_to_segment_distance(gps_points[-1]['coords'], segments[1])['dist'])
        return segments[0] if criterion_2 > criterion_1 else segments[1]



