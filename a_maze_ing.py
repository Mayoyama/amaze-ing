from MazeGenerator import MazeGenerator
from map_data import temp_data
from typing import Any
from mlx_render import mlx_render




if __name__ == "__main__":
    map_data = temp_data()
	
    mazeGen = MazeGenerator(map_data)
    try:
        newmaze = mazeGen.gen_map()
        mlx_render(newmaze)

    except ValueError as e:
        print(e)
