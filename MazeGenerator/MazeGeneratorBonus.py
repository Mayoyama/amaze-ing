"""Maze Generation Bonus Module

This module provides the core engine for generating 2D grid mazes. It
encapsulates the algorithmic logic required to transition a solid
matrix of walls into an open maze layout using a modified variation of the
Sidewinder algorithm.
"""

import random
from MapData import MapData
from MazeGenerator.MazeGen import MazeGenBase


class MazeGeneratorBonus(MazeGenBase):
    """A child class of MazeGenBase to generate the bonus maze.

    It uses a different pattern_42 to create a "42" shape layout
    (where 0 represents a full wall).
    """

    _pattern_42 = [
        [0, 6, 10, 12, 0, 0, 0],     # Row 0: █ . . . █ █ █
        [0, 1, 0, 7, 10, 8, 0],      # Row 1: █ . █ . . . █
        [0, 0, 0, 5, 0, 0, 0],       # Row 2: █ █ █ . █ █ █
        [6, 12, 0, 5, 0, 2, 10],     # Row 3: . . █ . █ . .
        [1, 5, 0, 5, 0, 0, 0],       # Row 4: . . █ . █ █ █
    ]

    def __init__(self, data: MapData) -> None:
        """Initializes the maze configuration."""
        super().__init__(data, pattern_42=self._pattern_42)
        self.fixed_cells: set[tuple[int, int]] = self._embed_42_pattern("full")
        self.full_42_cells = self.fixed_cells

    def _validate_point(self) -> None:
        """Validates entry/exit against solid-wall cells only, matching
        DFS behaviour where traversable '42' pattern cells are permitted.
        """
        for name, cell in [("ENTRY", self.start_point),
                           ("EXIT", self.end_point)]:
            r, c = cell
            x, y = self._convert_rc_to_xy(r, c)
            if cell in self.full_42_cells:
                raise ValueError(f"{name}: ({x}, {y}) collides with "
                                 "'42' pattern.")

    def gen_map(self) -> list[list[int]]:
        """Generates the full maze layout."""
        random.seed(self.seed)
        self.fixed_cells = self._embed_42_pattern("all")
        self._validate_point()

        for row in range(self.height):
            for col in range(self.width):
                if (row, col) in self.fixed_cells:
                    rnd = self._pattern_42[row][col]
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
                        rnd = random.choice([2, 4])

                if rnd != 0:
                    self.grid[row][col] &= ~rnd
                self._check_neighbors(row, col)

        if not self._perfect_map:
            self._non_perfect()
            for row in range(self.height):
                for col in range(self.width):
                    self._check_neighbors(row, col)
            self._ensure_alt_path()

        self._remove_excessive_rooms()

        return self.grid
