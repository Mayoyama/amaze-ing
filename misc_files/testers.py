from MazeGenerator import MazeGenerator
from map_data import temp_data
from typing import Any
# from mlx_render import mlx_render
from collections import deque

def find_path(grid, start, goal):
    h, w = len(grid), len(grid[0])

    # (dr, dc, direction_char, wall_bit)
    dirs = [
        (-1, 0, "N", 1),
        (0, 1, "E", 2),
        (1, 0, "S", 4),
        (0, -1, "W", 8),
    ]

    q = deque([start])
    parent = {start: None}
    move = {}

    while q:
        r, c = q.popleft()

        if (r, c) == goal:
            break

        for dr, dc, ch, bit in dirs:
            nr, nc = r + dr, c + dc

            if not (0 <= nr < h and 0 <= nc < w):
                continue

            # YOUR representation: wall bit in current cell blocks movement
            if grid[r][c] & bit:
                continue

            if (nr, nc) in parent:
                continue

            parent[(nr, nc)] = (r, c)
            move[(nr, nc)] = ch
            q.append((nr, nc))

    # unreachable safety
    if goal not in parent:
        return None

    # reconstruct path
    path = []
    cur = goal

    while cur != start:
        path.append(move[cur])
        cur = parent[cur]

    return "".join(reversed(path))


def has_cycle(grid, start):
    h, w = len(grid), len(grid[0])
    visited = set()

    def dfs(cell, parent):
        r, c = cell
        visited.add(cell)

        dirs = [
            (-1, 0, 1),
            (1, 0, 4),
            (0, -1, 8),
            (0, 1, 2),
        ]

        for dr, dc, bit in dirs:
            nr, nc = r + dr, c + dc
            nxt = (nr, nc)

            if not (0 <= nr < h and 0 <= nc < w):
                continue
            if grid[r][c] & bit:
                continue

            if nxt == parent:
                continue

            if nxt in visited:
                return True

            if dfs(nxt, cell):
                return True

        return False

    return dfs(start, None)

def decode(cell: int) -> str:
    return (
        f"N:{bool(cell & 1)} "
        f"E:{bool(cell & 2)} "
        f"S:{bool(cell & 4)} "
        f"W:{bool(cell & 8)}"
    )


def dump_grid_decoded(grid: list[list[int]]) -> None:
    for r, row in enumerate(grid):
        print(f"\nRow {r}")
        for c, cell in enumerate(row):
            print(f"({r},{c}) {cell:2d} [{decode(cell)}]", end="   ")
        print()

def dump_grid_hex_compact(grid: list[list[int]]) -> None:
    for row in grid:
        print("".join(f"{cell:X}" for cell in row))

if __name__ == "__main__":
    map_data = temp_data()
	
    mazeGen = MazeGenerator(map_data)
    try:
        newmaze = mazeGen.gen_map()
        #dump_grid_decoded(newmaze)
        dump_grid_hex_compact(newmaze)
        # mlx_render(newmaze)
        print()
        start = map_data.entry
        goal = map_data.exit
        s1, s2 = start
        e1, e2 = goal
        print(f"{s1}, {s2}")
        print(f"{e1}, {e2}")
        path = find_path(newmaze, start, goal)
        print(path)

        print(f"{has_cycle(newmaze, start)}")

    except ValueError as e:
        print(e)
