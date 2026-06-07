from mlx import Mlx
from typing import Any
from MazeGenerator import MazeGenerator
from map_data import temp_data, mapData
from dataclasses import dataclass
import random


@dataclass
class render_settings:
    width: int = 1600
    height: int = 1000
    cell_size: int = 15
# maze size  = maze size + menu!!!

@dataclass
class UI_state:

    wall_color: tuple[int, int, int] = (0, 255, 0)
    logo42_color: tuple[int, int, int] = (255, 255, 255)
    path_color: tuple[int, int, int] = (255, 0, 0)
    show_path: bool = False
    running: bool = True
    menu_visible: bool = False


class Renderer:
    """
    Responsible only for drawing a maze grid into an MLX image buffer.
    """

    def __init__(self, grid: list[list[int]], map_data: mapData, fixed_cells: set[tuple[int, int]], data: memoryview, size_line: int, cell_size: int, ui: UI_state) -> None:
        self.grid = grid
        self.ui = ui
        self.data = data
        self.size_line = size_line
        self.cell_size = cell_size
        self.map_data = map_data
        self.fixed_cells = fixed_cells

    @staticmethod
    def has_N_wall(cell: int) -> bool:
        return bool(cell & 1)

    @staticmethod
    def has_E_wall(cell: int) -> bool:
        return bool(cell & 2)

    @staticmethod
    def has_S_wall(cell: int) -> bool:
        return bool(cell & 4)

    @staticmethod
    def has_W_wall(cell: int) -> bool:
        return bool(cell & 8)



    def _draw_horizontal_line(self, x: int, y: int, length: int):
        for i in range(length):
            self.put_pixel(x + i, y, self.ui.wall_color)

    def _draw_vertical_line(self, x: int, y: int, length: int):
        for i in range(length):
            self.put_pixel(x, y + i, self.ui.wall_color)

    def _fill_cell(self, r: int, c: int, color: tuple[int, int, int]):
        x = c * self.cell_size
        y = r * self.cell_size
        for r_offset in range(1, self.cell_size - 1):
            for c_offset in range(1, self.cell_size - 1):
                self.put_pixel(x + c_offset, y + r_offset, color)

    def fill_logo42(self):
        for r, c in self.fixed_cells:
            self._fill_cell(r, c, self.ui.logo42_color)

    def fill_start_cell(self):
        r, c = self.map_data.entry
        self._fill_cell(r, c, (0, 210, 0))  # Grass green

    def fill_end_cell(self) -> None:
        r, c = self.map_data.exit
        self._fill_cell(r, c, (128, 0, 32))  # Burgundy

    def draw_cell(self, x: int, y: int, cell: int):
        if self.has_N_wall(cell):
            self._draw_horizontal_line(x, y, self.cell_size)
        if self.has_E_wall(cell):
            self._draw_vertical_line(x + self.cell_size, y, self.cell_size)
        if self.has_S_wall(cell):
            self._draw_horizontal_line(x, y + self.cell_size, self.cell_size)
        if self.has_W_wall(cell):
            self._draw_vertical_line(x, y, self.cell_size)

    def put_pixel(self, x: int, y: int, color: tuple[int, int, int]):
        offset = (y * self.size_line) + (x * 4)
        self.data[offset + 0] = color[2]
        self.data[offset + 1] = color[1]
        self.data[offset + 2] = color[0]
        self.data[offset + 3] = 255

    def render_grid(self):
        for r in range(len(self.grid)):
            for c in range(len(self.grid[0])):
                cell = self.grid[r][c]
                x = c * self.cell_size
                y = r * self.cell_size
                self.draw_cell(x, y, cell)


class App:
    """
    Owns MLX runtime and connects generator output to renderer.
    """

    def __init__(self):
        self.map_data = temp_data()
        self.mazeGen = MazeGenerator(self.map_data)
        self.grid = self.mazeGen.gen_map()
        self.r_config = render_settings()
        self.ui = UI_state()
        self.mlx = Mlx()

        self.mlx_ptr = self.mlx.mlx_init()
        self.win = self.mlx.mlx_new_window(self.mlx_ptr, self.r_config.width, self.r_config.height, "maze")
        self.img = self.mlx.mlx_new_image(self.mlx_ptr, self.r_config.width, self.r_config.height)
        self.data, self.bpp, self.size_line, self.fmt = self.mlx.mlx_get_data_addr(self.img)
        self.renderer = Renderer(self.grid, self.map_data, self.mazeGen.fixed_cells, self.data, self.size_line, self.r_config.cell_size, self.ui)
        self._setup_hooks()

    def next_color(self) -> tuple[int, int, int]:
        color_palette = [(34, 139, 34), (255, 165, 0), (255, 255, 0), (255, 0, 0), (64, 224, 208), (0, 0, 128), (135, 206, 235), (255, 192, 203), (255, 0, 255)]
        return random.choice(color_palette)

    def _setup_hooks(self):
        def key_handler(keycode, param):
            if keycode == 49:
                self.ui.wall_color = self.next_color()
            elif keycode == 50:
                self.ui.logo42_color = self.next_color()
            elif keycode ==  51:
                self.ui.show_path = not self.ui.show_path
            elif keycode == 52:
                pass
                #update (perfect) map seed and regenerate new map, then re-render
            elif keycode == 53:
                pass
                #update (not perfect) map seed and regenerate new map, then re-render
            elif keycode == 65307:
                self.mlx.mlx_loop_exit(self.mlx_ptr)
            self.redraw_map()
        self.mlx.mlx_key_hook(self.win, key_handler, None)

    def draw_menu(self):
        menu_x = 10
        menu_y_start = (len(self.grid[0]) * self.r_config.cell_size) + 10
        spacing = 20
        menu_list = [
            "Welcome to A*Maze*Ing! Make you selection:", "",
            "1: Change maze color                2: Change '42' color",
            "3: Show/Hide shortest path",
            "4: Generate new perfect map         5: Generate new random map",
            "ESC: Exit"
        ]
        for i, string in enumerate(menu_list):
            menu_y = menu_y_start + (i * spacing)
            self.mlx.mlx_string_put(self.mlx_ptr, self.win, menu_x, menu_y, 0xFFFFFF, string)

    def redraw_map(self):
        pass
        # clear image/ clear buffer (later)
        self.renderer.render_grid()
        self.renderer.fill_logo42()
        self.renderer.fill_start_cell()
        self.renderer.fill_end_cell()
        if self.ui.show_path:
            pass
            # draw path if enabled
        self.mlx.mlx_put_image_to_window(
            self.mlx_ptr, self.win,
            self.img, 0, 0)

        # display image
        self.draw_menu()

    def run(self):
        self.renderer.render_grid()

        self.renderer.fill_logo42()
        self.renderer.fill_start_cell()
        self.renderer.fill_end_cell()
        self.mlx.mlx_put_image_to_window(
            self.mlx_ptr, self.win,
            self.img, 0, 0)
        self.draw_menu()
        self.mlx.mlx_loop(self.mlx_ptr)


if __name__ == "__main__":
    try:
        app = App()
        app.run()

    except ValueError as e:
        print(e)
