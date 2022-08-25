from src.StateMatcher import StateMatcher
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", help="path to gps points in json format")
    parser.add_argument("--method", help="method to match the map on switches")
    parser.add_argument("--start_r", default=20, help="starting distance for interval choosing method")
    parser.add_argument("--end_r", default=25, help="ending distance for interval choosing method")
    args = parser.parse_args()
    matcher = StateMatcher(int(args.method), int(args.start_r), int(args.end_r), gps_points_path=args.path)
    matcher.match()
    matcher.draw_full_map(matcher.result)
    #checker = Checker(matcher.switches, gps_points_path=args.path)
    #checker.matcher.draw_full_map(checker.matcher.result)
    #checker.check_for_success_switch_choosing()

    #matcher.draw_full_map(matcher.result)