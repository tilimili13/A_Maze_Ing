from __future__ import annotations

import random
import colorsys
from dataclasses import dataclass
from .config import Config

@dataclass
class MazeColors:
    wall: int = 0xFFFFFF
    path: int = 0x00FF00
    entry: int = 0x00AAFF
    exit: int = 0xFF3333
    p42: int = 0xFFAA00
    bg: int = 0x000000

class Color:
    wall: int       = 0
    path: int       = 0
    entry: int      = 0
    exit: int       = 0
    p42: int        = 0
    bg: int         = 0
    UI_BG: int      = 0x202020
    BTN: int        = 0x404040
    BTN_ACTIVE: int = 0x606060
    BTN_BORDER: int = 0xA0A0A0
    default: MazeColors

    def __init__(self, cfg: Config) -> None:
        self.default = MazeColors()
        self.default.wall = cfg.color_wall
        self.default.path = cfg.color_path
        self.default.entry = cfg.color_entry
        self.default.exit = cfg.color_exit
        self.default.p42 = cfg.color_pattern42
        self.default.bg = cfg.color_background
        self.set_default()

    def set_default(self) -> None:
        self.wall = self.default.wall
        self.path = self.default.path
        self.entry = self.default.entry
        self.exit = self.default.exit
        self.p42 = self.default.p42
        self.bg = self.default.bg

    def random(self) -> None:
        """
        Generates a set of visually distinct hex colors for a console maze.
        Uses evenly spaced hues on the color wheel to guarantee high contrast.
        """
        start_hue = random.random()
        new_colors = []
        for i in range(5):
            hue = (start_hue + (i / 5.0)) % 1.0
            saturation = 1.0 if i == 4 else 0.85
            value = 1.0 if i == 4 else 0.85
            r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
            color_hex = (int(r * 255) << 16) | (int(g * 255) << 8) | int(b * 255)
            new_colors.append(color_hex)
        self.wall, self.path, self.entry, self.exit, self.p42 = new_colors
        p42_hue = (start_hue + (4 / 5.0)) % 1.0
        bg_hue = (p42_hue + 0.5) % 1.0
        bg_r, bg_g, bg_b = colorsys.hsv_to_rgb(bg_hue, 0.5, 0.15)
        self.bg = (int(bg_r * 255) << 16) | (int(bg_g * 255) << 8) | int(bg_b * 255)