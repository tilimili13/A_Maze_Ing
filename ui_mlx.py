from __future__ import annotations
import logging

from typing import Sequence
from mlx import Mlx
from maze import make_maze
from utils import Maze, Button, Color, Config, Direction, Drawer, MlxContext, Point

# Wall bits (closed if bit=1)
N, E, S, W = 1, 2, 4, 8

CELL = 40
DOT_MARGIN = 12

# Toolbar UI
UI_H = 26
PAD = 6
BTN_W = 90
BTN_H = 18
BTN_GAP = 10


def draw_dot(
    drawer: Drawer,
    cx: int,
    cy: int,
    color: int
        ) -> None:
    x = cx * CELL + DOT_MARGIN
    y = cy * CELL + UI_H + DOT_MARGIN
    a = CELL - 2 * DOT_MARGIN
    drawer.fill_rect(x, y, a, a, color)


def path_cells_from_path(
    entry: Point,
    path: Sequence[Direction] | None
        ) -> set[Point]:
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


def redraw(ctx: MlxContext, cfg: Config) -> None:
    drawer: Drawer = ctx.drawer

    h = len(ctx.maze)
    w = len(ctx.maze[0])

    """Clear full background"""
    drawer.fill_rect(0, 0, ctx.win_w, ctx.win_h, fill_color=ctx.colors.bg)

    """Draw buttons """
    for b in (ctx.btn_new, ctx.btn_path, ctx.btn_wall):
        b.draw(drawer, ctx.colors)

    """Draw maze walls"""
    for y in range(h):
        for x in range(w):
            cell = int(ctx.maze[y][x])
            px = x * CELL
            py = y * CELL + UI_H

            if cell & N:
                drawer.hline(px, px + CELL, py, ctx.colors.wall)
            if cell & W:
                drawer.vline(px, py, py + CELL, ctx.colors.wall)

            if y == h - 1 and (cell & S):
                drawer.hline(px, px + CELL, py + CELL, ctx.colors.wall)
            if x == w - 1 and (cell & E):
                drawer.vline(px + CELL, py, py + CELL, ctx.colors.wall)

    """Path overlay"""
    if ctx.show_path:
        for (px, py) in ctx.path_cells:
            draw_dot(drawer, px, py, ctx.colors.path)

    """Entry / Exit"""
    (en_x, en_y) = cfg.entry
    (ex_x, ex_y) = cfg.exit
    draw_dot(drawer, en_x, en_y, ctx.colors.entry)
    draw_dot(drawer, ex_x, ex_y, ctx.colors.exit)

    """Blit image to window"""
    ctx.m.mlx_put_image_to_window(ctx.mlx_ptr, ctx.win_ptr, ctx.img, 0, 0)

    """Draw text on top after blit"""
    for button in (ctx.btn_new, ctx.btn_path, ctx.btn_wall):
        (tx, ty) = button.labelxy
        ctx.m.mlx_string_put(
            ctx.mlx_ptr, ctx.win_ptr, tx, ty, button.text_color, button.label
        )


def regenerate(ctx: MlxContext, cfg: Config) -> None:
    if ctx.cfg.seed is None:
        ctx.cfg.seed = 0
    ctx.cfg.seed += 1
    ctx.maze, path = make_maze(ctx.cfg, ctx.logger)
    ctx.path_cells = path_cells_from_path(cfg.entry, path)


def on_mouse(button: int, x: int, y: int, ctx: MlxContext) -> int:
    if button != 1:
        return 0
    for b in (ctx.btn_new, ctx.btn_path, ctx.btn_wall):
        if b.inside(x, y):
            if b.on_click is not None:
                b.on_click()
            redraw(ctx, ctx.cfg)
            break
    return 0


def on_key(keysym: int, ctx: MlxContext) -> int:
    # Quit: ESC / q / 4
    if keysym in (65307, 113, 52):
        ctx.m.mlx_loop_exit(ctx.mlx_ptr)
        return 0

    # 1: NEW (regenerate)
    if keysym == 49:
        regenerate(ctx, ctx.cfg)
        redraw(ctx, ctx.cfg)
        return 0

    # 2: toggle path
    if keysym == 50:
        ctx.show_path = not ctx.show_path
        redraw(ctx, ctx.cfg)
        return 0

    # 3: wall color
    if keysym == 51:
        ctx.colors.random()
        redraw(ctx, ctx.cfg)
        return 0

    return 0


def interactive_display(
    cfg: Config,
    colors: Color,
    logger: logging.Logger
) -> None:

    def click_new() -> None:
        regenerate(ctx, cfg)

    def click_path() -> None:
        ctx.show_path = not ctx.show_path
        ctx.btn_path.active = ctx.show_path

    def click_color() -> None:
        ctx.colors.random()

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
    btn_new = Button.add("NEW", on_click=click_new)
    btn_path = Button.add("PATH", on_click=click_path, active=cfg.show_path)
    btn_wall = Button.add("COLOR", on_click=click_color)
    ctx: MlxContext = MlxContext(
        cfg = cfg,
        m =  m,
        mlx_ptr =  mlx_ptr,
        win_ptr =  win_ptr,
        img =  img,
        drawer =  drawer,
        win_w =  win_w,
        win_h =  win_h,
        show_path =  cfg.show_path,
        wall_idx =  0,
        colors =  colors,
        maze =  Maze(),
        entry =  cfg.entry,
        exit =  cfg.exit,
        path_cells =  [],
        btn_new = btn_new,
        btn_path = btn_path,
        btn_wall = btn_wall,
        logger = logger
    )

    regenerate(ctx, cfg)
    redraw(ctx, cfg)

    m.mlx_key_hook(win_ptr, on_key, ctx)
    m.mlx_mouse_hook(win_ptr, on_mouse, ctx)
    m.mlx_hook(win_ptr, 33, 0,lambda *_: m.mlx_loop_exit(mlx_ptr), None)
    m.mlx_loop(mlx_ptr)
    m.mlx_destroy_image(mlx_ptr, img)
    m.mlx_destroy_window(mlx_ptr, win_ptr)
