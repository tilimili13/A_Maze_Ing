from __future__ import annotations
import logging
import sys

from ui_ascii import print_maze
from ui_mlx import interactive_display
from utils import Color, Config, safe



logger = logging.getLogger(__name__)

@safe
def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
    )

    config_file = sys.argv[1] if len(sys.argv) > 1 else "utils/default.cfg"
    cfg = Config.load(config_file)
    colors = Color(cfg)

    logger.info(
        "Config: %dx%d  entry=%s  exit=%s  perfect=%s  seed=%s",
        cfg.width, cfg.height, cfg.entry, cfg.exit, cfg.perfect, cfg.seed,
    )

    if cfg.display == "ascii":
        print_maze(cfg, colors, logger)
    else:
        interactive_display(cfg, colors, logger)

if __name__ == "__main__":
    main()
