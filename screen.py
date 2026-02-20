from typing import Any
from utils.maze_types import Maze, Point
from config import Config
from button import Button
from mlx import Mlx

PAD: int = 6
BTN_W: int = 90
BTN_H: int = 18
BTN_GAP: int = 10

class Screen:
    CELL: int = 20
    UI_H = 26
    UI_BG = 0x202020
    BTN_BG = 0x404040
    BTN_BG_ACTIVE = 0x606060
    BTN_BORDER = 0xA0A0A0
    win_w: int
    win_h: int
    ml_ptr: Any
    win_ptr: Any
    img: Any
    buf: memoryview
    line_length: int
    cfg: Config
    show_path: bool = True
    wall_idx: int = 0
    wall_color: int = 0xFFFFFF
    maze: Maze
    path_cells: set[Point]
    seed: int
    buttons: dict[str, Button]
    def __init__(self, cfg: Config, m: Mlx) -> None:
        self.cfg = cfg
        self.__m = m
        self.win_w = cfg.width * self.CELL + 1
        self.win_h = cfg.height * self.CELL + self.UI_H + 1
        self.ml_ptr = m.mlx_init()
        self.win_ptr = m.mlx_new_window(
            self.ml_ptr,
            self.win_w,
            self.win_h,
            "A-Maze-ing  1:new 2:path 3:color 4:quit",
        )
        self.img = m.mlx_new_image(self.ml_ptr, self.win_w, self.win_h)
        self.buf, _, self.line_length, _ = m.mlx_get_data_addr(self.img)
        self.maze = [[0]]
        self.path_cells = set()
        self.seed = cfg.seed
        self.buttons = {
            "new": Button("New", PAD, 4, BTN_W, BTN_H),
            "path": Button("Path", PAD + (BTN_W + BTN_GAP) * 1, 4, BTN_W, BTN_H),
            "wall": Button("Wall", PAD + (BTN_W + BTN_GAP) * 2, 4, BTN_W, BTN_H),
        }

    def put_to_window(self) -> None:
        self.__m.mlx_put_image_to_window(
            self.ml_ptr, self.win_ptr, self.img, 0, 0
        )
    
    def exit(self) -> None:
        self.__m.mlx_loop_exit(self.ml_ptr)
    
    def destroy(self) -> None:
        self.__m.mlx_destroy_image(self.ml_ptr, self.img)
        self.__m.mlx_destroy_window(self.ml_ptr, self.win_ptr)

    def fill_cell(self, cx: int, cy: int, color: int, y_offset: int) -> None:
        margin: int = 7
        self.fill_rect(
            cx * self.CELL + margin,
            cy * self.CELL + y_offset + margin,
            self.CELL - margin * 2,
            self.CELL - margin * 2,
            color
        )

    def fill_rect(self, x0: int, y0: int, w: int, h: int, color: int) -> None:
        self.draw((x0, y0), (x0 + w, y0 + h), color)

    def rect_border(self, x0: int, y0: int, w: int, h: int, color: int) -> None:
        self.draw((x0, y0), (x0, y0 + h), color)
        self.draw((x0 + w, y0), (x0 + w, y0 + h), color)
        self.draw((x0, y0), (x0 + w, y0), color)
        self.draw((x0, y0 + h), (x0 + w, y0 + h), color)

    def draw(self, s: Point, e: Point, color: int) -> None:
        [x0, y0] = s
        [x1, y1] = e
        if x0 > x1:
            x0, x1 = x1, x0
        if y0 > y1:
            y0, y1 = y1, y0
        for y in range(y0, y1):
            for x in range(x0, x1):
                self._put_pixel(x, y, color)

    def _put_pixel(self, x: int, y: int, color: int) -> None:
        off = y * self.line_length + x * 4
        [r, g, b] = self._parse_color(color)
        self.buf[off + 0] = b
        self.buf[off + 1] = g
        self.buf[off + 2] = r
        self.buf[off + 3] = 255 

    def _parse_color(self, color: int) -> tuple[int, int, int]:
        r = (color >> 16) & 0xFF
        g = (color >> 8) & 0xFF
        b = color & 0xFF
        return r, g, b
