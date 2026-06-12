"""Maze Generation Module.

This module provides the core engine for generating 2D grid mazes. It
encapsulates the algorithmic logic required to transition a solid
matrix of walls into an open maze layout using the Depth-First Search (DFS) algorithm.
"""

import random
from map_data import mapData
from MazeGenerator.MazeGen import MazeGenBase


class MazeGenerator(MazeGenBase):
    """A child class of MazeGenBase to generate the main maze using the DFS algorithm.

    It uses pattern_42 to create a "42" shape layout (where 1 represents a full wall, 
    and -1 represents an empty space).
    """
    pattern_42 = [
        [1, -1, -1, -1, 1, 1, 1],    # Row 0: █ . . . █ █ █
        [1, -1, 1, -1, -1, -1, 1],   # Row 1: █ . █ . . . █
        [1, 1, 1, -1, 1, 1, 1],      # Row 2: █ █ █ . █ █ █
        [-1, -1, 1, -1, 1, -1, -1],  # Row 3: . . █ . █ . .
        [-1, -1, 1, -1, 1, 1, 1],    # Row 4: . . █ . █ █ █
    ]

    def __init__(self, data: mapData) -> None:
        """Initializes maze config."""
        super().__init__(data, pattern_42=self.pattern_42)

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


    def _final_map_adjustment(self) -> None:
        """Performs final checks on the maze layout. 
        
        Ensures the '42' label is preserved and verifies that there are no accidental 
        3x3 empty areas, create a non-perfect map if it's requested.
        """
        def _verify_42() -> None:
            """Ensures that the '42' pattern cells are completely closed off as solid walls."""
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

        if self.height < 3 or self.width < 3:
            return


        _verify_42()

        if not self.perfect_map:
            self._non_perfect()
            _verify_42()
            for row in range(self.height):
                for col in range(self.width):
                    self._check_neighbors(row, col)
        
        self._remove_excessive_rooms()

    def gen_map(self) -> list[list[int]]:
        """Generates the full maze layout."""
        random.seed(self.seed)

        self._validate_point()

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
