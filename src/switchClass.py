import utils.utils as utils
from utils.utils import point_to_segment_projection, point_to_segment_distance


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
            7: utils.find_cur_line_min_by__last_point_min_dist,
            8: utils.find_cur_line_by_sum_of_dists_in_interval
        }
        self.method_point_connection = {
            1: self.multiple_points_method,
            2: self.multiple_points_method,
            3: self.multiple_points_method,
            4: self.multiple_points_method,
            5: self.multiple_points_method,
            6: self.multiple_points_method,
            7: self.single_point_method,
            8: self.multiple_points_method
        }

    def multiple_points_method(self, gps_points: list, observed_segments: dict, **kwargs) -> tuple:
        criterion_1, criterion_2 = 0.0, 0.0
        for i in range(len(gps_points)):
            criterion_1 += self.methods_dict[self.method_id](gps_points, observed_segments[0], i, **kwargs)
            criterion_2 += self.methods_dict[self.method_id](gps_points, observed_segments[1], i, **kwargs)
        return criterion_1, criterion_2

    def single_point_method(self, gps_points: list, observed_segments: dict, **kwargs) -> tuple:
        return self.methods_dict[self.method_id](gps_points[-1], observed_segments[0]), \
               self.methods_dict[self.method_id](gps_points[-1], observed_segments[1])

    def find_cur_line(self, gps_points: list, segments: list, **kwargs):
        observed_segments = kwargs["consider"](segments, kwargs['r'])
        criterion_1, criterion_2 = self.method_point_connection[self.method_id](gps_points, observed_segments, **kwargs)
        print(criterion_1)
        print(criterion_2)
        return observed_segments[0] if criterion_2 > criterion_1 else observed_segments[1]



