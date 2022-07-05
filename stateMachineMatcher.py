from constants import GPS_POINTS_PATH, POINTS_PATH, LINES_PATH, MIN_DIST, R_MAX
from RailMap import RailLines
from GPSPoints import GPSPoints
from numpy.linalg import norm
import numpy as np
import matplotlib.pyplot as plt
from skspatial.objects import Line
from PointClass import Point
from Matcher import Matcher
from utils import find_min_dict_x, find_min_dict_y, find_max_dict_x, find_max_by_y, find_sublist, find_index
from createTree import Node

R_CROSS = 30


class StateMachineMatcher(Matcher):
    def find_dict(self, point_id) -> dict:
        found_dict = next(item for item in self.points if item["id"] == point_id)
        return found_dict

    @staticmethod
    def state_point_to_segment_distance(p: Point, line: list) -> dict:
        a = line[0]["coords"]
        b = line[1]["coords"]
        ab = b - a
        ap = p - a

        if ap.dot(ab) <= 0.0:  # Point is lagging behind start of the segment, so perpendicular distance is not viable.
            print("line1")
            return {"dist": ap.norm, "flag": False, "line_point": True}  # Use distance to start of segment instead.


        bp = p - b

        if bp.dot(ab) >= 0.0:  # Point is advanced past the end of the segment, so perpendicular distance is not viable.
            print("line2")
            return {"dist": bp.norm, "flag": False, "line_point": False}  # Use distance to end of the segment instead.

        return {"dist": (ab.cross(ap)).norm / ab.norm, "flag": True}
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
                current_dict = self.state_point_to_segment_distance(initial_point["coords"], line_points)
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
        found_dict = list(filter(lambda x: x["cross"] is True, points))
        return found_dict

    def find_min_dist(self, point_dict: dict) -> Point:
        try:
            l1 = self.state_point_to_segment_distance(point_dict["coords"], point_dict["cur_line"])["dist"]
        except:
            l1 = 1000
        try:
            l2 = self.state_point_to_segment_distance(point_dict["coords"], point_dict["last_line"])["dist"]
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

    def find_new_line_segment(self, point: dict, condition: bool) -> dict:
        #print(self.lines)
        for i in range(len(self.lines)):
            if point['id'] in self.lines[i]["points"]:
                return self.find_dict(find_sublist(point['id'], self.lines[i]["points"], condition))

    def find_segments_from_point(self, point: dict, condition: bool) -> list:
        result = []
        for i in range(len(self.lines)):
            if point['id'] in self.lines[i]["points"] and point['id'] != self.lines[i]["points"][-1]:
                index = find_index(point['id'], self.lines[i]["points"])
                if condition:
                    segment = [self.find_dict(x) for x in self.lines[i]["points"][:index+2]]
                else:
                    segment = [self.find_dict(x) for x in self.lines[i]["points"][index-2:]]
                result.append(segment)
        return result

    def draw_tree(self, root: list) -> None:
        fig = plt.figure()
        ax = fig.add_subplot(111)
        for tree in root:
            tree.draw_tree(ax)
        plt.show()

    def draw_full_map(self, new_points: list) -> None:
        fig = plt.figure()
        ax = fig.add_subplot(111)
        RailLines.draw_lines(self.lines, self.points, ax)
        RailLines.draw_points(self.gps_points, ax, "green")
        # RailLines.draw_points(new_points, ax, 'blue')
        RailLines.draw_connected_points(self.points, new_points, ax)
        #plt.savefig("res_map_before.png")
        plt.show()

    def match(self) -> None:
        self.find_all_cross()
        initial_dict = self.initialize(self.gps_points[0])
        result = [[self.gps_points[0], initial_dict['gps_point']]]
        for i in range(1, len(self.gps_points)):
            # print(i)
            p1, p2 = initial_dict['cur_line']
            ortho_point_dist = self.state_point_to_segment_distance(self.gps_points[i]['coords'], initial_dict["cur_line"])
            if ortho_point_dist['flag']:
                result.append([self.gps_points[i], self.point_to_segment_projection(
                    {"gps_point": self.gps_points[i], "cur_line": initial_dict["cur_line"]})]
                              )
            else:
                if not ortho_point_dist['line_point'] and p1["cross"] is False and p2["cross"] is False:
                    new_line_segment = self.find_new_line_segment(find_max_dict_x(initial_dict['cur_line']), True)
                    next_line_dist = self.state_point_to_segment_distance(self.gps_points[i]['coords'], [p2, new_line_segment])
                    if next_line_dist['dist'] > ortho_point_dist['dist']:
                        result.append([self.gps_points[i], p2["coords"]])
                        initial_dict = self.initialize(self.gps_points[i+1])
                    else:
                        initial_dict = self.initialize(self.gps_points[i])
                        result.append([self.gps_points[i], initial_dict['gps_point']])
                if ortho_point_dist['line_point'] and p1["cross"] is False and p2["cross"] is False:
                    new_line_segment = self.find_new_line_segment(find_min_dict_x(initial_dict['cur_line']), True)
                    next_line_dist = self.state_point_to_segment_distance(self.gps_points[i]['coords'], [new_line_segment, p1])
                    if next_line_dist['dist'] > ortho_point_dist['dist']:
                        result.append([self.gps_points[i], p1["coords"]])
                        initial_dict = self.initialize(self.gps_points[i+1])
                    else:
                        initial_dict = self.initialize(self.gps_points[i])
                        result.append([self.gps_points[i], initial_dict['gps_point']])
                if not ortho_point_dist['line_point'] and p1["cross"] is False and p2['cross'] is True:
                    segments = self.find_segments_from_point(p2, True)
                    dist1 = 0
                    dist2 = 0
                    points = []
                    while (self.gps_points[i]["coords"] - p2['coords']).norm < R_MAX:
                        try:
                            dist1 += self.point_to_segment_distance(self.gps_points[i]['coords'], p2['coords'],
                                                                    segments[0][1]['coords'])["dist"]
                        except:
                            dist1 = 10000
                        try:
                            dist2 += self.point_to_segment_distance(self.gps_points[i]['coords'], p2['coords'], segments[1][1]['coords'])["dist"]
                        except:
                            dist2 = 10000
                        points.append(self.gps_points[i])
                        i += 1
                    if dist1 > dist2:
                        [result.append([x, self.point_to_segment_projection(
                            {"gps_point": x, "cur_line": [p2, segments[1][1]]})]) for x in points]
                    else:
                        [result.append([x, self.point_to_segment_projection(
                            {"gps_point": x, "cur_line": [p2, segments[0][1]]})]) for x in points]
                    if (self.gps_points[i]["coords"] - p2['coords']).norm > R_MAX:
                        initial_dict = self.initialize(self.gps_points[i])
                        result.append([self.gps_points[i], initial_dict['gps_point']])
                if ortho_point_dist['line_point'] and p1["cross"] is True and p2['cross'] is False:
                    segments = self.find_segments_from_point(p1, False)
                    dist1 = 0
                    dist2 = 0
                    points = []
                    while (self.gps_points[i]["coords"] - p1['coords']).norm < R_MAX:
                        try:
                            dist1 += self.point_to_segment_distance(self.gps_points[i]['coords'], p1['coords'], segments[0][1]['coords'])["dist"]
                        except:
                            dist1 = 10000
                        try:
                            dist2 += self.point_to_segment_distance(self.gps_points[i]['coords'], p1['coords'], segments[1][1]['coords'])["dist"]
                        except:
                            dist2 = 10000
                        points.append(self.gps_points[i])
                        i += 1
                    if dist1 > dist2:
                        [result.append([x, self.point_to_segment_projection(
                            {"gps_point": x, "cur_line": [p1, segments[1][1]]})]) for x in points]
                    else:
                        [result.append([x, self.point_to_segment_projection(
                            {"gps_point": x, "cur_line": [p1, segments[0][1]]})]) for x in points]
                    if (self.gps_points[i]["coords"] - p1['coords']).norm > R_MAX:
                        initial_dict = self.initialize(self.gps_points[i])
                        result.append([self.gps_points[i], initial_dict['gps_point']])
                if p1["cross"] is True and p2['cross'] is True:
                    new_line_segment = self.find_new_line_segment(find_max_dict_x(initial_dict['cur_line']), False)
                    next_line_dist = self.state_point_to_segment_distance(self.gps_points[i]['coords'],
                                                                          [new_line_segment,p1])
                    if next_line_dist['dist'] > ortho_point_dist['dist']:
                        result.append([self.gps_points[i], p1["coords"]])
                        initial_dict = self.initialize(self.gps_points[i + 1])
                    else:
                        initial_dict = self.initialize(self.gps_points[i])
                        result.append([self.gps_points[i], initial_dict['gps_point']])
        self.draw_full_map(result)


if __name__ == "__main__":
    matcher = StateMachineMatcher()
    matcher.match()
