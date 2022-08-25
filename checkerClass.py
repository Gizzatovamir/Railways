from StateMatcher import StateMatcher
from constants import LINES_PATH, POINTS_PATH, GPS_POINTS_PATH
from itertools import zip_longest

R_CROSS = 30


class Checker:
    def __init__(self, switches: list, path_to_lines=LINES_PATH, path_to_points=POINTS_PATH,
                 gps_points_path=GPS_POINTS_PATH):
        self.res_switches = switches
        self.matcher = StateMatcher(3, path_to_lines, path_to_points, gps_points_path)
        self.matcher.match(R_CROSS)
        self.new_switches = self.matcher.switches
        self.coincidence_counter = 0

    def check_for_success_switch_choosing(self) -> None:
        for res_switch, new_switch in zip_longest(self.res_switches, self.new_switches):
            try:
                if all([x['id'] == y['id'] for x, y in zip_longest(res_switch['line'], new_switch['line'])]):
                    self.coincidence_counter += 1
                    print(*[x['id'] for x in res_switch['line']], " Result line on switch {}".format(res_switch['id']))
                    print(*[x['id'] for x in new_switch['line']], " Checker line on switch {}".format(new_switch['id']))
                    print("__________________________")
                else:
                    print("line with ids {} {} in result is not equal to the line with ids {} {} in checker".format(*[x['id'] for x in res_switch['line']], *[x['id'] for x in new_switch['line']]))
            except TypeError:
                pass

        print("{} out of {} is correct".format(self.coincidence_counter, len(self.new_switches)))