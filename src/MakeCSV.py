import pandas as pd
import utils.utils as utils
from typing import List, Dict, Tuple
import os


class MakeCSV:
    def __init__(self, dir_name: str):
        self.dir_name = dir_name
        if not os.path.isdir(dir_name):
            os.mkdir(dir_name)

    @staticmethod
    def get_tmp_frame(point: Dict, index: int) -> pd.DataFrame:
        latitude, longitude, height = utils.transform_ecef_to_geodetic(point)
        try:
            tmp_dict = {
                "latitude": latitude,
                "longitude": longitude,
                "height": height,
                "line_id": point["poly_line_id"],
            }
        except KeyError:
            tmp_dict = {
                "latitude": latitude,
                "longitude": longitude,
                "height": height,
                "line_id": "-",
            }
        return pd.DataFrame(
            tmp_dict,
            columns=["latitude", "longitude", "height", "line_id"],
            index=[index],
        )

    def raw_dict_list_to_data_frame(self, data: List[Dict]) -> None:
        res = pd.DataFrame(columns=["latitude", "longitude", "height"])
        for i in range(len(data)):
            tmp_frame = self.get_tmp_frame(data[i], i)
            res = pd.concat([res, tmp_frame])
        res.to_csv("{}result_df_raw.csv".format(self.dir_name), sep=str(","))

    def matched_dict_list_to_data_frame(
        self, data: List[Dict], file_path="matched"
    ) -> None:
        res_linked_gps_points = pd.DataFrame(
            columns=["latitude", "longitude", "height", "line_id"]
        )
        for i in range(len(data)):
            # print(data[i][0])
            tmp_linked_frame = self.get_tmp_frame(
                {"coords": data[i][1], "poly_line_id": data[i][0]["poly_line"].id}, i
            )
            res_linked_gps_points = pd.concat([res_linked_gps_points, tmp_linked_frame])
        res_linked_gps_points.to_csv(
            "{}result_df_{}.csv".format(self.dir_name, file_path), sep=str(",")
        )
