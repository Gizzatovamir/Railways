from utils.constants import GPS_POINTS_PATH, POINTS_PATH, LINES_PATH, MIN_DIST, R_MAX
from src.RailMap import RailLines
from src.GPSPoints import GPSPoints
import matplotlib.pyplot as plt
from src.PointClass import Point
import utils.utils

class Matcher:
    def __init__(self, path_to_lines=LINES_PATH, path_to_points=POINTS_PATH, gps_points_path=GPS_POINTS_PATH):
        rail_lines = RailLines(path_to_lines=path_to_lines, path_to_points=path_to_points)
        gps_points = GPSPoints(gps_points_path=gps_points_path)
        utils.lines = rail_lines.lines
        utils.points = rail_lines.points
        utils.gps_points = gps_points.points
        utils.initial_dict = {}
        utils.result = []
        utils.sub_points = []
        utils.sub_segments = []

    def find_min_dist_among_every_line(self, gps_point: dict, lines: list, min_dist=MIN_DIST) -> dict:
        points = {}
        for line in lines:
            line_points = [line["line_p1"], line["line_p2"]]
            current_dict = self.point_to_segment_distance(gps_point['coords'], line_points[0], line_points[1])

            if current_dict["dist"] < min_dist:
                #print(current_dict["dist"], " - cur_dist")

                min_dist = current_dict["dist"]
                points = {"gps_point": gps_point, "line_p1": line_points[0], "line_p2": line_points[1],
                          "line_point_id": current_dict['point_id']}

        return points

    def find_dict(self, point_id) -> Point:
        found_dict = next(item for item in self.points if item["id"] == point_id)
        return found_dict["coords"]

    @staticmethod
    def point_to_segment_projection(points: dict) -> dict:
        """ Finds point projection on a line segment.

            Args:
                points['gps_point']: point from projection is made
                points['line_p1']: start of the segment
                points['line_p2']: end of the segment
            Returns:
                Point: projection of p to line segment [a,b].
        """

        p = points['gps_point']['coords']
        b = points['line_p2']
        a = points['line_p1']

        v = b - a
        res = a + v * (v.dot(p - a) / v.dot(v))
        return res

    @staticmethod
    def point_to_segment_distance(p: Point, a: Point, b: Point) -> dict:
        ab = b - a
        ap = p - a

        if ap.dot(ab) <= 0.0:  # Point is lagging behind start of the segment, so perpendicular distance is not viable.
            return {"dist": ap.norm, "point_id": 'line_p1'}  # Use distance to start of segment instead.

        bp = p - b

        if bp.dot(ab) >= 0.0:  # Point is advanced past the end of the segment, so perpendicular distance is not viable.
            return {"dist": bp.norm, "point_id": 'line_p2'}  # Use distance to end of the segment instead.

        return {"dist": (ab.cross(ap)).norm / ab.norm, "point_id": "gps_point"}
        # Perpendicular distance of point to segment. Use distance to start of segment instead.

    def draw_full_map(self, new_points: list) -> None:
        fig = plt.figure()
        ax = fig.add_subplot(111)
        RailLines.draw_lines(self.lines, self.points, ax)
        # RailLines.draw_points(self.gps_points, ax, "green")
        # RailLines.draw_points(new_points, ax, 'blue')
        RailLines.draw_connected_points(new_points, ax)
        plt.savefig("res_map_before.png")
        plt.show()

    def find_condition(self, gps_point: Point, p1: Point, p2: Point) -> bool:
        if self.point_to_segment_distance(gps_point, p1, p2)["dist"] <= R_MAX:
            return True
        else:
            return False

    def select_lines_in_range(self, gps_point: Point) -> list:
        res_points = []
        for i in range(len(self.lines)):
            for j in range(len(self.lines[i]["points"]) - 1):
                line_points = [self.find_dict(self.lines[i]["points"][j]),
                               self.find_dict(self.lines[i]["points"][j + 1])]
                if self.find_condition(gps_point, line_points[0], line_points[1]):
                    res_points.append({"line_p1": line_points[0], "line_p2": line_points[1]})
        return res_points

    def match(self) -> None:
        res_points = []
        for gps_point in self.gps_points:
            lines = self.select_lines_in_range(gps_point['coords'])
            points = self.find_min_dist_among_every_line(gps_point, lines)
            if points != {}:
                if points["line_point_id"] != "gps_points":
                    res_point = self.point_to_segment_projection(points)
                else:
                    print(points[points['line_point_id']])
                    res_point = points[points['line_point_id']]['coords']
                res_points.append([gps_point, res_point])
        self.draw_full_map(res_points)


if __name__ == "__main__":
    matcher = Matcher()
    matcher.match()
