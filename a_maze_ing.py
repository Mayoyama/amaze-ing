from MazeGenerator import MazeGenerator
from map_data import temp_data
from typing import Any




if __name__ == "__main__":
    map_data = temp_data()
	
    newmaze = MazeGenerator(map_data)
    try:
        newmaze.gen_map()
        #  newmaze.render_terminal()    old, dont use
    except ValueError as e:
        print(e)
