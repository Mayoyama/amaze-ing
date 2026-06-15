*This project has been created as part of the 42 curriculum by speterse and ikryvenk*
# A-Maze-ing — Project Documentation

Welcome to the **A-Maze-ing** project repository. This document serves as the comprehensive guide for the system architecture, installation, configuration, and team workflow.

---

## Table of Contents

* [Description](#description)
* [Instructions](#instructions)
* [Configuration File Structure](#configuration-file-structure)
* [Technical Design & Algorithms](#technical-design--algorithms)
* [Advanced Features](#advanced-features)
* [Code Reusability](#code-reusability)
* [Resources & AI Usage](#resources--ai-usage)
* [Team & Project Management](#team--project-management)

---

## Description

### Project Goal
The goal of this project is to generate, solve, and visually render 2D mazes based on a configuration file. The system produces a deterministic maze (based on a seed), finds the shortest path between entry and exit points, and renders everything to the screen using a graphical display via the MiniLibX (MLX) library.

### Overview
* **Language:** Written in Python 3.10.
* **Generation & Reproducibility:** The maze is randomly generated, but supports full reproducibility using a seed. 
* **Cell Structure:** Each cell in the maze has between 0 and 4 walls corresponding to the cardinal points (North, East, South, West).
* **Features:** 
  * The maze features a visible "42" pattern drawn by several fully closed cells (and yes, you can customize its color!).
  * Supports the creation of both **perfect maps** (exactly one valid path) and **non-perfect maps** (multiple possible paths/loops).
* **Storage:** Cells are stored sequentially row by row, with one row per line.


The program follows a full pipeline:

1. A configuration file is parsed into a structured `MapData` object.
2. A maze grid is generated using either a standard generator or a bonus variant.
3. The grid encodes walls using bitwise values per cell.
4. A BFS-based solver computes the shortest path between ENTRY and EXIT.
5. The maze is rendered in a graphical window using MLX, including optional overlays such as the solution path, a sprite animation along the path, and a fixed “42” pattern embedded into the maze.
6. The final maze and solution can also be exported to a text file.
---

### Maze Bitmask Reference Key 

Each cell is represented by a 4-bit integer (ranging from 0 to 15). 
* A bit set to **1** means the wall is **CLOSED**.
* A bit set to **0** means the wall is **OPEN**.

| Bit Position | Direction | Integer Value | Binary Mask | Hex Equivalent |
| :--- | :--- | :--- | :--- | :--- |
| **Bit 0 (LSB)** | North (N) | 1 | `0001` | `0x1` |
| **Bit 1** | East (E) | 2 | `0010` | `0x2` |
| **Bit 2** | South (S) | 4 | `0100` | `0x4` |
| **Bit 3 (MSB)** | West (W) | 8 | `1000` | `0x8` |

#### Common State Examples:
* **15** (`0xF` / `1111`) => All 4 walls are **CLOSED** (Initial grid cell state)
* **0** (`0x0` / `0000`) => Crossroads; all 4 walls are **OPEN**
* **5** (`0x5` / `0101`) => East, and West are **OPEN**; North and South are **CLOSED** (Horizontal Hallway)
* **10** (`0xA` / `1010`) => North and South **OPEN**; East and West are **CLOSED** (Vertical Hallway)
* **11** (`0xB` / `1011`) => South wall is **OPEN**; North, East, and West are **CLOSED**


[▲ Back to Top](#table-of-contents)

---

## Instructions

### Prerequisites
<!-- List any system dependencies, Python version requirements, or terminal requirements here -->
* **OS:** Linux or macOS (required for MiniLibX compatibility).
* **Language:** Python 3.10 or higher.
* A standard 'python -m venv' named maze_venv
* **Python Packages:** `mypy` and `flake8` (for linting and development).
* A working installation of MLX provided via local wheel (`mlx-2.2-py3-none-any.whl`)

### Installation / Setup
To install the project, clone the repository and run the setup command in your terminal:

```bash
git clone <repository-url>
make install
```

All the required dependencies, venv and files will be automatically installed.

### Execution

To run the program execute:

```bash
source maze_venv/bin/activate 
make run
```

You can also use the following development and utility commands:

* make debug — Launches the program in debug mode with verbose logging.

* make clean — Cleans up temporary files and deletes the .mypy_cache and .pycache folders.

* make lint — Runs `flake8` and `mypy` with the required flags to check for code style and type compliance.

* make lint_strict — Performs the same checks as make lint, but enforces mypy with the `--strict` flag.

* make uninstall - In addition to running `make clean`, it will also remove the venv. Note the venv must be deactivated before the venv folder can be removed.


[▲ Back to Top](#table-of-contents)

---

## Configuration File Structure

### Format Specification

The configuration file passed as an argument must contain the following variables:

    - WIDTH: The integer width of the maze grid.

    - HEIGHT: The integer height of the maze grid.

    - ENTRY: The coordinates (x,y) of the maze entry point.

    - EXIT: The coordinates (x,y) of the maze exit point.

    - OUTPUT_FILE: The name/path of the file where the generated maze will be saved.

    - PERFECT: Set to True for a single-path maze, or False for a maze with multiple paths/loops.

    - SEED: An integer value used to seed the random generator for reproducible mazes.

    - BONUS: Set to True or False to enable or disable bonus maze.

    - VERBOSE: Set to True or False. When True, the program prints extra map-analysis info (alternate path search results) to the terminal after each maze generation.

Note: You can include comments in the configuration file; blank lines and lines starting with # will be ignored.

### Complete Template
```ini
# Example configuration structure mapping variables.
WIDTH=20
HEIGHT=20
ENTRY=10,10
EXIT=15,15
OUTPUT_FILE=output_maze.txt
PERFECT=True
SEED=42
BONUS=False
VERBOSE=False
```

### Constraints & Validation Rules

To ensure stability, proper rendering performance, and logical consistency, the configuration file must adhere to the following rules:

* **Dimensions:**  Width and height must be integers between `2` and `75`.
    * *Reasoning:*  While it is possible to render maps larger than 75x75, setting dimensions higher than 75 significantly degrades performance during the graphical MiniLibX (MLX) animation, as the entire maze grid is redrawn on every single frame.

* **Coordinates:** 
  * The entry and exit points must be located strictly within the bounds of the map.
  * The entry and exit coordinates cannot be identical.
  * The entry and exit points cannot overlap with any cells designated for the "42" pattern.

* **Special Rules:** 
  * **SEED**: Must be a valid **positive** integer. Providing the same seed ensures identical maze generation for testing and reproducibility.
  * **PERFECT, BONUS & VERBOSE**: These flags must strictly be set to either `True` or `False`.

NB: If any values in the config file are invalid or left blank, an appropriate error message will be provided, and the program will terminate.

* **"42" Pattern:** Requires a minimum map size of 8x6. If the configured WIDTH/HEIGHT is smaller, the pattern is omitted and an error message is printed to the console.

[▲ Back to Top](#table-of-contents)

---

## Technical Design & Algorithms

### Chosen Maze Generation Algorithm

The primary generator uses a **Depth-First Search** (DFS) backtracking algorithm implemented with an explicit stack.

The algorithm begins at a starting cell and repeatedly moves to a randomly chosen unvisited neighbor, removing the wall between the two cells. When a cell has no unvisited neighbors remaining, the algorithm backtracks to the most recent cell with unexplored paths and continues the process. This continues until all reachable cells have been visited, producing a fully connected maze. When perfect maze generation is enabled, there is exactly one unique path between any two points in the maze.

#### Selection Justification
DFS backtracking was chosen because:
- Produces perfect mazes when enabled
- Simple stack-based implementation
- Deterministic with seed
- Produces long corridors

### Pathfinding Solver
**Breadth-First Search** (BFS) is used to guarantee shortest path in an unweighted grid.

BFS is a graph traversal algorithm that explores all possible positions in a maze level by level. Starting from the entry point, it first visits all directly reachable neighboring cells, then expands outward to their neighbors, and so on. This “layer-by-layer” exploration ensures that the first time the exit is reached, the path taken is the shortest possible in terms of number of steps.

In this project, BFS keeps track of visited cells and records the previous cell for each step, allowing the final path to be reconstructed by backtracking from the exit to the entry once the search completes

### Map Analysis Algorithm

Like the BFS solver, `find_alt_paths` searches for routes between ENTRY and EXIT, but uses **DFS** to enumerate distinct simple paths (paths that never revisit a cell), stopping once 2 are found. If only one exists, the maze is confirmed perfect; if a second is found, the maze has loops. On large non-perfect mazes the number of possible paths grows very quickly, which is why this search is size-capped (see Verbose Mode above).

### Chosen Maze Generation Algorithm for Bonus

For the bonus algorithm, we implemented a modified variation of the **Sidewinder** algorithm. The generation process iterates through the grid row by row from top to bottom, and from right to left. For each individual cell, the algorithm makes a randomized decision on whether to destroy the eastern (right) wall or the southern (bottom) wall. As it processes each cell, it actively checks the state of its neighbors and merges them accordingly into sets. 

A distinct structural feature (and limitation) of this algorithm is its inherent geometric bias: because of the way boundaries are handled at the edges, the **far-right corridor** and the **bottom row** of the maze will always be completely open and devoid of intersecting walls.

#### Selection Justification

**Sidewinder adaptation** algorithm was chosen because:
- Was interesting to implement
- Was easy to understand
- Is totally different of our main algorithm
- Was compatible with our "42" pattern requirement

### Non-perfect map

Both of our algorithms create a perfect map. So for the non-perfect map we destroy some of the cells. `Random.randint` is used to select a predetermined number of cells to destroy (ranging from 5 to 15). Care is also taken to ensure the neighbouring cell's wall integrity is maintained. We also created a protective barrier around the "42" pattern to ensure it is not affected by the process.

### Issue regarding linters and the MiniLibX python wrapper

Mlx is not a native module/library for python. It is actually a **C-language library**, which has had a wrapper applied to it. The wrapper does not have any typing, which causes `mypy --strict` to complain about the lack of typing **in the module itself**:
```ini
a_maze_ing.py:3: error: Skipping analyzing "mlx": module is installed, but missing library stubs or py.typed marker  [import-untyped]
```
Since modifying the module and wrapper is outside the scope of this project and not feasible with a prepackaged .whl, we decided to handle this mypy error by using the inline comment # type: ignore[import-untyped], which only specifically triggers for imported modules without typing.

[▲ Back to Top](#table-of-contents)

---

## Advanced Features & Controls

When rendering the maze using the MiniLibX (MLX) graphical interface, you can interact with the program in real-time using the following keyboard shortcuts:

* **Key [1]**: Change the primary maze color.
* **Key [2]**: Change the "42" pattern color.
* **Key [3]**: Toggle the visibility of the shortest path (Show/Hide).
* **Key [4]**: Animated sprite traversal along path - Using in-built functions from MLX, the user can start, pause and restart the animation of a fish sprite, which swims along the path from the start to the end.
* **Key [5]**: Generate a new **perfect map** using the primary (DFS) algorithm.
* **Key [6]**: Generate a new **non-perfect map** using the primary algorithm.
* **Key [7]**: Generate a new **perfect map** using the bonus (Sidewinder adaptation) algorithm.
* **Key [8]**: Generate a new **non-perfect map** using the bonus algorithm.
* **Key [ESC]**: Safely exit the program and close the graphical window.

### Export of maze + solution path to text file:

In addition to the above, upon each generation of a new maze, a file output_maze.txt will be generated and populated with a hex representation of the cell values, the start and end coordinates and the directions of how to move between the start and end points.

### Map Analysis (Verbose Mode)

When `VERBOSE=True`, every time a maze is generated (on startup and after pressing keys 5-8) the program searches for alternate paths between ENTRY and EXIT and prints a short summary to the terminal — either confirming the maze is "perfect" (only one possible path), or listing the alternate paths found.

Because this search can take a long time on large non-perfect mazes with higher numbers of loops, it is skipped for non-perfect maps larger than 20x20, printing "Feature unavailable for maps larger than 20x20" instead. Set `VERBOSE=False` to skip this analysis entirely.

[▲ Back to Top](#table-of-contents)

---

## Code Reusability

### Reusable Components
- MazeSolver (BFS pathfinding) - Requires a populated maze grid (`list[list[int]]`) and map data
- Renderer (visual layer) - Limited reusability as it requires various external data currently provided by `App()` to function fully, but could be adapted to render similar objects in the future.
- export_map (export utility) - Requires a maze (from a mazegenerator), map data and a string with the path
- find_alt_paths (map analysis utility) - Requires a maze grid (`list[list[int]]`) and the entry/exit coordinates. Returns the number of distinct paths found and a list of their direction strings.
- MapData (configuration model) - Requires the following data to be either parsed from a config file, using `parse_config()` or instantiated separately.
```ini
width: int
height: int
entry: tuple[int, int]
exit: tuple[int, int]
output_file: str
perfect: bool
seed: int
bonus: bool
verbose: bool
```

#### MazeGenerator / MazeGeneratorBonus Reusability

In this project, the MazeGenerator code was designed modularly, in way that it could easily allow new and additional algorithms to be added relatively easily simply by creating a child class that inherits from the `MazeGenBase(ABC)` class.

To instantiate the primary DFS-based algorithm, the following are required:
- Maze data - outlined above
- pattern_42: `list[list[int]]` - this is a customizable pattern that will be embedded into the maze. 
```ini
DFS example:
    pattern_42 = [
        [1, -1, -1, -1, 1, 1, 1],    # Row 0: █ . . . █ █ █
        [1, -1, 1, -1, -1, -1, 1],   # Row 1: █ . █ . . . █
        [1, 1, 1, -1, 1, 1, 1],      # Row 2: █ █ █ . █ █ █
        [-1, -1, 1, -1, 1, -1, -1],  # Row 3: . . █ . █ . .
        [-1, -1, 1, -1, 1, 1, 1],    # Row 4: . . █ . █ █ █
    ]

Sidewinder example:
    pattern_42 = [
        [0, 6, 10, 12, 0, 0, 0],     # Row 0: █ . . . █ █ █
        [0, 1, 0, 7, 10, 8, 0],      # Row 1: █ . █ . . . █
        [0, 0, 0, 5, 0, 0, 0],       # Row 2: █ █ █ . █ █ █
        [6, 12, 0, 5, 0, 2, 10],     # Row 3: . . █ . █ . .
        [1, 5, 0, 5, 0, 0, 0],       # Row 4: . . █ . █ █ █
    ]
```
As you can see, the pattern is completely flexible in how it is implemented, according to the needs of the individual maze algorithm. The pattern_42 should be set as a class variable before the \_\_init__ definition and should be initialised in the `super().__init__()`.

    def __init__(self, data: MapData) -> None:
        """Initializes maze config."""
        super().__init__(data, pattern_42=self.pattern_42)

To instantiate the DFS-based maze generator, use:
```ini
mazeGen = MazeGenerator(map_data)
```

An instance of the MapData dataclass type object can be instantiated as:
```ini
map_data = MapData(width, height, entry, exit, output_file, perfect, seed, bonus, verbose)
```
Additional parameters can be added or removed by adjusting the MapData dataclass
```ini
Example:
@dataclass
class MapData:
    width: int
    height: int
    entry: tuple[int, int]
    exit: tuple[int, int]
    output_file: str
    perfect: bool
    seed: int
    bonus: bool
	verbose: bool
    NEW_PARAMETER: {data type}
```

and made available in the mapgenerator class by setting a class variable from data.{...} :
```ini
Example:
def __init__(self, data: MapData, pattern_42: list[list[int]]) -> None:
    """Initializes maze config and instantiates a solid wall grid."""
    self.width = data.width
    self.height = data.height
    self.NEW_PARAM = data.{param name}
```

Since the parent class is an Abstract Base Class (ABC), all inheriting children must have a gen_map method, which is what will be called to generate a new map. It is prototyped as:
```ini
def gen_map(self) -> list[list[int]]:
```

This method will contain the necessary code to generate the populated map, and will vary greatly depending on the map generation algorithm used. It should `return self.map`, to be accessed by the calling function or method
```ini
Example from DFS algorithm:
def gen_map(self) -> list[list[int]]:
    """Generates the full maze layout."""
    random.seed(self.seed)

    self._validate_point()

    start_cell = (self.height - 1, 0)

    stack: list[tuple[int, int]] = [start_cell]
    visited: set[tuple[int, int]] = {start_cell} | self.fixed_cells

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

    self._final_map_adjustment()
    return self.grid
```

This grid could then be used with utilities such as ExportMap and MazeSolver, and then rendered to the screen using Renderer

Standalone Package (mazegen)

To satisfy the project's reusability requirements, the core maze generation and solving logic (MapData, MazeGenerator, MazeGeneratorBonus, MazeSolver) is also packaged as a separate, pip-installable module called mazegen. It is fully independent of the MLX rendering code, and is built
from the mazegen/ directory and pyproject.toml at the root of this repository using python -m build, producing mazegen-1.0.0-py3-none-any.whl and mazegen-1.0.0.tar.gz (also kept at the repo root).

**Installation**

bashpip install mazegen-1.0.0-py3-none-any.whl

**Basic usage**

python
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

**Custom parameters**

width / height: grid dimensions in cells. Must be at least 8x6 for the "42" pattern to be drawn - smaller mazes silently omit it (check with generator.can_fit_42()).
entry / exit: (row, col) tuples marking the start and end cells, within the grid and not inside the "42" pattern.
perfect: True for exactly one path between any two cells, False for extra loops/multiple paths.
seed: any integer - the same seed and parameters always produce the same maze.
output_file, bonus, verbose: not used by this package; kept for compatibility with the main app's config format and default automatically.

Use MazeGeneratorBonus instead of MazeGenerator for the Sidewinder-style algorithm - it has the same constructor and gen_map() interface.

**Accessing the maze structure and a solution**

generator.gen_map() returns a list[list[int]] using the same 4-bit N/E/S/W wall bitmask described in the Maze Bitmask Reference Key above (1 = wall closed, 0 = wall open). Note this is not the same format as output_maze.txt.

MazeSolver(grid, data).generate_final_path() returns (path_cells, path_directions): the ordered list of (row, col) cells from entry to exit, and a string of "N"/"E"/"S"/"W" steps describing that path (e.g. "ESSWN").

Full usage details and the bitmask table are also documented in mazegen/README.md, which is included as the package's own README.


### Extension Guidelines
- Add new generators by matching grid format + bitmask encoding
- Solver works with any compatible grid
- Renderer extended via UI_state
- Config extensible via MapData updates

[▲ Back to Top](#table-of-contents)

---

## Resources & AI Usage

### Technical References

* [Maze Algorithms — Jamis Buck](https://www.jamisbuck.org/mazes/) — Interactive demonstrations and explanations of many maze generation algorithms, including Recursive Backtracking, Sidewinder, Prim's, Kruskal's, Wilson's, and more.
* [Maze Generation: Sidewinder Algorithm — Jamis Buck](https://weblog.jamisbuck.org/2011/2/3/maze-generation-sidewinder-algorithm.html) — Detailed explanation of the Sidewinder algorithm, including implementation details and discussion of its strengths and weaknesses.
* [Maze Generation Algorithm — Wikipedia](https://en.wikipedia.org/wiki/Maze_generation_algorithm) — Overview of common maze generation approaches including DFS, Prim's, Kruskal's, Eller's, Binary Tree, and Sidewinder algorithms.
* [Breadth-First Search (BFS) — Wikipedia](https://en.wikipedia.org/wiki/Breadth-first_search) — Reference for the shortest-path algorithm used to solve the maze.
* [Depth-First Search (DFS) — Wikipedia](https://en.wikipedia.org/wiki/Depth-first_search) — Background information on DFS traversal, which forms the basis of the recursive backtracker maze generator.
* [Deque — Python Documentation](https://docs.python.org/3/library/collections.html#collections.deque) — Documentation for the queue structure used by the BFS pathfinding implementation.
* [Dataclasses — Python Documentation](https://docs.python.org/3/library/dataclasses.html) — Reference for the `@dataclass` structures used throughout the project for configuration and UI state management.
* Mlx documentation provided in the whl file

### AI Usage & Attributions
* **Tasks Delegated to AI:** 
	- Designing the format of the README
	- Providing a breakdown of the functions of the MLX wrapper
	- Brainstorming ideas for the find_alt_paths algorithm (DFS vs BFS, iterative vs recursive)
	- Debugging MLX related errors
	- Gathering information relating to things such as different algorithms for maze generation and solving, bit operations, math related to rendering pixels to the screen with MLX etc
	
* **Project Areas Impacted:** 
	- README.md
	- Assistance in understanding how to render the PNG sprite to the screen and animation loops in mlx_render.py
	- find_alt_paths (map analysis utility)

[▲ Back to Top](#table-of-contents)

---

## Team & Project Management

### Team Roles & Responsibilities
* **speterse:**

  Team leader. Creation of the App() class and the overall structure of how the program would run. Handled the entirety of the graphical rendering using the MiniLibX (MLX) library. He developed the primary maze-generation algorithm as well as the pathfinding  and find_alt_paths algorithms used to solve for the optimal route. Additionally, he implemented all real-time interactive features. One of his most innovative contributions was engineering the path animation featuring a small fish that automatically scales its size based on the dimensions of the maze cells. He also took charge of code readability. A fantastic teammate all around!

* **ikryvenk:**

  Awesome partner. Spearheaded the robust configuration file parser, ensuring all inputs are validated against project constraints. He implemented the bonus maze-generation algorithm and wrote the core post-processing logic required to transform perfect mazes into non-perfect ones by safely introducing loops. Took charge of refactoring parent-child relationshiips of the maze generation logic.

  NB: Various other tasks were performed collaboratively, and each task was cross-checked by the other person.

### Project Planning & Evolution

From the start, speterse took leadership of the project. Due to different levels of progression in the python modules, tasks were roughly divided based on progression:
* speterse: setting up the overall Mazegenerator() and App() class structures, implementing the original maze generation logic
* ikryvenk: data parsing, continuous testing and debugging, README

As the project advanced, speterse decided to implement the MiniLibX module to render the map to the screen rather than rendering to the terminal. This decision was made for a few reasons:
1. Interest in learning how to render pixels to the screen
2. Greater flexibility and control in exactly how the maze would be rendered (not restricted to ASCII representations)
3. Allowed for animation using a PNG (decision to add animation was made after the map rendering itself was stabilised)
4. Overall visually impressive output

Workflow was controlled via an online repository hosted on GitHub. The primary version of the code was kept on a "Testing" branch, with several other branches made as the project progressed.
Although we worked on our respective tasks somewhat independently, we met several times to discuss progress and to identify remaining tasks and contacted each other via slack.

In regards to anticipated milestones, it was hoped that the project could be finished by June 11th, knowing that we have other external commitments to also take care of. However, due to some major bugs, an extra few days were required to finish debugging and refactoring of the code.

### Retrospective
* **What Worked Well:** 
* Both team members were committed to the project and actively worked on their respective parts. 
* Our collaboration style was mainly to to work individually on most of the tasks, but also keep an open communication line and discuss things face-to-face, which really helped to keep the project going smoothly overall.
* When one person finished a task, they checked with the other what else needed to be done, which meant both members were always actively working on something.

* **Areas for Improvement:**
* Unfortunately, at the start, there was a bit of miscommunication about the workflow regarding testing branch and individual sub-branches on GitHub, causing work to be pushed to the wrong branch.
* Also, there was a situation where a section of the code had been refactored differently on each of our respective branches, which posed a challenge when it came time to resolving merge conflicts between the 2 versions.
* As team leader, I should have taken extra care to go over these things, both at the start of and during the project.
* The original DFS algorith had the '42' logo in the middle, however it was proving difficult to implement the bonus algorith while keeping it in the middle. A compromise was reached that both algorithms would position the logo in the top left corner of the map. If I did this project again, I would like to have had more time to explore a way to make it work for both algorithms to be able to have the logo in the center instead.

### Toolkit
The code was hosted on a GitHub repository, and in general it worked ok by having a testing branch and then making sub-branches from the testing branch.
We used the provided 'output_validator.py' checker as well as manual checking of the output_maze.txt file to ensure the integrity of cell-pair walls were being maintained and respected.

[▲ Back to Top](#table-of-contents)