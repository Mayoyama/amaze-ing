from map_data import mapData
from collections import deque


class MazeSolver:
    directions = [
        (-1, 0, "N", 1),
        (0, 1, "E", 2),
        (1, 0, "S", 4),
        (0, -1, "W", 8),
    ]

    def __init__(self,  grid: list[list[int]], data: mapData) -> None:
        self.grid = grid
        self.start = data.entry
        self.end = data.exit
        self.height = len(self.grid)
        self.width = len(self.grid[0])
        self.perfect = data.perfect

    def _get_neighbours(self, current: tuple[int,
                                             int]) -> list[tuple[int,
                                                                 int, str]]:
        r, c = current
        neighbours: list[tuple[int, int, str]] = []

        for row_offset, col_offset, direction, wall_bit in self.directions:
            next_row, next_col = r + row_offset, c + col_offset
            if (
              0 <= next_row < self.height
              and 0 <= next_col < self.width
              and (self.grid[r][c] & wall_bit) == 0
              ):
                neighbours.append((next_row, next_col, direction))
        return neighbours

    def _search_path(self) -> dict[tuple[int,
                                         int], tuple[tuple[int, int], str]]:
        visited: set[tuple[int, int]] = {self.start}
        queue: deque[tuple[int, int]] = deque([self.start])
        trail: dict[tuple[int, int], tuple[tuple[int, int], str]] = {}
        while queue:
            current = queue.popleft()
            if current == self.end:
                break

            for next_r, next_c, direction in self._get_neighbours(current):
                if (next_r, next_c) not in visited:
                    visited.add((next_r, next_c))
                    trail[(next_r, next_c)] = (current, direction)
                    queue.append((next_r, next_c))

        return trail

    def generate_final_path(self) -> tuple[list[tuple[int, int]], str]:
        path_cells = []
        direction_list = []
        route = self._search_path()
        current = self.end
        while current in route:
            prev_cell, direction = route[current]
            path_cells.append(current)
            direction_list.append(direction)
            current = prev_cell

        path_cells.append(self.start)
        path_cells.reverse()
        direction_list.reverse()
        direction_str = "".join(direction_list)
        return path_cells, direction_str
