from MazeGenerator.MazeGenerator import MazeGenerator
from MazeGenerator.MazeGeneratorBonus import MazeGeneratorBonus
from MapData import MapData


def export_map(maze: MazeGenerator | MazeGeneratorBonus,
               map_data: MapData, path: str) -> None:
    """Writes the generated maze and its solution to the output file.

    The file format is: each grid row as a line of uppercase hex
    digits (one per cell, encoding its N/E/S/W wall bitmask), followed
    by a blank line, the start cell's "row,col" coordinates, the end
    cell's "row,col" coordinates, and finally the solution path as a
    direction string.

    Args:
        maze: The maze generator whose grid, start_point, and
            end_point are written.
        map_data: Parsed configuration; used for the output file path.
        path: The solution path as a direction string (e.g. "ESSWN").

    Raises:
        Exception: If the output file cannot be opened for writing.
    """
    try:
        with open(map_data.output_file, "w") as file:
            for row in maze.grid:
                for col in row:
                    file.write(hex(col)[2:].upper())
                file.write("\n")
            file.write("\n")
            file.write(f"{maze.start_point[0]},{maze.start_point[1]}\n")
            file.write(f"{maze.end_point[0]},{maze.end_point[1]}\n")
            file.write(f"{path}")
    except (FileNotFoundError, PermissionError) as e:
        raise Exception(f"Error opening file '{map_data.output_file}': {e}")
