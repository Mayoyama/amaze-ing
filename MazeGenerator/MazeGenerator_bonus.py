"""Maze Generation Module.

This module provides the core engine for generating 2D grid mazes. It encapsulates the algorithmic logic required to transition a solid
matrix of walls into an open, perfect maze layout.
"""

import random
from dataclasses import dataclass


class MazeGenerator_bonus:
    """An algorithmic engine responsible for carving perfect 2D grid mazes.

    Attributes:
        width (int): Total column count of the maze grid.
        height (int): Total row count of the maze grid.
        seed (int): The numeric seed value used to initialize the pseudo-random 
            number generator, ensuring deterministic and reproducible maze layouts.
        grid (list): The internal 2D list matrix representing the maze layout.
        pattern_42 (matrix): The template for the '42' pattern that must appear in the middle of the generated map.
    """
    pattern_42 = [
        [1, 0, 0, 0, 1, 1, 1],  # Row 0: █ . . . █ █ █
        [1, 0, 1, 0, 0, 0, 1],  # Row 1: █ . █ . . . █
        [1, 1, 1, 0, 1, 1, 1],  # Row 2: █ █ █ . █ █ █
        [0, 0, 1, 0, 1, 0, 0],  # Row 3: . . █ . █ . .
        [0, 0, 1, 0, 1, 1, 1],  # Row 4: . . █ . █ █ █
    ]

    def __init__(self, data: dataclass) -> None:
        """Initializes the maze configuration and instantiates a solid wall grid."""
        self.width = data.width
        self.height = data.height
        self.seed = data.seed
        self.grid = self._initialize_empty_grid()
        self.start_point = data.entry
        self.end_point = data.exit
        self.perfect_map = data.perfect


    def _initialize_empty_grid(self) -> list[list[int]]:
        """creates and initializes the grid to be used in map generation."""
        grid: list[list[int]] = []

        for r in range(self.height):
            curr_row: list[int] = []
            for c in range(self.width):
                curr_row.append(15)
            grid.append(curr_row)
        return grid

    def _can_fit_42(self) -> bool:
        """Check if the maze dimensions are large enough to hold the '42' pattern."""
        if self.height < 6 or self.width < 8:
            return False
        return True

    def _embed_42_pattern(self) -> set[tuple[int, int]]:
        """Returns set[tuple[int, int]] to embed '4 2' correctly on the map"""
        fixed_42_cells: set[tuple[int, int]] = set()

        if self._can_fit_42():
            if self.height == 6 and self.width == 8:
                ft_start_row = 0
                ft_start_col = 0
            else: 
                ft_start_row = (self.height - 5) // 2
                ft_start_col = (self.width - 7) // 2
            for r in range(5):
                for c in range(7):
                    ft_grid_r = ft_start_row + r
                    ft_grid_c = ft_start_col + c

                    if self.pattern_42[r][c] == 1:
                        fixed_42_cells.add((ft_grid_r, ft_grid_c))
        return fixed_42_cells

    def _validate_point(self, fixed_cells: set[tuple[int, int]]) -> None:
       for name, cell in [("Start", self.start_point), ("End", self.end_point)]:
           r, c = cell
           if not (0 <= r < self.height and 0 <= c < self.width):
               raise ValueError(f"{name} point at {cell} is out of bounds. Please set a new coordinate.")
           if cell in fixed_cells:
               raise ValueError(f"{name} point at {cell} collides with '42' pattern. Please set a new coordinate.")
        

    #def _check_valid_neighbors(self, current: tuple[int, int], visited: set[tuple[int, int]], fixed_cells: set[tuple[int, int]]) -> list[tuple[int, int]]:
    #    """Returns a list of unvisited, non-fixed adjacent cells."""
    #    valid_neighbors = []
    #    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    #    r, c = current

    #    for dr, dc in directions:
    #        nextr, nextc = r + dr, c + dc
    #        if 0 <= nextr < self.height and 0 <= nextc < self.width:
    #            if (nextr, nextc) not in fixed_cells:
    #                if (nextr, nextc) not in visited:
    #                    valid_neighbors.append((nextr, nextc))
    #    return valid_neighbors
            
    #def _open_wall(self, current: tuple[int, int], next_cell: tuple[int, int],) -> None:
    #    """Removes the shared wall between the current cell and the next cell."""
    #    curr_r, curr_c = current
    #    next_r, next_c = next_cell

    #    direction_r = next_r - curr_r
    #    direction_c = next_c - curr_c
    #    if direction_r == -1:
    #        self.grid[curr_r][curr_c] &= ~1
    #        self.grid[next_r][next_c] &= ~4
    #    if direction_r == 1:
    #        self.grid[curr_r][curr_c] &= ~4
    #        self.grid[next_r][next_c] &= ~1
    #    if direction_c == -1:
    #        self.grid[curr_r][curr_c] &= ~8
    #        self.grid[next_r][next_c] &= ~2
    #    if direction_c == 1:
    #        self.grid[curr_r][curr_c] &= ~2
    #        self.grid[next_r][next_c] &= ~8

    #def _final_map_adjustment(self) -> None:
    #    if self.height < 3 or self.width < 3:
    #        return

    #    for scan_r in range(self.height - 2):
    #        for scan_c in range(self.width - 2):
    #            is_open_room = True
    #            for window_r in range(scan_r, scan_r + 3):
    #                for window_c in range(scan_c, scan_c + 3):
    #                    if self.grid[window_r][window_c] != 0:
    #                        is_open_room = False
    #                        break
    #                if not is_open_room:
    #                    break

    #            if is_open_room is True:
    #                self.grid[scan_r + 1][scan_c + 1] |= 1
    #                self.grid[scan_r][scan_c + 1] |= 4

    def check_neighbors(self, row: int, col: int) -> None:
        if col > 0:
           if self.grid[row][col-1] & 2 == 0:
              self.grid[row][col] &= ~8
        if row > 0:
            if self.grid[row-1][col] & 4 == 0:
                self.grid[row][col] &= ~1 

    def gen_map(self) -> list[list[int]]:
        """Generates the full maze layout, embedding the 42 pattern first."""
        random.seed(self.seed)
        fixed_cells = self._embed_42_pattern()

        self._validate_point(fixed_cells)
        
        if self._can_fit_42():
            if self.height == 6 and self.width == 8:
                ft_start_col = 0
                ft_start_row = 0
            else:
                ft_start_row = (self.height - 5) // 2
                ft_start_col = (self.width - 7) // 2
            
            ft_end_row = ft_start_row + 4
            ft_end_col = ft_start_col + 6
        else:
           ft_start_row = ft_end_row = ft_start_col = ft_end_col = -1

        
        for row in range(self.height):
            for col in range(self.width):
                if (row, col) in fixed_cells:
                    continue

                is_last_row = (row == self.height - 1)
                is_last_col = (col == self.width - 1)

                is_top_42 = (row == ft_start_row - 1) and (ft_start_col <= col <= ft_end_col)
                is_bottom_42 = (row == ft_end_row + 1) and (ft_start_col <= col <= ft_end_col)
                is_left_42 = (col == ft_start_col - 1) and (ft_start_row <= row <= ft_end_row - 3)
                is_right_42 = (col == ft_end_col + 1) and (ft_start_row <= row <= ft_end_row)
                is_middle_42 = (ft_start_row <= row <= ft_end_row) and (col == ft_start_col + 3)

                if is_middle_42:
                    rnd: int = 2 if is_last_row else 4
                elif is_top_42 and not is_last_col:
                    rnd: int = 1
                elif is_bottom_42:
                    rnd: int = 2 if is_last_row else 4
                elif is_left_42 and not is_last_col:
                    rnd: int = 2 if is_last_col else 4
                elif is_right_42:
                    rnd: int =  2 if is_last_col else 4
                elif is_last_row and is_last_col:
                    rnd: int = 0
                elif is_last_row:
                    rnd: int = 2
                elif is_last_col:
                    rnd: int = 4
                else:
                    rnd: int = random.choice([2, 4])
                
                if rnd != 0:
                    self.grid[row][col] &= ~rnd
                self.check_neighbors(row, col)
                
        return self.grid