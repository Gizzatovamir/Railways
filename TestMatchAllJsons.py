from src.StateMatcher import StateMatcher
from src.TesterClass import Tester
from utils.constants import GPS_POINTS_PATH, POINTS_PATH, LINES_PATH
import argparse
from os import walk
from glob import glob


DIR = "./results/"

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--logs_path", default=GPS_POINTS_PATH, help="path to directory with all json logs")
    parser.add_argument("--points_path", default=POINTS_PATH, help="path to map points in json format")
    parser.add_argument("--lines_path", default=LINES_PATH, help="path to map lines in json format")
    parser.add_argument("--method", type=int, help="method to match the map on switches")
    parser.add_argument("--mode", choices=['whole', 'last_n', 'interval'], default='whole', help="mode to select points used in methods to choose path")
    parser.add_argument("-n", type=int, default=1, help='n points that will be considered in methods')
    parser.add_argument("--start_r", type=int, default=20, help="starting distance for interval choosing method")
    parser.add_argument("--end_r", type=int, default=25, help="ending distance for interval choosing method")
    args = parser.parse_args()
    existing_files = glob(DIR + 'mode-{}_method-{}_*.txt'.format(args.mode, args.method))
    logs_path = next(walk(args.logs_path), (None, None, []))
    f = open(DIR + "mode-{}_method-{}_n-{}.txt".format(args.mode, args.method, len(existing_files)), "w")
    for gps_points_path in logs_path[2]:
        args.path = "{}/{}".format(logs_path[0], gps_points_path)
        print("Now {} log is matching".format(args.path))
        matcher = StateMatcher(**vars(args))
        matcher.match()
        #matcher.draw_full_map(matcher.result)
        tester = Tester(matcher.switch_information)
        coincidence_counter, count_of_switches, result = tester.test_switches()
        f.write("Now {} log is matching\n {} out of {} switches are correct\n{}\n".format(args.path,coincidence_counter, count_of_switches, result))
    f.close()

