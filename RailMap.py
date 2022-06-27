from utils import get_json
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

    def print_lines(self) -> None:
        print(self.lines)


if __name__ == "__main__":
    new_map = RailLines(LINES_PATH, POINTS_PATH)
