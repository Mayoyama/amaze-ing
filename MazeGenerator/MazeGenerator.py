"""Maze Generation Module.

This module provides the core engine for generating 2D grid mazes. It
encapsulates the algorithmic logic required to transition a solid
matrix of walls into an open, perfect maze layout.
"""

import random
from dataclasses import dataclass
from map_data import mapData


class MazeGenerator:
    """An algorithmic engine responsible for carving perfect 2D grid mazes.

    Attributes:
        width (int): Total column count of the maze grid.
        height (int): Total row count of the maze grid.
        seed (int): Numeric seed value used to initialize the pseudo-random
            number generator, ensuring and reproducible maze layouts.
        grid (list): The internal 2D list matrix representing the maze layout.
        pattern_42 (matrix): The template for the '42' pattern that must
            appear in the middle of the generated map.
    """
    pattern_42 = [
        [1, 0, 0, 0, 1, 1, 1],  # Row 0: █ . . . █ █ █
        [1, 0, 1, 0, 0, 0, 1],  # Row 1: █ . █ . . . █
        [1, 1, 1, 0, 1, 1, 1],  # Row 2: █ █ █ . █ █ █
        [0, 0, 1, 0, 1, 0, 0],  # Row 3: . . █ . █ . .
        [0, 0, 1, 0, 1, 1, 1],  # Row 4: . . █ . █ █ █
    ]

    def __init__(self, data: mapData) -> None:
        """Initializes maze config and instantiates a solid wall grid."""
        self.width = data.width
        self.height = data.height
        self.seed = data.seed
        self.grid = self._initialize_empty_grid()
        self.start_point = data.entry
        self.end_point = data.exit
        self.perfect_map = data.perfect
        self.fixed_cells: set[tuple[int, int]] = self._embed_42_pattern(0)

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
        """Check if maze dimensions are large enough to hold '42' pattern."""
        if self.height < 6 or self.width < 8:
            return False
        return True

    def _embed_42_pattern(self, perfect: int) -> set[tuple[int, int]]:
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

                    if perfect == 0:
                        if self.pattern_42[r][c] == 1:
                            fixed_42_cells.add((ft_grid_r, ft_grid_c))
                    else:
                        if self.pattern_42[r][c] >= 0:
                            fixed_42_cells.add((ft_grid_r, ft_grid_c))
                            if ft_grid_r == 0:
                                fixed_42_cells.add((ft_grid_r - 1, ft_grid_c))
                            if ft_grid_r == 4:
                                fixed_42_cells.add((ft_grid_r + 1, ft_grid_c))
                            if ft_grid_c == 0:
                                fixed_42_cells.add((ft_grid_r, ft_grid_c - 1))
                            if ft_grid_c == 6:
                                fixed_42_cells.add((ft_grid_r, ft_grid_c + 1))
        return fixed_42_cells

    def _validate_point(self) -> None:
        for name, cell in [("Start", self.start_point),
                           ("End", self.end_point)]:
            r, c = cell
            if not (0 <= r < self.height
                    and 0 <= c < self.width):
                raise ValueError(f"{name} point at {cell} is out of "
                                 "bounds. Please set a new coordinate.")
            if cell in self.fixed_cells:
                raise ValueError(f"{name} point at {cell} collides with '42' "
                                 "pattern. Please set a new coordinate.")

    def _check_valid_neighbors(self, current: tuple[int, int],
                               visited: set[tuple[int,
                                                  int]]) -> list[tuple[int,
                                                                       int]]:
        """Returns a list of unvisited, non-fixed adjacent cells."""
        valid_neighbors = []
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        r, c = current

        for dr, dc in directions:
            nextr, nextc = r + dr, c + dc
            if 0 <= nextr < self.height and 0 <= nextc < self.width:
                if (nextr, nextc) not in self.fixed_cells:
                    if (nextr, nextc) not in visited:
                        valid_neighbors.append((nextr, nextc))
        return valid_neighbors

    def _open_wall(self, current: tuple[int, int],
                   next_cell: tuple[int, int],) -> None:
        """Removes shared wall between the current cell and the next cell."""
        curr_r, curr_c = current
        next_r, next_c = next_cell

        direction_r = next_r - curr_r
        direction_c = next_c - curr_c
        if direction_r == -1:
            self.grid[curr_r][curr_c] &= ~1
            self.grid[next_r][next_c] &= ~4
        if direction_r == 1:
            self.grid[curr_r][curr_c] &= ~4
            self.grid[next_r][next_c] &= ~1
        if direction_c == -1:
            self.grid[curr_r][curr_c] &= ~8
            self.grid[next_r][next_c] &= ~2
        if direction_c == 1:
            self.grid[curr_r][curr_c] &= ~2
            self.grid[next_r][next_c] &= ~8
    
    def check_neighbors(self, row: int, col: int) -> None:
        if (row, col) not in self.fixed_cells:
            if col >= 0:
                if self.grid[row][col-1] & 2 == 0:
                    self.grid[row][col] &= ~8
            if col + 1 < self.width:
                if self.grid[row][col+1] & 8 == 0:
                    self.grid[row][col] &= ~2
            if row >= 0:
                if self.grid[row-1][col] & 4 == 0:
                    self.grid[row][col] &= ~1
            if row + 1 < self.height:
                if self.grid[row+1][col] & 1 == 0:
                    self.grid[row][col] &= ~4

    def _final_map_adjustment(self) -> None:
        if self.height < 3 or self.width < 3:
            return

        for scan_r in range(self.height - 2):
            for scan_c in range(self.width - 2):
                is_open_room = True
                for window_r in range(scan_r, scan_r + 3):
                    for window_c in range(scan_c, scan_c + 3):
                        if self.grid[window_r][window_c] != 0:
                            is_open_room = False
                            break
                    if not is_open_room:
                        break

                if is_open_room is True:
                    self.grid[scan_r + 1][scan_c + 1] |= 1
                    self.grid[scan_r][scan_c + 1] |= 4

        for r, c in self.fixed_cells:
            if r > 0:
                self.grid[r - 1][c] |= 4
            if r < self.height - 1:
                self.grid[r + 1][c] |= 1
            if c > 0:
                self.grid[r][c - 1] |= 2
            if c < self.width - 1:
                self.grid[r][c + 1] |= 8
            self.grid[r][c] = 15
        
        if not self.perfect_map:
            self.fixed_cells = self._embed_42_pattern(1)
            nbr_break = random.randint(5, 15)
            for _ in range(nbr_break):
                random_row = random.randint(1, self.height - 2)
                random_col = random.randint(1, self.width - 2)
                if (random_row, random_col) not in self.fixed_cells:
                    rnd = 15
                    self.grid[random_row][random_col] &= ~rnd
            for row in range(self.height):
                for col in range(self.width):
                    self.check_neighbors(row, col)

    def gen_map(self) -> list[list[int]]:
        """Generates the full maze layout, embedding the 42 pattern first."""
        random.seed(self.seed)

        self._validate_point()

        if self._can_fit_42():
            ft_start_row = (self.height - 5) // 2
            ft_start_col = (self.width - 7) // 2
            start_cell = (ft_start_row + 2, ft_start_col + 1)
        else:
            start_cell = (self.height - 1, 0)

        stack: list[tuple[int, int]] = [start_cell]
        visited: set[tuple[int, int]] = {start_cell} | self.fixed_cells  # fixed_cells  Needed? Need to test!!

        while stack:
            current = stack[-1]
            valid_dests = self._check_valid_neighbors(current, visited)

            if valid_dests:
                next_cell = random.choice(valid_dests)
                self._open_wall(current, next_cell)
                visited.add(next_cell)
                stack.append(next_cell)
            else:
                stack.pop()

        self._final_map_adjustment()
        return self.grid
