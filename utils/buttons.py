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
        text: int = 0xFFFFFF,
    ) -> None:
        bg = fill_active if self.active else fill

        # draw rectangle into image buffer
        drawer.fill_rect(
            self.x, self.y, self.w, self.h, fill_color=bg, border_color=border
        )
        """
        queue text to draw AFTER the image is blitted
        (mlx_string_put draws directly to the window)
        """
        ctx.setdefault("text", []).append(
            (self.x + 10, self.y + (self.h // 2), text, self.label)
        )
