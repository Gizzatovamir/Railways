from StateMatcher import StateMatcher
from checkerClass import Checker
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", help="path to gps points in json format")
    parser.add_argument("--method", help="method to match the map on switches")
    args = parser.parse_args()
    matcher = StateMatcher(int(args.method), gps_points_path=args.path)
    matcher.match()
    matcher.draw_full_map(matcher.result)
    #checker = Checker(matcher.switches, gps_points_path=args.path)
    #checker.matcher.draw_full_map(checker.matcher.result)
    #checker.check_for_success_switch_choosing()

    #matcher.draw_full_map(matcher.result)