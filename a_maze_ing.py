from MazeGenerator import MazeGenerator
from map_data import temp_data
from typing import Any
from mlx_render import App
from collections import deque
from mazeSolver import MazeSolver



if __name__ == "__main__":
    app = App()
    try:
        app.run()



    except ValueError as e:
        print(e)
