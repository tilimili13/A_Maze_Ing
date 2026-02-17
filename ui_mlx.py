from __future__ import annotations

from typing import Any

from mlx import Mlx

from config import Config
from generator import generate_maze
from solution import solve
from io_utils import dump_maze
from maze_types import Direction

# Wall bits (closed if bit=1)
N, E, S, W = 1, 2, 4, 8

CELL = 20

# Colors
PATH_COLOR = 0x00FF00
ENTRY_COLOR = 0x00AAFF
EXIT_COLOR = 0xFF3333
BG_COLOR = 0x000000

WALL_COLORS = [0xFFFFFF, 0xFFAA00, 0x00AAFF, 0xFF3333, 0x00FF00]

# Toolbar UI
UI_H = 26
PAD = 6
BTN_W = 90
BTN_H = 18
BTN_GAP = 10
UI_BG = 0x202020
BTN_BG = 0x404040
BTN_BG_ACTIVE = 0x606060
BTN_BORDER = 0xA0A0A0


def put_pixel32(
        buf: memoryview, 
        line_length: int, 
        x: int, 
        y: int, 
        color: int) -> None:
    off = y * line_length + x * 4
    r = (color >> 16) & 0xFF
    g = (color >> 8) & 0xFF
    b = color & 0xFF
    buf[off + 0] = b
    buf[off + 1] = g
    buf[off + 2] = r
    buf[off + 3] = 255


def hline(
        buf: memoryview, 
        line_length: int, 
        x0: int, 
        x1: int, 
        y: int, 
        color: int) -> None:
    if x0 > x1:
        x0, x1 = x1, x0
    for x in range(x0, x1 + 1):
        put_pixel32(buf, line_length, x, y, color)


def vline(
        buf: memoryview, 
        line_length: int, 
        x: int, 
        y0: int, 
        y1: int, 
        color: int) -> None:
    if y0 > y1:
        y0, y1 = y1, y0
    for yy in range(y0, y1 + 1):
        put_pixel32(buf, line_length, x, yy, color)


def fill_rect(
        buf: memoryview, 
        line_length: int, 
        x0: int, 
        y0: int, 
        w: int, 
        h: int, 
        color: int) -> None:
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            put_pixel32(buf, line_length, x, y, color)


def rect_border(buf: memoryview, 
                line_length: int, 
                x0: int, 
                y0: int, 
                w: int, 
                h: int, 
                color: int) -> None:
    hline(buf, line_length, x0, x0 + w - 1, y0, color)
    hline(buf, line_length, x0, x0 + w - 1, y0 + h - 1, color)
    vline(buf, line_length, x0, y0, y0 + h - 1, color)
    vline(buf, line_length, x0 + w - 1, y0, y0 + h - 1, color)


def fill_cell(buf: memoryview, line_length: int, cx: int, cy: int, color: int, y_offset: int) -> None:
    # “dot” look inside the cell
    margin = 7
    x0 = cx * CELL + margin
    y0 = cy * CELL + y_offset + margin
    x1 = (cx + 1) * CELL - margin
    y1 = (cy + 1) * CELL + y_offset - margin
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            put_pixel32(buf, line_length, x, y, color)


def inside(mx: int, my: int, rect: tuple[int, int, int, int]) -> bool:
    x, y, w, h = rect
    return x <= mx < x + w and y <= my < y + h


def path_cells_from_dirs(entry: tuple[int, int], path: list[Direction] | None) -> set[tuple[int, int]]:
    x, y = entry
    cells = {(x, y)}
    if not path:
        return cells
    for d in path:
        dx, dy = d.delta
        x += dx
        y += dy
        cells.add((x, y))
    return cells

def clear_image(
        buf: memoryview, 
        line_length: int, 
        win_w: int, 
        win_h: int, 
        color: int) -> None:
    for y in range(win_h):
        for x in range(win_w):
            put_pixel32(buf, line_length, x, y, color)


def draw_toolbar(ctx: dict[str, Any]) -> None:
    buf = ctx["buf"]
    ll = ctx["line_length"]

    fill_rect(buf, ll, 0, 0, ctx["win_w"], UI_H, UI_BG)

    # NEW
    x, y, w, h = ctx["btn_new"]
    fill_rect(buf, ll, x, y, w, h, BTN_BG)
    rect_border(buf, ll, x, y, w, h, BTN_BORDER)

    # PATH
    x, y, w, h = ctx["btn_path"]
    fill_rect(buf, ll, x, y, w, h, BTN_BG_ACTIVE if ctx["show_path"] else BTN_BG)
    rect_border(buf, ll, x, y, w, h, BTN_BORDER)

    # WALL
    x, y, w, h = ctx["btn_wall"]
    fill_rect(buf, ll, x, y, w, h, BTN_BG)
    rect_border(buf, ll, x, y, w, h, BTN_BORDER)

    # wall color swatch
    sw = 12
    fill_rect(buf, ll, x + w - sw - 3, y + 3, sw, h - 6, ctx["wall_color"])


def redraw(ctx: dict[str, Any]) -> None:
    maze = ctx["maze"]
    entry = ctx["entry"]
    exit_ = ctx["exit"]
    buf = ctx["buf"]
    ll = ctx["line_length"]
    y_offset = UI_H
    wall_color = ctx["wall_color"]

    h = len(maze)
    w = len(maze[0])

    # Clear whole image buffer (toolbar + maze area)
    buf[:] = b"\x00" * (ll * ctx["win_h"])
    clear_image(buf, ll, ctx["win_w"], ctx["win_h"], BG_COLOR)

    # Toolbar
    draw_toolbar(ctx)

    # Walls
    for y in range(h):
        for x in range(w):
            cell = int(maze[y][x])
            px = x * CELL
            py = y * CELL + y_offset

            if cell & N:
                hline(buf, ll, px, px + CELL, py, wall_color)
            if cell & W:
                vline(buf, ll, px, py, py + CELL, wall_color)

            if y == h - 1 and (cell & S):
                hline(buf, ll, px, px + CELL, py + CELL, wall_color)
            if x == w - 1 and (cell & E):
                vline(buf, ll, px + CELL, py, py + CELL, wall_color)

    # Path overlay
    if ctx["show_path"]:
        for (x, y) in ctx["path_cells"]:
            fill_cell(buf, ll, x, y, PATH_COLOR, y_offset)

    # Entry / Exit
    fill_cell(buf, ll, entry[0], entry[1], ENTRY_COLOR, y_offset)
    fill_cell(buf, ll, exit_[0], exit_[1], EXIT_COLOR, y_offset)

    m: Mlx = ctx["m"]
    m.mlx_put_image_to_window(ctx["mlx_ptr"], ctx["win_ptr"], ctx["img"], 0, 0)


def regenerate(ctx: dict[str, Any]) -> None:
    cfg: Config = ctx["cfg"]

    seed = ctx.get("seed")
    if seed is None:
        seed = cfg.seed
    if seed is None:
        seed = 0
    seed += 1
    ctx["seed"] = seed

    maze = generate_maze(
        cfg.width,
        cfg.height,
        cfg.entry,
        cfg.exit,
        perfect=cfg.perfect,
        seed=seed,
    )
    path = solve(maze, cfg.entry, cfg.exit, perfect=cfg.perfect) or []

    ctx["maze"] = maze
    ctx["entry"] = cfg.entry
    ctx["exit"] = cfg.exit
    ctx["path_cells"] = path_cells_from_dirs(cfg.entry, path)

    # Optional: keep writing output file for your project requirements
    dump_maze(maze, cfg.entry, cfg.exit, path, cfg.output_file)


def cycle_wall_color(ctx: dict[str, Any]) -> None:
    ctx["wall_idx"] = (ctx["wall_idx"] + 1) % len(WALL_COLORS)
    ctx["wall_color"] = WALL_COLORS[ctx["wall_idx"]]


def on_mouse(button: int, x: int, y: int, ctx: dict[str, Any]):
    if button != 1:
        return 0

    if inside(x, y, ctx["btn_new"]):
        regenerate(ctx)
        redraw(ctx)
        return 0

    if inside(x, y, ctx["btn_path"]):
        ctx["show_path"] = not ctx["show_path"]
        redraw(ctx)
        return 0

    if inside(x, y, ctx["btn_wall"]):
        cycle_wall_color(ctx)
        redraw(ctx)
        return 0

    return 0


def on_key(keysym: int, ctx: dict[str, Any]):
    # Quit: ESC / q / 4
    if keysym in (65307, 113, 52):
        ctx["m"].mlx_loop_exit(ctx["mlx_ptr"])
        return 0

    # 1: NEW (regenerate)
    if keysym == 49:
        regenerate(ctx)
        redraw(ctx)
        return 0

    # 2: toggle path
    if keysym == 50:
        ctx["show_path"] = not ctx["show_path"]
        redraw(ctx)
        return 0

    # 3: wall color
    if keysym == 51:
        cycle_wall_color(ctx)
        redraw(ctx)
        return 0

    return 0


def interactive_display(cfg: Config) -> None:
    win_w = cfg.width * CELL + 1
    win_h = cfg.height * CELL + UI_H + 1

    m = Mlx()
    mlx_ptr = m.mlx_init()
    win_ptr = m.mlx_new_window(
        mlx_ptr,
        win_w,
        win_h,
        "A-Maze-ing  1:new 2:path 3:color 4:quit",
    )

    img = m.mlx_new_image(mlx_ptr, win_w, win_h)
    buf, bpp, line_length, endian = m.mlx_get_data_addr(img)

    ctx: dict[str, Any] = {
        "cfg": cfg,
        "seed": cfg.seed,
        "m": m,
        "mlx_ptr": mlx_ptr,
        "win_ptr": win_ptr,
        "img": img,
        "buf": buf,
        "line_length": line_length,
        "win_w": win_w,
        "win_h": win_h,
        "show_path": True,
        "wall_idx": 0,
        "wall_color": WALL_COLORS[0],
        # placeholders, filled by regenerate()
        "maze": [[int(N | E | S | W)]],
        "entry": cfg.entry,
        "exit": cfg.exit,
        "path_cells": set(),
    }

    ctx["btn_new"] = (PAD, 4, BTN_W, BTN_H)
    ctx["btn_path"] = (PAD + (BTN_W + BTN_GAP) * 1, 4, BTN_W, BTN_H)
    ctx["btn_wall"] = (PAD + (BTN_W + BTN_GAP) * 2, 4, BTN_W, BTN_H)

    regenerate(ctx)
    redraw(ctx)

    m.mlx_key_hook(win_ptr, on_key, ctx)
    m.mlx_mouse_hook(win_ptr, on_mouse, ctx)
    m.mlx_hook(win_ptr, 33, 0, lambda *_: m.mlx_loop_exit(mlx_ptr), None)

    m.mlx_loop(mlx_ptr)

    m.mlx_destroy_image(mlx_ptr, img)
    m.mlx_destroy_window(mlx_ptr, win_ptr)

if __name__ == "__main__":
    filename = sys.argv[1] if len(sys.argv) > 1 else "maze.txt"
    display_maze_file(filename)
