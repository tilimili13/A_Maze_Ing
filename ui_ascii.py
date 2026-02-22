from __future__ import annotations
import logging

from maze import make_maze
from typing import Sequence
from utils import Color, Maze, Point, Direction, CLOSED_CELL


def _fg(r: int, g: int, b: int) -> str:
    return f"\033[38;2;{r};{g};{b}m"


def _bg(r: int, g: int, b: int) -> str:
    return f"\033[48;2;{r};{g};{b}m"


RESET = "\033[0m"


def render_maze_ascii(
    maze: Maze,
    colors: Color,
    entry: Point | None = None,
    exit_: Point | None = None,
    path: Sequence[Direction] | None = None,
    show_path: bool = True
) -> str:
    """
    Render the maze as a multiline ASCII string.

    Layout per cell (2 chars wide for cell body):
      +--+--+
      |  |  |        top row = north walls (+ corners)
      +--+--+        cell body = 2 spaces or marker
      |  |  |
      +--+--+

    Markers:
      'O ' = entry
      'X ' = exit
      '## ' = '42' pattern cell
      'o ' = path cell
    """

    height = len(maze)
    width = len(maze[0])

    path_cells: set[Point] = set()
    if path and show_path:
        px, py = entry if entry else (0, 0)
        path_cells.add((px, py))
        for d in path:
            dx, dy = d.delta
            px, py = px + dx, py + dy
            path_cells.add((px, py))

    closed: set[Point] = {
        (x, y)
        for y in range(height)
        for x in range(width)
        if maze[y][x] == int(CLOSED_CELL)
    }

    lines: list[str] = []

    wall_fg = _fg(*Color.hex_to_rgb(colors.wall))

    for y in range(height):
        # top
        top = ""
        for x in range(width):
            cell = maze[y][x]
            top += wall_fg + "+" + RESET
            if cell & Direction.NORTH:
                top += wall_fg + "--" + RESET
            else:
                top += "  "
        top += wall_fg + "+" + RESET
        lines.append(top)
        # row
        row = ""
        for x in range(width):
            cell = maze[y][x]
            # left wall
            if cell & Direction.WEST:
                row += wall_fg + "|" + RESET
            else:
                row += " "
            # body
            body = _cell_body(x, y, entry, exit_, path_cells, closed, colors)
            row += body
        # right wall of last cell
        if maze[y][width - 1] & Direction.EAST:
            row += wall_fg + "|" + RESET
        else:
            row += " "
        lines.append(row)

    # bottom
    bottom = ""
    for x in range(width):
        cell = maze[height - 1][x]
        bottom += wall_fg + "+" + RESET
        if cell & Direction.SOUTH:
            bottom += wall_fg + "--" + RESET
        else:
            bottom += "  "
    bottom += wall_fg + "+" + RESET
    lines.append(bottom)

    return "\n".join(lines)


def _cell_body(
    x: int,
    y: int,
    entry: Point | None,
    exit_: Point | None,
    path_cells: set[Point],
    closed: set[Point],
    colors: Color,
) -> str:
    if (x, y) == entry:
        return _fg(*Color.hex_to_rgb(colors.entry)) + "O " + RESET
    if (x, y) == exit_:
        return _fg(*Color.hex_to_rgb(colors.exit)) + "X " + RESET
    if (x, y) in closed:
        return _bg(*Color.hex_to_rgb(colors.p42)) + "  " + RESET
    if (x, y) in path_cells:
        return _fg(*Color.hex_to_rgb(colors.path)) + "o " + RESET
    return _fg(*Color.hex_to_rgb(colors.bg)) + "  " + RESET

def _get_next_action() -> int:
    inp: str = input("Choice? (1-4) ")
    try:
        next_action = int(inp)
    except:
        next_action = 0
    return next_action


def print_maze(
    cfg: Config,
    colors: Color,
    logger: logging.Logger
) -> None:
        show_path = cfg.show_path
        next_action: int = 0
        maze, path = make_maze(cfg, logger)
        while next_action != 4:
            rendered = render_maze_ascii(
                maze,
                colors=colors,
                entry=cfg.entry,
                exit_=cfg.exit,
                path=path,
                show_path=show_path,
            )
            print(rendered)
            print("=== A-maze-ing ===")
            print("1. Re-generate a new maze")
            print("2. Show/Hide path from entry to exit")
            print("3. Change maze colors")
            print("4. Quit")
            next_action = _get_next_action()
            if next_action == 1:
                if cfg.seed is None:
                    cfg.seed = 42
                else:
                    cfg.seed = int(cfg.seed) + 1
                maze, path = make_maze(cfg, logger)
            elif next_action == 2:
                show_path = not show_path
            elif next_action == 3:
                colors.random()
            elif next_action != 4:
                while 1 <= next_action <= 4:
                    next_action = _get_next_action()
