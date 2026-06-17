
def find_alt_paths(grid: list[list[int]], start: tuple[int, int],
                   target: tuple[int, int],
                   max_count: int = 2) -> tuple[int, list[str]]:
    """Finds up to max_count unique paths from start to target.

    Performs an iterative depth-first search (using an explicit stack
    to avoid recursion) over the maze grid, exploring every simple
    path (one that never revisits a cell) from start to target. Each
    completed path is recorded as a direction string (e.g. "ESSWN"),
    using the same N/E/S/W convention as the output_maze file.

    While perfect maps should have no issues, even at large sizes
    (at least 75x75), it is not recommended to be used on non-perfect
    maps of sizes greater than around 20x20, due to the nature of
    DFS and looping.

    Args:
        grid: The maze grid, where each cell is a 4-bit wall bitmask
            (N=1, E=2, S=4, W=8; 1 = wall closed).
        start: The (row, col) coordinates of the starting cell.
        target: The (row, col) coordinates of the destination cell.
        max_count: The maximum number of distinct paths to search for
            before stopping. Must be >= 2.

    Returns:
        A tuple of (number of distinct paths found, list of direction
        strings for each path found). The list has between 0 and
        max_count entries, in no guaranteed order

    Raises:
        ValueError: If max_count is less than 2.

    Attributes:
        path_stack: Cells visited along the current path, from start
            to the current cell.
        path_dirs: Directions taken between consecutive cells in
            path_stack (one element shorter than path_stack).
        neighbour_stack: For each cell in path_stack, its list of open
            neighbours and the index of the next one to try.
        visited: Cells currently in path_stack, used to prevent the
            search revisiting a cell within the same path.
        paths_set: Direction strings found so far, used to avoid
            reporting the same path twice.
    """
    if max_count < 2:
        raise ValueError("max_count must be >= 2")

    directions = [
        (-1, 0, "N", 1),
        (0, 1, "E", 2),
        (1, 0, "S", 4),
        (0, -1, "W", 8),
    ]
    width = len(grid[0])
    height = len(grid)

    def check_open_neighbours(cell: tuple[int,
                                          int]) -> list[tuple[int, int, str]]:
        """Returns the open (wall-free) neighbours of a cell, with
        their directions.
        """
        neighbours: list[tuple[int, int, str]] = []
        r, c = cell
        for r_offset, c_offset, direction, bit_value in directions:
            if (
              0 <= (r + r_offset) < height
              and 0 <= (c + c_offset) < width
              and (grid[r][c] & bit_value) == 0
              ):
                neighbours.append(((r + r_offset), (c + c_offset), direction))
        return neighbours

    total_paths_found = 0
    paths_set: set[str] = set()
    path_stack: list[tuple[int, int]] = [start]
    visited: set[tuple[int, int]] = set()
    visited.add(start)
    path_dirs: list[str] = []
    neighbour_stack: list[tuple[list[tuple[int, int, str]],
                                int]] = [(check_open_neighbours(start), 0)]

    while path_stack and total_paths_found < max_count:
        neighs, index = neighbour_stack[-1]
        if index >= len(neighs):
            popped_cell = path_stack.pop()
            neighbour_stack.pop()
            if path_dirs:
                path_dirs.pop()
            visited.discard(popped_cell)
            continue
        else:
            nxt_r, nxt_c, nxt_dir = neighs[index]
            neighbour_stack[-1] = (neighs, index + 1)
            if (nxt_r, nxt_c) == target:
                new_path = "".join(path_dirs) + nxt_dir
                if new_path not in paths_set:
                    paths_set.add(new_path)
                    total_paths_found += 1
            elif (nxt_r, nxt_c) not in visited:
                path_stack.append((nxt_r, nxt_c))
                visited.add((nxt_r, nxt_c))
                path_dirs.append(nxt_dir)
                neighbour_stack.append((check_open_neighbours((nxt_r,
                                                               nxt_c)), 0))

    # print("Map Analysis".center(30, "="))
    # if total_paths_found == 0:
    #     print("Warning! Path not found!")
    # elif total_paths_found == 1:
    #     perfect_path = next(iter(paths_set))
    #     print(f"Maze is Perfect! Only one possible path found:"
    #           "\n{perfect_path}")
    # elif total_paths_found > 1:
    #     print("Multiple paths found!")
    #     for path in paths_set:
    #         print(f"Path found:\n[{path}]")

    return total_paths_found, list(paths_set)


'''
def _verify_map(self) -> None:
        """Analyses the current maze and prints a set number of
        distinct start-to-exit paths exist (default is 2).

        Callers should only invoke this when map_data.verbose is True —
        find_alt_paths can take quite a long time to process on a large
        non-perfect maze, which would otherwise make the maze window
        appear frozen with no indication in the terminal of why.

        As a further safeguard, the search is still skipped on non-perfect
        mazes larger than 20x20, printing a message instead.
        """
        if (not self._map_data.perfect
                and (self._map_data.width > 20 or self._map_data.height > 20)):
            print("Feature unavailable for maps larger than 20x20")
            return

        count, paths = find_alt_paths(self._grid, self._map_data.entry,
                                      self._map_data.exit)

        print("Map Analysis".center(30, "="))
        if count == 0:
            print("Warning! Path not found!")
        elif count == 1:
            print(f"Maze is Perfect! Only one possible path "
                  f"found:\n{paths[0]}")
        else:
            print("Multiple paths found!")
            for path in paths:
                print(f"Path found:\n[{path}]")
'''
