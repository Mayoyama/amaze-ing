"""Maze Generation Base Module.

This module provides the core engine for generating 2D grid mazes. It contains
a parent class that aggregates core map configuration data and shared methods
utilized across different maze generation algorithms.
"""

import random
from .map_data import MapData
from abc import ABC, abstractmethod


class MazeGenBase(ABC):
    """An algorithmic engine responsible for carving 2D grid mazes.

    Attributes:
        width (int): Total column count of the maze grid.
        height (int): Total row count of the maze grid.
        seed (int): Numeric seed value used to initialize the pseudo-random
            number generator, ensuring reproducible maze layouts.
        grid (list[list[int]]): The internal 2D matrix representing
            the maze layout.
        pattern_42 (list[list[int]]): The template for the '42' pattern
            that must appear in the generated map.
        start_point (tuple[int, int]): Row and column coordinates for
            the maze entrance.
        end_point (tuple[int, int]): Row and column coordinates for the
            maze exit.
        perfect_map (bool): True if the maze is a perfect maze (no loops),
            False otherwise.
        fixed_cells (set[tuple[int, int]]): Grid coordinates reserved by
            the '42' pattern.
    """
    def __init__(self, data: MapData, pattern_42: list[list[int]]) -> None:
        """Initializes maze config and instantiates a solid wall grid."""
        self.width = data.width
        self.height = data.height
        self.seed = data.seed
        self.grid = self._initialize_empty_grid()
        self.start_point = data.entry
        self.end_point = data.exit
        self.perfect_map = data.perfect
        self.pattern_42 = pattern_42
        self.fixed_cells: set[tuple[int, int]] = self._embed_42_pattern("all")

    @staticmethod
    def _convert_rc_to_xy(r: int, c: int) -> tuple[int, int]:
        """Converts row and column matrix indices into standard 1-indexed
        (x, y) coordinates.
        """
        return (c + 1, r + 1)

    def _initialize_empty_grid(self) -> list[list[int]]:
        """Creates and initializes the grid with fully intact walls (value 15)
         to use in map generation.
        """
        grid: list[list[int]] = []
        for r in range(self.height):
            curr_row: list[int] = []
            for c in range(self.width):
                curr_row.append(15)
            grid.append(curr_row)
        return grid

    def can_fit_42(self) -> bool:
        """Check if maze dimensions are large enough to hold '42' pattern."""
        return self.height >= 6 and self.width >= 8

    def _embed_42_pattern(self, pattern: str) -> set[tuple[int, int]]:
        """Returns a set of coordinate tuples to reserve the '42' pattern
        spaces on the grid.
        """
        fixed_42_cells: set[tuple[int, int]] = set()

        if not self.can_fit_42():
            return fixed_42_cells

        ft_start_row = 0
        ft_start_col = 0
        for r in range(5):
            for c in range(7):
                if pattern == "all":
                    if self.pattern_42[r][c] >= 0:
                        fixed_42_cells.add((ft_start_row + r,
                                            ft_start_col + c))
                elif pattern == "full":
                    if self.pattern_42[r][c] == 0:
                        fixed_42_cells.add((ft_start_row + r,
                                            ft_start_col + c))

        return fixed_42_cells

    def _validate_point(self) -> None:
        """Validates that the Entry and Exit points do not collide
        with the '42' pattern.
        """
        for name, cell in [("ENTRY", self.start_point),
                           ("EXIT", self.end_point)]:
            r, c = cell
            x, y = self._convert_rc_to_xy(r, c)
            if cell in self.fixed_cells:
                raise ValueError(f"{name}: ({x}, {y}) collides with "
                                 "'42' pattern.")

    def _check_neighbors(self, row: int, col: int) -> None:
        """Synchronizes wall states by ensuring adjacent cells share
        matching open paths.

        If a neighboring cell has removed its wall facing the current cell,
        this removes the corresponding wall in the current cell.
        """
        if (row, col) not in self.fixed_cells:
            if col > 0:
                if self.grid[row][col-1] & 2 == 0:
                    self.grid[row][col] &= ~8
            if col + 1 < self.width:
                if self.grid[row][col+1] & 8 == 0:
                    self.grid[row][col] &= ~2
            if row > 0:
                if self.grid[row-1][col] & 4 == 0:
                    self.grid[row][col] &= ~1
            if row + 1 < self.height:
                if self.grid[row+1][col] & 1 == 0:
                    self.grid[row][col] &= ~4

    def _non_perfect(self) -> None:
        """Introduces loops into the maze by removing walls at random
        locations, keeping both sides of every removed wall in sync.
        """
        # bit -> (row_offset, col_offset, matching bit on the neighbour)
        wall_links = {
            1: (-1, 0, 4),   # N wall  <-> neighbour's S wall
            2: (0, 1, 8),    # E wall  <-> neighbour's W wall
            4: (1, 0, 1),    # S wall  <-> neighbour's N wall
            8: (0, -1, 2),   # W wall  <-> neighbour's E wall
        }

        def _break_wall(row: int, col: int, bit: int) -> None:
            """Clears 'bit' on (row, col) and the matching bit on the
            neighbour across that wall. Does nothing if there is no
            neighbour on that side, or if the neighbour is part of the
            '42' pattern.
            """
            row_offset, col_offset, opposite_bit = wall_links[bit]
            n_row, n_col = row + row_offset, col + col_offset

            if not (0 <= n_row < self.height and 0 <= n_col < self.width):
                return  # this side faces the maze boundary - leave it walled
            if (n_row, n_col) in self.fixed_cells:
                return  # don't carve a hole into the '42' pattern

            self.grid[row][col] &= ~bit
            self.grid[n_row][n_col] &= ~opposite_bit

        nbr_break = max(5, (self.width * self.height) // 25)
        for _ in range(nbr_break):
            random_row = random.randint(1, self.height)
            random_col = random.randint(1, self.width)
            r, c = random_row - 1, random_col - 1

            if (r, c) not in self.fixed_cells:
                for bit in wall_links:
                    _break_wall(r, c, bit)

    def _remove_excessive_rooms(self) -> None:
        """Scans in a 3x3 window and adds a wall if a blank 3x3 space is
        found.
        """
        def _is_open_horizontal(r: int, c: int) -> bool:
            """Check whether the wall between (r,c) and (r,c+1) is open."""
            return (self.grid[r][c] & 2 == 0 and
                    self.grid[r][c + 1] & 8 == 0)

        def _is_open_vertical(r: int, c: int) -> bool:
            """Check whether the wall between (r,c) and (r+1,c) is open."""
            return (self.grid[r][c] & 4 == 0 and
                    self.grid[r + 1][c] & 1 == 0)

        for scan_r in range(self.height - 2):
            for scan_c in range(self.width - 2):
                is_open_room = True
                # Check all horizontal boundaries in the window
                for window_r in range(scan_r, scan_r + 3):
                    for window_c in range(scan_c, scan_c + 2):
                        if not _is_open_horizontal(window_r, window_c):
                            is_open_room = False
                            break
                    if not is_open_room:
                        break

                if is_open_room:
                    # Check all vertical boundaries in the window
                    for window_r in range(scan_r, scan_r + 2):
                        for window_c in range(scan_c, scan_c + 3):
                            if not _is_open_vertical(window_r, window_c):
                                is_open_room = False
                                break
                        if not is_open_room:
                            break

                # Add a wall through the center of the room
                if is_open_room:
                    self.grid[scan_r + 1][scan_c + 1] |= 1
                    self.grid[scan_r][scan_c + 1] |= 4

    @abstractmethod
    def gen_map(self) -> list[list[int]]:
        pass
