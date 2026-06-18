import os
from random import choice
from mlx import Mlx  # type: ignore[import-untyped]
from dataclasses import dataclass
from typing import cast, Any
from MazeGenerator.MazeGenerator import MazeGenerator
from MazeGenerator.MazeGeneratorBonus import MazeGeneratorBonus
from Rendering.MlxRender import Renderer, UI_state
from Utils.MazeSolver import MazeSolver
from MapData import parse_config
from Utils.Utils import export_map
import signal


@dataclass(frozen=True)
class RenderSettings:
    """
    Stores and freezes rendering configuration values such as window
    dimensions and maze cell size.
    """
    min_win_width: int = 550
    cell_size: int = 12
    animation_speed_L_map: int = 180
    animation_speed_S_map: int = 480
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
        signal.signal(signal.SIGTSTP, self._handle_termination)
        signal.signal(signal.SIGINT, self._handle_termination)
        self._map_data = parse_config()
        self._mazeGen = MazeGenerator(self._map_data)
        self._mazeGenBonus = MazeGeneratorBonus(self._map_data)
        self._r_config = RenderSettings()
        self._ui = UI_state()
        self._mlx = Mlx()
        self._mlx_ptr = self._mlx.mlx_init()

        self._generate_maze()
        self._load_sprite()
        self._compute_window_size()
        self._init_mlx_window()
        self._init_renderer()

    def _handle_termination(self, signum: int, frame: Any) -> None:
        self._mlx.mlx_loop_exit(self._mlx_ptr)
        sig_name = "Ctrl+C" if signum == signal.SIGINT else "Ctrl+Z"
        print(f"\n{sig_name} was detected! Terminating program.")
        os._exit(0)

    def _generate_maze(self) -> None:
        """Generates the maze grid (DFS or sidewinder bonus, per config)
        and computes its solution path.
        """
        if self._map_data.bonus:
            self._grid = self._mazeGenBonus.gen_map()
            self._fixed_cells = self._mazeGenBonus.full_42_cells
        else:
            self._grid = self._mazeGen.gen_map()
            self._fixed_cells = self._mazeGen.fixed_cells
        self._solver = MazeSolver(self._grid, self._map_data)
        self._path_cells, self._pathstr = self._solver.generate_final_path()

    def _compute_window_size(self) -> None:
        """Computes window and image pixel dimensions.

        The window is sized to fit the maze plus the menu strip below it
        (the +160). The image is sized to cover just the maze plus
        margin, with a small extra allowance (overflow_x/overflow_y) so
        the sprite is never clipped when drawn at the last row/column.
        Keeping the image smaller than the window means clear_map() and
        the per-frame blit never touch the menu's pixels, so the menu no
        longer needs to be redrawn every frame.
        """
        cell = self._r_config.cell_size

        self._win_width = max(self._r_config.min_win_width,
                              (len(self._grid[0]) + 2) * cell)
        self._win_height = (len(self._grid) + 1) * cell + 160

        overflow_x = max(0, self._sprite_width
                         - Renderer.SPRITE_OFFSET_X - cell)
        overflow_y = max(0, self._sprite_height
                         - Renderer.SPRITE_OFFSET_Y - cell)

        self._img_width = (len(self._grid[0]) + 1) * cell + cell + overflow_x
        self._img_height = (len(self._grid) + 1) * cell + overflow_y

    def _load_sprite(self) -> None:
        """Loads the sprite PNG and initialises animation state."""
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

    def _init_mlx_window(self) -> None:
        """Creates the MLX window and its backing image buffer."""
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

    def _init_renderer(self) -> None:
        """Creates the Renderer and attaches the sprite to it."""
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
        # Sets up the keybinds and the rendering loops
        self._setup_keycode_hooks()
        self._setup_loop_hook()

    def _save_map_textfile(self) -> None:
        """Exports the current maze, start/end points, and solution path
        to the configured output file.
        """
        if self._map_data.bonus:
            export_map(self._mazeGenBonus, self._map_data, self._pathstr)
        else:
            export_map(self._mazeGen, self._map_data, self._pathstr)

    def _regenerate_map(self) -> None:
        """Generates a new maze using the current config (DFS or
        sidewinder, perfect or not), recomputes its solution path, resets
        sprite/animation state, and re-exports and re-verifies the map.
        """

        self._mazeGen = MazeGenerator(self._map_data)
        self._mazeGenBonus = MazeGeneratorBonus(self._map_data)
        self._generate_maze()
        self._renderer.update_grid(self._grid, self._fixed_cells)
        self._sprite_index = 0
        self._sprite_pos = self._path_cells[0] if self._path_cells else (0, 0)
        self._ui.show_sprite = False
        self._save_map_textfile()

    def _draw_menu(self) -> None:
        """Draws the on-screen control legend below the maze."""
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
        """Clears and redraws the maze, optional solution path overlay,
        optional sprite, and the menu.
        """
        self._renderer.clear_map()
        self._renderer.render_grid(self._path_cells)
        self._background_snapshot = bytes(self._data)
        if self._ui.show_sprite:
            cast(Any, self._renderer.draw_sprite)(self._sprite_pos)
        self._mlx.mlx_put_image_to_window(
            self._mlx_ptr, self._win,
            self._img, 0, 0)

    def _next_color(self) -> tuple[int, int, int]:
        """Returns a random colour from the palette, excluding the
        current wall colour.
        """
        color_palette: set[tuple[int, int, int]] = {
            (34, 139, 34), (255, 165, 0), (255, 255, 0), (255, 0, 0),
            (64, 224, 208), (0, 0, 128), (255, 192, 203), (255, 0, 255)
        }
        new_color = color_palette.difference({self._ui.wall_color})
        return choice(list(new_color))

    def _setup_keycode_hooks(self) -> None:
        """Registers the key-press handler mapping keys 1-8 and ESC to
        display toggles, maze regeneration, and program exit.
        """

        def key_handler(keycode: int, param: Any) -> None:
            """Handles one key press: toggles display options, regenerates
            the maze, or exits, then redraws the map.
            """
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
                self._map_data.perfect = False
                self._map_data.seed += 1
                self._regenerate_map()
            elif keycode == 55:
                self._ui.animate_sprite = False
                self._map_data.bonus = True
                self._map_data.perfect = True
                self._map_data.seed += 1
                self._regenerate_map()
            elif keycode == 56:
                self._ui.animate_sprite = False
                self._map_data.bonus = True
                self._map_data.perfect = False
                self._map_data.seed += 1
                self._regenerate_map()
            elif keycode == 65307:
                self._mlx.mlx_loop_exit(self._mlx_ptr)
            self._redraw_map()
        self._mlx.mlx_key_hook(self._win, key_handler, None)

    def _setup_loop_hook(self) -> None:
        """Registers the per-frame hook that advances the sprite one cell
        along the solution path every other tick while animating.
        """
        def update_img(param: Any) -> None:
            """Advances the sprite one cell along the solution path every
            second tick, while animation is enabled.
            """

            if not self._ui.animate_sprite:
                return

            self._animation_tick += 1

            # adjust the animation speed of thr sprite based on map size
            if self._map_data.height * self._map_data.width <= 4000:
                if self._animation_tick % \
                   self._r_config.animation_speed_S_map != 0:
                    return
            else:
                if self._animation_tick % \
                   self._r_config.animation_speed_L_map != 0:
                    return

            if self._path_cells:
                if self._sprite_index < len(self._path_cells) - 1:
                    r, c = self._sprite_pos
                    self._sprite_index += 1
                    self._sprite_pos = self._path_cells[self._sprite_index]

                    sprite_x, sprite_y = self._renderer._cell_to_pixel(r, c)
                    sprite_x -= self._renderer.SPRITE_OFFSET_X
                    sprite_y -= self._renderer.SPRITE_OFFSET_Y

                    for y in range(self._sprite_height):
                        row_start = ((sprite_y + y) * self._size_line) \
                                      + (sprite_x * 4)
                        row_end = row_start + self._sprite_width * 4
                        self._data[row_start:row_end] = \
                            self._background_snapshot[row_start:row_end]

                    cast(Any, self._renderer.draw_sprite)(self._sprite_pos)
                    self._mlx.mlx_put_image_to_window(self._mlx_ptr,
                                                      self._win,
                                                      self._img, 0, 0)

        self._mlx.mlx_loop_hook(self._mlx_ptr, update_img, None)

    def run(self) -> None:
        """Renders the initial maze, exports and verifies it, then starts
        the blocking MLX event loop.
        """
        if not self._mazeGen.can_fit_42():
            print(f"Error: maze size {self._map_data.width}x"
                  f"{self._map_data.height} is too small to fit the '42' "
                  f"pattern (requires at least 8x6) - the pattern will be "
                  f"omitted.")
        self._renderer.clear_map()
        self._renderer.render_grid(self._path_cells)
        self._background_snapshot = bytes(self._data)

        self._save_map_textfile()

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
