from matplotlib.axis import Axis
from constants import GPS_POINTS_PATH, POINTS_PATH, LINES_PATH, MIN_DIST, R_MAX
from RailMap import RailLines
from GPSPoints import GPSPoints
from numpy.linalg import norm
import numpy as np
import matplotlib.pyplot as plt
from PointClass import Point
import utils
from switchClass import SwitchClass

from utils import point_to_segment_distance, point_to_segment_projection
R_CROSS = 20



class stateMachineMatcher:
    def __init__(self, method_id, path_to_lines=LINES_PATH, path_to_points=POINTS_PATH,
                 gps_points_path=GPS_POINTS_PATH):
        rail_lines = RailLines(path_to_lines=path_to_lines, path_to_points=path_to_points)
        gps_points = GPSPoints(gps_points_path=gps_points_path)
        self.lines = rail_lines.lines
        self.points = rail_lines.points
        self.gps_points = gps_points.points
        self.initial_dict = {}
        self.matching_method_id = method_id
        self.result = []
        self.sub_points = []
        self.sub_segments = []
        self.find_path_class = SwitchClass(method_id)
        self.switches = []
        self.switch_id = 0

    def find_initial_state(self, initial_point: dict, last_line=None, min_dist=MIN_DIST) -> dict:
        points = None
        for i in range(len(self.lines)):
            for j in range(len(self.lines[i]["points"]) - 1):
                line_points = [utils.find_dict(self.points, self.lines[i]["points"][j]),
                               utils.find_dict(self.points, self.lines[i]["points"][j + 1])]
                current_dict = point_to_segment_distance(initial_point["coords"], line_points)
                if current_dict["dist"] < min_dist and current_dict['flag']:
                    min_dist = current_dict["dist"]
                    points = {"gps_point": initial_point, "cur_line": line_points, "last_line": last_line}
        if points:
            points['gps_point'] = point_to_segment_projection(points['gps_point']['coords'], points['cur_line'])
        return points

    def initialize(self) -> (dict, int):
        i = 0
        while i < len(self.gps_points):
            state = self.find_initial_state(self.gps_points[i])
            i += 1
            if state:
                self.gps_points[i]['cur_line'] = state['cur_line']
                return state, i

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
        #RailLines.draw_points(self.gps_points, ax, "green")
        # RailLines.draw_points(new_points, ax, 'blue')
        RailLines.draw_connected_points(self.points, new_points, ax)
        plt.grid()
        plt.show()

    def add_point_to_result(self, point: dict, line_point: dict, ortho_point_dist: dict, condition: bool) -> (
            list, bool):
        next_segment = self.find_next_segment(line_point, condition)
        #print(next_segment)
        next_seg_dist = point_to_segment_distance(point['coords'], next_segment)
        if next_seg_dist['break']:
            return [[[point, point['coords']]], True]
        if next_seg_dist['flag']:
            self.initial_dict['cur_line'] = next_segment
            if next_segment[0]['end'] and not condition:
                #print("BREAK, left add point")
                break_condition = True
            elif next_segment[1]['end'] and condition:
                #print("BREAK, right add point")
                break_condition = True
            else:
                break_condition = False
            return [[[point,
                      point_to_segment_projection(point['coords'], next_segment)]],
                    break_condition]
        else:
            if ortho_point_dist['cur_line'][0]['end'] or ortho_point_dist['cur_line'][1]['end']:
                break_condition = True
            else:
                break_condition = False
            if ortho_point_dist['flag']:
                new_point = point_to_segment_projection(point['coords'], ortho_point_dist['cur_line'])
                return [[[point, new_point]], break_condition]
            else:
                self.initial_dict['cur_line'] = next_segment
                return [[[point, line_point['coords']]], break_condition]

    def find_next_segment(self, line_point: dict, condition: bool) -> list:
        for line in self.lines:
            if line_point['id'] in line['points']:
                #print(line_point['id'], ' id of point to find next segment from')
                #print(line['points'], ' line to check in find next segment')
                if line_point['id'] != line['points'][0] and line_point['id'] != line['points'][-1]:
                    next_line_point = self.find_next_point_in_line(line_point, line['points'], condition)
                    #print(next_line_point,' next line point')
                    return [line_point, next_line_point]
                else:
                    if condition:
                        next_line_point = self.find_new_line_from_point_right(line_point)
                        #print(next_line_point,' next line point right')
                        return [line_point, next_line_point]
                    else:
                        next_line_point = self.find_new_line_from_point_left(line_point)
                        #print(next_line_point,' next line point left')
                        return [next_line_point, line_point]

    def find_new_line_from_point_right(self, line_point: dict) -> dict:
        for line in self.lines:
            if line_point['id'] == line['points'][0]:
                #print(line['points'], ' found line starting from {}'.format(line_point['id']))
                return utils.find_dict(self.points, line['points'][1])

    def find_new_line_from_point_left(self, line_point: dict) -> dict:
        for line in self.lines:
            if line_point['id'] == line['points'][-1]:
                #print(line['points'], " found left line")
                return utils.find_dict(self.points, line['points'][-2])

    def find_next_point_in_line(self, line_point: dict, originial_list: list, condition: bool) -> dict:
        for i in range(len(originial_list)):
            if line_point['id'] == originial_list[i]:
                return utils.find_dict(self.points, originial_list[i + 1 if condition else i - 1])

    def dist_to_switch_segment(self, gps_point: dict, line_point: dict, segments: list, condition: bool) -> int:
        try:
            if condition:
                return point_to_segment_distance(gps_point['coords'], [line_point,
                                                                             segments[0]])["dist"]
            else:
                return point_to_segment_distance(gps_point['coords'], [line_point,
                                                                             segments[1]])["dist"]
        except:
            return 10000

    def find_next_segment_in_line(self, line_point: dict, condition: bool) -> list:
        for line in self.lines:
            if line_point['id'] in line['points']:
                index = utils.find_index(line_point, line['points'])
                if 0 < index < len(line['points']) - 1:
                    new_end_point = utils.find_dict(self.points, line['points'][index + 1 if condition else index - 1])
                    return [line_point, new_end_point]

    def consider_segments(self, segments: list, r_cross: float) -> list:
        try:
            if (segments[0][0]['coords'] - segments[0][1]['coords']).norm < r_cross:
                observed_segments = [[segments[0][1], segments[0][2]], [segments[1][0], segments[1][1]]]
                self.initial_dict['last_line'] = [segments[0][0], segments[0][1]]
            elif (segments[1][0]['coords'] - segments[1][1]['coords']).norm < r_cross:
                observed_segments = [[segments[0][0], segments[0][1]], [segments[1][1], segments[1][2]]]
                self.initial_dict['last_line'] = [segments[1][0], segments[1][1]]
            else:
                observed_segments = [[segments[0][0], segments[0][1]], [segments[1][0], segments[1][1]]]
        except:
            observed_segments = [[segments[0][0], segments[0][1]], [segments[1][0], segments[1][1]]]
        return observed_segments

    def get_result_on_switch(self, i: int, line_point: dict, last_line_ortho_point_dist: dict, condition: bool, r_cross) -> (
            list, bool, int):
        # print(i, ' start i')
        points = []
        result = []
        segments = self.find_segments_from_point(line_point) if condition else \
            self.find_segments_from_point_left(line_point)

        if len(segments) == 1:
            # print(segments)
            # self.initial_dict = self.initialize(self.gps_points[i])
            self.initial_dict['cur_line'] = segments[0]
            result = [[self.gps_points[i], point_to_segment_projection(
                self.gps_points[i]['coords'], last_line_ortho_point_dist['cur_line'])]]
            return [result, True if segments[0][1]['end'] or segments[0][0]['end'] else False, 0]

        while (self.gps_points[i]["coords"] - line_point['coords']).norm <= r_cross and i < len(self.gps_points) - 1:
            # print(i)
            self.gps_points[i]["is_on_switch"] = True
            points.append(self.gps_points[i])
            i += 1

        cur_line = self.find_path_class.choose_method(points, segments, r_cross, self.consider_segments)
        self.switches.append({"id": self.switch_id, "line": cur_line})
        self.switch_id += 1
        #print("added final point on cross. Point id - {}".format(self.gps_points[i]['id']))
        self.initial_dict['cur_line'] = cur_line
        for point in points[::-1] if condition else points:
            ortho_point_dist = point_to_segment_distance(
                point['coords'], cur_line
            )
            if ortho_point_dist['flag']:
                result.append([point, point_to_segment_projection(
                    point['coords'], cur_line)]
                              )
            else:
                if ortho_point_dist['line_point']:
                    next_segment = self.find_next_segment(cur_line[0], False)
                    cur_line = next_segment
                    result.append([point, point_to_segment_projection(
                        point['coords'], next_segment)]
                                  )
                else:
                    next_segment = self.find_next_segment(cur_line[1], True)
                    cur_line = next_segment
                    result.append([point, point_to_segment_projection(
                        point['coords'], next_segment)]
                                  )

        result.append([self.gps_points[i], point_to_segment_projection(self.gps_points[i]['coords'],
                                                                        self.initial_dict['cur_line'])])
        #self.initial_dict['cur_line'] = cur_line
        if cur_line[1]['end'] and condition:
            #print("BREAK, right add on cross")
            return [result, True, len(points)]
        elif cur_line[0]['end'] and not condition:
            #print("BREAK, left add on cross")
            return [result, True, len(points)]
        return [result, False, len(points)]

    def add_point_on_cross(self, i: int, line_point: dict, ortho_point_dist: dict, condition: bool, r_cross) -> list:
        if (self.gps_points[i]["coords"] - line_point['coords']).norm <= r_cross:
            return self.get_result_on_switch(i, line_point, ortho_point_dist, condition,r_cross)
        else:
            new_points, break_condition = self.add_point_to_result(self.gps_points[i], line_point, ortho_point_dist,
                                                                   condition)
            return [new_points, break_condition, 0]

    def match(self, r_cross=R_CROSS) -> None:
        # self.gps_points = sorted(self.gps_points, key=lambda point: (point['coords'].x, point['coords'].y))
        #self.gps_points = self.gps_points[::-1]
        self.initial_dict, i = self.initialize()
        #print(len(self.gps_points))
        self.result = [[self.gps_points[i - 1], self.initial_dict['gps_point']]]
        step = 0
        while i < len(self.gps_points):
            #print(i)
            p1, p2 = self.initial_dict['cur_line']
            ortho_point_dist = point_to_segment_distance(
                self.gps_points[i]['coords'], self.initial_dict["cur_line"]
            )
            if ortho_point_dist['flag']:
                self.result.append([self.gps_points[i], point_to_segment_projection(
                    self.gps_points[i]['coords'], self.initial_dict["cur_line"])]
                              )
            else:
                if not ortho_point_dist['line_point']:
                    if p2['cross']:
                        new_points, break_condition, step = self.add_point_on_cross(i, p2, ortho_point_dist, True,r_cross)
                    elif all([p2['cross'], p1['cross']]):
                        new_points, break_condition, step = self.add_point_on_cross(i, p1, ortho_point_dist, True,r_cross)
                    else:
                        new_points, break_condition = self.add_point_to_result(self.gps_points[i], p2, ortho_point_dist,
                                                                               True)
                else:
                    if p1['cross']:
                        new_points, break_condition, step = self.add_point_on_cross(i, p1, ortho_point_dist, False,
                                                                                    r_cross)
                    elif all([p2['cross'], p1['cross']]):
                        new_points, break_condition, step = self.add_point_on_cross(i, p2, ortho_point_dist, False,
                                                                                    r_cross)
                    else:
                        new_points, break_condition = self.add_point_to_result(self.gps_points[i], p1, ortho_point_dist,
                                                                               False)

                if break_condition and i > len(self.gps_points) - 300:
                    break
                self.result.extend(new_points)
                i += step
                # print(step, "- step")
                step = 0
            i += 1


if __name__ == "__main__":
    matcher = stateMachineMatcher(3)
    matcher.match()
