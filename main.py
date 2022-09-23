import utils.utils
from src.StateMatcher import StateMatcher
from src.GroundTruthMatcher import GroundTruthMatcher
from src.PolyLineMatcher import PolyLineMatcher
from src.TesterClass import Tester
from utils.constants import GPS_POINTS_PATH, POINTS_PATH, LINES_PATH
import argparse
import sys


GROUND_TRUTH_FILE = "ground_truth"
MATCHED_TRUTH_FILE = "matched"
GROUND_TRUTH_CONFIG_NAME = "ground_truth_config"
MATCHING_CONFIG_NAME = "matching_config"


def get_arg_list(config_name) -> dict:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cfg", default=None, help="path to config file")
    parser.add_argument(
        "--path", default=GPS_POINTS_PATH, help="path to gps points in json format"
    )
    parser.add_argument(
        "--points_path", default=POINTS_PATH, help="path to map points in json format"
    )
    parser.add_argument(
        "--lines_path", default=LINES_PATH, help="path to map lines in json format"
    )
    parser.add_argument("--method", help="method to match the map on switches")
    parser.add_argument(
        "--mode",
        choices=["whole", "last_n", "interval"],
        default="whole",
        help="mode to select points used in methods to choose path",
    )
    parser.add_argument(
        "-n", type=int, help="n points that will be considered in methods"
    )
    parser.add_argument(
        "--start_r", type=int, help="starting distance for interval choosing method"
    )
    parser.add_argument(
        "--end_r", type=int, help="ending distance for interval choosing method"
    )
    parser.add_argument(
        "--result_csv_path", type=str, help="path to dir with result csv files"
    )
    parser.add_argument(
        "--logs_path", type=str, help=" path to all logs in json format"
    )
    args = parser.parse_args()
    arg_list = utils.utils.get_arg_list(args, config_name)
    return arg_list


if __name__ == "__main__":
    sys.setrecursionlimit(3500)
    print(sys.getrecursionlimit(), "recursion limit")
    ground_truth_arg_list = get_arg_list(GROUND_TRUTH_CONFIG_NAME)
    matcher = GroundTruthMatcher(ground_truth_arg_list)
    # matcher.draw_trajectory()
    matcher.match(GROUND_TRUTH_FILE)
    matcher.draw_full_map(matcher.result)
