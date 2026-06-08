"""Maze Generation Module.

This module provides the core engine for generating 2D grid mazes. It encapsulates the algorithmic logic required to transition a solid
matrix of walls into an open, perfect maze layout.
"""

import random
from dataclasses import dataclass


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
            self.grid[curr_r][curr_c] &= ~1 # MAYBE IT'S HERE
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

    def gen_map(self) -> list[list[int]]:
        """Generates the full maze layout, embedding the 42 pattern first."""
        random.seed(self.seed)
        fixed_cells = self._embed_42_pattern()

        self._validate_point(fixed_cells)
        
        if self._can_fit_42():
            ft_start_row = (self.height - 5) // 2
            ft_start_col = (self.width - 7) // 2
            start_cell = (ft_start_row + 2, ft_start_col + 1)
        else:
            start_cell = (self.height - 1, 0)


        stack: list[tuple[int, int]] = [start_cell]
        visited: set[tuple[int, int]] = {start_cell} | fixed_cells #  | fixed_cells  Needed? Need to test!!

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

        self._final_map_adjustment()
        return self.grid

'''
    def render_terminal(self) -> None:
        """Prints a highly readable text representation of the maze to the console."""
        if not self.grid or self.start_point is None or self.end_point is None:
            print("Error: Map must be generated via gen_map() before rendering.")
            return

        fixed_cells = self._embed_42_pattern()

        # ANSI Color escape codes
        RESET = "\033[0m"
        WALL_COLOR = "\033[90m"   # Dark Grey
        START_COLOR = "\033[92m"  # Bright Green
        END_COLOR = "\033[91m"    # Bright Red
        TEXT_42_COLOR = "\033[96m" # Cyan
        PATH_COLOR = "\033[97m"   # White (for clear paths)

        render_w = self.width * 2 + 1
        render_h = self.height * 2 + 1
        buffer = [["█" for _ in range(render_w)] for _ in range(render_h)]

        for r in range(self.height):
            for c in range(self.width):
                buf_r = r * 2 + 1
                buf_c = c * 2 + 1
                cell_val = self.grid[r][c]

                # Assign characters to the floor paths
                if (r, c) == self.start_point:
                    buffer[buf_r][buf_c] = f"{START_COLOR}S{RESET}"
                elif (r, c) == self.end_point:
                    buffer[buf_r][buf_c] = f"{END_COLOR}E{RESET}"
                elif (r, c) in fixed_cells:
                    # Let's show the actual digit character for the fixed walls
                    char_42 = "4" if c < (self.width // 2) else "2"
                    buffer[buf_r][buf_c] = f"{TEXT_42_COLOR}{char_42}{RESET}"
                else:
                    buffer[buf_r][buf_c] = " "

                # Clear out the shared wall spaces between cells if open
                if (cell_val & 1) == 0:  # North
                    buffer[buf_r - 1][buf_c] = " "
                if (cell_val & 2) == 0:  # East
                    buffer[buf_r][buf_c + 1] = " "
                if (cell_val & 4) == 0:  # South
                    buffer[buf_r + 1][buf_c] = " "
                if (cell_val & 8) == 0:  # West
                    buffer[buf_r][buf_c - 1] = " "

        # Print the grid, wrapping the wall blocks in the wall color string
        for row in buffer:
            colored_line = ""
            for char in row:
                if char == "█":
                    colored_line += f"{WALL_COLOR}█{RESET}"
                else:
                    colored_line += char
            print(colored_line)
'''
