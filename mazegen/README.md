# mazegen

A standalone 2D maze generator and solver, extracted from the
A-Maze-ing project. It can generate perfect mazes (exactly one path
between any two cells) or non-perfect mazes (extra loops), optionally
embedding a "42" pattern, and can compute the shortest solution path
between an entry and exit cell.

## Installation

```bash
pip install mazegen-1.0.0-py3-none-any.whl
```

## Basic usage

```python
from mazegen import MapData, MazeGenerator, MazeSolver

# 1. Describe the maze you want
data = MapData(
    width=20, height=20,
    entry=(0, 0), exit=(19, 19),
    perfect=True, seed=42,
)

# 2. Generate it
generator = MazeGenerator(data)
grid = generator.gen_map()

# 3. Solve it
solver = MazeSolver(grid, data)
path_cells, path_directions = solver.generate_final_path()

print(path_directions)  # e.g. "EESSWWN..."
```

## Custom parameters

`MapData` takes the following fields:

- `width` / `height`: grid dimensions in cells. Must be at least 8x6
  for the "42" pattern to be drawn - smaller mazes will omit it (see
  "42 pattern" below).
- `entry` / `exit`: `(row, col)` tuples, 0-indexed, marking the start
  and end cells. Must be within the grid and not inside the "42"
  pattern.
- `perfect`: `True` for a maze with exactly one path between any two
  cells (no loops). `False` adds extra connections, creating loops
  and multiple possible paths.
- `seed`: any integer. The same seed and parameters always produce the
  same maze.
- `output_file`, `bonus`, `verbose`: not used by this package - they
  exist only for compatibility with the main app's config format, and
  have default values so they can be omitted.

For the bonus (Sidewinder-style) generator, use `MazeGeneratorBonus`
instead of `MazeGenerator` - it has the same constructor and `gen_map()`
interface.

## Accessing the maze structure

`generator.gen_map()` returns a `list[list[int]]`: one row per maze
row, one integer per cell. Each cell is a 4-bit bitmask describing its
walls:

| Bit | Value | Direction |
| --- | --- | --- |
| 0 | 1 | North |
| 1 | 2 | East |
| 2 | 4 | South |
| 3 | 8 | West |

A bit set to `1` means that wall is **closed**; `0` means it's **open**.
For example, a cell with value `5` (`0b0101`) has its North and South
walls closed, and East/West open.

Note: this is *not* the same format as `output_maze.txt` produced by
the main app (which stores this same grid as hex digits, plus extra
metadata such as the entry/exit coordinates and solution path).

## Accessing a solution

`MazeSolver(grid, data).generate_final_path()` returns a tuple of:

- `path_cells`: the ordered list of `(row, col)` cells from entry to
  exit, inclusive.
- `path_directions`: a string of `"N"`/`"E"`/`"S"`/`"W"` steps
  describing that path, e.g. `"ESSWN"`.

## "42" pattern

Both generators embed a small "42" pattern into the top-left corner of
the maze, walling it off from the rest of the maze. This requires a
minimum maze size of 8 columns x 6 rows (`width >= 8` and
`height >= 6`). If the maze is smaller than this, the pattern is
silently omitted - you can check `generator.can_fit_42()` beforehand
if you need to know whether it will be included.
