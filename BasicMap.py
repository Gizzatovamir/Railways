import numpy as np
import pymap3d as pm
from PointClass import Point
from utils import find_l0_h0


class BasicMap:
    @staticmethod
    def line_transform(lines) -> list:
        res = []
        for i in range(len(lines)):
            res.append({"line_id": lines["{}".format(i)]["line_id"],
                        "points": lines["{}".format(i)]["point_ids"]})
        return res

    @staticmethod
    def find_dict(line_dict, line_id) -> list:
        found_list = next(item for item in line_dict if item["line_id"] == line_id)
        return found_list["points"]

    def point_transform(self, dict_point: dict, lines: list) -> list:
        res = []
        under_line_ids = self.find_dict(lines, 967)
        for i in range(len(dict_point)):
            x, y, z = pm.geodetic2ecef(dict_point["{}".format(i)]["latitude"],
                                       dict_point["{}".format(i)]["longitude"],
                                       dict_point["{}".format(i)]["height"])
            if dict_point["{}".format(i)]["point_id"] in under_line_ids:
                z = -10
            else:
                z = 0
            point = Point(x, y, z)
            res.append({"id": dict_point['{}'.format(i)]["point_id"],
                        "coords": point})
        return res

    @staticmethod
    def draw_points(points: list, ax, color: str) -> None:
        for point in points:
            lat_0, lon_0, h_0 = find_l0_h0()
            x, y, z = pm.ecef2ned(*point["coords"].vector, lat_0, lon_0, h_0)
            ax.plot(x, y, 'ro', color=color)
            #ax.plot(point["coords"].x, point["coords"].y, point["coords"].z, 'ro', color=color)

    @staticmethod
    def draw_connected_points(points: list, new_points: list, ax) -> None:
        for gps_point, new_gps_point in new_points:
            lat_0, lon_0, h_0 = find_l0_h0()
            gps_x, gps_y, gps_z = pm.ecef2ned(*gps_point['coords'].vector, lat_0, lon_0, h_0)
            new_x, new_y, new_z = pm.ecef2ned(*new_gps_point.vector, lat_0, lon_0, h_0)
            ax.plot([gps_x, new_x],
                    [gps_y, new_y],
                    linestyle='--', color='black'
                    )
            ax.plot(new_x, new_y, 'ro', color='b')
            ax.plot(gps_x, gps_y, 'ro', color='r')

    @staticmethod
    def draw_lines(lines: dict, points: list, ax) -> None:
        for i in range(len(lines)):
            x = []
            y = []
            z = []
            for point_id in lines[i]["points"]:
                for true_point in points:
                    if true_point['id'] == point_id:
                        lat_0, lon_0, h_0 = find_l0_h0()
                        new_x, new_y, new_z = pm.ecef2ned(*true_point["coords"].vector, lat_0, lon_0, h_0)
                        x.append(new_x)
                        y.append(new_y)
                        #z.append(true_point["coords"].z)
                        #ax.text(true_point["coords"].x, true_point["coords"].y, true_point["coords"].z)
                ax.plot(x, y)
                #ax.plot(x, y)
