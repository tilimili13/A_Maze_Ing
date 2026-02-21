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

def make_maze(cfg: Config) -> tuple[list[list[int]], list[Direction] | None]:
    maze, path = generate_and_solve(cfg)
    dump_maze(maze, cfg.entry, cfg.exit, path or [], cfg.output_file)
    logger.info("Maze written to %s", cfg.output_file)
    logger.info("Shortest path (%d steps): %s", len(path), path_to_str(path))
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
    maze, path = make_maze(cfg)

    # ASCII
    if cfg.display in ("ascii", "both"):
        next_action: int = 0
        show_path=True
        while next_action != 4:
            print_maze(
                maze,
                colors=colors,
                entry=cfg.entry,
                exit_=cfg.exit,
                path=path,
                show_path=show_path,
            )
            print("=== A-maze-ing ===")
            print("1. Re-generate a new maze")
            print("2. Show/Hide path from entry to exit")
            print("3. Change maze colors")
            print("4. Quit")
            next_action = int(input("Choice? (1-4) "))
            if next_action == 1:
                if cfg.seed is None:
                    cfg.seed = 42
                else:
                    cfg.seed = int(cfg.seed) + 1
                maze, path = make_maze(cfg)
            elif next_action == 2:
                show_path = not show_path
            elif next_action == 3:
                colors.random()
            elif next_action != 4:
                while 1 <= next_action <= 4:
                    print(f"Wrong choice: {next_action}")
                    next_action = int(input("Choice? (1-4) "))




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
