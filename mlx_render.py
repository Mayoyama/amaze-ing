from mlx import Mlx
from typing import Any
from MazeGenerator import MazeGenerator
from map_data import parse


def has_N_wall(cell: int) -> bool:
    return bool(cell & 1)

def has_E_wall(cell: int) -> bool:
    return bool(cell & 2)

def has_S_wall(cell: int) -> bool:
    return bool(cell & 4)

def has_W_wall(cell: int) -> bool:
    return bool(cell & 8)

class Renderer:
    """
    Responsible only for drawing a maze grid into an MLX image buffer.
    """

    def __init__(self, grid: list[list[int]], data: memoryview, size_line: int, cell_size: int):
        self.grid = grid
        self.data = data
        self.size_line = size_line
        self.cell_size = cell_size

    def put_pixel(self, x: int, y: int, color: tuple[int, int, int]):
        offset = (y * self.size_line) + (x * 4)
        self.data[offset + 0] = color[2]
        self.data[offset + 1] = color[1]
        self.data[offset + 2] = color[0]
        self.data[offset + 3] = 255

    def draw_horizontal_line(self, x: int, y: int, length: int):
        for i in range(length):
            self.put_pixel(x + i, y, (0, 255, 0))

    def draw_vertical_line(self, x: int, y: int, length: int):
        for i in range(length):
            self.put_pixel(x, y + i, (0, 255, 0))

    def draw_cell(self, x: int, y: int, cell: int):
        if has_N_wall(cell):
            self.draw_horizontal_line(x, y, self.cell_size)
        if has_E_wall(cell):
            self.draw_vertical_line(x + self.cell_size, y, self.cell_size)
        if has_S_wall(cell):
            self.draw_horizontal_line(x, y + self.cell_size, self.cell_size)
        if has_W_wall(cell):
            self.draw_vertical_line(x, y, self.cell_size)

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

    def __init__(self, mlx, grid: list[list[int]], width: int, height: int, cell_size: int):
        self.mlx = mlx
        self.grid = grid
        self.cell_size = cell_size

        self.mlx_ptr = mlx.mlx_init()
        self.win = mlx.mlx_new_window(self.mlx_ptr, 800, 600, "maze")

        self.img = mlx.mlx_new_image(self.mlx_ptr, width, height)
        self.data, self.bpp, self.size_line, self.fmt = mlx.mlx_get_data_addr(self.img)

        self.renderer = Renderer(grid, self.data, self.size_line, cell_size)

        self._setup_hooks()


    def _setup_hooks(self):
        def key_handler(keycode, param):
            print("KEY:", keycode)
            self.mlx.mlx_loop_exit(self.mlx_ptr)

        self.mlx.mlx_key_hook(self.win, key_handler, None)


    def run(self):
        self.renderer.render_grid()

        self.mlx.mlx_put_image_to_window(
            self.mlx_ptr,
            self.win,
            self.img,
            0,
            0
        )
        self.mlx.mlx_loop(self.mlx_ptr)


if __name__ == "__main__":
    try:
        map_data = parse()

        mazeGen = MazeGenerator(map_data)
        newmaze = mazeGen.gen_map()

        mlx = Mlx()

        app = App(
            mlx=mlx,
            grid=newmaze,
            width=800,
            height=600,
            cell_size=20
        )

        app.run()

    except ValueError as e:
        print(e)
    except Exception as e:
        print(e)
