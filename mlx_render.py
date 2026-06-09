from mlx import Mlx
from typing import Any
from MazeGenerator import MazeGenerator
from mazeSolver import MazeSolver
from map_data import parse_config, mapData
from dataclasses import dataclass
import random
import os
from utils import print_map


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
    path_animation: bool = False


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

        self.sprite_data = None
        self.sprite_size_line = 0
        self.sprite_w = 0
        self.sprite_h = 0

    @staticmethod
    def _has_N_wall(cell: int) -> bool:
        return bool(cell & 1)

    @staticmethod
    def _has_E_wall(cell: int) -> bool:
        return bool(cell & 2)

    @staticmethod
    def _has_S_wall(cell: int) -> bool:
        return bool(cell & 4)

    @staticmethod
    def _has_W_wall(cell: int) -> bool:
        return bool(cell & 8)

    def clear_map(self) -> None:
        for r in range(len(self.grid)):
            for c in range(len(self.grid[0])):
                x = c * self.cell_size
                y = r * self.cell_size
                for cell_x in range(self.cell_size):
                    for cell_y in range(self.cell_size):
                        self._put_pixel(x + cell_x, y + cell_y, (0, 0, 0))

    def set_sprite(self, sprite_data, sprite_size_line, sprite_w, sprite_h):
        self.sprite_data = sprite_data
        self.sprite_size_line = sprite_size_line
        self.sprite_w = sprite_w
        self.sprite_h = sprite_h

    def draw_sprite(self, sprite_pos):
        if not self.sprite_data or not sprite_pos:
            return

        r, c = sprite_pos

        x0 = c * self.cell_size - 8
        y0 = r * self.cell_size - 7

        for y in range(self.sprite_h):
            for x in range(self.sprite_w):
                src_offset = (y * self.sprite_size_line) + (x * 4)

                b = self.sprite_data[src_offset + 0]
                g = self.sprite_data[src_offset + 1]
                rcol = self.sprite_data[src_offset + 2]
                a = self.sprite_data[src_offset + 3]

                if a == 0:
                    continue

                dst_x = x0 + x
                dst_y = y0 + y

                if 0 <= dst_x < len(self.grid[0]) * self.cell_size and 0 <= dst_y < len(self.grid) * self.cell_size:
                    offset = (dst_y * self.size_line) + (dst_x * 4)

                    self.data[offset + 0] = b
                    self.data[offset + 1] = g
                    self.data[offset + 2] = rcol
                    self.data[offset + 3] = 255

    def _draw_horizontal_line(self, x: int, y: int, length: int) -> None:
        for i in range(length):
            self._put_pixel(x + i, y, self.ui.wall_color)

    def _draw_vertical_line(self, x: int, y: int, length: int) -> None:
        for i in range(length):
            self._put_pixel(x, y + i, self.ui.wall_color)

    def draw_path(self, path_cells: list[tuple[int, int]]) -> None:
        if not path_cells:
            return

        color = self.ui.path_color

        for r, c in path_cells:
            x = c * self.cell_size
            y = r * self.cell_size

            for dy in range(2, self.cell_size - 2):
                for dx in range(2, self.cell_size - 2):
                    self._put_pixel(x + dx, y + dy, color)

    def _fill_cell(self, r: int, c: int, color: tuple[int, int, int]) -> None:
        x = c * self.cell_size
        y = r * self.cell_size
        for r_offset in range(1, self.cell_size - 1):
            for c_offset in range(1, self.cell_size - 1):
                self._put_pixel(x + c_offset, y + r_offset, color)

    def _fill_logo42(self) -> None:
        for r, c in self.fixed_cells:
            self._fill_cell(r, c, self.ui.logo42_color)

    def _fill_start_cell(self) -> None:
        r, c = self.map_data.entry
        self._fill_cell(r, c, (0, 210, 0))  # Grass green

    def _fill_end_cell(self) -> None:
        r, c = self.map_data.exit
        self._fill_cell(r, c, (128, 0, 32))  # Burgundy

    def _draw_cell(self, x: int, y: int, cell: int) -> None:
        if self._has_N_wall(cell):
            self._draw_horizontal_line(x, y, self.cell_size)
        if self._has_E_wall(cell):
            self._draw_vertical_line(x + self.cell_size, y, self.cell_size)
        if self._has_S_wall(cell):
            self._draw_horizontal_line(x, y + self.cell_size, self.cell_size)
        if self._has_W_wall(cell):
            self._draw_vertical_line(x, y, self.cell_size)

    def _put_pixel(self, x: int, y: int, color: tuple[int, int, int]) -> None:
        offset = (y * self.size_line) + (x * 4)
        self.data[offset + 0] = color[2]
        self.data[offset + 1] = color[1]
        self.data[offset + 2] = color[0]
        self.data[offset + 3] = 255

    def render_grid(self, path_cells: list[tuple[int, int]]) -> None:
        for r in range(len(self.grid)):
            for c in range(len(self.grid[0])):
                cell = self.grid[r][c]
                x = c * self.cell_size
                y = r * self.cell_size
                self._draw_cell(x, y, cell)

        self._fill_logo42()
        if self.ui.show_path:
            self.draw_path(path_cells)
        self._fill_start_cell()
        self._fill_end_cell()

       


class App:
    def __init__(self) -> None:
        self.map_data = parse_config()
        self.mazeGen = MazeGenerator(self.map_data)
        self.grid = self.mazeGen.gen_map()

        self.solver = MazeSolver(self.grid, self.map_data)
        self.path_cells, self.pathstr = self.solver.generate_final_path()

        self.r_config = render_settings()
        self.ui = UI_state()

        sprite_path = "renderer/puffy_tiny.png"

        if not os.path.exists(sprite_path):
            raise FileNotFoundError(sprite_path)

        self.mlx = Mlx()
        self.mlx_ptr = self.mlx.mlx_init()

        self.animation_tick = 0
        self.sprite_index = 0
        self.sprite_pos = self.path_cells[0] if self.path_cells else (0, 0)

        sprite_result = self.mlx.mlx_png_file_to_image(
            self.mlx_ptr,
            sprite_path
        )

        if not sprite_result or sprite_result[0] is None:
            raise RuntimeError("MLX failed to load PNG")

        self.sprite_img, self.sprite_w, self.sprite_h = sprite_result

        self.sprite_data, self.sprite_bpp, self.sprite_size_line, self.sprite_fmt = \
            self.mlx.mlx_get_data_addr(self.sprite_img)

        self.win = self.mlx.mlx_new_window(
            self.mlx_ptr,
            self.r_config.width,
            self.r_config.height,
            "A*Maze*ing"
        )

        self.img = self.mlx.mlx_new_image(
            self.mlx_ptr,
            self.r_config.width,
            self.r_config.height
        )

        self.data, self.bpp, self.size_line, self.fmt = \
            self.mlx.mlx_get_data_addr(self.img)

        self.renderer = Renderer(
            self.grid,
            self.map_data,
            self.mazeGen.fixed_cells,
            self.data,
            self.size_line,
            self.r_config.cell_size,
            self.ui
        )

        self.renderer.set_sprite(
            self.sprite_data,
            self.sprite_size_line,
            self.sprite_w,
            self.sprite_h
        )

        self._setup_hooks()
        self.setup_loop_hook()


    def _regenerate_map(self) -> None:
        self.mazeGen = MazeGenerator(self.map_data)
        self.grid = self.mazeGen.gen_map()
        self.renderer.grid = self.grid
        self.renderer.fixed_cells = self.mazeGen.fixed_cells
        self.solver = MazeSolver(self.grid, self.map_data)
        self.path_cells, self.path_dirs = self.solver.generate_final_path()
        self.sprite_index = 0
        self.sprite_pos = self.path_cells[0] if self.path_cells else (0, 0)

    def _draw_menu(self) -> None:
        menu_x = 10
        menu_y_start = (len(self.grid) * self.r_config.cell_size) + 10
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
            self.mlx.mlx_string_put(self.mlx_ptr, self.win, menu_x, menu_y, 0xFFFFFF, string)

    def _redraw_map(self) -> None:
        self.renderer.clear_map()
        self.renderer.render_grid(self.path_cells)
        self.renderer.draw_sprite(self.sprite_pos)
        self.mlx.mlx_put_image_to_window(
            self.mlx_ptr, self.win,
            self.img, 0, 0)

    def _next_color(self) -> tuple[int, int, int]:
        color_palette: set[tuple[int, int, int]] = {(34, 139, 34), (255, 165, 0), (255, 255, 0), (255, 0, 0), (64, 224, 208), (0, 0, 128), (255, 192, 203), (255, 0, 255)}
        new_color = color_palette.difference({self.ui.wall_color})
        return random.choice(list(new_color))

    def _setup_hooks(self) -> None:
        def key_handler(keycode, param):
            if keycode == 49:
                self.ui.wall_color = self._next_color()
            elif keycode == 50:
                self.ui.logo42_color = self._next_color()
            elif keycode ==  51:
                self.ui.show_path = not self.ui.show_path
            elif keycode ==  52:
                self.ui.path_animation = not self.ui.path_animation
            elif keycode == 53:
                self.map_data.perfect = True
                self.map_data.seed += 1
                self._regenerate_map()
            elif keycode == 54:
                # self.map_data.perfect = False  (FALSE NOT IMPLEMENTED YET)
                self.map_data.seed += 1
                self._regenerate_map()

            elif keycode == 65307:
                self.mlx.mlx_loop_exit(self.mlx_ptr)
            self._redraw_map()
        self.mlx.mlx_key_hook(self.win, key_handler, None)

    def setup_loop_hook(self) -> None:

        def update_img(param):
            if not self.ui.path_animation:
                return

            self.animation_tick += 1

            # move only every second callback
            if self.animation_tick % 8 != 0:
                return

            if self.path_cells:
                if self.sprite_index < len(self.path_cells) - 1:
                    self.sprite_index += 1
                    self.sprite_pos = self.path_cells[self.sprite_index]

                    self._redraw_map()

        self.mlx.mlx_loop_hook(self.mlx_ptr, update_img, None)


    def run(self) -> None:
        self.renderer.render_grid(self.path_cells)
        print_map(self.mazeGen ,self.map_data, self.pathstr)
        self.mlx.mlx_put_image_to_window(
            self.mlx_ptr, self.win,
            self.img, 0, 0)
        self._draw_menu()
        self.mlx.mlx_loop(self.mlx_ptr)


if __name__ == "__main__":
    try:
        app = App()
        app.run()

    except ValueError as e:
        print(e)
