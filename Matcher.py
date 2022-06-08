from constants import GPS_POINTS_PATH, POINTS_PATH, LINES_PATH
from RailMap import RailLines
from GPSPoints import GPSPoints
from numpy.linalg import norm
import numpy as np
import matplotlib.pyplot as plt
from skspatial.objects import Line
from skspatial.objects import Point
"""перевести в геоцентрические координаты (pymap3d.ecef)"""


class Matcher:
    def __init__(self,path_to_lines=LINES_PATH, path_to_points=POINTS_PATH, gps_points_path=GPS_POINTS_PATH):
        rail_lines = RailLines(path_to_lines=path_to_lines, path_to_points=path_to_points)
        gps_points = GPSPoints(gps_points_path=gps_points_path)
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
        #print(px, " - X", py, " - Y")
        return {"coords":[px, py]}

    @staticmethod
    def orthoProjection_v2(points):
        #print(points)
        if points != {}:
            point = points["gps_point"]
        else:
            return {}
        line = Line(point=points["line_p1"], direction=points["line_p2"])
        point_projected = line.project_point(point)
        return {"coords": np.array(point_projected)}

    def print_data(self):
        print(self.lines)
        print(self.points)

    @staticmethod
    def points_sub(p1, p2):
        return p2-p1

    def find_min_dist_among_every_line(self, gps_point):
        points = {}
        #points = {"gps_point" : gps_point["coords"], "line_p1" : [59.62584952,28.54439231], "line_p2" : [59.62592992,28.54392169]}
        for i in range(len(self.lines)):
            min_dist = 1000
            for j in range(len(self.lines[i]["points"]) - 1):
                line_points = [self.find_dict(self.lines[i]["points"][j]), self.find_dict(self.lines[i]["points"][j+1])]
                #print(line_points)
                cur_dist = self.find_min_dist_v2(np.array(gps_point["coords"]), line_points)
                print(cur_dist)
                #print(cur_dist, ' - dist')
                if cur_dist < min_dist and cur_dist > 0:
                    #print(cur_dist, " - current dist")
                    min_dist = cur_dist
                    #print(min_dist, " - min dist")
                    points = {"gps_point" : gps_point["coords"], "line_p1" : line_points[0], "line_p2" : line_points[1]}
                    #print(points)

        return points

    def find_dict(self, point_id):
        found_dict = next(item for item in self.points if item["id"] == point_id)
        return found_dict["coords"]

    @staticmethod
    def find_min_dist(gps_point, line_points):
        P2 = line_points[0]
        P1 = line_points[1]

        dist = abs(norm(np.cross(P2 - P1, np.array(gps_point) - P1)))/norm(P2 - P1)
        return dist

    def find_min_dist_v2(self, gps_point, line_points):
        point = self.orthoProjection_v2({"gps_point" : gps_point, "line_p1" : line_points[0], "line_p2" : line_points[1]})
        ortho_point = point['coords']
        if min(line_points[0][0],line_points[1][0]) < ortho_point[0] < max(line_points[0][0],line_points[1][0]):
            if min(line_points[0][1], line_points[1][1]) < ortho_point[1] < max(line_points[0][1], line_points[1][1]):
                return np.linalg.norm(gps_point - ortho_point)
            else:
                return -1
        else:
            return -1

    def draw_full_map(self, new_points):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        RailLines.draw_lines(self.lines,self.points, ax)
        RailLines.draw_points(self.gps_points, ax,"red")
        RailLines.draw_points(new_points, ax,'blue')
        plt.savefig("res_map_before.png")
        plt.show()

    def match(self):
        res_points = []
        for gps_point in self.gps_points:
            #print(gps_point, " - gps_point")
            points = self.find_min_dist_among_every_line(gps_point)
            #print(points)
            res_point = self.orthoProjection_v2(points)
            if self.orthoProjection_v2(points) != {}:
                res_points.append(res_point)
        self.draw_full_map(res_points)



if __name__ == "__main__":
    matcher = Matcher()
    matcher.match()
