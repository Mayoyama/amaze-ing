from mlx import Mlx
from MazeGenerator import MazeGenerator
from mazeSolver import MazeSolver
from map_data import parse_config, mapData
from dataclasses import dataclass
import random
import os
from utils import print_map


@dataclass
class render_settings:
    """
    Stores rendering configuration values such as window dimensions
    and maze cell size.
    """
    
    width: int = 1600
    height: int = 1000
    cell_size: int = 10
# maze size  = maze size + menu!!!


@dataclass
class UI_state:
    """
    Stores mutable UI settings including colors and display toggles
    used by the renderer.
    """
    wall_color: tuple[int, int, int] = (0, 255, 0)
    logo42_color: tuple[int, int, int] = (255, 255, 255)
    path_color: tuple[int, int, int] = (56, 175, 205)
    show_path: bool = False
    path_animation: bool = False


class Renderer:
    """
    Handles all maze rendering operations.

    This class is responsible for drawing maze walls, special cells,
    solution paths, and animated sprites into an MLX image buffer.
    It owns no game logic and does not generate or solve mazes;
    it only visualizes data provided by the App.

    Main Attributes:
        _grid: 2D maze grid containing wall bitmasks.
        _map_data: Maze metadata including entry and exit locations.
        _fixed_cells: Cells used to render the 42 logo.
        _data: Raw MLX image buffer memory.
        _size_line: Number of bytes per image row.
        _cell_size: Pixel size of each maze cell.
        _ui: Shared UI state containing colors and display options.
    """

    def __init__(self, grid: list[list[int]], map_data: mapData, fixed_cells: set[tuple[int, int]], data: memoryview, size_line: int, cell_size: int, ui: UI_state) -> None:
        self._grid = grid
        self._fixed_cells = fixed_cells
        self._ui = ui
        self._data = data
        self._size_line = size_line
        self._cell_size = cell_size
        self._map_data = map_data

        self._sprite_data = None
        self._sprite_size_line = 0
        self._sprite_width = 0
        self._sprite_height = 0

    @staticmethod
    def _has_N_wall(cell: int) -> bool:
        """Returns True/False whether the cell has a north wall"""
        return bool(cell & 1)

    @staticmethod
    def _has_E_wall(cell: int) -> bool:
        """Returns True/False whether the cell has a east wall"""
        return bool(cell & 2)

    @staticmethod
    def _has_S_wall(cell: int) -> bool:
        """Returns True/False whether the cell has a south wall"""
        return bool(cell & 4)

    @staticmethod
    def _has_W_wall(cell: int) -> bool:
        """Returns True/False whether the cell has a west wall"""
        return bool(cell & 8)

    def clear_map(self) -> None:
        """Fill the entire maze image buffer with black pixels."""
        for r in range(len(self._grid)):
            for c in range(len(self._grid[0])):
                x = c * self._cell_size
                y = r * self._cell_size
                for cell_x in range(self._cell_size):
                    for cell_y in range(self._cell_size):
                        self._put_pixel(x + cell_x, y + cell_y, (0, 0, 0))

    def set_sprite(self, sprite_data, sprite_size_line, sprite_width, sprite_height):
        """Store sprite image data for later rendering."""
        self._sprite_data = sprite_data
        self._sprite_size_line = sprite_size_line
        self._sprite_width = sprite_width
        self._sprite_height = sprite_height

    def draw_sprite(self, sprite_pos):
        """Draw the sprite PNG at the specified maze cell."""
        if not self._sprite_data or not sprite_pos:
            return

        r, c = sprite_pos

        sprite_x = c * self._cell_size - 8
        sprite_y = r * self._cell_size - 7

        for y in range(self._sprite_height):
            for x in range(self._sprite_width):
                src_offset = (y * self._sprite_size_line) + (x * 4)

                b = self._sprite_data[src_offset + 0]
                g = self._sprite_data[src_offset + 1]
                r = self._sprite_data[src_offset + 2]
                a = self._sprite_data[src_offset + 3]

                if a == 0:
                    continue

                dest_x = sprite_x + x
                dest_y = sprite_y + y

                if 0 <= dest_x < len(self._grid[0]) * self._cell_size and 0 <= dest_y < len(self._grid) * self._cell_size:
                    offset = (dest_y * self._size_line) + (dest_x * 4)

                    self._data[offset + 0] = b
                    self._data[offset + 1] = g
                    self._data[offset + 2] = r
                    self._data[offset + 3] = 255

    def _put_pixel(self, x: int, y: int, color: tuple[int, int, int]) -> None:
        """Renders pixels to the screen, based on RGBA values"""
        offset = (y * self._size_line) + (x * 4)
        self._data[offset + 0] = color[2]
        self._data[offset + 1] = color[1]
        self._data[offset + 2] = color[0]
        self._data[offset + 3] = 255

    def _draw_horizontal_line(self, x: int, y: int, length: int) -> None:
        """Renders a straight horizontal line to the screen"""
        for i in range(length):
            self._put_pixel(x + i, y, self._ui.wall_color)

    def _draw_vertical_line(self, x: int, y: int, length: int) -> None:
        """Renders a straight vertical line to the screen"""
        for i in range(length):
            self._put_pixel(x, y + i, self._ui.wall_color)

    def draw_path(self, path_cells: list[tuple[int, int]]) -> None:
        """Renders the path between ENTRY and EXIT by filling in each cell in the path"""
        if not path_cells:
            return

        color = self._ui.path_color

        for r, c in path_cells:
            x = c * self._cell_size
            y = r * self._cell_size

            for dy in range(2, self._cell_size - 2):
                for dx in range(2, self._cell_size - 2):
                    self._put_pixel(x + dx, y + dy, color)

    def _fill_cell(self, r: int, c: int, color: tuple[int, int, int]) -> None:
        """Loops to fill in every pixel within a cell. Requires RGB to be passed in"""
        x = c * self._cell_size
        y = r * self._cell_size
        for r_offset in range(1, self._cell_size - 1):
            for c_offset in range(1, self._cell_size - 1):
                self._put_pixel(x + c_offset, y + r_offset, color)

    def _fill_logo42(self) -> None:
        """Wrapper function to fill in the cells of the 42 logo"""
        for r, c in self._fixed_cells:
            self._fill_cell(r, c, self._ui.logo42_color)

    def _fill_start_cell(self) -> None:
        """Wrapper function to fill in the ENTRY cell"""
        r, c = self._map_data.entry
        self._fill_cell(r, c, (0, 210, 0))  # Grass green

    def _fill_end_cell(self) -> None:
        """Wrapper function to fill in the EXIT cell"""
        r, c = self._map_data.exit
        self._fill_cell(r, c, (128, 0, 32))  # Burgundy

    def _draw_cell(self, x: int, y: int, cell: int) -> None:
        """Checks the binary values (LSB) and draws walls if they exist"""
        if self._has_N_wall(cell):
            self._draw_horizontal_line(x, y, self._cell_size)
        if self._has_E_wall(cell):
            self._draw_vertical_line(x + self._cell_size, y, self._cell_size)
        if self._has_S_wall(cell):
            self._draw_horizontal_line(x, y + self._cell_size, self._cell_size)
        if self._has_W_wall(cell):
            self._draw_vertical_line(x, y, self._cell_size)

    def render_grid(self, path_cells: list[tuple[int, int]]) -> None:
        """Renders walls, logo, start/end cells and optional solution path."""
        for r in range(len(self._grid)):
            for c in range(len(self._grid[0])):
                cell = self._grid[r][c]
                x = c * self._cell_size
                y = r * self._cell_size
                self._draw_cell(x, y, cell)

        self._fill_logo42()
        if self._ui.show_path:
            self.draw_path(path_cells)
        self._fill_start_cell()
        self._fill_end_cell()


class App:
    """Main application controller.

    Creates and manages the maze generation, solving, rendering,
    user input handling, animation updates, and MLX runtime.
    The App acts as the coordinator between the maze generator,
    maze solver, renderer, and event loop.

    Responsibilities:
        - Generate new mazes.
        - Compute solution paths.
        - Load sprite assets.
        - Handle keyboard input.
        - Control animation state.
        - Trigger redraws.
        - Start and maintain the MLX event loop.

    Attributes:
        _mazeGen: Maze generation component.
        _solver: Pathfinding component.
        _renderer: Rendering component.
        _mlx: MLX graphics wrapper.
        _grid: Current maze grid.
        _path_cells: Ordered solution path cells.
        _sprite_pos: Current sprite position within the maze.
        _ui: Shared UI state and display settings.
    """
    def __init__(self) -> None:
        self._map_data = parse_config()
        self._mazeGen = MazeGenerator(self._map_data)
        self._grid = self._mazeGen.gen_map()

        self._solver = MazeSolver(self._grid, self._map_data)
        self._path_cells, self._pathstr = self._solver.generate_final_path()

        self._r_config = render_settings()
        self._ui = UI_state()

        sprite_path = "renderer/puffy_tiny.png"

        if not os.path.exists(sprite_path):
            raise FileNotFoundError(sprite_path)

        self._mlx = Mlx()
        self._mlx_ptr = self._mlx.mlx_init()

        self._animation_tick = 0
        self._sprite_index = 0
        self._sprite_pos = self._path_cells[0] if self._path_cells else (0, 0)

        sprite_result = self._mlx.mlx_png_file_to_image(
            self._mlx_ptr,
            sprite_path
        )

        if not sprite_result or sprite_result[0] is None:
            raise RuntimeError("MLX failed to load PNG")

        self._sprite_img, self._sprite_width, self._sprite_height = sprite_result

        self._sprite_data, _, self._sprite_size_line, _ = \
            self._mlx.mlx_get_data_addr(self._sprite_img)

        self._win = self._mlx.mlx_new_window(
            self._mlx_ptr,
            self._r_config.width,
            self._r_config.height,
            "A*Maze*ing"
        )

        self._img = self._mlx.mlx_new_image(
            self._mlx_ptr,
            self._r_config.width,
            self._r_config.height
        )

        self._data, _, self._size_line, _ = \
            self._mlx.mlx_get_data_addr(self._img)

        self._renderer = Renderer(
            self._grid,
            self._map_data,
            self._mazeGen.fixed_cells,
            self._data,
            self._size_line,
            self._r_config.cell_size,
            self._ui
        )

        self._renderer.set_sprite(
            self._sprite_data,
            self._sprite_size_line,
            self._sprite_width,
            self._sprite_height
        )

        self._setup_keycode_hooks()
        self._setup_loop_hook()

    def _regenerate_map(self) -> None:
        self._mazeGen = MazeGenerator(self._map_data)
        self._grid = self._mazeGen.gen_map()
        self._renderer._grid = self._grid
        self._renderer._fixed_cells = self._mazeGen.fixed_cells
        self._solver = MazeSolver(self._grid, self._map_data)
        self._path_cells, _ = self._solver.generate_final_path()
        self._sprite_index = 0
        self._sprite_pos = self._path_cells[0] if self._path_cells else (0, 0)

    def _draw_menu(self) -> None:
        menu_x = 10
        menu_y_start = (len(self._grid) * self._r_config.cell_size) + 10
        spacing = 20
        menu_list = [
            "Welcome to A*Maze*Ing! Make you selection:", "",
            "1: Change maze color                2: Change '42' color",
            "3: Show/Hide shortest path          4. Toggle animated path",
            "5: Generate new perfect map         6: Generate new random map",
            "ESC: Exit"
        ]
        for i, string in enumerate(menu_list):
            menu_y = menu_y_start + (i * spacing)
            self._mlx.mlx_string_put(self._mlx_ptr, self._win, menu_x, menu_y, 0xFFFFFF, string)

    def _redraw_map(self) -> None:
        self._renderer.clear_map()
        self._renderer.render_grid(self._path_cells)
        self._renderer.draw_sprite(self._sprite_pos)
        self._mlx.mlx_put_image_to_window(
            self._mlx_ptr, self._win,
            self._img, 0, 0)

    def _next_color(self) -> tuple[int, int, int]:
        color_palette: set[tuple[int, int, int]] = {(34, 139, 34), (255, 165, 0), (255, 255, 0), (255, 0, 0), (64, 224, 208), (0, 0, 128), (255, 192, 203), (255, 0, 255)}
        new_color = color_palette.difference({self._ui.wall_color})
        return random.choice(list(new_color))

    def _setup_keycode_hooks(self) -> None:
        def key_handler(keycode, param):
            if keycode == 49:
                self._ui.wall_color = self._next_color()
            elif keycode == 50:
                self._ui.logo42_color = self._next_color()
            elif keycode ==  51:
                self._ui.show_path = not self._ui.show_path
            elif keycode ==  52:
                self._ui.path_animation = not self._ui.path_animation
            elif keycode == 53:
                self._ui.path_animation = False
                self._map_data.perfect = True
                self._map_data.seed += 1
                self._regenerate_map()
            elif keycode == 54:
                self._ui.path_animation = False
                # self._map_data.perfect = False  (FALSE NOT IMPLEMENTED YET)
                self._map_data.seed += 1
                self._regenerate_map()

            elif keycode == 65307:
                self._mlx.mlx_loop_exit(self._mlx_ptr)
            self._redraw_map()
        self._mlx.mlx_key_hook(self._win, key_handler, None)

    def _setup_loop_hook(self) -> None:

        def update_img(param):
            if not self._ui.path_animation:
                return

            self._animation_tick += 1

            # move only every second callback
            if self._animation_tick % 2 != 0:
                return

            if self._path_cells:
                if self._sprite_index < len(self._path_cells) - 1:
                    self._sprite_index += 1
                    self._sprite_pos = self._path_cells[self._sprite_index]

                    self._redraw_map()

        self._mlx.mlx_loop_hook(self._mlx_ptr, update_img, None)


    def run(self) -> None:
        self._renderer.render_grid(self._path_cells)
        print_map(self._mazeGen ,self._map_data, self._pathstr)
        self._mlx.mlx_put_image_to_window(
            self._mlx_ptr, self._win,
            self._img, 0, 0)
        self._draw_menu()
        self._mlx.mlx_loop(self._mlx_ptr)


if __name__ == "__main__":
    try:
        app = App()
        app.run()

    except ValueError as e:
        print(e)
