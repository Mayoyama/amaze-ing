from MazeGenerator import MazeGenerator
import random
from typing import Any


STARTING_CONFIG = {
    "width": 70,  # Tip: Stick to odd numbers for grid-based wall carving
    "height": 11,
    "seed": random.randint(1, 256),
    "start": (2, 0),
    "end": (10, 60),
    "perfect": True
}

#def render_map_terminal(maze: MazeGenerator, config: dict[Any]) -> None:
