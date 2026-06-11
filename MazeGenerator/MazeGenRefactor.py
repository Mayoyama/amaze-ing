import random
from map_data import mapData


class MazeGenerator:
    pattern_42 = [
        [1, 0, 0, 0, 1, 1, 1],
        [1, 0, 1, 0, 0, 0, 1],
        [1, 1, 1, 0, 1, 1, 1],
        [0, 0, 1, 0, 1, 0, 0],
        [0, 0, 1, 0, 1, 1, 1],
    ]

    def __init__(self, data: mapData) -> None:
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
        grid = []
        for r in range(self.height):
            row = []
            for c in range(self.width):
                row.append(15)
            grid.append(row)
        return grid

    def _can_fit_42(self) -> bool:
        return self.height >= 6 and self.width >= 8

    def _embed_42_pattern(self) -> set[tuple[int, int]]:
        fixed_42_cells = set()

        if not self._can_fit_42():
            return fixed_42_cells

        if self.bonus or (self.height == 6 and self.width == 8):
            ft_start_row = 0
            ft_start_col = 0
        else:
            ft_start_row = (self.height - 5) // 2
            ft_start_col = (self.width - 7) // 2

        def build(sr, sc):
            return {
                (sr + r, sc + c)
                for r in range(5)
                for c in range(7)
                if self.pattern_42[r][c] == 1
            }

        fixed_42_cells = build(ft_start_row, ft_start_col)

        if not self.bonus:
            if (self.start_point in fixed_42_cells
                or self.end_point in fixed_42_cells):
                fixed_42_cells = build(0, 0)

        return fixed_42_cells

    def _validate_point(self, fixed_cells: set[tuple[int, int]]) -> None:
        for name, cell in [("ENTRY", self.start_point), ("EXIT", self.end_point)]:
            r, c = cell
            x, y = self._convert_rc_to_xy(r, c)

            if not (0 <= r < self.height and 0 <= c < self.width):
                raise ValueError(f"{name}: ({x}, {y}) is out of bounds.")
            if cell in fixed_cells:
                raise ValueError(f"{name}: ({x}, {y}) collides with '42' pattern.")



class MazeGeneratorDFS(MazeGenerator):

    def _check_valid_neighbors(self, current, visited):
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

    def _open_wall(self, current, next_cell):
        curr_r, curr_c = current
        next_r, next_c = next_cell

        dr = next_r - curr_r
        dc = next_c - curr_c

        if dr == -1:
            self.grid[curr_r][curr_c] &= ~1
            self.grid[next_r][next_c] &= ~4
        if dr == 1:
            self.grid[curr_r][curr_c] &= ~4
            self.grid[next_r][next_c] &= ~1
        if dc == -1:
            self.grid[curr_r][curr_c] &= ~8
            self.grid[next_r][next_c] &= ~2
        if dc == 1:
            self.grid[curr_r][curr_c] &= ~2
            self.grid[next_r][next_c] &= ~8

    def gen_map(self):
        random.seed(self.seed)

        self._validate_point(self.fixed_cells)

        if self._can_fit_42():
            ft_start_row = (self.height - 5) // 2
            ft_start_col = (self.width - 7) // 2
            start_cell = (ft_start_row + 2, ft_start_col + 1)
        else:
            start_cell = (self.height - 1, 0)

        stack = [start_cell]
        visited = {start_cell} | self.fixed_cells

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

        return self.grid



class MazeGeneratorBonus(MazeGenerator):

    def check_neighbors(self, row: int, col: int) -> None:
        if col > 0:
            if self.grid[row][col - 1] & 2 == 0:
                self.grid[row][col] &= ~8

        if row > 0:
            if self.grid[row - 1][col] & 4 == 0:
                self.grid[row][col] &= ~1

    def gen_map(self):
        random.seed(self.seed)

        self._validate_point(self.fixed_cells)

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
                    rnd = 1
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
                    rnd = random.choice([2, 4])

                if rnd != 0:
                    self.grid[row][col] &= ~rnd

                self.check_neighbors(row, col)

        return self.grid
