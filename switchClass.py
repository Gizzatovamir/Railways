import utils
from utils import point_to_segment_projection, point_to_segment_distance

class SwitchClass:
    def __init__(self, method_id):
        self.method_id = method_id
        self.methods_dict = {
            1: utils.find_cur_line_by_sin_of_angle,
            2: utils.find_cur_line_by_accum_dist,
            3: utils.find_cur_line_min_by_multiply_dists,
            4: utils.find_cur_line_cos_beta_adjacent_angle,
            5: utils.find_cur_line_by_min_dist_with_multiplier,
            6: utils.find_cur_line_by_sin_of_angle_with_multiplier,
            7: utils.find_cur_line_min_by__last_point_min_dist
        }
        self.method_point_connection = {
            1: self.multiple_points_method,
            2: self.multiple_points_method,
            3: self.multiple_points_method,
            4: self.multiple_points_method,
            5: self.multiple_points_method,
            6: self.multiple_points_method,
            7: self.single_point_method
        }


    def multiple_points_method(self, gps_points: list, observed_segments: dict) -> tuple:
        criterion_1, criterion_2 = 0.0, 0.0
        for i in range(len(gps_points)):
            criterion_1 += self.methods_dict[self.method_id](gps_points, observed_segments[0], i)
            criterion_2 += self.methods_dict[self.method_id](gps_points, observed_segments[1], i)
        return criterion_1, criterion_2
    def single_point_method(self, gps_points: list, observed_segments: dict) -> tuple:
        criterion_1 = self.methods_dict[self.method_id](gps_points[-1], observed_segments[0])
        criterion_2 = self.methods_dict[self.method_id](gps_points[-1], observed_segments[1])
        return criterion_1, criterion_2
    def find_cur_line(self, gps_points:list, segments: list, *args):
        observed_segments = args[1](segments, args[0])
        criterion_1, criterion_2 = self.method_point_connection[self.method_id](gps_points, observed_segments)
        return observed_segments[0] if criterion_2 > criterion_1 else observed_segments[1]



