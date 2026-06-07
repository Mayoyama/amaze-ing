from MazeGenerator import MazeGenerator
from map_data import parse
from typing import Any
from mlx_render import mlx_render




if __name__ == "__main__":
    map_data = parse()
	
    mazeGen = MazeGenerator(map_data)
    try:
        newmaze = mazeGen.gen_map()
        mlx_render(newmaze)
        #  newmaze.render_terminal()    old, dont use
    except ValueError as e:
        print(e)
