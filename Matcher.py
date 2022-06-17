from constants import GPS_POINTS_PATH, POINTS_PATH, LINES_PATH
from RailMap import RailLines
from GPSPoints import GPSPoints
from numpy.linalg import norm
import numpy as np
import matplotlib.pyplot as plt
from skspatial.objects import Line
from PointClass import Point
"""перевести в геоцентрические координаты (pymap3d.ecef)"""


class Matcher:
    def __init__(self, path_to_lines=LINES_PATH, path_to_points=POINTS_PATH, gps_points_path=GPS_POINTS_PATH):
        rail_lines = RailLines(path_to_lines=path_to_lines, path_to_points=path_to_points)
        gps_points = GPSPoints(gps_points_path=gps_points_path)
        self.lines = rail_lines.lines
        self.points = rail_lines.points
        self.gps_points = gps_points.points

    def find_min_dist_among_every_line(self, gps_point):
        points = {}
        for i in range(len(self.lines)):
            min_dist = 1000
            for j in range(len(self.lines[i]["points"]) - 1):
                line_points = [self.find_dict(self.lines[i]["points"][j]), self.find_dict(self.lines[i]["points"][j+1])]
                cur_dist = self.point_to_segment_distance(gps_point['coords'], line_points[0], line_points[1])
                if cur_dist < min_dist:
                    min_dist = cur_dist
                    points = {"gps_point" : gps_point, "line_p1" : line_points[0], "line_p2" : line_points[1]}

        return points

    def find_dict(self, point_id):
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
        return {"coords" : res}

    @staticmethod
    def point_to_segment_distance(p: Point, a: Point, b: Point) -> float:
        ab = b - a
        ap = p - a

        if ap.dot(ab) <= 0.0:  # Point is lagging behind start of the segment, so perpendicular distance is not viable.
            return ap.norm  # Use distance to start of segment instead.

        bp = p - b

        if bp.dot(ab) >= 0.0:  # Point is advanced past the end of the segment, so perpendicular distance is not viable.
            return bp.norm  # Use distance to end of the segment instead.

        return (ab.cross(ap)).norm / ab.norm  # Perpendicular distance of point to segment.

    def draw_full_map(self, new_points: list) -> None:
        fig = plt.figure()
        #ax = fig.add_subplot(111, projection='3d')
        ax = fig.add_subplot(111)
        RailLines.draw_lines(self.lines, self.points, ax)
        RailLines.draw_points(self.gps_points, ax, "red")
        RailLines.draw_points(new_points, ax, 'blue')
        plt.savefig("res_map_before.png")
        plt.show()

    def match(self) -> None:
        res_points = []
        #print(self.gps_points)
        for gps_point in self.gps_points:
            points = self.find_min_dist_among_every_line(gps_point)
            res_point = self.point_to_segment_projection(points)
            #print(res_point, " - res_point")
            if self.point_to_segment_projection(points) != {}:
                res_points.append(res_point)
        self.draw_full_map(res_points)



if __name__ == "__main__":
    matcher = Matcher()
    matcher.match()
