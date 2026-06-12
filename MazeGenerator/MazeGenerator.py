"""Maze Generation Module.

This module provides the core engine for generating 2D grid mazes. It
encapsulates the algorithmic logic required to transition a solid
matrix of walls into an open, perfect maze layout.
"""

import random
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
        [1, -1, -1, -1, 1, 1, 1],   # Row 0: █ . . . █ █ █
        [1, -1, 1, -1, -1, -1, 1],  # Row 1: █ . █ . . . █
        [1, 1, 1, -1, 1, 1, 1],     # Row 2: █ █ █ . █ █ █
        [-1, -1, 1, -1, 1, -1, -1], # Row 3: . . █ . █ . .
        [-1, -1, 1, -1, 1, 1, 1],   # Row 4: . . █ . █ █ █
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
        self.bonus = data.bonus
        self.fixed_cells: set[tuple[int, int]] = self._embed_42_pattern()

    @staticmethod
    def _convert_rc_to_xy(r: int, c: int) -> tuple[int, int]:
        return (c + 1, r + 1)

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
        return self.height >= 6 and self.width >= 8

    def _embed_42_pattern(self) -> set[tuple[int, int]]:
        """Returns set[tuple[int, int]] to embed '4 2' correctly on the map"""
        fixed_42_cells: set[tuple[int, int]] = set()

        if not self._can_fit_42():
            return fixed_42_cells

        start_row = 0
        start_col = 0

        for r in range(5):
            for c in range(7):
                if self.pattern_42[r][c] == 1:
                    fixed_42_cells.add((start_row + r, start_col + c))

        return fixed_42_cells

    def _validate_point(self) -> None:
        for name, cell in [("ENTRY", self.start_point),
                           ("EXIT", self.end_point)]:
            r, c = cell
            x, y = self._convert_rc_to_xy(r, c)
            if not (0 <= r < self.height and 0 <= c < self.width):
                raise ValueError(f"{name}: ({x}, {y}) is out of bounds.")
            if cell in self.fixed_cells:
                raise ValueError(f"{name}: ({x}, {y}) collides with "
                                 "'42' pattern.")

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
            protected_cells: set[tuple[int, int]] = set()

            if self._can_fit_42():
                logo_42_start_row = 0
                logo_42_start_col = 0

                for r in range(5):
                    for c in range(7):
                        ft_grid_r = logo_42_start_row + r
                        ft_grid_c = logo_42_start_col + c

                        protected_cells.add((ft_grid_r, ft_grid_c))

                        if ft_grid_r == logo_42_start_row:
                            protected_cells.add((ft_grid_r - 1, ft_grid_c))

                        if ft_grid_r == logo_42_start_row + 4:
                            protected_cells.add((ft_grid_r + 1, ft_grid_c))

                        if ft_grid_c == logo_42_start_col:
                            protected_cells.add((ft_grid_r, ft_grid_c - 1))

                        if ft_grid_c == logo_42_start_col + 6:
                            protected_cells.add((ft_grid_r, ft_grid_c + 1))

            nbr_break = random.randint(5, 15)
            for _ in range(nbr_break):
                random_row = random.randint(1, self.height - 2)
                random_col = random.randint(1, self.width - 2)
                if (random_row, random_col) not in protected_cells:
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
            logo_42_start_row = (self.height - 5) // 2
            logo_42_start_col = (self.width - 7) // 2
            start_cell = (logo_42_start_row + 2, logo_42_start_col + 1)
        else:
            start_cell = (self.height - 1, 0)

        stack: list[tuple[int, int]] = [start_cell]
        visited: set[tuple[int, int]] = {start_cell} | self.fixed_cells

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
