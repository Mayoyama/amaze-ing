from MazeGenerator import MazeGenerator
from map_data import temp_data
from typing import Any
from mlx_render import App
from collections import deque
from mazeSolver import MazeSolver



if __name__ == "__main__":
    map_data = temp_data()
	
    mazeGen = MazeGenerator(map_data)
    app = App()
    try:
        app.run()
        newmap = app.renderer.grid
        solver = MazeSolver(newmap, map_data)
        solution = solver.generate_final_path
        print(solution)
        # newmaze = mazeGen.gen_map()
        # solver = MazeSolver(newmaze, map_data)
        # parent = solver._search_path()
        # print(solver.end in parent)
        # print(parent[solver.end])


    except ValueError as e:
        print(e)
