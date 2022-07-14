from utils import get_json, find_dict
from constants import POINTS_PATH, LINES_PATH, GPS_POINTS_PATH
from BasicMap import BasicMap


class RailLines(BasicMap):
    def __init__(self, path_to_lines, path_to_points):
        old_lines = get_json(path_to_lines)
        old_points = get_json(path_to_points)
        self.lines = self.line_transform(old_lines)
        self.points = self.point_transform(old_points, self.lines)
        self.find_all_cross()
        #self.find_all_ends()
        #self.merge_lines()

    def find_all_cross(self) -> None:
        for i in range(len(self.points)):
            count = 0
            end_count = 0
            for j in range(len(self.lines)):
                if self.points[i]["id"] in self.lines[j]['points']:
                    count += 1
                if self.points[i]['id'] == self.lines[j]['points'][0] or self.points[i]['id'] == self.lines[j]['points'][-1]:
                    end_count += 1
            if count >= 3:
                self.points[i]["cross"] = True
            else:
                self.points[i]["cross"] = False
            if end_count == 1:
                self.points[i]['end'] = True
            else:
                self.points[i]['end'] = False

    def print_lines(self) -> None:
        print(self.lines)

    '''def merge_lines(self):
        i = 0
        for point in self.points:
            sub_list_of_lines = []
            while i < len(self.lines):
                if point['cross'] is False and (point['id'] is self.lines[i]['points'][0] or point['id'] is self.lines[i]['points'][-1]):
                    sub_list_of_lines.append(i)
                    i+=1
                if point['cross'] is False and (point['id'] is not self.lines[i]['points'][0] or point['id'] is not self.lines[i]['points'][-1]):
                    continue
                i += 1
            if len(sub_list_of_lines) > 1:
                if self.lines[sub_list_of_lines[0]]['points'][0] == self.lines[sub_list_of_lines[1]]['points'][-1]:
                    print(self.lines[sub_list_of_lines[0]]['points'], " start")
                    print(self.lines[sub_list_of_lines[1]]['points'], " end")
                    print("_________________")
                    self.lines[sub_list_of_lines[1]]['points'] = self.lines[sub_list_of_lines[1]]['points'][:-1] + self.lines[sub_list_of_lines[0]]['points']
                    self.lines.remove(self.lines[sub_list_of_lines[0]])
                elif self.lines[sub_list_of_lines[1]]['points'][0] == self.lines[sub_list_of_lines[0]]['points'][-1]:
                    print(self.lines[sub_list_of_lines[1]]['points'], " start")
                    print(self.lines[sub_list_of_lines[0]]['points'], " end")
                    print("_________________")
                    self.lines[sub_list_of_lines[0]]['points'] = self.lines[sub_list_of_lines[0]]['points'][:-1] + \
                                                                 self.lines[sub_list_of_lines[1]]['points']
                    self.lines.remove(self.lines[sub_list_of_lines[-1]])'''


if __name__ == "__main__":
    new_map = RailLines(LINES_PATH, POINTS_PATH)
