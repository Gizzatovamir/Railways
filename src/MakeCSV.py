import pandas as pd
import pymap3d as pm


class MakeCSV:
    def __init__(self, file_name: str):
        self.file_name = file_name

    @staticmethod
    def get_tmp_frame(point: dict, index: int) -> pd.DataFrame:
        latitude, longitude, height = pm.ecef2geodetic(
            *point["coords"].vector, deg=True
        )
        try:
            tmp_dict = {
                "latitude": latitude,
                "longitude": longitude,
                "height": height,
                "line_id": point["poly_line_id"],
            }
        except Exception as e:
            tmp_dict = {
                "latitude": latitude,
                "longitude": longitude,
                "height": height,
                "line_id": "-"
            }
        return pd.DataFrame(
            tmp_dict,
            columns=["latitude", "longitude", "height", "line_id"],
            index=[index],
        )

    def raw_dict_list_to_data_frame(self, data):
        res = pd.DataFrame(columns=["latitude", "longitude", "height"])
        for i in range(len(data)):
            tmp_frame = self.get_tmp_frame(data[i], i)
            res = pd.concat([res, tmp_frame])
        res.to_csv(self.file_name + "_raw.csv", sep=str(","))

    def linked_dict_list_to_data_frame(self, data):
        res_linked_gps_points = pd.DataFrame(
            columns=["latitude", "longitude", "height", "line_id"]
        )
        for i in range(len(data)):
            print(data[i][0])
            tmp_linked_frame = self.get_tmp_frame(
                {"coords": data[i][1], "poly_line_id": data[i][0]["poly_line_id"]}, i
            )
            res_linked_gps_points = pd.concat([res_linked_gps_points, tmp_linked_frame])
        res_linked_gps_points.to_csv(self.file_name + "_linked.csv", sep=str(","))
