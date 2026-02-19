from __future__ import annotations

import logging
import sys

from config import Config, load_config
from decorators import safe
from generator import generate_maze
from io_utils import dump_maze
from maze_types import Direction
from ui_ascii import AsciiColors, print_maze
from ui_mlx import interactive_display

# something will be here
from solution import (
    validate_maze,
    solve,
    path_to_str,
)


logger = logging.getLogger(__name__)

def colors_from_config(cfg: Config) -> AsciiColors:
    return AsciiColors(
        wall=cfg.color_wall,
        path=cfg.color_path,
        entry=cfg.color_entry,
        exit=cfg.color_exit,
        pattern42=cfg.color_pattern42,
        background=cfg.color_background,
    )

def generate_and_solve(cfg: Config) -> tuple[list[list[int]], list[Direction] | None]:
    maze = generate_maze(
        cfg.width,
        cfg.height,
        cfg.entry,
        cfg.exit,
        perfect=cfg.perfect,
        seed=cfg.seed,
    )

    # validate
    ok, messages = validate_maze(maze, perfect=cfg.perfect)
    for msg in messages:
        logger.info(msg)
    if not ok:
        raise RuntimeError("Generated maze failed validation — see log above")

    # solve
    path = solve(maze, cfg.entry, cfg.exit, perfect=cfg.perfect)
    return maze, path


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
    )

    config_file = sys.argv[1] if len(sys.argv) > 1 else "default.cfg"
    cfg = load_config(config_file)

    logger.info(
        "Config: %dx%d  entry=%s  exit=%s  perfect=%s  seed=%s",
        cfg.width, cfg.height, cfg.entry, cfg.exit, cfg.perfect, cfg.seed,
    )
    maze, path = generate_and_solve(cfg)

    # output file
    dump_maze(maze, cfg.entry, cfg.exit, path or [], cfg.output_file)
    logger.info("Maze written to %s", cfg.output_file)

    if path:
        logger.info("Shortest path (%d steps): %s", len(path), path_to_str(path))
    else:
        logger.warning("No path found from %s to %s!", cfg.entry, cfg.exit)

    # ASCII
    colors = colors_from_config(cfg)
    if cfg.display in ("ascii", "both"):
        print_maze(
            maze,
            entry=cfg.entry,
            exit_=cfg.exit,
            path=path,
            show_path=True,
            colors=colors,
        )

        # MLX
    if cfg.display in ("mlx", "both"):
        try:
            interactive_display(cfg)
        except ImportError as exc:
            logger.warning("MLX viewer not available (%s). Skipping MLX.", exc)

if __name__ == "__main__":
    main()
