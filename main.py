from stateMachineMatcher import StateMachineMatcher
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", help="path to gps points in json format")
    args = parser.parse_args()
    matcher = StateMachineMatcher(gps_points_path=args.path)
    matcher.match()