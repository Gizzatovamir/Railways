from utils import get_json, find_dict
from constants import POINTS_PATH, LINES_PATH, GPS_POINTS_PATH
from basicMap import basicMap


class RailLines(basicMap):
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
            end_count = 0
            for j in range(len(self.lines)):
                if self.points[i]["id"] in self.lines[j]['points']:
                    count += 1
                if self.points[i]['id'] == self.lines[j]['points'][0] or self.points[i]['id'] == self.lines[j]['points'][-1]:
                    end_count += 1
            if count > 2:
                self.points[i]["cross"] = True
            else:
                self.points[i]["cross"] = False
            if end_count == 1:
                self.points[i]['end'] = True
            else:
                self.points[i]['end'] = False

    def print_lines(self) -> None:
        print(self.lines)

    def merge_lines(self) -> None:
        i = 0
        j, k = 0, 0
        print(len(self.lines))
        while i < len(self.lines):
            line_points = [find_dict(self.points, self.lines[i]['points'][x]) for x in range(len(self.lines[i]['points']))]
            if line_points[0]['cross'] is False:
                while j < len(self.lines):
                    if self.lines[j]['points'][-1] == line_points[0]['id']:
                        print(self.lines[j]['points'], ' j start')
                        print(self.lines[i]['points'], ' i end')
                        self.lines[j]['points'] = self.lines[j]['points'] + self.lines[i]['points'][1:]
                        print(self.lines[j]['points'])
                        self.lines.remove(self.lines[i])
                        print(self.lines[j]['points'])
                        i = 0
                        j = 0
                    if self.lines[j]['points'][0] == line_points[0]['id']:
                        print(self.lines[j]['points'], ' j start')
                        print(self.lines[i]['points'], ' i end')
                        self.lines[i]['points'] = self.lines[i]['points'][::-1]
                        self.lines[j]['points'] = self.lines[j]['points'] + self.lines[i]['points'][1:]
                        print(self.lines[j]['points'])
                        self.lines.remove(self.lines[i])
                        print(self.lines[j]['points'])
                        i = 0
                        j = 0
                    j+=1
            if line_points[-1]['cross'] is False:
                while k < len(self.lines):
                    if self.lines[k]['points'][0] == line_points[-1]['id']:
                        print(self.lines[i]['points'], ' i start')
                        print(self.lines[k]['points'], ' k end')
                        self.lines[i]['points'] = self.lines[i]['points'] + self.lines[k]['points'][1:]
                        print(self.lines[i]['points'])
                        self.lines.remove(self.lines[k])
                        print(self.lines[i]['points'])
                        k = 0
                        i = 0
                    if self.lines[k]['points'][-1] == line_points[-1]['id']:
                        print(self.lines[i]['points'], ' i start')
                        print(self.lines[k]['points'], ' k end')
                        self.lines[k]['points'] = self.lines[k]['points'][::-1]
                        self.lines[i]['points'] = self.lines[i]['points'] + self.lines[k]['points'][1:]
                        print(self.lines[i]['points'])
                        self.lines.remove(self.lines[k])
                        print(self.lines[i]['points'])
                        k = 0
                        i = 0
                    k+=1
            #print(i)
            i += 1
        print(len(self.lines))

if __name__ == "__main__":
    new_map = RailLines(LINES_PATH, POINTS_PATH)
