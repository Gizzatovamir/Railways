import pandas as pd
import csv
import argparse
import os
from typing import Dict, Tuple, List
from src.PointClass import Point
import utils.utils as utils

MIN_ACCEPTABLE_ERROR = 0.15
STEP_IN_LIST = 2
MIN_LIMIT_VALUE = 2.5
INCORRECT_LOGS_DIR_PATH = "incorrect/"


class Checker:
    def __init__(self, **kwargs):
        self.config_for_compare = {
            "diff": {
                "get_points_func": utils.get_points_from_different_samples,
                "comparator": utils.point_comparator,
            },
            "same": {
                "get_points_func": utils.get_points_from_same_sample,
                "comparator": utils.segment_comparator,
            },
        }
        self.compare = kwargs["compare"]
        self.min_dist = kwargs["min_dist"]

    @staticmethod
    def get_data_from_path(path: str) -> List[Dict]:
        with open(path) as file_1:
            result_list_of_dicts = [
                {k: v for k, v in row.items()}
                for row in csv.DictReader(file_1, skipinitialspace=True)
            ]
        return result_list_of_dicts

    def check_logs(
        self, path_to_log_1: str, path_to_log_2: str, limit_value: float, **kwargs
    ) -> Tuple[bool, float, List[int]]:
        result_list = []
        logs = sorted(
            [self.get_data_from_path(path) for path in [path_to_log_1, path_to_log_2]],
            key=lambda x: len(x),
        )
        for index in range(len(logs[0])):
            points = kwargs["get_points_func"](index, *logs)
            if points:
                result_list.append(kwargs["comparator"](*points, limit_value))
        return (
            all([condition for condition, dist, id in result_list]),
            *max(result_list, key=lambda x: x[1])[1:3],
        )

    def check(self, log_1_path, log_2_path) -> Tuple[bool, float, List[int]]:
        return self.check_logs(
            log_1_path,
            log_2_path,
            self.min_dist,
            **self.config_for_compare[self.compare]
        )


def get_args_for_check() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type=str, help="path to dir with dir with csv files")
    parser.add_argument(
        "--compare",
        type=str,
        default="diff",
        choices=["diff", "same"],
        help="this is an argument to compare 2 csvs. "
        "Options:[diff - compare points from "
        "different csvs, same - get points "
        "increment from 1 scv and then compare "
        "the increments]",
    )
    parser.add_argument(
        "--min_dist",
        type=float,
        default=MIN_LIMIT_VALUE,
        help="minimal distance between 2 points that is considered as inaccurate ",
    )
    parser.add_argument(
        "--logs",
        nargs=2,
        default=["ground_truth", "raw"],
        type=str,
        help="argument for logs choosing from 3 csvs options",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = get_args_for_check()
    checker = Checker(**vars(args))
    logs_path = next(os.walk(args.path), (None, None, []))
    if not os.path.isdir(INCORRECT_LOGS_DIR_PATH):
        os.mkdir(INCORRECT_LOGS_DIR_PATH)
    with open(INCORRECT_LOGS_DIR_PATH + "logs.txt", "w+") as f:
        for logs_dir_path in logs_path[1]:
            print(logs_dir_path)
            # paths = utils.get_all_file_paths(logs_path[0] + logs_dir_path + "/")
            logs = utils.get_all_file_paths(
                "{}{}/".format(logs_path[0], logs_dir_path), args.logs
            )
            print(logs)
            condition, max_dist, point_id = checker.check(*logs)
            if not condition:
                f.write(
                    "{}{}/ : max distance - {}, point id - {}\n".format(
                        logs_path[0], logs_dir_path, max_dist, point_id
                    )
                )
    print(len(logs_path[1]))
