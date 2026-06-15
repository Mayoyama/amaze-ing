from MapData import MapData
from collections import deque


class MazeSolver:
    """Finds the shortest path between two cells in a maze grid.

    Performs a breadth-first search over the maze grid (where each
    cell is a 4-bit N/E/S/W wall bitmask) from the entry to the exit
    cell, then reconstructs that route as a list of cells and a
    direction string using the same N/E/S/W convention as
    find_alt_paths.

    Attributes:
        directions: Class-level list of (row_offset, col_offset,
            direction_label, wall_bit) tuples, one per cardinal
            direction, used to step to each neighbouring cell.
    """
    directions = [
        (-1, 0, "N", 1),
        (0, 1, "E", 2),
        (1, 0, "S", 4),
        (0, -1, "W", 8),
    ]

    def __init__(self,  grid: list[list[int]], data: MapData) -> None:
        """Stores the maze grid and the entry/exit cells to solve for.

        Args:
            grid: The maze grid, where each cell is a 4-bit wall
                bitmask (N=1, E=2, S=4, W=8; 1 = wall closed).
            data: Parsed configuration providing the entry and exit
                cell coordinates.
        """
        self._grid = grid
        self._start = data.entry
        self._end = data.exit
        self._height = len(self._grid)
        self._width = len(self._grid[0])
        self._perfect = data.perfect

    def _get_neighbors(self, current: tuple[int,
                                            int]) -> list[tuple[int,
                                                                int, str]]:
        """Returns the open (wall-free) neighbours of a cell.

        Args:
            current: The (row, col) coordinates of the cell to check.

        Returns:
            A list of (row, col, direction) tuples, one for each
            neighbour reachable from `current` without crossing a wall.
        """
        r, c = current
        neighbors: list[tuple[int, int, str]] = []

        for row_offset, col_offset, direction, wall_bit in self.directions:
            next_row, next_col = r + row_offset, c + col_offset
            if (
              0 <= next_row < self._height
              and 0 <= next_col < self._width
              and (self._grid[r][c] & wall_bit) == 0
              ):
                neighbors.append((next_row, next_col, direction))
        return neighbors

    def _search_path(self) -> dict[tuple[int,
                                         int], tuple[tuple[int, int], str]]:
        """Performs a breadth-first search from the entry to the exit.

        Returns:
            A mapping from each visited cell to the (previous_cell,
            direction) pair used to reach it, used by
            generate_final_path to reconstruct the route. If the exit
            is unreachable, it will be absent from the mapping.
        """
        visited: set[tuple[int, int]] = {self._start}
        queue: deque[tuple[int, int]] = deque([self._start])
        trail: dict[tuple[int, int], tuple[tuple[int, int], str]] = {}
        while queue:
            current = queue.popleft()
            if current == self._end:
                break

            for next_r, next_c, direction in self._get_neighbors(current):
                if (next_r, next_c) not in visited:
                    visited.add((next_r, next_c))
                    trail[(next_r, next_c)] = (current, direction)
                    queue.append((next_r, next_c))

        return trail

    def generate_final_path(self) -> tuple[list[tuple[int, int]], str]:
        """Reconstructs the shortest path from entry to exit.

        Returns:
            A tuple of (path_cells, direction_str): path_cells is the
            ordered list of (row, col) cells from entry to exit
            inclusive, and direction_str is the matching sequence of
            N/E/S/W steps (e.g. "ESSWN"). If no path exists,
            path_cells contains only the entry cell and direction_str
            is empty.
        """
        path_cells = []
        direction_list = []
        route = self._search_path()
        current = self._end
        while current in route:
            prev_cell, direction = route[current]
            path_cells.append(current)
            direction_list.append(direction)
            current = prev_cell

        path_cells.append(self._start)
        path_cells.reverse()
        direction_list.reverse()
        direction_str = "".join(direction_list)
        return path_cells, direction_str
