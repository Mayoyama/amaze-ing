from map_data import mapData
from dataclasses import dataclass


@dataclass
class UI_state:
    """
    Stores mutable UI settings including colors and display toggles
    used by the renderer.
    """
    wall_color: tuple[int, int, int] = (0, 255, 0)
    logo42_color: tuple[int, int, int] = (0, 180, 0)# (255, 255, 255)
    path_color: tuple[int, int, int] = (56, 175, 205)
    show_path: bool = False
    animate_sprite: bool = False
    show_sprite: bool = False


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

    def __init__(self, grid: list[list[int]], map_data: mapData, fixed_cells: set[tuple[int, int]], data: memoryview, img_w: int, img_h: int, size_line: int, cell_size: int, ui: UI_state) -> None:
        self._grid = grid
        self._fixed_cells = fixed_cells
        self._ui = ui
        self._data = data
        self._size_line = size_line
        self._cell_size = cell_size
        self._map_data = map_data
        self._margin = self._cell_size

        self._sprite_data = None
        self._sprite_size_line = 0
        self._sprite_width = 0
        self._sprite_height = 0
        self._image_width = img_w
        self._image_height = img_h

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

    def _cell_to_pixel(self, r: int, c: int) -> tuple[int, int]:
        x = self._margin + (c * self._cell_size)
        y = self._margin + (r * self._cell_size)
        return x, y

    def clear_map(self) -> None:
        for y in range(self._image_height):
            for x in range(self._image_width):
                self._put_pixel(x, y, (0, 0, 0))

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

        sprite_x, sprite_y = self._cell_to_pixel(r, c)
        sprite_x -= 8
        sprite_y -= 7

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

                if 0 <= dest_x < self._image_width and 0 <= dest_y < self._image_height:
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
            x, y = self._cell_to_pixel(r, c)

            for dy in range(2, self._cell_size - 2):
                for dx in range(2, self._cell_size - 2):
                    self._put_pixel(x + dx, y + dy, color)

    def _fill_cell(self, r: int, c: int, color: tuple[int, int, int]) -> None:
        """Loops to fill in every pixel within a cell. Requires RGB to be passed in"""
        x, y = self._cell_to_pixel(r, c)
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
                x, y = self._cell_to_pixel(r, c)
                self._draw_cell(x, y, cell)

        self._fill_logo42()
        if self._ui.show_path:
            self.draw_path(path_cells)
        self._fill_start_cell()
        self._fill_end_cell()
