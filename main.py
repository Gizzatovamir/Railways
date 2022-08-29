from src.StateMatcher import StateMatcher
from src.testerClass import Tester
from utils.constants import GPS_POINTS_PATH, POINTS_PATH, LINES_PATH
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", default=GPS_POINTS_PATH, help="path to gps points in json format")
    parser.add_argument("--points_path", default=POINTS_PATH, help="path to map points in json format")
    parser.add_argument("--lines_path", default=LINES_PATH, help="path to map lines in json format")
    parser.add_argument("--method", type=int, help="method to match the map on switches")
    parser.add_argument("--mode", choices=['whole', 'last_n', 'interval'], default='whole', help="mode to select points used in methods to choose path")
    parser.add_argument("-n", type=int, default=1, help='n points that will be considered in methods')
    parser.add_argument("--start_r", type=int, default=20, help="starting distance for interval choosing method")
    parser.add_argument("--end_r", type=int, default=25, help="ending distance for interval choosing method")
    args = parser.parse_args()
    matcher = StateMatcher(**vars(args))
    matcher.match()
    matcher.draw_full_map(matcher.result)
    #tester = Tester(matcher.switch_information)
    #tester.test_switches()
