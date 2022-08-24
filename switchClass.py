import utils

class SwitchClass:
    def __init__(self, method_id):
        self.method_id = method_id
        self.methods_dict = {
            1: utils.find_cur_line_by_sin_of_angle,
            2: utils.find_cur_line_by_accum_dist,
            3: utils.find_cur_line_min_by__last_point_min_dist,
            4: utils.find_cur_line_min_by_multiply_dists,
            5: utils.find_cur_line_cos_beta_adjacent_angle,
            6: utils.find_cur_line_by_min_dist_with_multiplier,
            7: utils.find_cur_line_by_sin_of_angle_with_multiplier
        }

    def choose_method(self, points, segments, r_cross, consider_segments):
        return self.methods_dict[self.method_id](points, consider_segments(segments, r_cross))


