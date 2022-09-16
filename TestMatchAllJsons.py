from src.StateMatcher import StateMatcher
from src.TesterClass import Tester
from utils.constants import GPS_POINTS_PATH, POINTS_PATH, LINES_PATH
import argparse
from os import walk
from glob import glob
from main import get_arg_list
from src.GroundTruthMatcher import GroundTruthMatcher
import sys

DIR = "./results/"

if __name__ == "__main__":
    sys.setrecursionlimit(10000)
    arg_list = get_arg_list()
    logs_path = next(walk(arg_list["logs_path"]), (None, None, []))
    print(arg_list)
    for gps_points_path in logs_path[2]:
        arg_list["path"] = "{}/{}".format(logs_path[0], gps_points_path)
        print("Now {} log is matching".format(arg_list["path"]))
        matcher = GroundTruthMatcher(arg_list)
        # matcher.draw_trajectory()
        matcher.match()
        # matcher.draw_full_map(matcher.result)
