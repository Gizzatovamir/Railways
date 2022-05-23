import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import json
from main import get_json

POINTS_PATH = "jsons/map_points.json"
LINES_PATH = "jsons/map_lines.json"

def line_transform(lines):
    res = []
    for i in range(len(lines)):
        res.append({"line_id" : lines["{}".format(i)]["line_id"], "points" : lines["{}".format(i)]["point_ids"]})
    return res

def point_transform(dict_point):
    #res = {}
    res = []
    for i in range(len(dict_point)):
        #res[dict_point["{}".format(i)]["point_id"]] = [dict_point["{}".format(i)]["latitude"],dict_point["{}".format(i)]["longitude"],dict_point["{}".format(i)]["height"]]
        res.append({"id":dict_point['{}'.format(i)]["point_id"], "coords":[dict_point["{}".format(i)]["latitude"],dict_point["{}".format(i)]["longitude"],dict_point["{}".format(i)]["height"]]})
    return res


def draw_full_map(true_points,lines):

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    for i in range(len(lines)):
        latitude = []
        longitude = []
        height = []
        for point_id in lines[i]["points"]:
            for true_point in true_points:
                if true_point['id'] == point_id:
                    print(true_point)
                    latitude.append(true_point["coords"][0])
                    longitude.append(true_point["coords"][1])
                    height.append(true_point["coords"][2])
                    ax.plot(latitude, longitude, height)
    plt.show()

if __name__ == "__main__":
    points = get_json(POINTS_PATH)
    lines = get_json(LINES_PATH)
    reformed_points = point_transform(points)
    reformed_lines = line_transform(lines)
    print(reformed_lines)
    print(reformed_points)
    draw_full_map(reformed_points,reformed_lines)


