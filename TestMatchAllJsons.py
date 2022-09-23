from src.StateMatcher import StateMatcher
from src.TesterClass import Tester
from utils.constants import GPS_POINTS_PATH, POINTS_PATH, LINES_PATH
import argparse
import os
from main import get_arg_list
from src.GroundTruthMatcher import GroundTruthMatcher
from src.PolyLineMatcher import PolyLineMatcher
import sys

GROUND_TRUTH_FILE = "ground_truth"
MATCHED_TRUTH_FILE = "matched"
GROUND_TRUTH_CONFIG_NAME = "ground_truth_config"
MATCHING_CONFIG_NAME = "matching_config"


if __name__ == "__main__":
    sys.setrecursionlimit(3500)
    ground_truth_arg_list = get_arg_list(GROUND_TRUTH_CONFIG_NAME)
    matching_arg_list = get_arg_list(MATCHING_CONFIG_NAME)
    logs_path = next(os.walk(matching_arg_list["logs_path"]), (None, None, []))
    for gps_points_path in logs_path[2]:
        matching_arg_list["path"] = "{}/{}".format(logs_path[0], gps_points_path)
        ground_truth_arg_list["path"] = "{}/{}".format(logs_path[0], gps_points_path)
        print(matching_arg_list)
        print(ground_truth_arg_list)
        print("Now {} log is matching".format(matching_arg_list["path"]))
        matcher = GroundTruthMatcher(ground_truth_arg_list)
        poly_line_matcher = PolyLineMatcher(matching_arg_list)
        # matcher.draw_trajectory()
        matcher.match(GROUND_TRUTH_FILE)
        poly_line_matcher.match(MATCHED_TRUTH_FILE)
        # matcher.draw_full_map(matcher.result)
