import pandas as pd
import os
import argparse
from typing import List, Tuple, Dict

PATH_TO_QGIS_PROJECT = "/home/amir/Desktop/Лужская_QGIS_20082022/result_df.csv"


def get_all_df(path: str) -> pd.DataFrame:
    dir_paths = next(os.walk(path), (None, None, []))
    result_data_frame = pd.DataFrame(
        columns=["latitude", "longitude", "height", "line_id", "state"]
    )
    for df in dir_paths[2]:
        res_path = "{}/{}".format(dir_paths[0], df)
        tmp_frame = pd.read_csv(res_path)
        tmp_frame["state"] = [
            df.split("_")[-1].split(".")[0] for i in range(len(tmp_frame["line_id"]))
        ]
        result_data_frame = pd.concat([result_data_frame, tmp_frame])
    return result_data_frame


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type=str, help="path to dir with csv files")
    args = parser.parse_args()
    res_df = get_all_df(args.path)
    res_df.to_csv(PATH_TO_QGIS_PROJECT)
