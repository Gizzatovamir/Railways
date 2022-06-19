import pymap3d as pm
from PointClass import Point


class BasicMap:
    @staticmethod
    def line_transform(lines) -> list:
        res = []
        for i in range(len(lines)):
            res.append({"line_id": lines["{}".format(i)]["line_id"],
                        "points": lines["{}".format(i)]["point_ids"]})
        return res

    @staticmethod
    def point_transform(dict_point: dict) -> list:
        res = []
        for i in range(len(dict_point)):
            point = Point(*pm.geodetic2ecef(dict_point["{}".format(i)]["latitude"],
                                            dict_point["{}".format(i)]["longitude"],
                                            dict_point["{}".format(i)]["height"])
                          )
            res.append({"id": dict_point['{}'.format(i)]["point_id"],
                        "coords": point})
        return res

    @staticmethod
    def draw_points(points: list, ax, color: str) -> None:
        for point in points:
            ax.plot(point['coords'].x, point['coords'].y, 'ro', color=color)
            #ax.plot(point["coords"].x, point["coords"].y, point["coords"].z, 'ro', color=color)

    @staticmethod
    def draw_connected_points(new_points: list, ax) -> None:
        for gps_point, new_gps_point in new_points:
            ax.plot([gps_point['coords'].x, new_gps_point.x],
                    [gps_point['coords'].y, new_gps_point.y],
                    linestyle='--', color='black'
                    )
            ax.plot(new_gps_point.x, new_gps_point.y, 'ro', color='b')
            ax.plot(gps_point['coords'].x, gps_point['coords'].y, 'ro', color='r')

    @staticmethod
    def draw_lines(lines: dict, points: list, ax) -> None:
        for i in range(len(lines)):
            x = []
            y = []
            z = []
            for point_id in lines[i]["points"]:
                for true_point in points:
                    if true_point['id'] == point_id:
                        x.append(true_point["coords"].x)
                        y.append(true_point["coords"].y)
                        #z.append(true_point["coords"].z)
                #    ax.plot(x, y, z)
                ax.plot(x, y)
