
from __future__ import annotations
import logging
import sys
from generator import generate_maze
from solution import solve, path_to_str
from utils import Config, Direction, dump_maze

def _generate_and_solve(cfg: Config, logger: logging.Logger) -> \
        tuple[list[list[int]], list[Direction] | None]:
    maze = generate_maze(
        cfg.width,
        cfg.height,
        cfg.entry,
        cfg.exit,
        perfect=cfg.perfect,
        seed=cfg.seed,
    )

    path = solve(maze, cfg.entry, cfg.exit)
    return maze, path

def make_maze(cfg: Config, logger: logging.Logger) -> \
        tuple[list[list[int]], list[Direction] | None]:
    maze, path = _generate_and_solve(cfg, logger)
    dump_maze(maze, cfg.entry, cfg.exit, path or [], cfg.output_file)
    logger.info("Maze written to %s", cfg.output_file)
    logger.info("Shortest path (%d steps): %s", len(path), path_to_str(path))
    return maze, path