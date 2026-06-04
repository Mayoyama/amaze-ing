"""Maze Generation Module.

This module provides the core engine for generating 2D grid mazes. It encapsulates the algorithmic logic required to transition a solid
matrix of walls into an open, perfect maze layout.
"""

import random


class MazeGenerator:
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

    def __init__(self, width: int, height: int, seed: int) -> None:
        """Initializes the maze configuration and instantiates a solid wall grid."""
        self.width = width
        self.height = height
        self.seed = seed
        self.grid = self._initialize_empty_grid()


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


    def _check_valid_neighbors(self, current: tuple[int, int], visited: set[tuple[int, int]], fixed_cells: set[tuple[int, int]]) -> list[tuple[int, int]]:
        """Returns a list of unvisited, non-fixed adjacent cells."""
        valid_neighbors = []
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        r, c = current

        for dr, dc in directions:
            nextr, nextc = r + dr, c + dc
            if 0 <= nextr < self.height and 0 <= nextc < self.width:
                if (nextr, nextc) not in fixed_cells:
                    if (nextr, nextc) not in visited:
                        valid_neighbors.append((nextr, nextc))
        return valid_neighbors
            
    def _open_wall(self, current: tuple[int, int], next_cell: tuple[int, int],) -> None:
        """Removes the shared wall between the current cell and the next cell."""
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





    def gen_map(self) -> list[list[int]]:
        """Generates the full maze layout, embedding the 42 pattern first."""
        fixed_cells = self._embed_42_pattern()

        start_cell = (self.height - 1, 0)

        stack: list[tuple[int, int]] = [start_cell]
        visited: set[tuple[int, int]] = {start_cell}

        random.seed(self.seed)

        while stack:
            current = stack[-1]
            valid_dests = self._check_valid_neighbors(current, visited, fixed_cells)

            if valid_dests:
                next_cell = random.choice(valid_dests)
                self._open_wall(current, next_cell)
                visited.add(next_cell)
                stack.append(next_cell)
            else:
                stack.pop()
        return self.grid
