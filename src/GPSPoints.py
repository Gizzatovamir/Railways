from utils.utils import get_json
from src.BasicMap import BasicMap
import pymap3d as pm
from src.PointClass import Point


class GPSPoints(BasicMap):
    def __init__(self, gps_points_path):
        self.points = self.point_transform(get_json(gps_points_path))

    def __len__(self):
        return len(self.points)

    @staticmethod
    def point_transform(dict_point):
        res = []
        for i in range(len(dict_point)):
            x, y, z = pm.geodetic2ecef(
                dict_point["{}".format(i)]["latitude"],
                dict_point["{}".format(i)]["longitude"],
                0,
            )
            point = Point(x, y, z)
            res.append({"id": i, "coords": point, "is_on_switch": False})
        return res
