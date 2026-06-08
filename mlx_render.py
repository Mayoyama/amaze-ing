from mlx import Mlx
from typing import Any
from MazeGenerator.MazeGenerator_bonus import MazeGenerator_bonus
from map_data import parse, print_map


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
        self.nbr_try: int = 0

    def put_pixel(self, x: int, y: int, color: tuple[int, int, int]):
        offset = (y * self.size_line) + (x * 4)
        self.data[offset + 0] = color[2]
        self.data[offset + 1] = color[1]
        self.data[offset + 2] = color[0]
        self.data[offset + 3] = 255

    def draw_horizontal_line(self, x: int, y: int, length: int):
        if self.nbr_try == 0:
            for i in range(length):
                self.put_pixel(x + i, y, (0, 255, 0))
        else:
            for i in range(length):
                self.put_pixel(x + i, y, (200, 100, 200))

    def draw_vertical_line(self, x: int, y: int, length: int):
        if self.nbr_try == 0:
            for i in range(length):
                self.put_pixel(x, y + i, (0, 255, 0))
        else:
            for i in range(length):
                self.put_pixel(x, y + i, (200, 100, 200))

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
                x = c * self.cell_size + 7
                y = r * self.cell_size + 5
                self.draw_cell(x, y, cell)
        if self.nbr_try == 0:
            self.nbr_try = 1
        else:
            self.nbr_try = 0



class App:
    """
    Owns MLX runtime and connects generator output to renderer.
    """

    def __init__(self, mlx, grid: list[list[int]], width: int, height: int, cell_size: int):
        self.mlx = mlx
        self.grid = grid
        self.cell_size = cell_size
        self.width = width
        self.height = height

        self.mlx_ptr = mlx.mlx_init()
        self.win = mlx.mlx_new_window(self.mlx_ptr, width, height, "maze")

        self.img = mlx.mlx_new_image(self.mlx_ptr, width, height)
        self.data, self.bpp, self.size_line, self.fmt = mlx.mlx_get_data_addr(self.img)

        self.renderer = Renderer(grid, self.data, self.size_line, cell_size)

        self._setup_hooks()


    def _setup_hooks(self):
        def key_handler(keycode, param):
            print("KEY:", keycode)
            if keycode == 51:
                mlx.mlx_clear_window(self.mlx_ptr, self.win)
                self.run()
            if keycode == 52:
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
        if self.width > self.cell_size * 18:
            mlx.mlx_string_put(self.mlx_ptr, self.win, 5, self.height - 35, 0xFFFFFF, "1: regen; 2: path; 3: color; 4: quit")
        self.mlx.mlx_loop(self.mlx_ptr)


if __name__ == "__main__":
    try:
        map_data = parse()

        mazeGen = MazeGenerator_bonus(map_data)
        newmaze = mazeGen.gen_map()
        
        print_map(mazeGen, map_data)

        mlx = Mlx()

        app = App(
            mlx=mlx,
            grid=newmaze,
            width=map_data.width * 20 + 20,
            height=map_data.height * 20 + 42,
            cell_size=20
        )

        app.run()

    except ValueError as e:
        print(e)
    except Exception as e:
        print(e)
