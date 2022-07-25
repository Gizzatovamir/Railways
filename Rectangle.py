from RailMap import RailLines
from constants import POINTS_PATH, LINES_PATH, GPS_POINTS_PATH
from utils import get_json

if __name__ == "__main__":
    old_points = get_json(POINTS_PATH)
    res = []
    for i in range(len(old_points)):
        res.append({"id": old_points['{}'.format(i)]["point_id"],
                    "latitude": old_points['{}'.format(i)]["latitude"],"longitude": old_points['{}'.format(i)]["longitude"]})
    new_res = sorted(res, key=lambda point: (point['latitude'], point['longitude']))
    print(new_res[0])
    print(new_res[-1])

