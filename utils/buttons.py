from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .drawer import Drawer


@dataclass
class Button:
    label: str
    x: int
    y: int
    w: int
    h: int
    on_click: Callable[[], None] | None = None
    active: bool = False

    def inside(self, mx: int, my: int) -> bool:
        return self.x <= mx < self.x + self.w and \
                self.y <= my < self.y + self.h

    def draw(
        self,
        drawer: Drawer,
        ctx: dict,
        fill: int = 0x404040,
        fill_active: int = 0x606060,
        border: int = 0xA0A0A0,
        text_color: int = 0xFFFFFF,
        pad_x: int = 10,
        text_baseline_fix: int = 4,
        center_text: bool = False,
    ) -> None:
        """Draw the button and queue its label for later window-text rendering.

        Args:
            drawer: Drawer used to render into the image buffer.
            ctx: UI context dict. This function appends to ctx["text"].
            fill: Background color when inactive.
            fill_active: Background color when active.
            border: Border color.
            text_color: Label color (used by mlx_string_put).
            pad_x: Left padding for label if not centered.
            text_baseline_fix: Small Y offset to visually center MLX text.
            center_text: If True, approximate horizontal centering.
        """
        bg = fill_active if self.active else fill

        """draw rectangle into image buffer"""
        drawer.fill_rect(
            self.x, self.y, self.w, self.h, fill_color=bg, border_color=border
        )

        if center_text:
            approx_text_w = len(self.label) * 6
            tx = self.x + max(0, (self.w - approx_text_w) // 2)
        else:
            tx = self.x + pad_x

        ty = self.y + (self.h // 2) - 10

        ctx.setdefault("text", []).append((tx, ty, text_color, self.label))
