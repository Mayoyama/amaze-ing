from dataclasses import dataclass


@dataclass
class MapData:
    """Container for the parameters needed to generate and solve a maze.

    This is a trimmed copy of the MapData class used by the main
    A-Maze-ing application. Only the fields needed for maze generation
    and solving (width, height, entry, exit, perfect, seed) need to be
    set explicitly - the remaining fields exist only for compatibility
    with the main app's config format and default to sensible values.

    Attributes:
        width: Number of columns in the maze grid.
        height: Number of rows in the maze grid.
        entry: The (row, col) coordinates of the maze entrance.
        exit: The (row, col) coordinates of the maze exit.
        perfect: True for a perfect maze (exactly one path between any
            two cells, no loops), False to add extra connections.
        seed: Seed for the random number generator. The same seed and
            parameters always produce the same maze.
        output_file: Unused by this package - kept for compatibility.
        bonus: Unused by this package - kept for compatibility.
        verbose: Unused by this package - kept for compatibility.
    """
    width: int
    height: int
    entry: tuple[int, int]
    exit: tuple[int, int]
    perfect: bool
    seed: int
    output_file: str = "output_maze.txt"
    bonus: bool = False
    verbose: bool = False
