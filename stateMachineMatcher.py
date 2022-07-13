
from constants import GPS_POINTS_PATH, POINTS_PATH, LINES_PATH, MIN_DIST, R_MAX
from RailMap import RailLines
from GPSPoints import GPSPoints
from numpy.linalg import norm
import numpy as np
import matplotlib.pyplot as plt
from skspatial.objects import Line
from PointClass import Point
from Matcher import Matcher
from utils import find_min_dict_x, find_min_dict_y, find_max_dict_x, find_max_by_y, find_sublist, find_index, find_dict
from createTree import Node

R_CROSS = 20


class StateMachineMatcher(Matcher):
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
                line_points = [find_dict(self.points, self.lines[i]["points"][j]),
                               find_dict(self.points, self.lines[i]["points"][j + 1])]
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

    def lower_all_ortho(self) -> list:
        res = []
        for i in range(len(self.gps_points)):
            res.append([self.gps_points[i], self.find_min_dist(self.gps_points[i])])
        return res

    def find_new_line_segment(self, point: dict, condition: bool) -> dict:
        for i in range(len(self.lines)):
            if point['id'] in self.lines[i]["points"]:
                return find_dict(self.points, find_sublist(point['id'], self.lines[i]["points"], condition))

    def find_segments_from_point(self, point: dict) -> list:
        result = []
        for i in range(len(self.lines)):
            if point['id'] in self.lines[i]["points"] and point['id'] != self.lines[i]["points"][-1]:
                result.append([find_dict(self.points, x) for x in self.lines[i]["points"]])
        return result

    def find_segments_from_point_left(self, point: dict) -> list:
        result = []
        for i in range(len(self.lines)):
            if point['id'] == self.lines[i]["points"][-1]:
                result.append([find_dict(self.points, x) for x in self.lines[i]["points"][::-1]])
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

    def dist_to_switch_segment(self, gps_point: dict, line_point: dict, segments: list, condition: bool) -> int:
        try:
            if condition:
                return self.point_to_segment_distance(gps_point['coords'], line_point['coords'],
                                                      segments[0]['coords'])["dist"]
            else:
                return self.point_to_segment_distance(gps_point['coords'], line_point['coords'],
                                                      segments[1]['coords'])["dist"]
        except:
            return 10000

    def find_next_segment_in_line(self, line_point: dict, condition: bool) -> list:
        for line in self.lines:
            if line_point['id'] in line['points']:
                index = find_index(line_point, line['points'])
                if 0 < index < len(line['points']) - 1:
                    new_end_point = find_dict(self.points, line['points'][index+1 if condition else index - 1])
                    return [line_point, new_end_point]

    def accumulate_dist(self, i: int, line_point: dict, condition: bool) -> (list, int):
        print(i, ' start i')
        points = []
        result = []
        if condition:
            segments = self.find_segments_from_point(line_point)
        else:
            segments = self.find_segments_from_point_left(line_point)

        if len(segments) == 1:
            print(segments)
            self.initial_dict = self.initialize(self.gps_points[i])
            result = [[self.gps_points[i], self.point_to_segment_projection(
                {"gps_point": self.gps_points[i], "cur_line": segments[0]})]]
            return [result, 0]

        if (segments[0][0]['coords'] - segments[0][1]['coords']).norm < R_CROSS:
            try:
                observed_segments = [[segments[0][1], segments[0][2]],[segments[1][0], segments[1][1]]]
            except:
                observed_segments = [[segments[0][0], segments[0][1]], [segments[1][0], segments[1][1]]]
        elif (segments[1][0]['coords'] - segments[1][1]['coords']).norm < R_CROSS:
            try:
                observed_segments = [[segments[0][0], segments[0][1]], [segments[1][1], segments[1][2]]]
            except:
                observed_segments = [[segments[0][0], segments[0][1]], [segments[1][0], segments[1][1]]]
        else:
            observed_segments = [[segments[0][0], segments[0][1]], [segments[1][0], segments[1][1]]]
        while (self.gps_points[i]["coords"] - line_point['coords']).norm <= R_CROSS:
            self.gps_points[i]['color'] = 'lime'
            points.append(self.gps_points[i])
            i += 1
        dist_1 = self.point_to_segment_distance(self.gps_points[i]['coords'],
                                                observed_segments[0][0]['coords'],
                                                observed_segments[0][1]['coords'])['dist']
        dist_2 = self.point_to_segment_distance(self.gps_points[i]['coords'],
                                                observed_segments[1][0]['coords'],
                                                observed_segments[1][1]['coords'])['dist']
        if dist_2 > dist_1:
            cur_line = segments[0]
        else:
            cur_line = segments[1]
        [result.append([x, self.point_to_segment_projection({"gps_point": x, 'cur_line': cur_line})]) for x in points]
        result.append([self.gps_points[i], self.point_to_segment_projection({"gps_point": self.gps_points[i],
                                                                             'cur_line': cur_line})])
        self.initial_dict = self.initialize(self.gps_points[i])
        print(i, ' end i')
        return [result, len(points)]

    def add_point_on_cross(self, i: int, line_point: dict, condition: bool) -> list:
        if (self.gps_points[i]["coords"] - line_point['coords']).norm > R_CROSS:
            result = []
            self.initial_dict = self.initialize(self.gps_points[i])
            result.append([self.gps_points[i], self.initial_dict['gps_point']])
            return [result, 0]
        else:
            return self.accumulate_dist(i, line_point, condition)


    def match(self) -> None:
        #self.gps_points = self.gps_points[::-1]
        self.initial_dict = self.initialize(self.gps_points[0])
        result = [[self.gps_points[0], self.initial_dict['gps_point']]]
        i = 1
        while i < len(self.gps_points[1:])+1:
            p1, p2 = self.initial_dict['cur_line']
            ortho_point_dist = self.state_point_to_segment_distance(
                self.gps_points[i]['coords'], self.initial_dict["cur_line"]
            )
            if ortho_point_dist['flag']:
                result.append([self.gps_points[i], self.point_to_segment_projection(
                    {"gps_point": self.gps_points[i], "cur_line": self.initial_dict["cur_line"]})]
                               )
            elif not ortho_point_dist['flag']:
                if ortho_point_dist['line_point'] is False:
                    if p1['cross'] is False and p2['cross'] is False:
                        new_points, step = self.add_point_to_result(i, p2, ortho_point_dist, True)
                        result.extend(new_points)
                        i += step
                        continue
                    elif p2['cross'] is True:
                        new_points, step = self.add_point_on_cross(i, p2, True)
                        result.extend(new_points)
                        i += step
                        continue
                    elif p2['cross'] is True and p1['cross'] is True:
                        new_points, step = self.add_point_on_cross(i, p1, True)
                        result.extend(new_points)
                        i += step
                        continue
                    else:
                        self.initial_dict = self.initialize(self.gps_points[i])
                        continue
                elif ortho_point_dist['line_point']:
                    next_seg = self.find_next_segment_in_line(p1, False)
                    print(next_seg)
                    if p1['cross'] is False and p2['cross'] is False:
                        new_points, step = self.add_point_to_result(i, p1, ortho_point_dist, False)
                        result.extend(new_points)
                        i += step
                        continue
                    elif p1['cross'] is True:
                    #if p1['cross'] is True:
                        new_points, step = self.add_point_on_cross(i, p1, False)
                        result.extend(new_points)
                        i += step
                        continue
                    elif p2['cross'] is True and p1['cross'] is True:
                        new_points, step = self.add_point_on_cross(i, p2, False)
                        result.extend(new_points)
                        i += step
                        continue
                    else:
                        self.initial_dict = self.initialize(self.gps_points[i])
                else:
                    self.initial_dict = self.initialize(self.gps_points[i])
            else:
                self.initial_dict = self.initialize(self.gps_points[i])
            i += 1

        self.draw_full_map(result)


if __name__ == "__main__":
    matcher = StateMachineMatcher()
    matcher.match()