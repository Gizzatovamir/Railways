from utils import get_json, find_dict
import matplotlib.pyplot as plt
from constants import POINTS_PATH, LINES_PATH, GPS_POINTS_PATH
from GPSPoints import GPSPoints
from BasicMap import BasicMap


class RailLines(BasicMap):
    def __init__(self, path_to_lines, path_to_points):
        old_lines = get_json(path_to_lines)
        old_points = get_json(path_to_points)
        self.lines = self.line_transform(old_lines)
        self.points = self.point_transform(old_points, self.lines)
        self.find_all_cross()
        #self.merge_lines()

    def find_all_cross(self) -> None:
        for i in range(len(self.points)):
            count = 0
            for j in range(len(self.lines)):
                if self.points[i]["id"] in self.lines[j]['points']:
                    count += 1
            if count >= 3:
                self.points[i]["cross"] = True
            else:
                self.points[i]["cross"] = False

    def print_lines(self) -> None:
        print(self.lines)

'''    def merge_lines(self):
        i = 0
        j = 0
        print(len(self.lines))
        while i < len(self.lines):
            while j < len(self.lines):
                if self.lines[i]['points'][-1] == self.lines[j]['points'][0] and \
                        find_dict(self.points, self.lines[j]['points'][0])['cross'] is False:
                    print("i start, j end")
                    print(find_dict(self.points, self.lines[i]['points'][-1]))
                    print(self.lines[i]['points'])
                    print(self.lines[j]['points'])
                    self.lines[i]['points'] = self.lines[i]['points'][:-1] + self.lines[j]['points']
                    print(self.lines[i]['points'])
                    print(self.lines[j]['points'])
                    self.lines.remove(self.lines[j])
                    print()
                if self.lines[i]['points'][0] == self.lines[j]['points'][-1] and \
                        find_dict(self.points, self.lines[j]['points'][-1])['cross'] is False:
                    print("j start, i end")
                    print(find_dict(self.points, self.lines[i]['points'][0]))
                    print(self.lines[j]['points'])
                    print(self.lines[i]['points'])
                    self.lines[j]['points'] = self.lines[j]['points'][:-1] + self.lines[i]['points']
                    print(self.lines[j]['points'])
                    print(self.lines[i]['points'])
                    self.lines.remove(self.lines[i])
                    print()
                j += 1
            i += 1
        print(len(self.lines))'''

if __name__ == "__main__":
    new_map = RailLines(LINES_PATH, POINTS_PATH)
