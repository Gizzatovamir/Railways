import pymap3d as pm

class BasicMap:
    @staticmethod
    def line_transform(lines):
        res = []
        for i in range(len(lines)):
            res.append({"line_id": lines["{}".format(i)]["line_id"], "points": lines["{}".format(i)]["point_ids"]})
        return res

    @staticmethod
    def point_transform(dict_point):
        res = []
        for i in range(len(dict_point)):
            #x, y, z = pm.geodetic2ecef(dict_point["{}".format(i)]["latitude"], dict_point["{}".format(i)]["longitude"],
            #                           0)
            x, y = dict_point["{}".format(i)]["latitude"], dict_point["{}".format(i)]["longitude"]
            res.append({"id": dict_point['{}'.format(i)]["point_id"],
                        "coords": [x, y]})#,
                                   #dict_point["{}".format(i)]["height"]]})
        return res

    @staticmethod
    def draw_points(points, ax,color):
        for point in points:
            #print(point["coords"][0],point["coords"][1])
            ax.plot(point["coords"][0],point["coords"][1],'ro', color=color)

    @staticmethod
    def draw_lines(lines, points, ax):
        for i in range(len(lines)):
            latitude = []
            longitude = []
            for point_id in lines[i]["points"]:
                for true_point in points:
                    if true_point['id'] == point_id:
                        latitude.append(true_point["coords"][0])
                        longitude.append(true_point["coords"][1])
                        ax.plot(latitude, longitude)