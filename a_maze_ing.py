from __future__ import annotations
import logging
import sys
from generator import generate_maze
from utils import Color, Config, Direction, dump_maze
from ui_ascii import print_maze
from ui_mlx import interactive_display

# something will be here
from solution import (
    validate_maze,
    solve,
    path_to_str,
)


logger = logging.getLogger(__name__)


def generate_and_solve(cfg: Config) -> \
        tuple[list[list[int]], list[Direction] | None]:
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
    cfg = Config.load(config_file)
    colors = Color(cfg)

    logger.info(
        "Config: %dx%d  entry=%s  exit=%s  perfect=%s  seed=%s",
        cfg.width, cfg.height, cfg.entry, cfg.exit, cfg.perfect, cfg.seed,
    )
    maze, path = generate_and_solve(cfg)

    # output file
    dump_maze(maze, cfg.entry, cfg.exit, path or [], cfg.output_file)
    logger.info("Maze written to %s", cfg.output_file)

    if path:
        logger.info(
            "Shortest path (%d steps): %s", len(path), path_to_str(path)
        )
    else:
        logger.warning("No path found from %s to %s!", cfg.entry, cfg.exit)

    # ASCII
    if cfg.display in ("ascii", "both"):
        print_maze(
            maze,
            colors=colors,
            entry=cfg.entry,
            exit_=cfg.exit,
            path=path,
            show_path=True,
        )

        # MLX
    if cfg.display in ("mlx", "both"):
        try:
            interactive_display(
                cfg, 
                maze,
                colors=colors,
                path=path,
                show_path=True
            )
        except ImportError as exc:
            logger.warning("MLX viewer not available (%s). Skipping MLX.", exc)


if __name__ == "__main__":
    main()
