from MazeGenerator import MazeGenerator
import random


STARTING_CONFIG = {
    "width": 70,  # Tip: Stick to odd numbers for grid-based wall carving
    "height": 11,
    "seed": random.randint(1, 256),
    "start": (2, 0),
    "end": (10, 60),
    "perfect": True
}

if __name__ == "__main__":
    newmaze = MazeGenerator(STARTING_CONFIG["width"], STARTING_CONFIG["height"], STARTING_CONFIG["seed"],
                            STARTING_CONFIG["start"], STARTING_CONFIG["end"], STARTING_CONFIG["perfect"])
    try:
        newmaze.gen_map()
        newmaze.render_terminal()
    except ValueError as e:
        print(e)
