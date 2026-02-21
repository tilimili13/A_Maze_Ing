from __future__ import annotations

from typing import Any, Sequence

from mlx import Mlx

from generator import generate_maze
from solution import solve
from utils import Button, Config, Direction, Drawer, dump_maze, MlxContext, Point

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
    y_offset = UI_H

    h = len(ctx.maze)
    w = len(ctx.maze[0])

    """Clear full background"""
    drawer.fill_rect(0, 0, ctx.win_w, ctx.win_h, fill_color=BG_COLOR)

    """Draw buttons """
    for b in (ctx.btn_new, ctx.btn_path, ctx.btn_wall):
        b.draw(drawer, ctx)

    """Draw maze walls"""
    for y in range(h):
        for x in range(w):
            cell = int(ctx.maze[y][x])
            px = x * CELL
            py = y * CELL + y_offset

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
            fill_cell(drawer, px, py, ctx.colors.path, y_offset)

    """Blit image to window"""
    ctx.m.mlx_put_image_to_window(ctx.mlx_ptr, ctx.win_ptr, ctx.img, 0, 0)

    """Walls"""
    for y in range(h):
        for x in range(w):
            cell = int(ctx.maze[y][x])
            px = x * CELL
            py = y * CELL + y_offset

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
        for (x, y) in ctx.path_cells:
            fill_cell(drawer, x, y, PATH_COLOR, y_offset)

    """Entry / Exit"""
    (en_x, en_y) = cfg.entry
    (ex_x, ex_y) = cfg.exit
    fill_cell(drawer, en_x, en_y, ctx.colors.entry, y_offset)
    fill_cell(drawer, ex_x, ex_y, ctx.colors.exit, y_offset)

    ctx.m.mlx_put_image_to_window(ctx.mlx_ptr, ctx.win_ptr, ctx.img, 0, 0)

    """Draw text on top after blit"""
    for button in (ctx.btn_new, ctx.btn_path, ctx.btn_wall):
        (tx, ty) = button.labelxy
        ctx.m.mlx_string_put(
            ctx.mlx_ptr, ctx.win_ptr, tx, ty, button.text_color, button.label
        )


def regenerate(ctx: MlxContext, cfg: Config, maze: Maze | None = None) -> None:
    seed = ctx.seed
    if seed is None:
        seed = cfg.seed
    if seed is None:
        seed = 0
    seed += 1
    ctx.seed = seed

    path = []
    if maze is None:
        maze = generate_maze(
            cfg.width, cfg.height, cfg.entry, cfg.exit, cfg.perfect, seed
        )
        path = solve(maze, cfg.entry, cfg.exit, perfect=cfg.perfect) or []

    ctx.maze = maze
    ctx.entry = cfg.entry
    ctx.exit = cfg.exit
    ctx.path_cells = path_cells_from_path(cfg.entry, path)

    dump_maze(maze, cfg.entry, cfg.exit, path, cfg.output_file)

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
    maze: Maze,
    colors: Color,
    path: Sequence[Direction] | None = None,
    show_path: bool = True
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

    ctx: MlxContext = MlxContext(
        cfg = cfg,
        seed = cfg.seed,
        m =  m,
        mlx_ptr =  mlx_ptr,
        win_ptr =  win_ptr,
        img =  img,
        drawer =  drawer,
        win_w =  win_w,
        win_h =  win_h,
        show_path =  True,
        wall_idx =  0,
        colors =  colors,
        # placeholders, filled by regenerate()
        maze =  maze,
        entry =  cfg.entry,
        exit =  cfg.exit,
        path_cells =  path,
        btn_new = Button("NEW", PAD, 4, BTN_W, BTN_H, on_click=click_new),
        btn_path = Button("PATH", PAD + (BTN_W + BTN_GAP), 4, 
                    BTN_W, BTN_H, on_click=click_path, active=True),
        btn_wall = Button("COLOR", PAD + (BTN_W + BTN_GAP) * 2, 4, 
                    BTN_W, BTN_H, on_click=click_color)
    )

    regenerate(ctx, cfg, maze)
    redraw(ctx, cfg)

    m.mlx_key_hook(win_ptr, on_key, ctx)
    m.mlx_mouse_hook(win_ptr, on_mouse, ctx)
    m.mlx_hook(win_ptr, 33, 0,lambda *_: m.mlx_loop_exit(mlx_ptr), None)
    m.mlx_loop(mlx_ptr)
    m.mlx_destroy_image(mlx_ptr, img)
    m.mlx_destroy_window(mlx_ptr, win_ptr)
