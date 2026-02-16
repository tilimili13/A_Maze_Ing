from __future__ import annotations

import sys
from mlx import Mlx

from io_utils import load_maze
from maze_types import Direction

# Wall bits (closed if bit=1)
N, E, S, W = 1, 2, 4, 8

CELL = 20
WALL_COLOR = 0xFFFFFF


def put_pixel32(buf: memoryview, line_length: int, x: int, y: int, color: int) -> None:
    off = y * line_length + x * 4
    r = (color >> 16) & 0xFF
    g = (color >> 8) & 0xFF
    b = color & 0xFF
    buf[off + 0] = b
    buf[off + 1] = g
    buf[off + 2] = r
    buf[off + 3] = 255


def hline(buf: memoryview, line_length: int, x0: int, x1: int, y: int, color: int) -> None:
    if x0 > x1:
        x0, x1 = x1, x0
    for x in range(x0, x1 + 1):
        put_pixel32(buf, line_length, x, y, color)


def vline(buf: memoryview, line_length: int, x: int, y0: int, y1: int, color: int) -> None:
    if y0 > y1:
        y0, y1 = y1, y0
    for y in range(y0, y1 + 1):
        put_pixel32(buf, line_length, x, y, color)


def draw_maze_to_image(buf: memoryview, line_length: int, maze: list[list[int]]) -> None:
    H = len(maze)
    Wc = len(maze[0])
    img_h = H * CELL + 1

    # clear to black
    buf[:] = b"\x00" * (line_length * img_h)

    for y in range(H):
        for x in range(Wc):
            cell = int(maze[y][x])
            px, py = x * CELL, y * CELL

            if cell & N:
                hline(buf, line_length, px, px + CELL, py, WALL_COLOR)
            if cell & W:
                vline(buf, line_length, px, py, py + CELL, WALL_COLOR)

            # bottom border for last row
            if y == H - 1 and (cell & S):
                hline(buf, line_length, px, px + CELL, py + CELL, WALL_COLOR)

            # right border for last col
            if x == Wc - 1 and (cell & E):
                vline(buf, line_length, px + CELL, py, py + CELL, WALL_COLOR)


def on_key(keysym, ctx):
    # ESC or q
    if keysym in (65307, 113):
        ctx["m"].mlx_loop_exit(ctx["mlx_ptr"])
    return 0


def display_maze_file(filename: str) -> None:
    maze = load_maze(filename)
    h = len(maze)
    w = len(maze[0])

    win_w = w * CELL + 1
    win_h = h * CELL + 1

    m = Mlx()
    mlx_ptr = m.mlx_init()
    win_ptr = m.mlx_new_window(mlx_ptr, win_w, win_h, "Spiral Maze")

    img = m.mlx_new_image(mlx_ptr, win_w, win_h)
    buf, bpp, line_length, endian = m.mlx_get_data_addr(img)

    draw_maze_to_image(buf, line_length, maze)
    m.mlx_put_image_to_window(mlx_ptr, win_ptr, img, 0, 0)

    ctx = {"m": m, "mlx_ptr": mlx_ptr}
    m.mlx_key_hook(win_ptr, on_key, ctx)
    m.mlx_hook(win_ptr, 33, 0, lambda *_: m.mlx_loop_exit(mlx_ptr), None)

    m.mlx_loop(mlx_ptr)

    m.mlx_destroy_image(mlx_ptr, img)
    m.mlx_destroy_window(mlx_ptr, win_ptr)


def main() -> None:
    filename = sys.argv[1] if len(sys.argv) > 1 else "maze.txt"
    display_maze_file(filename)


if __name__ == "__main__":
    main()
