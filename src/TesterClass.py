from utils.constants import LINES_PATH, POINTS_PATH, GPS_POINTS_PATH
from itertools import zip_longest
from src.SwitchClass import SwitchClass

R_CROSS = 30


class Tester:
    def __init__(self, args):
        self.switches = args["switches"]
        self.constants = args["constants"]
        self.find_path_class = args["switch_class"]
        self.find_path_class.change_config(method=0, mode="whole")
        self.coincidence_counter = 0
        self.result = []

    def test_switches(self) -> tuple:
        for switch in self.switches:
            cur_line = self.find_path_class.find_cur_line(
                switch["points"],
                switch["segments"],
                constants=self.constants,
                line_point=switch["line_point"],
            )
            if cur_line == switch["line"]:
                self.result.append(
                    "Matching on switch {} is successful".format(switch["id"])
                )
                self.coincidence_counter += 1
            else:
                self.result.append(
                    "Matching on switch {} is unsuccessful".format(switch["id"])
                )
        print(
            "total successful matches is {} out of {}".format(
                self.coincidence_counter, len(self.switches)
            )
        )
        return self.coincidence_counter, len(self.switches), self.result
