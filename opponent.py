from copy import deepcopy

class Node:
    def __init__(self, data):
        self.data = data
        self.children = []
        self.parent = None
    
    def add_child(self, child_node):
        child_node.parent = self
        self.children.append(child_node)
    
    def get_level(self):
        level = 0
        parent = self.parent
        while parent:
            level += 1
            parent = parent.parent
        return level

    def print_tree(self, max_level=10000):
        if self.get_level() > max_level:
            return
        print(f"{self.get_level()*'   ' + '|__'}{self.data}")
        for child in self.children:
            child.print_tree(max_level)
    
    def __repr__(self):
        return str(self.data)
    
class Tree:
    def __init__(self, board, depth=3):
        self.root = Node({(0,0,0,0):board.evaluate_position(board.turn)})
        self.board = board
        self.depth = depth
        self.construct_tree()
    
    def construct_tree(self, node=None, depth=None, board=None):
        if node is None:
            node = self.root
            depth = 1
            board = self.board
        if depth < self.depth:
            depth += 1
            all_valid_moves = deepcopy(board).get_all_valid_moves()
            for move in all_valid_moves:
                test_board = deepcopy(board)
                test_board.move(*move)
                new_node = Node({move:test_board.evaluate_position(test_board.turn)})
                test_board.change_turns()
                self.construct_tree(new_node, depth, test_board)
                node.add_child(new_node)
    
    def pick_best_move(self, node=None):
        if node is None:
            node = self.root
        for child in node.children:
            if child.children:
                self.pick_best_move(child)
            else:
                try:
                    node.data[list(node.data.keys())[0]] = -(max(list(child.data.values())[0] for child in node.children))
                    break
                except AttributeError:
                    self.root.print_tree(1)
                    print(node.data)
                    print(child.children)
                    quit()

class Opponent:
    def __init__(self, depth=3):
        self.depth = depth
    
    def make_move(self, board):
        tree = Tree(board, depth=self.depth)
        tree.pick_best_move()
        move = list(max([child.data for child in tree.root.children], key=lambda x: max(x.values())).keys())[0]
        board.move(*move)
