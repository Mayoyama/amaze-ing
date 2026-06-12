"""Maze Generation Module.

This module provides the core engine for generating 2D grid mazes. It encapsulates the algorithmic logic required to transition a solid
matrix of walls into an open, perfect maze layout.
"""

import random
from dataclasses import dataclass


class MazeGeneratorBonus:
    """An algorithmic engine responsible for carving perfect 2D grid mazes.

    Attributes:
        width (int): Total column count of the maze grid.
        height (int): Total row count of the maze grid.
        seed (int): The numeric seed value used to initialize the pseudo-random 
            number generator, ensuring deterministic and reproducible maze layouts.
        grid (list): The internal 2D list matrix representing the maze layout.
        pattern_42 (matrix): The template for the '42' pattern that must appear in the middle of the generated map.
    """
    # Row 0: █ . . . █ █ █
    # Row 1: █ . █ . . . █
    # Row 2: █ █ █ . █ █ █
    # Row 3: . . █ . █ . .
    # Row 4: . . █ . █ █ █
    pattern_42 = [
        [0, 6, 10, 12, 0, 0, 0],     # Row 0: █ . . . █ █ █
        [0, 1, 0, 7, 10, 8, 0],      # Row 1: █ . █ . . . █
        [0, 0, 0, 5, 0, 0, 0],       # Row 2: █ █ █ . █ █ █
        [6, 12, 0, 5, 0, 2, 10],     # Row 3: . . █ . █ . .
        [1, 5, 0, 5, 0, 0, 0],       # Row 4: . . █ . █ █ █
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
        self.fixed_cells = self._embed_42_pattern("all")
        self.full_42_celles = self._embed_42_pattern("full")


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

    def _embed_42_pattern(self, type: str) -> set[tuple[int, int]]:
        """Returns set[tuple[int, int]] to embed '4 2' correctly on the map"""
        fixed_42_cells: set[tuple[int, int]] = set()

        if self._can_fit_42():
            ft_start_row = 0
            ft_start_col = 0
            for r in range(5):
                    for c in range(7):
                        if type == "all":
                            if self.pattern_42[r][c] >= 0:
                                fixed_42_cells.add((ft_start_row + r, ft_start_col + c))
                        elif type == "full":
                            if self.pattern_42[r][c] == 0:
                                fixed_42_cells.add((ft_start_row + r, ft_start_col + c))

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

    def gen_map(self) -> list[list[int]]:
        """Generates the full maze layout, embedding the 42 pattern first."""
        random.seed(self.seed)
        self._validate_point()

        for row in range(self.height):
            for col in range(self.width):
                if (row, col) in self.fixed_cells:
                    rnd = self.pattern_42[row][col]
                else:
                    is_last_row = (row == self.height - 1)
                    is_last_col = (col == self.width - 1)
    
                    if is_last_row and is_last_col:
                        rnd = 0
                    elif is_last_row:
                        rnd = 2
                    elif is_last_col:
                        rnd = 4
                    else:
                        rnd: int = random.choice([2, 4])

                if rnd != 0:
                    self.grid[row][col] &= ~rnd
                self.check_neighbors(row, col)

        if not self.perfect_map:
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
                
        return self.grid