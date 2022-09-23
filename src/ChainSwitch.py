import utils.utils as utils
from src.PolyLine import PolyLine
from src.PointClass import Point
from typing import List, Dict, Tuple, Set


class ChainSwitch:
    def __init__(self, **kwargs):
        self.lines = kwargs["lines"]
        self.end_r = kwargs["end_r"]

    def get_next_poly_lines_for_graph(
        self, start_line: PolyLine, **kwargs
    ) -> List[PolyLine]:
        last_segment = (
            start_line.points_dict_list[2:][::-1]
            if kwargs["direction"] == "start"
            else start_line.points_dict_list[-2:]
        )
        next_poly_lines = utils.find_next_poly_lines_on_switch(
            self.lines, last_segment, **kwargs
        )
        return next_poly_lines

    def create_graph_on_switch_chain(
        self,
        start_line: PolyLine,
        next_poly_lines: List[PolyLine],
        graph: Dict,
        **kwargs
    ) -> Dict:
        if graph is None:
            graph = {}
        if next_poly_lines and start_line not in graph:
            graph[start_line] = next_poly_lines
        else:
            graph[start_line] = start_line
        for poly_line in next_poly_lines:
            if utils.is_in_decision_area(poly_line, self.end_r) and all(
                point["end"] for point in poly_line.points_dict_list
            ):
                child = self.get_next_poly_lines_for_graph(poly_line, **kwargs)
                if child:
                    graph[poly_line] = child
        return graph

    @staticmethod
    def delete_visited_nodes(
        paths: List[List[Dict]], true_sub_path: List[Dict]
    ) -> None:
        i = 0
        while i < len(paths) and len(paths) > 2:
            if true_sub_path[0]["id"] in paths[i]:
                paths[i] = paths[i][paths[i].index(true_sub_path[0]["id"]) + 1 :]
            else:
                paths.remove(paths[i])
                i -= 1
            i += 1
        print(paths, " paths after deleting all unnecessary paths")

    def find_path(
        self, graph: Dict, start: PolyLine, end: PolyLine, path=None
    ) -> List[PolyLine]:
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
    def dfs(graph: Dict) -> Set:
        leaves = set()
        leaves.update(*graph.values())
        leaves -= graph.keys()
        return leaves

    @staticmethod
    def print_graph(graph: Dict) -> None:
        for keys, values in graph.items():
            print("___________")
            print(keys.id_list, end=" ---> ")
            try:
                print(values[0].id_list, end=" | ")
                print(values[1].id_list)
            except Exception as e:
                print(values)
            print("___________")

    @staticmethod
    def print_path(path: List[PolyLine]) -> None:
        for poly_line in path:
            print(poly_line.id_list, end=" --> ")
        print("End")
