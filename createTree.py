import binarytree as bt
from stateMachineMatcher import StateMachineMatcher
from utils import find_min_by_x, find_min_by_y, find_max_by_x, find_max_by_y


class Node:
    def __init__(self, data):
        self.left = None
        self.right = None
        self.data = data

    # Insert Node
    def insert(self, data):
        print(data)
        if self.data.x:
            print(data.x)
            if data.x < self.data.x:
                if self.left is None:
                    self.left = Node(data)
                else:
                    self.left.insert(data)
            elif data.x == self.data.x:
                if data.y < self.data.y:
                    if self.left is None:
                        self.left = Node(data)
                    else:
                        self.left.insert(data)
            elif data.x > self.data.x:
                if self.right is None:
                    self.right = Node(data)
                else:
                    self.right.insert(data)
            else:
                self.data = data

    # Print the Tree
    def PrintTree(self):
        if self.left:
            self.left.PrintTree()
        print(self.data)
        if self.right:
            self.right.PrintTree()

    # Preorder traversal
    # Root -> Left ->Right
    def PreorderTraversal(self, root):
        res = []
        if root:
            res.append(root.data)
            res = res + self.PreorderTraversal(root.left)
            res = res + self.PreorderTraversal(root.right)
        return res

    def __copy__(self):
        return self


if __name__ == "__main__":
    matcher = StateMachineMatcher()
    root = matcher.find_initial_state(matcher.gps_points[0])
    print(root['cur_line'])
    map_tree = Node(find_min_by_x(root['cur_line']))
    tree_root = map_tree.__copy__()
    map_tree.insert(find_max_by_x(root['cur_line']))
    map_tree.PrintTree()
    print(tree_root.PrintTree())
