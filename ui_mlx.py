from __future__ import annotations

import sys
from typing import Iterable

from mlx import Mlx

from io_utils import load_maze
from maze_types import Direction

# Wall bits (closed if bit=1)
N, E, S, W = 1, 2, 4, 8

CELL = 20

# Colors (0xRRGGBB)
WALL_COLOR = 0xFFFFFF
PATH_COLOR = 0x00FF00
ENTRY_COLOR = 0x00AAFF
EXIT_COLOR = 0xFF3333
BG_COLOR = 0x000000


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
    for yy in range(y0, y1 + 1):
        put_pixel32(buf, line_length, x, yy, color)


def fill_cell(buf: memoryview, line_length: int, cx: int, cy: int, color: int) -> None:
    """Fill the inside of a cell (avoid overwriting walls)."""
    x0 = cx * CELL + 7
    y0 = cy * CELL + 7
    x1 = (cx + 1) * CELL - 7
    y1 = (cy + 1) * CELL - 7
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            put_pixel32(buf, line_length, x, y, color)


def draw_walls(buf: memoryview, line_length: int, maze: list[list[int]]) -> None:
    h = len(maze)
    w = len(maze[0])
    img_h = h * CELL + 1

    # clear to background
    # (fast fill; BG_COLOR is black so this is fine)
    buf[:] = b"\x00" * (line_length * img_h)

    # draw walls ONCE (no “net” look)
    for y in range(h):
        for x in range(w):
            cell = int(maze[y][x])
            px, py = x * CELL, y * CELL

            if cell & N:
                hline(buf, line_length, px, px + CELL, py, WALL_COLOR)
            if cell & W:
                vline(buf, line_length, px, py, py + CELL, WALL_COLOR)

            # bottom border for last row
            if y == h - 1 and (cell & S):
                hline(buf, line_length, px, px + CELL, py + CELL, WALL_COLOR)

            # right border for last col
            if x == w - 1 and (cell & E):
                vline(buf, line_length, px + CELL, py, py + CELL, WALL_COLOR)


def _parse_point(line: str) -> tuple[int, int] | None:
    line = line.strip()
    if not line:
        return None
    parts = line.split(",")
    if len(parts) != 2:
        return None
    return (int(parts[0].strip()), int(parts[1].strip()))


def load_maze_with_solution(filename: str) -> tuple[list[list[int]], tuple[int, int] | None, tuple[int, int] | None, str]:
    """
    Your dump format is:
      grid lines (hex)
      blank line
      entry "x,y"
      exit  "x,y"
      path  "NESW..."
    See dump_maze() docstring.【turn3file4†L14-L22】【turn3file4†L58-L73】
    """
    maze = load_maze(filename)

    # Now parse the tail (entry/exit/path)
    with open(filename, "r", encoding="utf-8") as f:
        lines = [ln.rstrip("\n") for ln in f]

    # find the first blank line after the grid
    sep = None
    for i, ln in enumerate(lines):
        if ln.strip() == "":
            sep = i
            break

    if sep is None:
        return maze, None, None, ""

    entry_line = lines[sep + 1] if sep + 1 < len(lines) else ""
    exit_line = lines[sep + 2] if sep + 2 < len(lines) else ""
    path_line = lines[sep + 3] if sep + 3 < len(lines) else ""

    entry = _parse_point(entry_line)
    exit_ = _parse_point(exit_line)
    path_raw = path_line.strip()

    return maze, entry, exit_, path_raw


def path_cells_from_raw(entry: tuple[int, int] | None, path_raw: str) -> set[tuple[int, int]]:
    if not entry or not path_raw:
        return set()
    x, y = entry
    cells = {(x, y)}
    for ch in path_raw:
        d = Direction.from_str(ch)
        dx, dy = d.delta
        x, y = x + dx, y + dy
        cells.add((x, y))
    return cells


def on_key(keysym, ctx):
    # ESC or q
    if keysym in (65307, 113):
        ctx["m"].mlx_loop_exit(ctx["mlx_ptr"])
    return 0


def display_maze_file(filename: str) -> None:
    maze, entry, exit_, path_raw = load_maze_with_solution(filename)
    h = len(maze)
    w = len(maze[0])

    win_w = w * CELL + 1
    win_h = h * CELL + 1

    m = Mlx()
    mlx_ptr = m.mlx_init()
    win_ptr = m.mlx_new_window(mlx_ptr, win_w, win_h, "A-Maze-ing")

    img = m.mlx_new_image(mlx_ptr, win_w, win_h)
    buf, bpp, line_length, endian = m.mlx_get_data_addr(img)

    # draw base
    draw_walls(buf, line_length, maze)

    # overlay path + endpoints (draw AFTER walls so it stays visible)
    pcs = path_cells_from_raw(entry, path_raw)
    for (x, y) in pcs:
        fill_cell(buf, line_length, x, y, PATH_COLOR)

    if entry:
        fill_cell(buf, line_length, entry[0], entry[1], ENTRY_COLOR)
    if exit_:
        fill_cell(buf, line_length, exit_[0], exit_[1], EXIT_COLOR)

    m.mlx_put_image_to_window(mlx_ptr, win_ptr, img, 0, 0)

    ctx = {"m": m, "mlx_ptr": mlx_ptr}
    m.mlx_key_hook(win_ptr, on_key, ctx)
    m.mlx_hook(win_ptr, 33, 0, lambda *_: m.mlx_loop_exit(mlx_ptr), None)

    m.mlx_loop(mlx_ptr)

    m.mlx_destroy_image(mlx_ptr, img)
    m.mlx_destroy_window(mlx_ptr, win_ptr)


if __name__ == "__main__":
    filename = sys.argv[1] if len(sys.argv) > 1 else "maze.txt"
    display_maze_file(filename)
