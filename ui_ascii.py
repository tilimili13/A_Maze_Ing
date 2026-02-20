from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from utils.maze_types import Maze, Point, Direction, CLOSED_CELL

def _fg(r: int, g: int, b: int) -> str:
    return f"\033[38;2;{r};{g};{b}m"


def _bg(r: int, g: int, b: int) -> str:
    return f"\033[48;2;{r};{g};{b}m"


RESET = "\033[0m"


def _hex_to_rgb(colour: int) -> tuple[int, int, int]:
    return (colour >> 16) & 0xFF, (colour >> 8) & 0xFF, colour & 0xFF

@dataclass
class AsciiColors:
    wall: int = 0xFFFFFF
    path: int = 0x00FF00
    entry: int = 0x00AAFF
    exit: int = 0xFF3333
    pattern42: int = 0xFFAA00
    background: int = 0x000000

def render_maze_ascii(
    maze: Maze,
    *,
    entry: Point | None = None,
    exit_: Point | None = None,
    path: Sequence[Direction] | None = None,
    show_path: bool = True,
    colors: AsciiColors | None = None,
    use_color: bool = True,
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
    if colors is None:
        colors = AsciiColors()

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

    wall_fg = _fg(*_hex_to_rgb(colors.wall)) if use_color else ""
    rst = RESET if use_color else ""

    for y in range(height):
        # top
        top = ""
        for x in range(width):
            cell = maze[y][x]
            top += wall_fg + "+" + rst
            if cell & Direction.NORTH:
                top += wall_fg + "--" + rst
            else:
                top += "  "
        top += wall_fg + "+" + rst
        lines.append(top)
        # row
        row = ""
        for x in range(width):
            cell = maze[y][x]
            # left wall
            if cell & Direction.WEST:
                row += wall_fg + "|" + rst
            else:
                row += " "
            # body
            body = _cell_body(
                x, y, entry, exit_, path_cells, closed, colors, use_color
            )
            row += body
        # right wall of last cell
        if maze[y][width - 1] & Direction.EAST:
            row += wall_fg + "|" + rst
        else:
            row += " "
        lines.append(row)

    # bottom
    bottom = ""
    for x in range(width):
        cell = maze[height - 1][x]
        bottom += wall_fg + "+" + rst
        if cell & Direction.SOUTH:
            bottom += wall_fg + "--" + rst
        else:
            bottom += "  "
    bottom += wall_fg + "+" + rst
    lines.append(bottom)

    return "\n".join(lines)


def _cell_body(
    x: int,
    y: int,
    entry: Point | None,
    exit_: Point | None,
    path_cells: set[Point],
    closed: set[Point],
    colors: AsciiColors,
    use_color: bool,
) -> str:
    rst = RESET if use_color else ""

    if (x, y) == entry:
        if use_color:
            return _fg(*_hex_to_rgb(colors.entry)) + "O " + rst
        return "O "
    if (x, y) == exit_:
        if use_color:
            return _fg(*_hex_to_rgb(colors.exit)) + "X " + rst
        return "X "
    if (x, y) in closed:
        if use_color:
            return _bg(*_hex_to_rgb(colors.pattern42)) + "  " + rst
        return "##"
    if (x, y) in path_cells:
        if use_color:
            return _fg(*_hex_to_rgb(colors.path)) + "o " + rst
        return "o "
    return "  "


def print_maze(
    maze: Maze,
    *,
    entry: Point | None = None,
    exit_: Point | None = None,
    path: Sequence[Direction] | None = None,
    show_path: bool = True,
    colors: AsciiColors | None = None,
    use_color: bool = True,
) -> None:
    print(
        render_maze_ascii(
            maze,
            entry=entry,
            exit_=exit_,
            path=path,
            show_path=show_path,
            colors=colors,
            use_color=use_color,
        )
    )
