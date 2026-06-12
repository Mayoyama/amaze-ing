from dataclasses import dataclass
import sys

@dataclass
class mapData:
    width: int
    height: int
    entry: tuple[int, int]
    exit: tuple[int, int]
    output_file: str
    perfect: bool
    seed: int
    bonus: bool

def parse_config() -> mapData:
    def found_value(param: str, value: str) -> int:
        if (value.isnumeric()):
            return (int(value))
        else:
            if len(value) == 0:
                value = "Empty value"
            raise ValueError(f"{param}: {value} is not valid")
            
    def inputfile() -> str:
        if len(sys.argv) != 2:
            print("You should give one argument to the program. Example: python3 a_maze_int.py <file.name>", file=sys.stderr)
            sys.exit(1)
        return sys.argv[1]

    # IO layer
    try:
        with open(inputfile(), "r") as file:
            lines = file.readlines()
    except (FileNotFoundError, PermissionError, IsADirectoryError) as e:
        print(f"Cannot access config file: {e}", file=sys.stderr)
        sys.exit(1)

    entry: tuple[int, int] = (0, 0)
    exit: tuple[int, int] = (0, 0)
    nbr_line = 0
    for line in lines:
        if line.strip() == '' or line.startswith("#"):
            continue

        if (line.startswith("WIDTH=") and nbr_line == 0):
            width: int = found_value("WIDTH", line[6:].strip())
            nbr_line += 1

        elif (line.startswith("HEIGHT=") and nbr_line == 1):
            height: int = found_value("HEIGHT", line[7:].strip())
            nbr_line += 1

        elif line.startswith("ENTRY=") and nbr_line == 2:
            entry_parts = line[6:].split(',')
            if len(entry_parts) != 2:
                raise ValueError("ENTRY: value should be 'ENTRY=x,y'")
            # config format: (x, y), user inputs top-left corner as (1, 1)
            entry_x: int = found_value("ENTRY (x,y)", entry_parts[0].strip())
            entry_y: int = found_value("ENTRY (x,y)", entry_parts[1].strip())
            if entry_x <= 0 or entry_y <= 0:
                raise ValueError("ENTRY: co-ordinate values must be >= 1")

            # internal format: (row, col) = (y, x), top-left as (0, 0)
            entry = (entry_y - 1, entry_x - 1)
            nbr_line += 1

        elif line.startswith("EXIT=") and nbr_line == 3:
            exit_parts = line[5:].split(',')
            if len(exit_parts) != 2:
                raise ValueError("EXIT: value should be 'EXIT=x,y'")
            # config format: (x, y), user inputs top-left corner as (1, 1)
            exit_x: int = found_value("EXIT (x,y)", exit_parts[0].strip())
            exit_y: int = found_value("EXIT (x,y)", exit_parts[1].strip())
            if exit_x <= 0 or exit_y <= 0:
                raise ValueError("EXIT: co-ordinate values must be >= 1")

            # internal format: (row, col) = (y, x), top-left as (0, 0)
            exit = (exit_y - 1, exit_x - 1)
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
            """
            DEBUGGING
            """

            seed: int = found_value("SEED", line[5:].strip())  # randint(1,100)
            nbr_line += 1

        elif (line.startswith("BONUS=") and nbr_line == 7):
            if (line[6:].strip() == "True"):
                bonus = True
            elif (line[6:].strip() == "False"):
                bonus = False
            else:
                raise ValueError("Bonus: must be either 'True' or 'False'")
        else:
            raise ValueError("Invalid, empty, or out-of-order "
                             "configuration field(s)")
    if nbr_line != 7:
        raise ValueError("Invalid, empty, or out-of-order configuration "
                         "field(s)")

    # Ensure dimensions are positive
    if width <= 0 or height <= 0:
        raise ValueError("Width and height must be positive")

    # Set maximum allowed dimensions to 50
    if width > 100 or height > 100:
        raise ValueError("Maximum size of map is 100")

    # Validate that ENTRY is inside map bounds
    if not (0 <= entry[0] < height and 0 <= entry[1] < width):
        raise ValueError("ENTRY is outside map bounds")

    # Validate that EXIT is inside map bounds
    if not (0 <= exit[0] < height and 0 <= exit[1] < width):
        raise ValueError("EXIT is outside map bounds")

    # Validate that EXIT and ENTRY is in different point
    if (exit == entry):
        raise ValueError("EXIT and ENTER should be different points")

    return mapData(width, height, entry, exit, output_file,
                   perfect, seed, bonus)
