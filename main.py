from stateMachineMatcher import StateMachineMatcher
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", help="path to gps points in json format")
    parser.add_argument("--method", choices=['1', '2', '3'], help="method to match the map on switches")
    args = parser.parse_args()
    print(type(args.method))
    matcher = StateMachineMatcher(int(args.method), gps_points_path=args.path)
    matcher.match()