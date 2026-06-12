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
The goal of this project is to generate a maze, render it using a **graphical display via the MiniLibX (MLX) library**, find the optimal path from start to finish, and display that solution on the screen.

### Overview
* **Language:** Written in Python 3.10.
* **Generation & Reproducibility:** The maze is randomly generated, but supports full reproducibility using a seed. 
* **Cell Structure:** Each cell in the maze has between 0 and 4 walls corresponding to the cardinal points (North, East, South, West).
* **Features:** 
  * The maze features a visible "42" pattern drawn by several fully closed cells (and yes, you can customize its color! *\_*).
  * Supports the creation of both **perfect maps** (exactly one valid path) and **non-perfect maps** (multiple possible paths/loops).
* **Storage:** Cells are stored sequentially row by row, with one row per line.

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
* **15** (`0xF` / `1111`) $\rightarrow$ All 4 walls **CLOSED** (Initial grid state)
* **0** (`0x0` / `0000`) $\rightarrow$ Crossroads; all 4 walls **OPEN**
* **11** (`0xB` / `1011`) $\rightarrow$ South wall is **OPEN**; North, East, and West are **CLOSED**
* **10** (`0xA` / `1010`) $\rightarrow$ East and West **CLOSED**; North and South **OPEN** (Vertical Hallway)

---

* After the executing, we print in output file our maze using a hexadecimal wall representation, entry and exit point, the good path.

[▲ Back to Top](#table-of-contents)

---

## Instructions

### Prerequisites
<!-- List any system dependencies, Python version requirements, or terminal requirements here -->
* **OS:** Linux or macOS (required for MiniLibX compatibility).
* **Language:** Python 3.10 or higher.
* **Python Packages:** `mypy` and `flake8` (for linting and development).

### Installation / Setup
To install the project, clone the repository and run the setup command in your terminal:

```bash
git clone <repository-url>
cd amaze-ing
make install
```

All the required dependencies and files will be automatically installed.

### Execution

To run the program execute:

```bash
make run
```

You can also use the following development and utility commands:

* make debug — Launches the program in debug mode with verbose logging.

* make clean — Cleans up temporary files and deletes the .mypy_cache folder.

* make lint — Runs flake8 and mypy with the required flags to check for code style and type compliance.

* make lint_strict — Performs the same checks as make lint, but enforces mypy with the --strict flag.


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

Note: You can include comments in the configuration file; lines starting with # will be ignored.

### Complete Template
```ini
# Example configuration structure mapping variables.
WIDTH=22
HEIGHT=20
ENTRY=1,1
EXIT=17,19
OUTPUT_FILE=output_maze.txt
PERFECT=False
SEED=45
BONUS=False
```

### Constraints & Validation Rules

To ensure stability, proper rendering performance, and logical consistency, the configuration file must adhere to the following rules:

* **Dimensions:**  Width and height must be integers between $0$ and $75$.
    * *Reasoning:*  Setting dimensions higher than 75 significantly degrades performance during the graphical MiniLibX (MLX) animation, as the entire maze grid is redrawn on every single frame.

* **Coordinates:** * The entry and exit points must be located strictly within the bounds of the map.
  * The entry and exit coordinates cannot be identical.
  * The entry and exit points cannot overlap with any cells designated for the "42" pattern.

* **Special Rules:** 
  * **SEED**: Must be a valid integer. Providing the same seed ensures identical maze generation for testing and reproducibility.
  * **PERFECT & BONUS**: These flags must strictly be set to either `True` or `False`.

[▲ Back to Top](#table-of-contents)

---

## Technical Design & Algorithms

### Chosen Maze Generation Algorithm
<!-- Specify the concrete algorithm implemented for maze generation -->

### Selection Justification
<!-- Explain the specific reasons why this algorithm was chosen for the architectural scope of the project -->

### Pathfinding Solver
<!-- Describe the shortest-path algorithm utilized to find the exit route -->

### Chosen Maze Generation Algorithm for Bonus

For the bonus algorithm, we implemented a modified variation of the **Sidewinder algorithm**. The generation process iterates through the grid row by row from top to bottom, and from right to left. For each individual cell, the algorithm makes a randomized decision on whether to destroy the eastern (right) wall or the southern (bottom) wall. As it processes each cell, it actively checks the state of its neighbors and merges them accordingly into sets. 

A distinct structural feature (and limitation) of this algorithm is its inherent geometric bias: because of the way boundaries are handled at the edges, the **far-right corridor** and the **bottom row** of the maze will always be completely open and devoid of intersecting walls.

#### Selection Justification

This algorithm was interesting to implement, it was easy to understand, it is totally different of our main algrithm, and it was compatible with our 42 pattern(but we moved it to the top right corner).

### Non-perfect map

Both our algorithme create a perfect map. So for do non-perfect map we destroy some of the cells(we decide by rondom how many cells we want to destroy from 5 to 15), after we look again in all the cells and checks the neighbours, if needed we change it. We also created one protected box for not distroy 42 pattern.

[▲ Back to Top](#table-of-contents)

---

## Advanced Features & Controls

When rendering the maze using the MiniLibX (MLX) graphical interface, you can interact with the program in real-time using the following keyboard shortcuts:

* **Key [1]**: Change the primary maze color.
* **Key [2]**: Change the "42" pattern color.
* **Key [3]**: Toggle the visibility of the shortest path (Show/Hide).
* **Key [4]**: Toggle the path-solving animation.
* **Key [5]**: Generate a new **perfect map** using the primary algorithm.
* **Key [6]**: Generate a new **non-perfect map** using the primary algorithm.
* **Key [7]**: Generate a new **perfect map** using the bonus algorithm.
* **Key [8]**: Generate a new **non-perfect map** using the bonus (Sidewinder) algorithm.
* **Key [ESC]**: Safely exit the program and close the graphical window.

[▲ Back to Top](#table-of-contents)

---

## Code Reusability

### Reusable Components
<!-- List specific classes, helper modules, or functional structures that were built to be modular -->

### Extension Guidelines
<!-- Explain how these components can be reused or extended for future programming scopes or projects -->

[▲ Back to Top](#table-of-contents)

---

## Resources & AI Usage

### Technical References
* [Reference Name](URL) — *Brief description of what this documentation/article provided.*
* [Reference Name](URL) — *Brief description of what this documentation/article provided.*

### AI Usage & Attributions
* **Tasks Delegated to AI:** <!-- Specify which architectural patterns or logic steps utilized AI assistance -->
* **Project Areas Impacted:** <!-- Specify the exact files or components built using AI tools -->

[▲ Back to Top](#table-of-contents)

---

## Team & Project Management

### Team Roles & Responsibilities
* **speterse:**

  Handled the entirety of the graphical rendering using the MiniLibX (MLX) library. He developed the primary maze-generation algorithm as well as the pathfinding algorithm used to solve for the optimal route. Additionally, he implemented all real-time interactive features. One of his most innovative contributions was engineering the path animation featuring a small fish that automatically scales its size based on the dimensions of the maze cells. He also took charge of code readability and refactoring. A fantastic teammate all around!

* **ikryvenk:**

  Spearheaded the robust configuration file parser, ensuring all inputs are validated against project constraints. He implemented the bonus maze-generation algorithm and wrote the core post-processing logic required to transform perfect mazes into non-perfect ones by safely introducing loops.

<!--I propose to delete this part-->

<!--### Project Planning & Evolution
<!-- Detail the initial anticipated milestones, schedule constraints, and how the workflow evolved dynamically through development -->

<!--### Retrospective
* **What Worked Well:** <!-- Detail successful project choices, collaboration strategies, or design patterns -->
<!--* **Areas for Improvement:** Detail what was challenging and how workflows could be optimized next time-->

<!--### Toolkit
List any specific workflow tools, version control mechanisms, tracking systems, or environment checkers used-->

[▲ Back to Top](#table-of-contents)