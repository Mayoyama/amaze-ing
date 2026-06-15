"""mazegen - a standalone 2D maze generator and solver.

Extracted from the A-Maze-ing project. See the package README for
usage examples.
"""

from .map_data import MapData
from .base import MazeGenBase
from .generator import MazeGenerator
from .generator_bonus import MazeGeneratorBonus
from .solver import MazeSolver

__all__ = [
    "MapData",
    "MazeGenBase",
    "MazeGenerator",
    "MazeGeneratorBonus",
    "MazeSolver",
]

__version__ = "1.0.0"
