from __future__ import annotations
import logging
from dataclasses import dataclass
from .config import Config
from mlx import Mlx
from .drawer import Drawer
from typing import Any, Sequence
from .maze_types import Maze, Point, Direction
from .buttons import Button
from .color import Color
@dataclass
class MlxContext:
    cfg: Config
    m: Mlx
    mlx_ptr: Any
    win_ptr: Any
    img: Any
    drawer: Drawer
    win_w: int
    win_h: int
    show_path: bool
    wall_idx: int
    colors: Color
    maze: Maze
    entry: Point
    exit: Point
    path_cells: Sequence[Direction]
    btn_new: Button
    btn_path: Button
    btn_wall: Button
    logger: logging.Logger
        
