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

R_CROSS = 25


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
            return {"dist": ap.norm, "flag": False, "line_point": True}  # Use distance to start of segment instead.

        bp = p - b

        if bp.dot(ab) >= 0.0:  # Point is advanced past the end of the segment, so perpendicular distance is not viable.
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
            if count > 2:
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
            return self.point_to_segment_projection(
                {"gps_point": point_dict, "cur_line": point_dict["last_line"]})

    def lower_all_ortho(self, path: list, points: list) -> list:
        res = []
        for segment, segment_points in zip(path, points):
            [res.append([segment_point,
                         self.point_to_segment_projection({'gps_point': segment_point, 'cur_line': segment})])
             for segment_point in segment_points]
        return res

    def find_new_line_segment(self, point: dict, condition: bool) -> dict:
        for i in range(len(self.lines)):
            if point['id'] in self.lines[i]["points"]:
                return self.find_dict(find_sublist(point['id'], self.lines[i]["points"], condition))

    def find_segments_from_point(self, point: dict) -> list:
        result = []
        for i in range(len(self.lines)):
            if point['id'] == self.lines[i]["points"][0]:
                result.append([self.find_dict(x) for x in self.lines[i]["points"]])
        return result

    def find_segments_from_point_left(self, point: dict) -> list:
        result = []
        for i in range(len(self.lines)):
            if point['id'] == self.lines[i]["points"][-1]:
                result.append([self.find_dict(x) for x in self.lines[i]["points"][::-1]])
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
        ax.set_aspect("equal")
        RailLines.draw_lines(self.lines, self.points, ax)
        RailLines.draw_points(self.gps_points, ax, "green")
        # RailLines.draw_points(new_points, ax, 'blue')
        RailLines.draw_connected_points(self.points, new_points, ax)
        # plt.savefig("res_map_before.png")
        plt.grid()
        plt.show()

    def add_point_to_result(self, i: int, line_point: dict, ortho_point_dist: dict, condotion: bool) -> list:
        result = []
        new_line_segment = self.find_new_line_segment(find_max_dict_x(self.initial_dict['cur_line']), condotion)
        if not condotion:
            next_line_dist = self.state_point_to_segment_distance(
                self.gps_points[i]['coords'], [line_point, new_line_segment])
        else:
            next_line_dist = self.state_point_to_segment_distance(
                self.gps_points[i]['coords'], [new_line_segment, line_point])
        if next_line_dist['dist'] > ortho_point_dist['dist']:
            result.append([self.gps_points[i], line_point["coords"]])
            self.initial_dict = self.initialize(self.gps_points[i])
        else:
            self.initial_dict = self.initialize(self.gps_points[i])
            result.append([self.gps_points[i], self.initial_dict['gps_point']])
        return [result, 1]

    def check_for_jump(self, result: list) -> list:
        result = list(set(result[0][:]['id']))
        # for i in range(len(result)):
        return result

    def get_result(self, segment: dict, line_point: dict, points: list) -> list:
        return [[x, self.point_to_segment_projection(
            {"gps_point": x, "cur_line": [line_point, segment]})] for x in points]

    def dist_to_switch_segment(self, gps_point: dict, line_point: dict, segments: list) -> float:
        try:
            return self.point_to_segment_distance(gps_point["coords"], line_point['coords'], segments[0][1])["dist"]
        except:
            return 10000

    def find_path_on_switch(self, i: int, line_point: dict, condition: bool) -> int:
        points = []
        path = []
        dist1 = 0
        dist2 = 0

        if condition:
            segments = self.find_segments_from_point(line_point)
        else:
            segments = self.find_segments_from_point_left(line_point)
        print(segments)
        if len(segments) == 1:
            self.initial_dict = self.initialize(self.gps_points[i])
            self.sub_segments = [[self.gps_points[i], self.point_to_segment_projection(
                {"gps_point": self.gps_points[i], "cur_line": segments[0]})]]
            self.sub_points.append(self.gps_points[i])
            return i
        while segments[0][1]['cross'] or segments[1][1]['cross']:
            while self.state_point_to_segment_distance(self.gps_points[i]['coords'], [line_point,
                                                                                      segments[0][1] if condition else
                                                                                      segments[1][1]])['flag']:
                dist1 += self.dist_to_switch_segment(self.gps_points[i], line_point,
                                                     segments[0][1])
                dist2 += self.dist_to_switch_segment(self.gps_points[i], line_point,
                                                     segments[1][1])
                print(self.gps_points[i])
                points.append(self.gps_points[i])
                i += 1

            tmp_point = segments[0][1] if dist2 > dist1 else segments[1][1]
            self.sub_segments.append([line_point, segments[1][1] if dist1 > dist2 else segments[0][1]])
            if condition:
                segments = self.find_segments_from_point(tmp_point)
            else:
                segments = self.find_segments_from_point_left(tmp_point)
            print(segments)
        ortho_points_1 = {"gps_point": self.gps_points[i], "cur_line": [line_point, segments[0][1]]}
        ortho_points_2 = {"gps_point": self.gps_points[i], "cur_line": [line_point, segments[1][1]]}
        self.sub_points.append(points)
        print(path)
        print(i)
        print(self.sub_points)
        if (self.point_to_segment_projection(ortho_points_1) - line_point['coords']).norm > R_CROSS and \
                (self.point_to_segment_projection(ortho_points_2) - line_point['coords']).norm > R_CROSS:
            result = []
            self.initial_dict = self.initialize(self.gps_points[i])
            result.append([self.gps_points[i], self.initial_dict['gps_point']])
            self.sub_points.append(self.gps_points[i])
        return i

    def add_point_on_cross(self, i: int, line_point: dict, condition: bool) -> (list, int):
        self.sub_points = []
        self.sub_segments = []
        step = self.find_path_on_switch(i, line_point, condition)
        result = self.lower_all_ortho(self.sub_segments, self.sub_points)
        return result, step

    def match(self) -> None:
        self.find_all_cross()
        # self.gps_points = self.gps_points[::-1]
        self.initial_dict = self.initialize(self.gps_points[0])
        self.result = [[self.gps_points[0], self.initial_dict['gps_point']]]
        step = 0
        new_points = []
        for i in range(1, len(self.gps_points)):
            p1, p2 = self.initial_dict['cur_line']
            ortho_point_dist = self.state_point_to_segment_distance(
                self.gps_points[i]['coords'], self.initial_dict["cur_line"]
            )
            if ortho_point_dist['flag']:
                self.result.append([self.gps_points[i], self.point_to_segment_projection(
                    {"gps_point": self.gps_points[i], "cur_line": self.initial_dict["cur_line"]})])
            elif not ortho_point_dist['line_point'] and p1["cross"] is False and p2['cross'] is True:
                new_points, step = self.add_point_on_cross(i, p2, True)
            elif not ortho_point_dist['line_point'] and p1["cross"] is False and p2['cross'] is False:
                new_points, step = self.add_point_to_result(i, p2, ortho_point_dist, True)
            elif ortho_point_dist['line_point'] and p1["cross"] is True and p2['cross'] is False:
                new_points, step = self.add_point_on_cross(i, p1, False)
            elif ortho_point_dist['line_point'] and p1["cross"] is False and p2['cross'] is False:
                new_points, step = self.add_point_to_result(i, p1, ortho_point_dist, False)
            else:
                self.initial_dict = self.initialize(self.gps_points[i])
                new_points = [[self.gps_points[i], self.initial_dict['gps_point']]]
            # print(self.gps_points[i])
            self.result.extend(new_points)
            i += step
        self.draw_full_map(self.result)


if __name__ == "__main__":
    matcher = StateMachineMatcher()
    matcher.match()