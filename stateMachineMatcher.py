from matplotlib.axis import Axis
from constants import GPS_POINTS_PATH, POINTS_PATH, LINES_PATH, MIN_DIST, R_MAX
from RailMap import RailLines
from GPSPoints import GPSPoints
from numpy.linalg import norm
import numpy as np
import matplotlib.pyplot as plt
from skspatial.objects import Line
from PointClass import Point
from Matcher import Matcher
from createTree import Node
import utils

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

    def find_initial_state(self, initial_point: dict, last_line=None, min_dist=MIN_DIST) -> dict:
        points = {}
        for i in range(len(self.lines)):
            for j in range(len(self.lines[i]["points"]) - 1):
                line_points = [utils.find_dict(self.points, self.lines[i]["points"][j]),
                               utils.find_dict(self.points, self.lines[i]["points"][j + 1])]
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

    def find_segments_from_point(self, point: dict) -> list:
        result = []
        for i in range(len(self.lines)):
            if point['id'] in self.lines[i]["points"] and point['id'] != self.lines[i]["points"][-1]:
                result.append([utils.find_dict(self.points, x) for x in self.lines[i]["points"]])
        return result

    def find_segments_from_point_left(self, point: dict) -> list:
        result = []
        for i in range(len(self.lines)):
            if point['id'] in self.lines[i]['points'] and point['id'] != self.lines[i]["points"][0]:
                result.append([utils.find_dict(self.points, x) for x in self.lines[i]["points"][::-1]])
        return result

    def draw_full_map(self, new_points: list) -> None:
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set_aspect("equal")
        RailLines.draw_lines(self.lines, self.points, ax)
        RailLines.draw_points(self.gps_points, ax, "green")
        # RailLines.draw_points(new_points, ax, 'blue')
        RailLines.draw_connected_points(self.points, new_points, ax)
        plt.grid()
        plt.show()

    def add_point_to_result(self, i: int, line_point: dict, ortho_point_dist: dict, condition: bool) -> list:
        next_segment = self.find_next_segment(line_point, condition)
        next_seg_dist = self.state_point_to_segment_distance(self.gps_points[i]['coords'], next_segment)

        if next_seg_dist['flag']:
            self.initial_dict['cur_line'] = next_segment
            if next_segment[0]['end'] or next_segment[1]['end']:
                break_condition = True
            else:
                break_condition = False
            return [[[self.gps_points[i], self.point_to_segment_projection({"gps_point": self.gps_points[i], "cur_line": next_segment})]], break_condition, 0]
        else:
            if ortho_point_dist['flag']:
                points = {'gps_point': self.gps_points[i], 'cur_line': self.initial_dict['cur_line']}
                new_point = self.point_to_segment_projection(points)
                return [[[self.gps_points[i], new_point]], False, 0]
            if next_seg_dist['line_point'] ^ ortho_point_dist['line_point']:
                self.initial_dict['cur_line'] = next_segment
                return [[[self.gps_points[i], line_point['coords']]], False, 0]
            '''if ortho_point_dist['flag']:
                points = {'gps_point': self.gps_points[i], 'cur_line': self.initial_dict['cur_line']}
                new_point = self.point_to_segment_projection(points)
                return [[[self.gps_points[i], new_point]], False, 0]'''

    def find_next_segment(self, line_point: dict, condition: bool) -> list:
        for line in self.lines:
            if line_point['id'] in line['points']:
                if line_point['id'] != line['points'][0] and line_point['id'] != line['points'][-1]:
                    next_line_point = self.find_next_point_in_line(line_point, line['points'], condition)
                    self.initial_dict['cur_line'] = [line_point, next_line_point]
                    return [line_point, next_line_point]
                else:
                    if condition:
                        next_line_point = self.find_new_line_from_point_right(line_point)
                        self.initial_dict['cur_line'] = [line_point, next_line_point]
                        return [line_point, next_line_point]
                    else:
                        next_line_point = self.find_new_line_from_point_left(line_point)
                        print('left - ', next_line_point)
                        print('point - ', line_point)
                        print("line - ", line['points'])
                        self.initial_dict['cur_line'] = [line_point, next_line_point]
                        print('cur_line - ', self.initial_dict['cur_line'])
                        return [line_point, next_line_point]

    def find_new_line_from_point_right(self, line_point: dict):
        for line in self.lines:
            if line_point['id'] == line['points'][0]:
                return utils.find_dict(self.points, line['points'][1])

    def find_new_line_from_point_left(self, line_point: dict):
        for line in self.lines:
            if line_point['id'] == line['points'][-1]:
                print(line['points'], " found left line")
                return utils.find_dict(self.points, line['points'][-2])

    def find_next_point_in_line(self, line_point: dict, originial_list: list, condition: bool) -> dict:
        for i in range(len(originial_list)):
            if line_point['id'] == originial_list[i]:
                return utils.find_dict(self.points, originial_list[i+1 if condition else i-1])

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
                index = utils.find_index(line_point, line['points'])
                if 0 < index < len(line['points']) - 1:
                    new_end_point = utils.find_dict(self.points, line['points'][index+1 if condition else index - 1])
                    return [line_point, new_end_point]

    def find_cur_line(self, gps_point: dict, observed_segments: list) -> list:
        dist_1 = self.point_to_segment_distance(gps_point['coords'],
                                                observed_segments[0][0]['coords'],
                                                observed_segments[0][1]['coords'])['dist']
        dist_2 = self.point_to_segment_distance(gps_point['coords'],
                                                observed_segments[1][0]['coords'],
                                                observed_segments[1][1]['coords'])['dist']
        if dist_2 > dist_1:
            cur_line = observed_segments[0]
        else:
            cur_line = observed_segments[1]
        return cur_line

    def accumulate_dist(self, i: int, line_point: dict, condition: bool) -> (list,bool, int):
        #print(i, ' start i')
        points = []
        result = []
        segments = self.find_segments_from_point(line_point) if condition else \
            self.find_segments_from_point_left(line_point)

        if len(segments) == 1:
            #print(segments)
            #self.initial_dict = self.initialize(self.gps_points[i])
            self.initial_dict['cur_line'] = segments[0]
            result = [[self.gps_points[i], self.point_to_segment_projection(
                {"gps_point": self.gps_points[i], "cur_line": segments[0]})]]
            return [result, True if segments[0][1]['end'] or segments[0][0]['end'] else False, 0]


        while (self.gps_points[i]["coords"] - line_point['coords']).norm <= R_CROSS and i < len(self.gps_points)-1:
            #print(i)
            self.gps_points[i]['color'] = 'lime'
            points.append(self.gps_points[i])
            i += 1
        observed_segments = utils.consider_segments(segments, R_CROSS)
        cur_line = self.find_cur_line(self.gps_points[i], observed_segments)
        print(cur_line)
        for point in points[::-1]:
            ortho_point_dist = self.state_point_to_segment_distance(
                point['coords'], cur_line
            )
            if ortho_point_dist['flag']:
                result.append([point, self.point_to_segment_projection(
                    {"gps_point": point, "cur_line": cur_line})]
                              )
            else:
                if ortho_point_dist['line_point']:
                    next_segment = self.find_next_segment(cur_line[0], False)
                    result.append([point, self.point_to_segment_projection(
                        {"gps_point": point, "cur_line": next_segment})]
                                  )
                else:
                    next_segment = self.find_next_segment(cur_line[1], True)
                    result.append([point, self.point_to_segment_projection(
                        {"gps_point": point, "cur_line": next_segment})]
                                  )
        self.initial_dict['cur_line'] = cur_line

        #[result.append([x, self.point_to_segment_projection({"gps_point": x, 'cur_line': cur_line})]) for x in points]
        result.append([self.gps_points[i], self.point_to_segment_projection({"gps_point": self.gps_points[i],
                                                                             'cur_line': cur_line})])
        if cur_line[1]['end']:
            return [result, True, len(points)]
        return [result, False, len(points)]

    def add_point_on_cross(self, i: int, line_point: dict, ortho_point_dist: dict, condition: bool) -> list:
        if (self.gps_points[i]["coords"] - line_point['coords']).norm < R_CROSS:
            return self.accumulate_dist(i, line_point, condition)
        else:
            return self.add_point_to_result(i, line_point, ortho_point_dist, condition)

    def match(self) -> None:
        #self.gps_points = sorted(self.gps_points, key=lambda point: (point['coords'].x, point['coords'].y))
        #self.gps_points = self.gps_points[::-1]
        self.initial_dict = self.initialize(self.gps_points[0])
        result = [[self.gps_points[0], self.initial_dict['gps_point']]]
        i = 1
        while i < len(self.gps_points[1:]):
            #print(len(self.initial_dict['cur_line']))
            p1, p2 = self.initial_dict['cur_line']
            ortho_point_dist = self.state_point_to_segment_distance(
                self.gps_points[i]['coords'], self.initial_dict["cur_line"]
            )
            if ortho_point_dist['flag']:
                result.append([self.gps_points[i], self.point_to_segment_projection(
                    {"gps_point": self.gps_points[i], "cur_line": self.initial_dict["cur_line"]})]
                              )
            else:
                if ortho_point_dist['line_point']:
                    if p1['cross'] is False and p2['cross'] is False:
                        new_points, break_condition, step = self.add_point_to_result(i, p1, ortho_point_dist, False)
                    elif p1['cross'] is True:
                        new_points, break_condition, step = self.add_point_on_cross(i, p1, ortho_point_dist, False)
                    elif p2['cross'] is True and p1['cross'] is True:
                        new_points, break_condition, step = self.add_point_on_cross(i, p2, ortho_point_dist, False)
                    else:
                        new_points, break_condition, step = self.add_point_to_result(i, p2, ortho_point_dist, False)
                else:
                    if p1['cross'] is False and p2['cross'] is False:
                        new_points, break_condition, step = self.add_point_to_result(i, p2, ortho_point_dist, True)
                    elif p2['cross'] is True:
                        new_points,break_condition, step = self.add_point_on_cross(i, p2,ortho_point_dist, True)
                    elif p2['cross'] is True and p1['cross'] is True:
                        new_points,break_condition, step = self.add_point_on_cross(i, p1,ortho_point_dist, True)
                    else:
                        new_points, break_condition, step = self.add_point_to_result(i, p1, ortho_point_dist, True)
                result.extend(new_points)
                i += step
                if break_condition:
                    break
            i += 1
        self.draw_full_map(result)


if __name__ == "__main__":
    matcher = StateMachineMatcher()
    matcher.match()