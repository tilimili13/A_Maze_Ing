from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable
from config import Config
from .maze_types import Maze, Point, Direction



@dataclass
class AsciiColors:
    wall: int = 0xFFFFFF
    path: int = 0x00FF00
    entry: int = 0x00AAFF
    exit: int = 0xFF3333
    pattern42: int = 0xFFAA00
    background: int = 0x000000

def colors_from_config(cfg: Config) -> AsciiColors:
    return AsciiColors(
        wall=cfg.color_wall,
        path=cfg.color_path,
        entry=cfg.color_entry,
        exit=cfg.color_exit,
        pattern42=cfg.color_pattern42,
        background=cfg.color_background,
    )

def dump_maze(
    maze: Maze,
    start: Point | None,
    finish: Point | None,
    path: Iterable[Direction],
    filename: str,
) -> None:
    """
    Write maze to file in required format:

    - HEIGHT lines of WIDTH hex digits
    - empty line
    - entry (x,y)
    - exit (x,y)
    - path string (N/E/S/W)
    """

    if not maze:
        raise ValueError("Maze is empty")

    width = len(maze[0])

    with open(filename, "w", encoding="utf-8", newline="\n") as f:

        # Write maze grid
        for row_index, row in enumerate(maze):

            if len(row) != width:
                raise ValueError(
                    f"Inconsistent row width at row {row_index}"
                )

            hex_row = []

            for col_index, cell in enumerate(row):

                if not isinstance(cell, int):
                    raise ValueError(
                        f"Invalid cell type at ({col_index},{row_index})"
                    )

                # Ensure single hex digit
                if not (0 <= cell <= 0xF):
                    raise ValueError(
                        f"Cell value out of range at "
                        f"({col_index},{row_index}): {cell}"
                    )

                hex_row.append(f"{int(cell):X}")

            f.write("".join(hex_row) + "\n")
        # Empty line
        f.write("\n")
        # Entry / Exit
        if start:
            f.write(f"{start[0]},{start[1]}\n")
        else:
            f.write("\n")

        if finish:
            f.write(f"{finish[0]},{finish[1]}\n")
        else:
            f.write("\n")

        # 1Path
        f.write("".join(str(d) for d in path) + "\n")


def load_maze(filename: str) -> Maze:
    maze: Maze = []

    with open(filename, "r", encoding="utf-8") as f:
        for line_number, line in enumerate(f, start=1):
            line = line.rstrip("\n")

            if not line:
                break

            row = []

            for col_index, char in enumerate(line):

                if char not in "0123456789ABCDEFabcdef":
                    raise ValueError(
                        f"Invalid hex char at line {line_number}, "
                        f"column {col_index}"
                    )

                row.append(int(char, 16))

            maze.append(row)

    if not maze:
        raise ValueError("Maze file is empty")

    width = len(maze[0])
    for row_index, row in enumerate(maze):
        if len(row) != width:
            raise ValueError(
                f"Inconsistent row width at row {row_index}"
            )

    return maze
