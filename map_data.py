from dataclasses import dataclass
from MazeGenerator import MazeGenerator

TEMP_CONFIG = {
    "width": 21,  # THIS GLOBAL NEEDS TO BE REPLACED BY PARSED DATA
    "height": 21,
    "entry": (2, 10),
    "exit": (10, 2),
    "output_file": "",
    "seed": 42,
    "perfect": True
}

class mapData:
    def __init__(self, width: int, height: int, entry: tuple[int, int], exit: tuple[int, int], output_file: str, perfect: bool, seed: int) -> None:
        self.width = width
        self.height = height
        self.entry = entry
        self.exit = exit
        self.output_file = output_file
        self.perfect = perfect
        self.seed = seed


'''
insert parse function from config.txt
'''
def parse() -> mapData:
    def found_value(string: str) -> int:
        if (string.isnumeric()):
            return(int(string))
        else:
            raise TypeError(f"{string} is not acceptable. Only integers are allowed")
    try:
        nbr_line: int = 0
        with open("config.txt", "r") as file:
            while True:
                line: str = file.readline()
                if not line:
                    break
                if line[0] != '#':
                    if (line.startswith("WIDTH=") and nbr_line == 0):
                        width: int = found_value(line[6:].strip('\n'))
                        nbr_line += 1
                    elif (line.startswith("HEIGHT=") and nbr_line == 1):
                        height: int = found_value(line[7:].strip('\n'))
                        nbr_line += 1
                    elif (line.startswith("ENTRY=") and nbr_line == 2):
                        entry_list: list[str] = line[6:].rsplit(',')
                        if (len(entry_list) != 2):
                            raise Exception("For ENTRY, value should be 'EMTRY=x,y'")
                        x_entry: int = found_value(entry_list[0].strip('\n'))
                        y_entry: int = found_value(entry_list[1].strip('\n'))
                        entry: tuple[int, int] = (x_entry, y_entry)
                        nbr_line += 1
                    elif (line.startswith("EXIT=") and nbr_line == 3):
                        exit_list: list[str] = line[5:].rsplit(',')
                        if (len(exit_list) != 2):
                            raise Exception("For EXIT, value should be 'EXIT=x,y'")
                        x_exit: int = found_value(exit_list[0].strip('\n'))
                        y_exit: int = found_value(exit_list[1].strip('\n'))
                        exit: tuple[int, int] = (x_exit, y_exit)
                        nbr_line += 1
                    elif (line.startswith("OUTPUT_FILE=") and nbr_line == 4):
                        output_file: str = line[12:].strip('\n')
                        if (output_file == ''):
                            raise Exception("OUTPUT_FILE can not be empty!")
                        nbr_line += 1
                    elif (line.startswith("PERFECT=") and nbr_line == 5):
                        if (line[8:].strip('\n') == "True"):
                            perfect: bool = True
                        elif (line[8:].strip('\n') == "False"):
                            perfect: bool = False
                        else:
                            raise Exception("Please put PERFECT correctly!")
                        nbr_line += 1
                    elif (line.startswith("SEED=") and nbr_line == 6):
                        seed: int = found_value(line[5:].strip('\n'))
                    else:
                        raise Exception("Not all value was given correctly or there is some empty line!")
        if nbr_line == 6:
            map: mapData = mapData(width, height, entry, exit, output_file, perfect, seed)
            if width > 25 or height > 25:
                raise Exception("Maximum size of map is 25")
            return(map)
        else:
            raise Exception("Not all value was given correctly!")
    except (FileNotFoundError, PermissionError, Exception, TypeError) as e:
        raise e

def print_map(maze: MazeGenerator, map_data: mapData) -> None:
    """Display a map and key point on output file"""
    try:
        with open(map_data.output_file, "w") as file:
            for row in maze.grid:
                for col in row:
                    file.write(hex(col)[2:].upper())
                file.write("\n")
            file.write("\n")
            file.write(repr(maze.start_point[0]) + ',' + repr(maze.start_point[1]) + '\n')
            file.write(repr(maze.end_point[0]) + ',' + repr(maze.end_point[1]))
    except (FileNotFoundError, PermissionError) as e:
        raise Exception(f"Error opening file '{map_data.output_file}': {e}")


def temp_data() -> mapData: #TO DELETE
    return mapData(**TEMP_CONFIG)


