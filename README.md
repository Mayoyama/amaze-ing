*This project has been created as part of the 42 curriculum by speterse[, ikryvenk].*

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
The goal of this project is to generate, solve, and visually render 2D mazes based on a configuration file. The system produces a deterministic maze (based on a seed), finds the shortest path between entry and exit points, and displays the result using a graphical interface.

### Overview
The program follows a full pipeline:

1. A configuration file is parsed into a structured `mapData` object.
2. A maze grid is generated using either a standard generator or a bonus variant.
3. The grid encodes walls using bitwise values per cell.
4. A BFS-based solver computes the shortest path between ENTRY and EXIT.
5. The maze is rendered in a graphical window using MLX, including optional overlays such as the solution path, a sprite animation along the path, and a fixed “42” pattern embedded into the maze.
6. The final maze and solution can also be exported to a text file.

[▲ Back to Top](#table-of-contents)

---

## Instructions

### Prerequisites
- Python 3.10+
- A Unix-like environment (required for MLX usage)
- A 'python -m venv' named maze_venv 
- A working installation of MLX provided via local wheel (`mlx-2.2-py3-none-any.whl`)

### Installation / Setup
```bash
git clone <repository-url>
make install
source maze_venv/bin/activate 
```

This creates a virtual environment (`maze_venv`) and installs all dependencies including MLX.

### Execution
```bash
make run
```
or directly:
```bash
python3 a_maze_ing.py config.txt
```

### Linters (Flake8 and Mypy)
```bash
make lint
```
or:
```bash
make lint-strict
```

## Uninstallation
```bash
make uninstall
```

[▲ Back to Top](#table-of-contents)

---

## Configuration File Structure

### Format Specification
The configuration file is a strict ordered key-value format.

Format:
KEY=VALUE

### Complete Template with Example
WIDTH=20
HEIGHT=20
ENTRY=10,10
EXIT=15,15
OUTPUT_FILE=output_maze.txt
PERFECT=True
SEED=1
BONUS=False

### Constraints & Validation Rules

- Dimensions: WIDTH/HEIGHT must be > 0, max 100x100
- Coordinates: ENTRY/EXIT must be inside bounds and must not overlap neither each other, nor the "42" logo
- Seed: used for deterministic generation
- PERFECT: toggles perfect maze generation
- BONUS: selects alternative algorithm's generator
- OUTPUT_FILE: must be non-empty

[▲ Back to Top](#table-of-contents)

---

## Technical Design & Algorithms

### Maze Generation Algorithm
The primary generator uses a Depth-First Search (DFS) backtracking algorithm implemented with an explicit stack.

The algorithm begins at a starting cell and repeatedly moves to a randomly chosen unvisited neighbor, removing the wall between the two cells. When a cell has no unvisited neighbors remaining, the algorithm backtracks to the most recent cell with unexplored paths and continues the process. This continues until all reachable cells have been visited, producing a fully connected maze. When perfect maze generation is enabled, there is exactly one unique path between any two points in the maze.

The bonus generator follows a different approach based on structured grid initialization with randomized carving behavior. Instead of progressively exploring cells through DFS, each cell is initialized according to predefined rules and random wall removals. Additional post-processing steps are then applied to maintain connectivity and improve the final maze layout while preserving special structures such as the embedded "42" pattern.

### Justification
DFS backtracking is used because:
- Produces perfect mazes when enabled
- Simple stack-based implementation
- Deterministic with seed
- Produces long corridors

### Pathfinding
Breadth-First Search (BFS) is used to guarantee shortest path in an unweighted grid.

BFS is a graph traversal algorithm that explores all possible positions in a maze level by level. Starting from the entry point, it first visits all directly reachable neighboring cells, then expands outward to their neighbors, and so on. This “layer-by-layer” exploration ensures that the first time the exit is reached, the path taken is the shortest possible in terms of number of steps.

In this project, BFS keeps track of visited cells and records the previous cell for each step, allowing the final path to be reconstructed by backtracking from the exit to the entry once the search completes

[▲ Back to Top](#table-of-contents)

---

## Advanced Features

<!-- If you implemented optional or advanced features (multiple generation algorithms, terminal display configurations, or specific graphical options), detail them here -->
- Bonus maze algorithm generator variant - 
- MLX-based graphical rendering - This project uses a python wrapper for C-based MiniLibX (MLX) for rendering the maze to the screen
- Animated sprite traversal along path - Using in-built functions from MLX, the user can start, pause and restart the animation of a fish sprite, which follows the path from the start to the end 
- Maze type swap menu options - 4 options are available for the user to freely swap between DFS and line-based algorithms, both perfect and non-perfect
- Export of maze + solution path to text file - Upon each maze generation, a file output_maze.txt will be generated and populated with a hex representation of the cell values, the start and end coordinates and the directions of how to move between the start and end points.

[▲ Back to Top](#table-of-contents)

---

## Code Reusability

### Reusable Components
- MazeGenerator / MazeGeneratorBonus
- MazeSolver (BFS pathfinding)
- Renderer (visual layer)
- mapData (configuration model)
- print_map (export utility)

### Extension Guidelines
- Add new generators by matching grid format + bitmask encoding
- Solver works with any compatible grid
- Renderer extended via UI_state
- Config extensible via mapData updates

[▲ Back to Top](#table-of-contents)

---

## Resources & AI Usage

### Technical References
* [Reference Name](URL) — *Brief description of what this documentation/article provided.*
* [Reference Name](URL) — *Brief description of what this documentation/article provided.*

### AI Usage & Attributions
* **Tasks Delegated to AI:** 
	- Designing the format of the README
	- Providing a breakdown of the functions of the MLX wrapper 
	- Debugging MLX related errors
	- Gathering information relating to things such as different algorithms for maze generation and solving, bit operations, math related to rendering pixels to the screen with MLX etc
	
* **Project Areas Impacted:** <!-- Specify the exact files or components built using AI tools -->
	- README.md
	- Assistance in rendering the sprite to the screen and animation loops in mlx_render.py

[▲ Back to Top](#table-of-contents)

---

## Team & Project Management

### Team Roles & Responsibilities
* **Member 1 (Role/Title):** <!-- Outline specific ownership areas, e.g., Engine, Algorithms -->
* **Member 2 (Role/Title):** <!-- Outline specific ownership areas, e.g., Parser, Rendering -->

### Project Planning & Evolution
<!-- Detail the initial anticipated milestones, schedule constraints, and how the workflow evolved dynamically through development -->

### Retrospective
* **What Worked Well:** <!-- Detail successful project choices, collaboration strategies, or design patterns -->
* **Areas for Improvement:** <!-- Detail what was challenging and how workflows could be optimized next time -->

### Toolkit
<!-- List any specific workflow tools, version control mechanisms, tracking systems, or environment checkers used -->

[▲ Back to Top](#table-of-contents)
