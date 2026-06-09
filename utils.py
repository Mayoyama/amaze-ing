from MazeGenerator.MazeGenerator import MazeGenerator
from map_data import mapData

def print_map(maze: MazeGenerator, map_data: mapData, path: str) -> None:
    """Display a map and key point on output file"""
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
