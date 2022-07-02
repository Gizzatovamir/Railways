from constants import GPS_POINTS_PATH, POINTS_PATH, LINES_PATH, MIN_DIST, R_MAX
from RailMap import RailLines
from GPSPoints import GPSPoints
from numpy.linalg import norm
import numpy as np
import matplotlib.pyplot as plt
from skspatial.objects import Line
from PointClass import Point
from Matcher import Matcher

R_CROSS = 30


class StateMachineMatcher(Matcher):
    def find_dict(self, point_id) -> dict:
        found_dict = next(item for item in self.points if item["id"] == point_id)
        return found_dict

    @staticmethod
    def point_to_segment_distance(p: Point, line: list) -> dict:
        a = line[0]["coords"]
        b = line[1]["coords"]
        ab = b - a
        ap = p - a

        if ap.dot(ab) <= 0.0:  # Point is lagging behind start of the segment, so perpendicular distance is not viable.
            return {"dist": ap.norm, "point_id": 'line_p1'}  # Use distance to start of segment instead.

        bp = p - b

        if bp.dot(ab) >= 0.0:  # Point is advanced past the end of the segment, so perpendicular distance is not viable.
            return {"dist": bp.norm, "point_id": 'line_p2'}  # Use distance to end of the segment instead.

        return {"dist": (ab.cross(ap)).norm / ab.norm, "point_id": "gps_point"}
        # Perpendicular distance of point to segment. Use distance to start of segment instead.

    @staticmethod
    def point_to_segment_projection(points: dict) -> Point:
        """ Finds point projection on a line segment.

            Args:
                points['gps_point']: point from projection is made
                points['line_p1']: start of the segment
                points['line_p2']: end of the segment
            Returns:
                Point: projection of p to line segment [a,b].
        """

        p = points['gps_point']['coords']
        b = points['cur_line'][0]["coords"]
        a = points['cur_line'][1]["coords"]

        v = b - a
        res = a + v * (v.dot(p - a) / v.dot(v))
        return res

    def unknown_point(self, point, last_line) -> dict:
        return {"gps_point": point, "cur_line": None, "last_line": last_line}

    def find_initial_state(self, initial_point: dict, last_line=None, min_dist=MIN_DIST) -> dict:
        points = {}
        for i in range(len(self.lines)):
            for j in range(len(self.lines[i]["points"]) - 1):
                line_points = [self.find_dict(self.lines[i]["points"][j]),
                               self.find_dict(self.lines[i]["points"][j + 1])]
                current_dict = self.point_to_segment_distance(initial_point["coords"], line_points)
                if current_dict["dist"] < min_dist:
                    min_dist = current_dict["dist"]
                    points = {"gps_point": initial_point, "cur_line": line_points, "last_line": last_line}
        points['gps_point'] = self.point_to_segment_projection(points)
        return points

    def initialize(self, gps_point, last_line=None) -> dict:
        state = self.find_initial_state(gps_point, last_line=last_line)
        gps_point['cur_line'] = state['cur_line']
        return state

    def find_all_cross(self) -> None:
        for i in range(len(self.points)):
            count = 0
            for j in range(len(self.lines)):
                if self.points[i]["id"] in self.lines[j]['points']:
                    count += 1
            if count > 1:
                self.points[i]["cross"] = True
            else:
                self.points[i]["cross"] = False

    @staticmethod
    def find_cross_points(points) -> list:
        found_dict = list(filter(lambda x: x["cross"] is True, points ))
        return found_dict

    def find_min_dist(self, point_dict: dict) -> Point:
        try:
            l1 = self.point_to_segment_distance(point_dict["coords"], point_dict["cur_line"])["dist"]
        except:
            l1 = 1000
        try:
            l2 = self.point_to_segment_distance(point_dict["coords"], point_dict["last_line"])["dist"]
        except:
            l2 = 1000
        if l1 < l2:
            return self.point_to_segment_projection({"gps_point": point_dict, "cur_line": point_dict["cur_line"]})
        else:
            print(point_dict)
            return self.point_to_segment_projection(
                {"gps_point": point_dict, "cur_line": point_dict["last_line"]})

    def lower_all_ortho(self) -> list:
        res = []
        for i in range(len(self.gps_points)):
            res.append([self.gps_points[i], self.find_min_dist(self.gps_points[i])])
        return res

    def draw_full_map(self, new_points: list) -> None:
        fig = plt.figure()
        ax = fig.add_subplot(111)
        RailLines.draw_lines(self.lines, self.points, ax)
        # RailLines.draw_points(self.gps_points, ax, "green")
        # RailLines.draw_points(new_points, ax, 'blue')
        RailLines.draw_connected_points(self.points, new_points, ax)
        plt.savefig("res_map_before.png")
        plt.show()

    def match(self) -> None:
        self.find_all_cross()
        initial_dict = self.initialize(self.gps_points[0])
        result = [[self.gps_points[0],initial_dict['gps_point']]]
        for i in range(1, len(self.gps_points)):
            #print(i)
            p1, p2 = initial_dict['cur_line']

            if (p1["coords"] - self.gps_points[i]["coords"]).norm > R_CROSS and (p2["coords"] - self.gps_points[i]["coords"]).norm > R_CROSS:
                self.gps_points[i]['cur_line'] = initial_dict['cur_line']
                continue
            else:
                if p1["cross"] and (p1["coords"] - self.gps_points[i]["coords"]).norm <= R_CROSS:
                    self.gps_points[i]['last_line'] = initial_dict['cur_line']
                    self.gps_points[i]['cur_line'] = None
                if p1["cross"] and (p2["coords"] - self.gps_points[i]["coords"]).norm <= R_CROSS:
                    self.gps_points[i]['last_line'] = initial_dict['cur_line']
                    self.gps_points[i]['cur_line'] = None
                initial_dict = self.initialize(self.gps_points[i], last_line=None)
                for j in range(1, i):
                    if self.gps_points[j]['cur_line'] is None:
                        self.gps_points[j]['cur_line'] = initial_dict['cur_line']
        result.extend(self.lower_all_ortho())
        self.draw_full_map(result)





if __name__ == "__main__":
    matcher = StateMachineMatcher()
    matcher.match()