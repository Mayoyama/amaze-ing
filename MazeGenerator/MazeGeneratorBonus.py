"""Maze Generation Module.

This module provides the core engine for generating 2D grid mazes. It encapsulates the algorithmic logic required to transition a solid
matrix of walls into an open, perfect maze layout.
"""

import random
from dataclasses import dataclass
from collections import deque


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
        """Check if the maze dimensions are large enough to hold the '42' pattern."""
        if self.height < 6 or self.width < 8:
            return False
        return True

    def _embed_42_pattern(self) -> set[tuple[int, int]]:
        """Returns set[tuple[int, int]] to embed '4 2' correctly on the map"""
        fixed_42_cells: set[tuple[int, int]] = set()

        if self._can_fit_42():
            ft_start_row = 0
            ft_start_col = 0
            for r in range(5):
                for c in range(7):
                    ft_grid_r = ft_start_row + r
                    ft_grid_c = ft_start_col + c

                    if self.pattern_42[r][c] == 1:
                        fixed_42_cells.add((ft_grid_r, ft_grid_c))
        return fixed_42_cells

    def _validate_point(self) -> None:
       for name, cell in [("ENTRY", self.start_point), ("EXIT", self.end_point)]:
           r, c = cell
           x, y = self._convert_rc_to_xy(r, c)
           if not (0 <= r < self.height and 0 <= c < self.width):
               raise ValueError(f"{name}: ({x}, {y}) is out of bounds.")
           if cell in self.fixed_cells:
               raise ValueError(f"{name}: ({x}, {y}) collides with '42' pattern.")

    def check_neighbors(self, row: int, col: int) -> None:
        if col > 0:
           if self.grid[row][col-1] & 2 == 0:
              self.grid[row][col] &= ~8
        if row > 0:
            if self.grid[row-1][col] & 4 == 0:
                self.grid[row][col] &= ~1 

    def gen_map(self) -> list[list[int]]:
        """Generates the full maze layout, embedding the 42 pattern first."""
        random.seed(self.seed)  # seed already set, is this needed?
        self._validate_point()
        
        if self._can_fit_42():
            ft_start_col = 0
            ft_start_row = 0

        else:
           ft_start_row = ft_start_col = -1


        for row in range(self.height):
            for col in range(self.width):
                if (row, col) in self.fixed_cells:
                    continue

                is_last_row = (row == self.height - 1)
                is_last_col = (col == self.width - 1)
                
                if col == ft_start_col + 1 and row == ft_start_row:
                    rnd = 6
                elif col == ft_start_col + 1 and row == ft_start_row + 1:
                    rnd  = 1
                elif col == ft_start_col + 2 and row == ft_start_row:
                    rnd = 2
                elif col == ft_start_col + 3 and row == ft_start_row:
                    rnd = 4
                elif col == ft_start_col + 3 and row == ft_start_row + 1:
                    rnd = 6
                elif col == ft_start_col + 3 and row == ft_start_row + 2:
                    rnd = 4
                elif col == ft_start_col + 3 and row == ft_start_row + 3:
                    rnd = 4
                elif col == ft_start_col + 3 and row == ft_start_row + 4:
                    rnd = 4
                elif col == ft_start_col and row == ft_start_row + 3:
                    rnd = 2
                elif col == ft_start_col + 1 and row == ft_start_row + 3:
                    rnd = 4
                elif col == ft_start_col + 1 and row == ft_start_row + 4:
                    rnd = 4
                elif col == ft_start_col + 4 and row == ft_start_row + 1:
                    rnd = 2
                elif col == ft_start_col + 5 and row == ft_start_row + 1:
                    rnd = 8
                elif col == ft_start_col + 5 and row == ft_start_row + 3:
                    rnd = 2
                elif col == ft_start_col + 6 and row == ft_start_row + 3:
                    rnd = 2
                elif col == ft_start_col + 3 and row == ft_start_row + 5:
                    rnd = 15
                elif is_last_row and is_last_col:
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
                
        return self.grid
"""
    # DEBUGGING
    def debug_unreachable_cells(self) -> None:
        '''
        DEBUG ONLY:
        Prints all cells that are NOT reachable from ENTRY.
        Does not modify the maze.
        '''

        height = self.height
        width = self.width
        start = self.start_point

        def can_move(r1, c1, r2, c2):
            dr, dc = r2 - r1, c2 - c1

            if dr == -1:
                return (self.grid[r1][c1] & 1) == 0
            if dr == 1:
                return (self.grid[r1][c1] & 4) == 0
            if dc == -1:
                return (self.grid[r1][c1] & 8) == 0
            if dc == 1:
                return (self.grid[r1][c1] & 2) == 0
            return False

        visited = set([start])
        queue = deque([start])

        # BFS from ENTRY
        while queue:
            r, c = queue.popleft()

            for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
                nr, nc = r + dr, c + dc

                if 0 <= nr < height and 0 <= nc < width:
                    if (nr, nc) not in visited:
                        if can_move(r, c, nr, nc):
                            visited.add((nr, nc))
                            queue.append((nr, nc))

        # collect unreachable cells
        unreachable = [
            (r, c)
            for r in range(height)
            for c in range(width)
            if (r, c) not in visited
            and (r, c) not in self.fixed_cells
        ]

        print("UNREACHABLE CELLS FROM ENTRY:")
        print(unreachable)
        print(f"Total: {len(unreachable)}")
"""
