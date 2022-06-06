from constants import GPS_POINTS_PATH, POINTS_PATH, LINES_PATH
from RailMap import RailLines
from GPSPoints import GPSPoints
from numpy.linalg import norm
import numpy as np
import matplotlib.pyplot as plt


class Matcher:
    def __init__(self):
        rail_lines = RailLines(path_to_lines=LINES_PATH, path_to_points=POINTS_PATH)
        gps_points = GPSPoints(gps_points_path=GPS_POINTS_PATH)
        self.lines = rail_lines.lines
        self.points = rail_lines.points
        self.gps_points = gps_points.points

    @staticmethod
    def orthoProjection(points):
        '''print(points["gps_point"], " - gps")
        print(points["line_p1"], " - 1")
        print(points["line_p2"], " - 2")'''
        ax, ay = points["gps_point"]
        bx, by = points["line_p1"]
        cx, cy = points["line_p2"]
        abx = bx - ax
        aby = by - ay
        acx = cx - ax
        acy = cy - ay
        t = (abx * acx + aby * acy) / (abx * abx + aby * aby)
        px = ax + t * abx
        py = ay + t * aby
        return {"coords":[px, py]}

    def print_data(self):
        print(self.lines)
        print(self.points)

    @staticmethod
    def points_sub(p1, p2):
        return p2-p1

    def find_min_dist_among_every_line(self, gps_point):
        min_dist = 0
        points = {}
        for i in range(len(self.lines)):
            for j in range(len(self.lines[i]["points"]) - 1):
                line_points = [self.lines[i]["points"][j], self.lines[i]["points"][j+1]]
                cur_dist = self.find_min_dist(gps_point["coords"], line_points)
                #print(cur_dist, ' - dist')
                if cur_dist > min_dist:
                    min_dist = cur_dist
                    points = {"gps_point" : gps_point["coords"], "line_p1" : self.find_dict(line_points[0]), "line_p2" : self.find_dict(line_points[1])}
        return points

    def find_dict(self, point_id):
        found_dict = next(item for item in self.points if item["id"] == point_id)
        return found_dict["coords"]

    def find_min_dist(self, gps_point, line_point):
        P2 = np.array(self.find_dict(line_point[1]))
        P1 = np.array(self.find_dict(line_point[0]))

        dist = abs(norm(np.cross(P2 - P1, np.array(gps_point) - P1)))/norm(P2 - P1)
        return dist

    def draw_full_map(self, new_points):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        RailLines.draw_lines(self.lines,self.points, ax)
        RailLines.draw_points(self.gps_points, ax,"red")
        RailLines.draw_points(new_points, ax,'blue')
        plt.show()

    def match(self):
        res_points = []
        for gps_point in self.gps_points:
            #print(gps_point, " - gps_point")
            points = self.find_min_dist_among_every_line(gps_point)
            print(points)
            res_points.append(self.orthoProjection(points))
        self.draw_full_map(res_points)



if __name__ == "__main__":
    matcher = Matcher()
    matcher.match()