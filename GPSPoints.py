from utils import get_json
from constants import GPS_POINTS_PATH
from BasicMap import BasicMap
import pymap3d as pm

class GPSPoints(BasicMap):
    def __init__(self,gps_points_path):
        self.points = self.point_transform(get_json(gps_points_path))

    def __len__(self):
        return len(self.points)

    @staticmethod
    def point_transform(dict_point):
        res = []
        for i in range(len(dict_point)):
            #x, y, z = pm.geodetic2ecef(dict_point["{}".format(i)]["latitude"], dict_point["{}".format(i)]["longitude"], 0)
            x, y = dict_point["{}".format(i)]["latitude"], dict_point["{}".format(i)]["longitude"]
            res.append({"id": i,
                        "coords": [x, y]})
        return res