"""Path utility functions for maze traversal.

Provides BFS path-finding and DFS path-counting used by the maze
generator to validate non-perfect maps. Neither function depends on
any other project module, so both can be imported freely without
creating circular dependencies.
"""

from collections import deque


def find_path(
    grid: list[list[int]],
    start: tuple[int, int],
    end: tuple[int, int],
) -> list[tuple[int, int]]:
    """Returns the shortest path from start to end via BFS.

    Args:
        grid: The maze grid where each cell is a 4-bit wall bitmask
            (N=1, E=2, S=4, W=8; 1 = wall closed).
        start: The (row, col) coordinates of the starting cell.
        end: The (row, col) coordinates of the destination cell.

    Returns:
        An ordered list of (row, col) cells from start to end inclusive,
        or an empty list if no path exists.
    """
    directions = [(-1, 0, 1), (0, 1, 2), (1, 0, 4), (0, -1, 8)]
    height, width = len(grid), len(grid[0])
    queue: deque[tuple[tuple[int, int], list[tuple[int, int]]]] = deque(
        [(start, [start])]
    )
    visited: set[tuple[int, int]] = {start}

    while queue:
        (r, c), path = queue.popleft()
        if (r, c) == end:
            return path
        for dr, dc, bit in directions:
            nr, nc = r + dr, c + dc
            if (0 <= nr < height and 0 <= nc < width
                    and (nr, nc) not in visited
                    and grid[r][c] & bit == 0):
                visited.add((nr, nc))
                queue.append(((nr, nc), path + [(nr, nc)]))
    return []


def count_paths(
    grid: list[list[int]],
    start: tuple[int, int],
    end: tuple[int, int],
    max_count: int = 2,
) -> int:
    """Counts distinct paths from start to end via iterative DFS.

    Stops early once max_count paths have been found. Returns only the
    count — not the paths themselves.

    Args:
        grid: The maze grid where each cell is a 4-bit wall bitmask
            (N=1, E=2, S=4, W=8; 1 = wall closed).
        start: The (row, col) coordinates of the starting cell.
        end: The (row, col) coordinates of the destination cell.
        max_count: Stop searching once this many distinct paths are
            found. Must be >= 2.

    Returns:
        The number of distinct paths found, between 0 and max_count.

    Raises:
        ValueError: If max_count is less than 2.
    """
    if max_count < 2:
        raise ValueError("max_count must be >= 2")

    directions = [(-1, 0, "N", 1), (0, 1, "E", 2),
                  (1, 0, "S", 4), (0, -1, "W", 8)]
    height, width = len(grid), len(grid[0])

    def get_exits(r: int, c: int) -> list[tuple[int, int, str]]:
        return [
            (r + dr, c + dc, d)
            for dr, dc, d, bit in directions
            if 0 <= r + dr < height and 0 <= c + dc < width
            and grid[r][c] & bit == 0
        ]

    total = 0
    seen: set[str] = set()
    cell_stack: list[tuple[int, int]] = [start]
    visited: set[tuple[int, int]] = {start}
    dir_log: list[str] = []
    nbr_stack: list[tuple[list[tuple[int, int, str]], int]] = [
        (get_exits(*start), 0)
    ]

    while cell_stack and total < max_count:
        neighbours, idx = nbr_stack[-1]
        if idx >= len(neighbours):
            popped = cell_stack.pop()
            nbr_stack.pop()
            if dir_log:
                dir_log.pop()
            visited.discard(popped)
            continue
        nr, nc, nd = neighbours[idx]
        nbr_stack[-1] = (neighbours, idx + 1)
        if (nr, nc) == end:
            p = "".join(dir_log) + nd
            if p not in seen:
                seen.add(p)
                total += 1
        elif (nr, nc) not in visited:
            cell_stack.append((nr, nc))
            visited.add((nr, nc))
            dir_log.append(nd)
            nbr_stack.append((get_exits(nr, nc), 0))

    return total
