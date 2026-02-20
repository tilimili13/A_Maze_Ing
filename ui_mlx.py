from __future__ import annotations

import sys
from typing import Any

from mlx import Mlx

from config import Config
from generator import generate_maze
from solution import solve
from utils.io_utils import dump_maze
from utils.maze_types import Direction
from utils.drawer import Drawer
from utils.buttons import Button

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


def fill_cell(
    drawer: Drawer, 
    cx: int, 
    cy: int, 
    color: int, 
    y_offset: int
    ) -> None:
    margin = 7
    x0 = cx * CELL + margin
    y0 = cy * CELL + y_offset + margin
    x1 = (cx + 1) * CELL - margin
    y1 = (cy + 1) * CELL + y_offset - margin
    for y in range(y0, y1 + 1):
        drawer.hline(x0, x1, y, color)

def path_cells_from_dirs(
    entry: tuple[int, int], 
    path: list[Direction] | None
    ) -> set[tuple[int, int]]:
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

def redraw(ctx: dict[str, Any]) -> None:
    drawer: Drawer = ctx["drawer"]
    maze = ctx["maze"]
    entry = ctx["entry"]
    exit_ = ctx["exit"]
    y_offset = UI_H
    wall_color = ctx["wall_color"]

    ctx["text"] = []

    h = len(maze)
    w = len(maze[0])

    """Clear full background"""
    drawer.fill_rect(0, 0, ctx["win_w"], ctx["win_h"], fill_color=BG_COLOR)

    """Draw buttons (rectangles into buffer, labels queued into ctx["text"])"""
    for b in ctx["buttons"]:
        b.draw(drawer, ctx)

    """Draw maze walls"""
    for y in range(h):
        for x in range(w):
            cell = int(maze[y][x])
            px = x * CELL
            py = y * CELL + y_offset

            if cell & N:
                drawer.hline(px, px + CELL, py, wall_color)
            if cell & W:
                drawer.vline(px, py, py + CELL, wall_color)

            if y == h - 1 and (cell & S):
                drawer.hline(px, px + CELL, py + CELL, wall_color)
            if x == w - 1 and (cell & E):
                drawer.vline(px + CELL, py, py + CELL, wall_color)

    """Path overlay"""
    if ctx.get("show_path", False):
        for (px, py) in ctx["path_cells"]:
            fill_cell(drawer, px, py, PATH_COLOR, y_offset)

    """Entry/Exit markers"""
    fill_cell(drawer, entry[0], entry[1], ENTRY_COLOR, y_offset)
    fill_cell(drawer, exit_[0], exit_[1], EXIT_COLOR, y_offset)

    """Blit image to window"""
    m = ctx["m"]
    m.mlx_put_image_to_window(ctx["mlx_ptr"], ctx["win_ptr"], ctx["img"], 0, 0)

    """Draw text on top after blit"""
    for tx, ty, color, s in ctx["text"]:
        m.mlx_string_put(ctx["mlx_ptr"], ctx["win_ptr"], tx, ty, color, s)

    """Walls"""
    for y in range(h):
        for x in range(w):
            cell = int(maze[y][x])
            px = x * CELL
            py = y * CELL + y_offset

            if cell & N:
                drawer.hline(px, px + CELL, py, wall_color)
            if cell & W:
                drawer.vline(px, py, py + CELL, wall_color)

            if y == h - 1 and (cell & S):
                drawer.hline(px, px + CELL, py + CELL, wall_color)
            if x == w - 1 and (cell & E):
                drawer.vline(px + CELL, py, py + CELL, wall_color)

    """Path overlay"""
    if ctx["show_path"]:
        for (x, y) in ctx["path_cells"]:
            fill_cell(drawer, x, y, PATH_COLOR, y_offset)

    """Entry / Exit"""
    fill_cell(drawer, entry[0], entry[1], ENTRY_COLOR, y_offset)
    fill_cell(drawer, exit_[0], exit_[1], EXIT_COLOR, y_offset)

    m: Mlx = ctx["m"]
    m.mlx_put_image_to_window(
        ctx["mlx_ptr"], 
        ctx["win_ptr"], 
        ctx["img"], 
        0, 0)


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
    path = solve(
        maze, 
        cfg.entry, 
        cfg.exit, 
        perfect=cfg.perfect) or []

    ctx["maze"] = maze
    ctx["entry"] = cfg.entry
    ctx["exit"] = cfg.exit
    ctx["path_cells"] = path_cells_from_dirs(cfg.entry, path)

    dump_maze(maze, cfg.entry, cfg.exit, path, cfg.output_file)


def cycle_wall_color(ctx: dict[str, Any]) -> None:
    ctx["wall_idx"] = (ctx["wall_idx"] + 1) % len(WALL_COLORS)
    ctx["wall_color"] = WALL_COLORS[ctx["wall_idx"]]


def on_mouse(button: int, x: int, y: int, ctx: dict):
    if button != 1:
        return 0

    for b in ctx["buttons"]:
        if b.inside(x, y):
            if b.on_click is not None:
                b.on_click()
            redraw(ctx)
            break

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
    buf, _, line_length, _ = m.mlx_get_data_addr(img)
    
    drawer = Drawer(buf, line_length)


    ctx: dict[str, Any] = {
        "cfg": cfg,
        "seed": cfg.seed,
        "m": m,
        "mlx_ptr": mlx_ptr,
        "win_ptr": win_ptr,
        "img": img,
        "drawer": drawer,
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
    
    ctx["show_path"] = True
    
    def click_new() -> None:
        regenerate(ctx)

    def click_path() -> None:
        ctx["show_path"] = not ctx["show_path"]
        ctx["btn_path"].active = ctx["show_path"]
        
    def click_color() -> None:
        cycle_wall_color(ctx)
        
    btn_new = Button("NEW", PAD, 4, BTN_W, BTN_H, on_click=click_new)
    btn_path = Button("PATH", PAD + (BTN_W + BTN_GAP), 4, BTN_W, BTN_H,
                      on_click=click_path, active=True)
    btn_wall = Button("COLOR", PAD + (BTN_W + BTN_GAP) * 2, 4, BTN_W, BTN_H,
                      on_click=click_color)
    
    ctx["btn_path"] = btn_path
    ctx["buttons"] = [btn_new, btn_path, btn_wall]

    regenerate(ctx)
    redraw(ctx)

    m.mlx_key_hook(win_ptr, on_key, ctx)
    m.mlx_mouse_hook(win_ptr, on_mouse, ctx)
    m.mlx_hook(win_ptr, 
               33, 0, 
               lambda *_: m.mlx_loop_exit(mlx_ptr), 
               None)

    m.mlx_loop(mlx_ptr)

    m.mlx_destroy_image(mlx_ptr, img)
    m.mlx_destroy_window(mlx_ptr, win_ptr)
