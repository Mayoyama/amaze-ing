import os
from random import choice
from mlx import Mlx
from dataclasses import dataclass
from typing import cast, Any
from MazeGenerator.MazeGenerator import MazeGenerator
from MazeGenerator.MazeGeneratorBonus import MazeGeneratorBonus
from Rendering.MlxRender import Renderer, UI_state
from Utils.MazeSolver import MazeSolver
from MapData import parse_config
from Utils.Utils import ExportMap


@dataclass(frozen=True)
class RenderSettings:
    """
    Stores and freezes rendering configuration values such as window
    dimensions and maze cell size.
    """
    min_win_width: int = 550
    cell_size: int = 10
    sprite_path: str = "Rendering/puffy_tiny.png"


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
        self._mazeGenBonus = MazeGeneratorBonus(self._map_data)
        self._r_config = RenderSettings()
        self._ui = UI_state()
        self._mlx = Mlx()
        self._mlx_ptr = self._mlx.mlx_init()

        if self._map_data.bonus:
            self._grid = self._mazeGenBonus.gen_map()
            self._fixed_cells = self._mazeGenBonus.full_42_celles
        else:
            self._grid = self._mazeGen.gen_map()
            self._fixed_cells = self._mazeGen.fixed_cells
        self._solver = MazeSolver(self._grid, self._map_data)
        self._path_cells, self._pathstr = self._solver.generate_final_path()

        self._win_width = max(self._r_config.min_win_width,
                              (len(self._grid[0]) + 2) *
                              self._r_config.cell_size)
        self._win_height = (len(self._grid)
                            + 1) * self._r_config.cell_size + 160
        self._img_width = self._win_width
        self._img_height = self._win_height

        if not os.path.exists(self._r_config.sprite_path):
            raise FileNotFoundError(self._r_config.sprite_path)
        self._animation_tick = 0
        self._sprite_index = 0
        self._sprite_pos = self._path_cells[0] if self._path_cells else (0, 0)

        sprite_res = self._mlx.mlx_png_file_to_image(
            self._mlx_ptr,
            self._r_config.sprite_path
        )

        if not sprite_res or sprite_res[0] is None:
            raise RuntimeError("MLX failed to load PNG")

        self._sprite_img, self._sprite_width, self._sprite_height = sprite_res

        self._sprite_data, _, self._sprite_size_line, _ = \
            self._mlx.mlx_get_data_addr(self._sprite_img)

        self._win = self._mlx.mlx_new_window(
            self._mlx_ptr,
            self._win_width,
            self._win_height,
            "A*Maze*ing"
        )

        self._img = self._mlx.mlx_new_image(
            self._mlx_ptr,
            self._img_width,
            self._img_height
        )

        self._data, _, self._size_line, _ = \
            self._mlx.mlx_get_data_addr(self._img)

        self._renderer = Renderer(
            self._grid,
            self._map_data,
            self._fixed_cells,
            self._data,
            self._img_width,
            self._img_height,
            self._size_line,
            self._r_config.cell_size,
            self._ui
        )

        cast(Any, self._renderer.set_sprite)(
            self._sprite_data,
            self._sprite_size_line,
            self._sprite_width,
            self._sprite_height
        )

        self._setup_keycode_hooks()
        self._setup_loop_hook()

    def _regenerate_map(self) -> None:
        self._mazeGen = MazeGenerator(self._map_data)
        self._mazeGenBonus = MazeGeneratorBonus(self._map_data)
        if self._map_data.bonus:
            self._grid = self._mazeGenBonus.gen_map()
            self._renderer._fixed_cells = self._mazeGenBonus.full_42_celles
        else:
            self._grid = self._mazeGen.gen_map()
            self._renderer._fixed_cells = self._mazeGen.fixed_cells
        self._renderer._grid = self._grid
        self._solver = MazeSolver(self._grid, self._map_data)
        self._path_cells, self._pathstr = self._solver.generate_final_path()
        self._sprite_index = 0
        self._sprite_pos = self._path_cells[0] if self._path_cells else (0, 0)
        self._ui.show_sprite = False
        if self._map_data.bonus:
            ExportMap(self._mazeGenBonus, self._map_data, self._pathstr)
        else:
            ExportMap(self._mazeGen, self._map_data, self._pathstr)

    def _draw_menu(self) -> None:
        menu_x = self._r_config.cell_size
        menu_y_start = (len(self._grid) * self._r_config.cell_size) + \
                       (self._r_config.cell_size) + 20
        spacing = 20
        menu_list = [
            "Welcome to A*Maze*Ing! Make you selection:", "",
            "1: Change maze color         2: Change '42' color",
            "3: Show/Hide shortest path   4. Toggle animated path",
            "5: Generate perfect map      6: Generate random map",
            "7: Bonus: perfect map        8: Bonus: random map",
            "ESC: Exit"
        ]
        for i, string in enumerate(menu_list):
            menu_y = menu_y_start + (i * spacing)
            self._mlx.mlx_string_put(self._mlx_ptr, self._win, menu_x,
                                     menu_y, 0xFFFFFF, string)

    def _redraw_map(self) -> None:
        self._renderer.clear_map()
        self._renderer.render_grid(self._path_cells)
        if self._ui.show_sprite:
            cast(Any, self._renderer.draw_sprite)(self._sprite_pos)
        self._mlx.mlx_put_image_to_window(
            self._mlx_ptr, self._win,
            self._img, 0, 0)
        self._draw_menu()

    def _next_color(self) -> tuple[int, int, int]:
        color_palette: set[tuple[int, int, int]] = {
            (34, 139, 34), (255, 165, 0), (255, 255, 0), (255, 0, 0),
            (64, 224, 208), (0, 0, 128), (255, 192, 203), (255, 0, 255)
        }
        new_color = color_palette.difference({self._ui.wall_color})
        return choice(list(new_color))

    def _setup_keycode_hooks(self) -> None:
        def key_handler(keycode: int, param: Any) -> None:
            if keycode == 49:
                self._ui.wall_color = self._next_color()
            elif keycode == 50:
                self._ui.logo42_color = self._next_color()
            elif keycode == 51:
                self._ui.show_path = not self._ui.show_path
            elif keycode == 52:
                if self._sprite_index == len(self._path_cells) - 1:
                    self._sprite_index = 0
                    self._sprite_pos = self._path_cells[0]
                    self._ui.show_sprite = True
                    self._ui.animate_sprite = True
                else:
                    if not self._ui.animate_sprite:
                        self._ui.show_sprite = True
                    self._ui.animate_sprite = not self._ui.animate_sprite
            elif keycode == 53:
                self._ui.animate_sprite = False
                self._map_data.bonus = False
                self._map_data.perfect = True
                self._map_data.seed += 1
                self._regenerate_map()
            elif keycode == 54:
                self._ui.animate_sprite = False
                self._map_data.bonus = False
                self._map_data.perfect = False  # (FALSE NOT IMPLEMENTED YET)
                self._map_data.seed += 1
                self._regenerate_map()
            elif keycode == 55:
                self._ui.animate_sprite = False
                self._map_data.bonus = True
                self._map_data.perfect = True
                self._map_data.seed += 1
                self._regenerate_map()
                # implement perfect bonus maze
            elif keycode == 56:
                self._ui.animate_sprite = False
                self._map_data.bonus = True
                self._map_data.perfect = False
                self._map_data.seed += 1
                self._regenerate_map()
                # implement non perfect bonus maze
            elif keycode == 65307:
                self._mlx.mlx_loop_exit(self._mlx_ptr)
            self._redraw_map()
        self._mlx.mlx_key_hook(self._win, key_handler, None)

    def _setup_loop_hook(self) -> None:

        def update_img(param: Any) -> None:
            if not self._ui.animate_sprite:
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
        self._renderer.clear_map()
        self._renderer.render_grid(self._path_cells)

        if self._map_data.bonus:
            ExportMap(self._mazeGenBonus, self._map_data, self._pathstr)
        else:
            ExportMap(self._mazeGen, self._map_data, self._pathstr)
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
