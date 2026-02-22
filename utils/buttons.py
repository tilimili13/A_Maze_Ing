from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, ClassVar

from .drawer import Drawer
from .maze_types import Point
from .color import Color


@dataclass
class Button:
    """Buttons on the mlx window"""
    label: str
    x: int
    y: int
    w: int
    h: int
    on_click: Callable[[], None] | None = None
    active: bool = False,
    text_color: int = 0xFFFFFF,
    labelxy: Point | None = None
    # static variables
    count: ClassVar[int] = 0
    xpad: ClassVar[int] = 6
    ypad: ClassVar[int] = 4
    width: ClassVar[int] = 90
    height: ClassVar[int] = 18
    gap: ClassVar[int] = 10

    def inside(self, mx: int, my: int) -> bool:
        return self.x <= mx < self.x + self.w and \
                self.y <= my < self.y + self.h

    def draw(
        self,
        drawer: Drawer,
        colors: Color,
        pad_x: int = 10,
        center_text: bool = False,
    ) -> list[str]:
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
        bg = colors.btn_active if self.active else colors.btn

        """draw rectangle into image buffer"""
        drawer.fill_rect(
            self.x, 
            self.y, 
            self.w, 
            self.h, 
            fill_color=bg, 
            border_color=colors.btn_border
        )

        if center_text:
            approx_text_w = len(self.label) * 6
            tx = self.x + max(0, (self.w - approx_text_w) // 2)
        else:
            tx = self.x + pad_x
        ty = self.y + (self.h // 2) - 10
        self.labelxy = (tx, ty)
        self.text_color = colors.btn_text

# Button("COLOR", PAD + (BTN_W + BTN_GAP) * 2, 4, BTN_W, BTN_H, on_click=click_color),

    @classmethod
    def add(cls, 
        label: str, 
        on_click: Callable[[], None] | None = None,
        active: bool = False,
        text_color: int = 0xFFFFFF,
        labelxy: Point | None = None
            ) -> Button:
        x: int = Button.xpad + Button.count * (Button.width + Button.gap)
        y: int = Button.ypad
        Button.count += 1
        return cls(
            label = label,
            x = x,
            y = y,
            w = Button.width,
            h = Button.height,
            on_click = on_click,
            active = active,
            text_color = text_color,
            labelxy = labelxy
        )
        
