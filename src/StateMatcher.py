from utils.constants import MIN_DIST
from src.RailMap import RailLines
from src.GPSPoints import GPSPoints
import matplotlib.pyplot as plt
import utils.utils as utils
from src.SwitchClass import SwitchClass
from utils.utils import point_to_segment_distance, point_to_segment_projection


class StateMatcher:
    def __init__(self, kwargs):
        rail_lines = RailLines(path_to_lines=kwargs['lines_path'], path_to_points=kwargs['points_path'])
        gps_points = GPSPoints(gps_points_path=kwargs['path'])
        self.lines = rail_lines.lines
        self.points = rail_lines.points
        self.gps_points = gps_points.points
        self.initial_dict = {}
        self.result = []
        self.find_path_class = SwitchClass(kwargs['method'], kwargs['mode'])
        self.switch_id = 0
        self.point_buffer = []
        self.end_r = kwargs['end_r']
        self.switch_information = {
            "constants": {
                "start_r": kwargs['start_r'],
                "end_r": kwargs['end_r'],
                "n": kwargs['n']
            },
            "method_id": kwargs['method'],
            "mode": kwargs['mode'],
            "switch_class": self.find_path_class,
            "switches": []
        }

    def find_initial_state(self, index: int, min_dist=MIN_DIST) -> dict:
        """
        Function that finds starting point if the train starts from out of bounds.
        Also checks if path is starting on switch.
        Args:
            index: index of point in list of points
            min_dist: minimal distance that that is considered to choose start segment
        Returns:
            tuple:(
                dict: {
                    gps point,
                    current line
                }
            )
        """
        points = None
        for i in range(len(self.lines)):
            for j in range(len(self.lines[i]["points"]) - 1):
                line_points = [utils.find_dict(self.points, self.lines[i]["points"][j]),
                               utils.find_dict(self.points, self.lines[i]["points"][j + 1])]
                current_dict = point_to_segment_distance(self.gps_points[index]["coords"], line_points)
                if current_dict["dist"] < min_dist and current_dict['is_ortho']:
                    min_dist = current_dict["dist"]
                    points = {"gps_point": self.gps_points[index]['coords'], "cur_line": line_points}
        if points:
            if all([not line_point['cross'] for line_point in points["cur_line"]]):
                points['gps_point'] = point_to_segment_projection(points['gps_point'], points['cur_line'])
            for point in points['cur_line']:
                if point['cross']:
                    if (self.gps_points[index]["coords"] - point['coords']).norm <= self.end_r:
                        self.point_buffer.append(self.gps_points[index])
                        self.gps_points[index]['is_on_switch'] = True
                        points = None
        return points

    def initialize(self) -> (dict, int):
        """
        Initializing blocks
        Returns:
            tuple:
            (
                initial dictionary:contains orthogonal projection of point to current line, and current line,
                i: index of point in list
            )
        """
        i = 0
        while i < len(self.gps_points):
            state = self.find_initial_state(i)
            i += 1
            if state:
                self.gps_points[i]['cur_line'] = state['cur_line']
                for point in self.point_buffer:
                    self.result.append([point, utils.point_to_segment_projection(point['coords'], state['cur_line'])])
                return state, i

    def find_segments_from_point(self, point: dict) -> list:
        """
        Function that finds all points in line starts with given point
        Args:
            point: starting point in line

        Returns:
            list: list of point ids in line
        """
        result = []
        for i in range(len(self.lines)):
            if point['id'] in self.lines[i]["points"] and point['id'] != self.lines[i]["points"][-1]:
                result.append([utils.find_dict(self.points, x) for x in self.lines[i]["points"]])
        return result

    def find_segments_from_point_left(self, point: dict) -> list:
        """
        Function that finds all points in line ends with given point
        Args:
            point: ending point in line

        Returns:
            list: list of point ids in line
        """
        result = []
        for i in range(len(self.lines)):
            if point['id'] in self.lines[i]['points'] and point['id'] != self.lines[i]["points"][0]:
                result.append([utils.find_dict(self.points, x) for x in self.lines[i]["points"][::-1]])
        return result

    def draw_full_map(self, new_points: list) -> None:
        """
            Draws map with result points
            Returns: None
        """
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set_aspect("equal")
        RailLines.draw_lines(self.lines, self.points, ax)
        RailLines.draw_points(self.gps_points, ax, "green")
        RailLines.draw_connected_points(self.points, new_points, ax)
        plt.grid()
        plt.show()

    def add_point_to_result(self, point: dict, line_point: dict, ortho_point_dist: dict, condition: bool) -> (
            list, bool):
        """function to add point with orthogonal projection to result.
        Function is used to add points until switch is reached.
            Args:
                point: gps point from list (self.gps_point[i])
                line_point: point to end of segment (segments consists of 2 points)
                ortho_point_dist: dictionary obout distance, flag is_ortho
                    (is it possible to lower the height on segment), e.t.c
                condition: bool that demonstrates end or start of segment (True if start and False if end)
            Returns:
                list: list(point, point after letting orthogonal projection), break condition (if segment is on the end
                    of the map True else if not)
        """
        next_segment = self.find_next_segment(line_point, condition)
        next_seg_dist = point_to_segment_distance(point['coords'], next_segment)
        if next_seg_dist['break']:
            return [[[point, point['coords']]], True]
        if next_seg_dist['is_ortho']:
            self.initial_dict['cur_line'] = next_segment
            if next_segment[0]['end'] and not condition:
                break_condition = True
            elif next_segment[1]['end'] and condition:
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
            if ortho_point_dist['is_ortho']:
                new_point = point_to_segment_projection(point['coords'], ortho_point_dist['cur_line'])
                return [[[point, new_point]], break_condition]
            else:
                self.initial_dict['cur_line'] = next_segment
                return [[[point, line_point['coords']]], break_condition]

    def find_next_segment(self, line_point: dict, condition: bool) -> list:
        """Function to find next segment of current segment.
            Args:
                line_point: end of current segment
                condition: bool that demonstrates end or start of segment (True if start and False if end)
            Returns:
                list: next segment in line or on new line.
        """
        for line in self.lines:
            if line_point['id'] in line['points']:
                if line_point['id'] != line['points'][0] and line_point['id'] != line['points'][-1]:
                    next_line_point = self.find_next_point_in_line(line_point, line['points'], condition)
                    return [line_point, next_line_point]
                else:
                    if condition:
                        next_line_point = self.find_new_line_from_point_right(line_point)
                        return [line_point, next_line_point]
                    else:
                        next_line_point = self.find_new_line_from_point_left(line_point)
                        return [next_line_point, line_point]

    def find_new_line_from_point_right(self, line_point: dict) -> dict:
        """Function to find new line that start from certain point
            Args:
                line_point: end of current segment
            Returns:
                dict: second point in segment (is used in find_next_segment())
        """
        for line in self.lines:
            if line_point['id'] == line['points'][0]:
                return utils.find_dict(self.points, line['points'][1])

    def find_new_line_from_point_left(self, line_point: dict) -> dict:
        """
        Function to find new line that ends on certain point
            Args:
                line_point: end of current segment
            Returns:
                dict: first point in segment (is used in find_next_segment())
        """
        for line in self.lines:
            if line_point['id'] == line['points'][-1]:
                return utils.find_dict(self.points, line['points'][-2])

    def find_next_point_in_line(self, line_point: dict, original_list: list, condition: bool) -> dict:
        """Function to find next segment in line. (is used until the end of line)
            Args:
                line_point: end of current segment,
                original_list: list of point ids of line
                condition: bool that demonstrates end or start of segment (True if start and False if end)
            Returns:
                dict: second point in segment (is used in find_next_segment())
        """
        for i in range(len(original_list)):
            if line_point['id'] == original_list[i]:
                return utils.find_dict(self.points, original_list[i + 1 if condition else i - 1])

    def find_next_segment_in_line(self, line_point: dict, condition: bool) -> list:
        """Function to find next segment in line. (is used until the end of line)
            Args:
                line_point: end of current segment,
                condition: bool that demonstrates end or start of segment (True if start and False if end)
            Returns:
                list:[
                    dict: end/start of current segment,
                    dict: next point of segment in line
                ]
        """
        for line in self.lines:
            if line_point['id'] in line['points']:
                index = utils.find_index(line_point, line['points'])
                if 0 < index < len(line['points']) - 1:
                    new_end_point = utils.find_dict(self.points, line['points'][index + 1 if condition else index - 1])
                    return [line_point, new_end_point]

    def consider_segments(self, segments: list) -> list:
        """function returns segments to hand them over to switch choosing class
            Args:
                segments: 2 lines on switch
            Returns:
                2 segments, that consist of [[p1,p2],[p3,p4]]
        """

        try:
            if (segments[0][0]['coords'] - segments[0][1]['coords']).norm < self.end_r:
                observed_segments = [[segments[0][1], segments[0][2]], [segments[1][0], segments[1][1]]]
            elif (segments[1][0]['coords'] - segments[1][1]['coords']).norm < self.end_r:
                observed_segments = [[segments[0][0], segments[0][1]], [segments[1][1], segments[1][2]]]
            else:
                observed_segments = [[segments[0][0], segments[0][1]], [segments[1][0], segments[1][1]]]
        except IndexError:
            observed_segments = [[segments[0][0], segments[0][1]], [segments[1][0], segments[1][1]]]
        # self.consider_segments()
        return observed_segments

    def add_points_to_result_on_switch(self, points: list, cur_line: list) -> tuple:
        """
        Function to add points to result on switch. if path on switch consists of 2 or more segments,
        the function finds previous segment and lowers heights on them.
            Args:
                points: point list that have to be added
                cur_line: current segment of switch
            Returns:
                tuple:(
                    lists [points, orthogonal projection of point],
                    current segment on the path [p1,p2]
                )
        """
        result = []
        for point in points:
            ortho_point_dist = point_to_segment_distance(
                point['coords'], cur_line
            )
            if ortho_point_dist['is_ortho']:
                result.append([point, point_to_segment_projection(
                    point['coords'], cur_line)]
                              )
            else:
                next_segment = self.find_next_segment(cur_line[0 if ortho_point_dist['line_point'] else 1],
                                                      ortho_point_dist['line_point'])
                cur_line = next_segment
                result.append([point, point_to_segment_projection(
                    point['coords'], next_segment)]
                              )
        return result, cur_line[:2]

    def get_result_on_switch(self, i: int, line: list, last_line_ortho_point_dist: dict, condition: bool) -> list:
        """function to find segment on switch based on chosen method and all points on switch to chosen path
            Args:
                i : index of gps point in list,
                line: current line the train is moving on,
                last_line_ortho_point_dist: dictionary with information about current line and last gps point in list
                condition: bool that says that the train is moving to start or end of the segment
            Returns:
                list:[
                    list: [point, orthogonal projection of point],
                    bool: did the train reach the end of map section,
                    step: len(points), step that will be skipped in while loop in match
                ]
        """
        line_point = line[1]
        points = []
        segments = self.find_segments_from_point(line_point) if condition else \
            self.find_segments_from_point_left(line_point)
        # if there are only 1 way
        if len(segments) == 1:
            self.initial_dict['cur_line'] = segments[0]
            result = [[self.gps_points[i], point_to_segment_projection(
                self.gps_points[i]['coords'], last_line_ortho_point_dist['cur_line'])]]
            return [result, True if segments[0][1]['end'] or segments[0][0]['end'] else False, 0]

        observed_segments = self.consider_segments(segments)
        is_valid_condition = utils.is_switch_valid(line, observed_segments)
        # get all points that lay in decision area
        while (self.gps_points[i]["coords"] - line_point['coords']).norm <= self.end_r and i < len(self.gps_points) - 1:
            points.append(self.gps_points[i])
            self.gps_points[i]['is_on_switch'] = is_valid_condition['is_valid']
            i += 1
        # checks if the switch is valid
        if not is_valid_condition['is_valid']:
            self.initial_dict['cur_line'] = is_valid_condition['line']
            result, tmp_line = self.add_points_to_result_on_switch(points, self.initial_dict['cur_line'])
            return [result,
                    True if is_valid_condition['line'][0]['end'] or is_valid_condition['line'][1]['end'] else False,
                    len(points)]
        # block to make decision on the switch
        cur_line = self.find_path_class.find_cur_line(points, observed_segments,
                                                      constants=self.switch_information['constants'],
                                                      line_point=line_point)
        # info to hand over to tester
        self.switch_information['switches'].append(
            {"id": self.switch_id, "line": cur_line, "points": points,
             "segments": observed_segments, "line_point": line_point})
        self.switch_id += 1
        self.initial_dict['cur_line'] = cur_line[:2]
        result, tmp_line = self.add_points_to_result_on_switch(points, cur_line)
        if not condition:
            self.initial_dict['cur_line'] = tmp_line
        result.append([self.gps_points[i], point_to_segment_projection(self.gps_points[i]['coords'],
                                                                       self.initial_dict['cur_line'])])
        if cur_line[1]['end'] and condition:
            return [result, True, len(points)]
        elif cur_line[0]['end'] and not condition:
            return [result, True, len(points)]
        return [result, False, len(points)]

    def add_point_on_cross(self, i: int, line: list, ortho_point_dist: dict, condition: bool) -> list:
        """
        Function to check if point in decision area. if it is in the area,
        then get_result_on_switch is called else it is added to result with add_point_to_result function
        Args:
            i: index of point in point list
            line: current segment on the map
            ortho_point_dist: dictionary obout distance, flag is_ortho
            (is it possible to lower the height on segment), e.t.c
            condition: bool that demonstrates end or start of segment (True if start and False if end)

        Returns:
            list:[
                    list: [point, orthogonal projection of point],
                    bool: did the train reach the end of map section,
                    step: len(points), step that will be skipped in while loop in match
                ]
        """
        if (self.gps_points[i]["coords"] - line[1]['coords']).norm <= self.end_r:
            return self.get_result_on_switch(i, line, ortho_point_dist, condition)
        else:
            new_points, break_condition = self.add_point_to_result(self.gps_points[i], line[1], ortho_point_dist,
                                                                   condition)
            return [new_points, break_condition, 0]

    def get_switch_info(self):
        """
        Returns:
            dict:{
                constants:
                    start radius,
                    end radius,
                    n points in last n mode
                method_id,
                mode,
                switch choosing class object,
                list of switches
            }
        """
        return self.switch_information

    def match(self) -> None:
        # self.gps_points = self.gps_points[::-1]
        """
            Function that initialize algorithm
            Returns: None
        """
        self.initial_dict, i = self.initialize()
        self.result.append([self.gps_points[i - 1], self.initial_dict['gps_point']])
        while i < len(self.gps_points):
            step = 0
            p1, p2 = self.initial_dict['cur_line']
            ortho_point_dist = point_to_segment_distance(
                self.gps_points[i]['coords'], self.initial_dict["cur_line"]
            )
            if ortho_point_dist['is_ortho']:
                self.result.append([self.gps_points[i], point_to_segment_projection(
                    self.gps_points[i]['coords'], self.initial_dict["cur_line"])]
                                   )
            else:
                line = [p1, p2] if not ortho_point_dist['line_point'] else [p2, p1]
                line_point = p2 if not ortho_point_dist['line_point'] else p1
                if p2['cross'] if not ortho_point_dist['line_point'] else p1['cross']:
                    new_points, break_condition, step = self.add_point_on_cross(i, line, ortho_point_dist,
                                                                                not ortho_point_dist['line_point'])
                elif all([p2['cross'], p1['cross']]):
                    new_points, break_condition, step = self.add_point_on_cross(i, line[::-1], ortho_point_dist,
                                                                                not ortho_point_dist['line_point'])
                else:
                    new_points, break_condition = self.add_point_to_result(self.gps_points[i], line_point,
                                                                           ortho_point_dist,
                                                                           not ortho_point_dist['line_point'])
                if break_condition and i > len(self.gps_points) - 150:
                    break
                self.result.extend(new_points)
                i += step
            i += 1

    def draw_trajectory(self):
        """
            Draws map with only gps point from log
            Returns: None
        """
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set_aspect("equal")
        RailLines.draw_lines(self.lines, self.points, ax)
        RailLines.draw_points(self.gps_points, ax, "green")
        plt.grid()
        plt.show()

