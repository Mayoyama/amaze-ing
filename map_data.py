from dataclasses import dataclass
# 
from typing import Any


@dataclass
class mapData:
    width: int
    height: int
    entry: tuple[int, int]
    exit: tuple[int, int]
    output_file: str
    perfect: bool
    seed: int


def parse_config() -> mapData:
    def found_value(string: str) -> int:
        if (string.isnumeric()):
            return (int(string))
        else:
            raise ValueError(f"{string} is not valid. Only integers are "
                             "allowed")

    # IO layer
    try:
        with open("config.txt", "r") as file:
            lines = file.readlines()
    except (FileNotFoundError, PermissionError, IsADirectoryError) as e:
        raise OSError("Cannot access config file") from e

    nbr_line = 0
    for line in lines:
        if line.strip() == '':
            continue
        if line.startswith("#"):
            continue
        if (line.startswith("WIDTH=") and nbr_line == 0):
            width: int = found_value(line[6:].strip())
            nbr_line += 1
        elif (line.startswith("HEIGHT=") and nbr_line == 1):
            height: int = found_value(line[7:].strip())
            nbr_line += 1
        elif (line.startswith("ENTRY=") and nbr_line == 2):
            entry_list: list[str] = line[6:].split(',')
            if (len(entry_list) != 2):
                raise ValueError("ENTRY: value should be 'ENTRY=x,y'")
            x_entry: int = found_value(entry_list[0].strip())
            y_entry: int = found_value(entry_list[1].strip())
            entry: tuple[int, int] = (x_entry, y_entry)
            nbr_line += 1
        elif (line.startswith("EXIT=") and nbr_line == 3):
            exit_list: list[str] = line[5:].split(',')
            if (len(exit_list) != 2):
                raise ValueError("EXIT: value should be 'EXIT=x,y'")
            x_exit: int = found_value(exit_list[0].strip())
            y_exit: int = found_value(exit_list[1].strip())
            exit: tuple[int, int] = (x_exit, y_exit)
            nbr_line += 1
        elif (line.startswith("OUTPUT_FILE=") and nbr_line == 4):
            output_file: str = line[12:].strip()
            if (output_file == ''):
                raise ValueError("OUTPUT_FILE: value can not be empty")
            nbr_line += 1
        elif (line.startswith("PERFECT=") and nbr_line == 5):
            if (line[8:].strip() == "True"):
                perfect = True
            elif (line[8:].strip() == "False"):
                perfect = False
            else:
                raise ValueError("PERFECT: must be either 'True' or 'False'")
            nbr_line += 1
        elif (line.startswith("SEED=") and nbr_line == 6):
            seed: int = found_value(line[5:].strip())
            nbr_line += 1
        else:
            raise ValueError("Invalid, empty, or out-of-order "
                             "configuration field(s)")
    if nbr_line != 7:
        raise ValueError("Invalid, empty, or out-of-order configuration "
                         "field(s)")

    # CHANGE: Ensure dimensions are positive
    if width <= 0 or height <= 0:
        raise ValueError("Width and height must be positive")

    # CHANGE: Set maximum allowed dimensions to 50
    if width > 50 or height > 50:
        raise ValueError("Maximum size of map is 50")

    # CHANGE: Validate that ENTRY is inside map bounds
    if not (0 <= entry[0] < width and 0 <= entry[1] < height):
        raise ValueError("ENTRY is outside map bounds")

    # CHANGE: Validate that EXIT is inside map bounds
    if not (0 <= exit[0] < width and 0 <= exit[1] < height):
        raise ValueError("EXIT is outside map bounds")

    return mapData(width, height, entry, exit, output_file, perfect, seed)
