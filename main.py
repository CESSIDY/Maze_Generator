import copy
import random
import time

import numpy as np


class Maze:
    def __init__(self):
        self.characters = {'wall': "#",
                           'start': " ",
                           'end': " ",
                           'path': ".",
                           }
        self.paths = list()
        self.walls = list()

        self.empty_maze = self.get_empty_maze()

        self.start_position = None
        self.end_position = None

        self.make_start_end_positions()
        self.pathfinders = None

    def get_empty_maze(self):
        maze = np.zeros((13, 17), 'U1')
        maze.fill(self.characters.get('wall'))
        col, row = maze.shape
        for i in range(col):
            for j in range(row):
                if (not i or not j) or (i == col - 1 or j == row - 1):
                    maze[i][j] = self.characters.get('wall')
                    self.walls.append([i, j])
        return maze

    def make_start_end_positions(self):
        self.start_position = self.get_random_position('top')
        self.end_position = self.get_random_position('bottom')

        self.empty_maze[self.start_position[0]][self.start_position[1]] = self.characters.get('start')
        self.empty_maze[self.end_position[0]][self.end_position[1]] = self.characters.get('end')

    def get_random_position(self, side):
        maze_col, maze_row = self.empty_maze.shape
        row = np.random.randint(1, maze_row - 1)
        if side == 'top':
            col = 0
        else:
            col = maze_col - 1
        return col, row

    def save_path(self, position):
        if (position != self.start_position) or (position != self.end_position):
            self.empty_maze[position[0]][position[1]] = self.characters.get('path')
            self.paths.append(list(position))

    def save_walls(self, positions):
        for position_col, position_row in positions:
            if [position_col, position_row] not in self.paths:
                self.empty_maze[position_col][position_row] = self.characters.get('wall')
                self.walls.append([position_col, position_row])

    def is_no_empty_square(self, position):
        left_top = [[position[0] - 1, position[1]],
                    [position[0] - 1, position[1] - 1],
                    [position[0], position[1] - 1]]
        left_bottom = [[position[0] - 1, position[1]],
                       [position[0] - 1, position[1] + 1],
                       [position[0], position[1] + 1]]
        right_top = [[position[0] + 1, position[1]],
                     [position[0] + 1, position[1] - 1],
                     [position[0], position[1] - 1]]
        right_bottom = [[position[0] + 1, position[1]],
                        [position[0] + 1, position[1] + 1],
                        [position[0], position[1] + 1]]
        squares = [left_top, left_bottom, right_top, right_bottom]
        for square in squares:
            if len(list(
                    filter(lambda x: ([x[0], x[1]] in self.paths) or ([x[0], x[1]] in self.pathfinders), square))) >= 3:
                return False
        return True

    def is_no_cut_corners(self, position):
        left_top = [[position[0] - 1, position[1]],
                    [position[0] - 1, position[1] - 1],
                    [position[0], position[1] - 1]]
        left_bottom = [[position[0] - 1, position[1]],
                       [position[0] - 1, position[1] + 1],
                       [position[0], position[1] + 1]]
        right_top = [[position[0] + 1, position[1]],
                     [position[0] + 1, position[1] - 1],
                     [position[0], position[1] - 1]]
        right_bottom = [[position[0] + 1, position[1]],
                        [position[0] + 1, position[1] + 1],
                        [position[0], position[1] + 1]]

        def is_empty_empty_cell(cell_position):
            return (cell_position not in self.paths) and (cell_position not in self.walls)

        squares = [left_top, left_bottom, right_top, right_bottom]
        for square in squares:
            if (square[0] in self.walls or is_empty_empty_cell(square[0])) and (
                    square[2] in self.walls or is_empty_empty_cell(square[2])) and (
                    square[1] in self.paths):
                return False
        return True

    def is_no_lonely_walls(self, position):
        left = [[position[0] + 1, position[1] - 1],
                [position[0], position[1] - 2],
                [position[0] - 1, position[1] - 1],
                [position[0], position[1] - 1]]
        top = [[position[0] - 1, position[1] - 1],
               [position[0] - 2, position[1]],
               [position[0] - 1, position[1] + 1],
               [position[0] - 1, position[1]]]
        right = [[position[0] - 1, position[1] + 1],
                 [position[0], position[1] + 2],
                 [position[0] - 1, position[1] + 1],
                 [position[0] - 1, position[1]]]
        bottom = [[position[0] + 1, position[1] + 1],
                  [position[0] + 2, position[1]],
                  [position[0] + 1, position[1] - 1],
                  [position[0] + 1, position[1]]]

        areas = [left, top, right, bottom]

        for area in areas:
            if (area[-1] in self.walls) and (
                    area[0] in self.paths) and (
                    area[1] in self.paths) and (
                    area[2] in self.paths):
                return False

        return True

    def get_pathfinders_in_one_position(self):
        pathfinders_groups = dict()
        pathfinders_positions = set()
        pathfinders_changed_formats = list(map(lambda path_finder: (path_finder[0], path_finder[1]), self.pathfinders))
        pathfinders_positions.update(pathfinders_changed_formats)
        for position in pathfinders_positions:
            temp_pathfinders = list()
            for pathfinder in self.pathfinders:
                if list(pathfinder) == list(position):
                    temp_pathfinders.append(pathfinder)
            pathfinders_groups[position] = temp_pathfinders
        return pathfinders_groups

    def make_move(self):
        maze_col, maze_row = self.empty_maze.shape
        new_pathfinders = list()
        path_finders_groups = self.get_pathfinders_in_one_position()
        for (key_col, key_row), path_finders_group in path_finders_groups.items():
            left_move = [key_col, key_row - 1]
            top_move = [key_col - 1, key_row]
            right_move = [key_col, key_row + 1]
            bottom_move = [key_col + 1, key_row]

            possible_move_list = list()

            if (0 <= left_move[1] < maze_row) and (left_move not in self.paths) and (left_move not in self.walls):
                possible_move_list.append(left_move)
            if (0 <= top_move[0] < maze_col) and (top_move not in self.paths) and (top_move not in self.walls):
                possible_move_list.append(top_move)
            if (0 <= right_move[1] < maze_row) and (right_move not in self.paths) and (right_move not in self.walls):
                possible_move_list.append(right_move)
            if (0 <= bottom_move[0] < maze_col) and (bottom_move not in self.paths) and (bottom_move not in self.walls):
                possible_move_list.append(bottom_move)

            allowed_paths = list()
            for move in possible_move_list:
                if self.is_no_empty_square(move) and self.is_no_cut_corners(move) and self.is_no_lonely_walls(move):
                    allowed_paths.append(move)

            if not allowed_paths:
                for pathfinder in self.pathfinders:
                    if pathfinder == [key_col, key_row]:
                        self.pathfinders.remove(pathfinder)
                continue

            for key, (pf_col, pf_row) in enumerate(path_finders_group):
                if (not allowed_paths) or key > 1:
                    for pathfinder in self.pathfinders:
                        if pathfinder == [key_col, key_row]:
                            self.pathfinders.remove(pathfinder)
                    break

                path = random.choice(allowed_paths)
                # allowed_paths.remove(path)
                try:
                    possible_move_list.remove(path)
                except ValueError:
                    pass

                for temp_key, tempt_pf in enumerate(self.pathfinders):
                    if tempt_pf == [pf_col, pf_row]:
                        self.pathfinders[temp_key] = path
                        new_pathfinders.append(path)
                        self.save_path(path)
                        break
            self.save_walls(possible_move_list)

        self.pathfinders += new_pathfinders

    def generate_my_algorithm(self):
        self.empty_maze = self.get_empty_maze()
        self.make_start_end_positions()
        self.pathfinders = [list(self.start_position), list(self.end_position)]
        while True:
            self.make_move()
            if len(self.pathfinders) == 0:
                break
        return self.empty_maze

    def generate_binary_tree_algorithm(self):
        self.empty_maze = self.get_empty_maze()
        self.make_start_end_positions()
        for row_key, row in enumerate(range(self.empty_maze.shape[0])):
            if (0 < row_key < self.empty_maze.shape[0] - 1) and (row_key % 2 != 0):
                for key, i in enumerate(range(self.empty_maze.shape[1])):
                    allowed_path = list()
                    if (0 < key < self.empty_maze.shape[1] - 1) and (key % 2 != 0):
                        if (key > 5) and (row - 1 != 0):
                            wall_count = 0
                            for temp_key, temp_row in enumerate(range(i - 6, key - 1)):
                                if self.empty_maze[row - 1][temp_row] == self.characters.get('wall'):
                                    wall_count += 1
                            if wall_count >= 5:
                                position_list = list()
                                for r in range(key - 6, key - 1):
                                    if r % 2 != 0:
                                        position_list.append(r)
                                self.empty_maze[row - 1][random.choice(position_list)] = self.characters.get('path')
                        if row - 1 > 0:
                            allowed_path.append([row - 1, i])
                        if i + 1 < self.empty_maze.shape[1] - 1:
                            allowed_path.append([row, i + 1])
                        else:
                            allowed_path.append([row, i - 1])
                        self.empty_maze[row][i] = self.characters.get('path')
                        if len(allowed_path):
                            path = random.choice(allowed_path)
                            self.empty_maze[path[0]][path[1]] = self.characters.get('path')

        self.empty_maze[self.start_position[0] + 1][self.start_position[1]] = self.characters.get('path')
        self.empty_maze[self.end_position[0] - 1][self.end_position[1]] = self.characters.get('path')
        return self.empty_maze


maze_generator = Maze()
binary_maze = maze_generator.generate_binary_tree_algorithm()
my_maze = maze_generator.generate_my_algorithm()
# print(binary_maze)
print(my_maze)
# with open("maze.txt", "a") as file_object:
#     for row in maze:
#         file_object.write(''.join(row) + '\n')
