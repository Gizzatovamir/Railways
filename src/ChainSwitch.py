import utils


class ChainSwitch:
    def switch_adding_condition(self, observed_segments: list, center: dict) -> bool:
        conditions = []
        for segment in observed_segments:
            print(center, "center of switch")
            print(segment[1], " end of segment")
            tmp_condition = (center["coords"] - segment[1]["coords"]).norm <= self.end_r
            conditions.append(tmp_condition)
        return any(conditions)

    @staticmethod
    def dfs(graph: dict) -> set:
        leaves = set()
        print(graph)
        leaves.update(*graph.values())
        leaves -= graph.keys()
        return leaves

    def find_path(self, graph: dict, start: int, end: int, path=None):
        if path is None:
            path = []
        path = path + [start]
        if start == end:
            return path
        if start not in graph:
            return None
        for node in graph[start]:
            if node not in path:
                new_path = self.find_path(graph, node, end, path)
                if new_path:
                    return new_path
        return None

    @staticmethod
    def get_paths_in_graph(paths: list) -> list:
        res = []
        for path in paths:
            if len(path) < 3:
                res.append(path)
            else:
                res.append(path[1:3])
        return res

    @staticmethod
    def delete_visited_nodes(paths: list, true_sub_path: list) -> None:
        i = 0
        while i < len(paths) and len(paths) > 2:
            if true_sub_path[0]["id"] in paths[i]:
                paths[i] = paths[i][paths[i].index(true_sub_path[0]["id"]) + 1 :]
            else:
                paths.remove(paths[i])
                i -= 1
            i += 1
        print(paths, " paths after deleting all unnecessary paths")

    def link_points_on_switch_chain(self, points: list, true_path: list) -> list:
        result = []
        for point in points:
            each_segment_dist = []
            for i in range(len(true_path) - 1):
                each_segment_dist.append(
                    [
                        utils.point_to_segment_distance(
                            point["coords"], true_path[i : i + 2]
                        ),
                        true_path[i : i + 2],
                    ]
                )
            min_dist_segment = min(each_segment_dist, key=lambda x: x[0]["dist"])[1]
            result.append(
                [
                    point,
                    utils.point_to_segment_projection(
                        point["coords"], min_dist_segment
                    ),
                ]
            )
        return result

    def get_result_on_chain_of_switches(
        self, i: int, line: list, ortho_point_dist: dict, condition: bool
    ) -> list:
        received_segments = self.get_segments_on_switch(
            i, line[1], ortho_point_dist, condition
        )
        points = []
        if received_segments["is_valid_switch"]:
            observed_segments = received_segments["segments"]
        else:
            return received_segments["res"]
        graph = {
            line[1]["id"]: [
                observed_segments[0][-1]["id"],
                observed_segments[1][-1]["id"],
            ]
        }

        while self.switch_adding_condition(observed_segments, observed_segments[0][0]):
            for segment_end in [segment[1] for segment in observed_segments]:
                next_segments = self.get_segments_on_switch(
                    i, segment_end, ortho_point_dist, condition
                )
                if next_segments["is_valid_switch"]:
                    observed_segments = next_segments["segments"]
                    print(
                        next_segments["segments"], " - next segments in graph creation"
                    )
                    graph[segment_end["id"]] = [
                        observed_segments[0][-1]["id"],
                        observed_segments[1][-1]["id"],
                    ]
        # print(graph)
        leaves = self.dfs(graph)
        paths = [self.find_path(graph, line[1]["id"], end_leaf) for end_leaf in leaves]
        true_path = [line[1]]
        while paths != [[]] and len(paths) > 2:
            lines = []
            sub_paths = self.get_paths_in_graph(paths)
            for path in sub_paths:
                lines.append([utils.find_dict(self.points, point) for point in path])
            cur_path = self.find_path_class.find_cur_line(
                [self.gps_points[i]],
                lines,
                constants=self.switch_information["constants"],
                line_point=line[1],
            )
            while any(
                [
                    (self.gps_points[i]["coords"] - segment[1]["coords"]).norm
                    <= self.end_r
                    for segment in lines
                ]
            ):
                points.append(self.gps_points[i])
                i += 1
            true_path.extend(cur_path)
            self.delete_visited_nodes(paths, cur_path)
            self.initial_dict["cur_line"] = cur_path
        print(true_path, " result path after algo")
        result = self.link_points_on_switch_chain(points, true_path)
        return [result, False, len(points)]

    def add_result_on_chain_of_switches(
        self, i: int, line: list, ortho_point_dist: dict, condition: bool
    ) -> list:
        if (line[1]["coords"] - line[0]["coords"]).norm <= self.end_r:
            print("STARTED CHAIN SWITCH")
            new_points, break_condition, step = self.get_result_on_chain_of_switches(
                i, line, ortho_point_dist, condition
            )
        else:
            new_points, break_condition, step = self.add_point_on_cross(
                i, line, ortho_point_dist, condition
            )
        return [new_points, break_condition, step]
