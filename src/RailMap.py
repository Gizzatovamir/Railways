import utils.utils
from utils.utils import get_json, find_dict
from utils.constants import POINTS_PATH, LINES_PATH
from src.BasicMap import BasicMap


class RailLines(BasicMap):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "instance"):
            cls._instance = super(RailLines, cls).__new__(cls)
        return cls._instance

    def __init__(self, path_to_lines, path_to_points):
        old_lines = get_json(path_to_lines)
        old_points = get_json(path_to_points)
        self.lines = self.line_transform(old_lines)
        self.points = self.point_transform(old_points, self.lines)
        self.find_all_cross()
        self.merge_lines()

    def find_all_cross(self) -> None:
        for i in range(len(self.points)):
            count = 0
            end_count = 0
            for j in range(len(self.lines)):
                if self.points[i]["id"] in self.lines[j]["points"]:
                    count += 1
                if (
                    self.points[i]["id"] == self.lines[j]["points"][0]
                    or self.points[i]["id"] == self.lines[j]["points"][-1]
                ):
                    end_count += 1
            if count > 2:
                self.points[i]["cross"] = True
            else:
                self.points[i]["cross"] = False
            if end_count == 1:
                self.points[i]["end"] = True
            else:
                self.points[i]["end"] = False
            if self.points[i]["id"] == 271:
                self.points[i]["cross"] = True
                self.points[i]["end"] = True

    def print_lines(self) -> None:
        print(self.lines)

    def merge_lines(self) -> None:
        i = 0
        while i < len(self.lines):
            j = 0
            while j < len(self.lines):
                if self.lines[i]["points"][-1] == self.lines[j]["points"][0]:
                    if not utils.utils.find_dict(
                        self.points, self.lines[i]["points"][-1]
                    )["cross"]:
                        self.lines[i]["points"] = (
                            self.lines[i]["points"] + self.lines[j]["points"][1:]
                        )
                        self.lines.remove(self.lines[j])
                        j -= 1
                if self.lines[j]["points"][-1] == self.lines[i]["points"][0]:
                    if not utils.utils.find_dict(
                        self.points, self.lines[j]["points"][-1]
                    )["cross"]:
                        self.lines[j]["points"] = (
                            self.lines[j]["points"] + self.lines[i]["points"][1:]
                        )
                        self.lines.remove(self.lines[i])
                j += 1
            i += 1


if __name__ == "__main__":
    new_map = RailLines(LINES_PATH, POINTS_PATH)
