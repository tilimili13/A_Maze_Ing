from __future__ import annotations


class Drawer:
    def __init__(self, buf: memoryview, line_length: int) -> None:
        self.buf = buf
        self.line_length = line_length

    def put_pixel(
        self,
        x: int,
        y: int,
        color: int
            ) -> None:
        off = y * self.line_length + x * 4
        r = (color >> 16) & 0xFF
        g = (color >> 8) & 0xFF
        b = color & 0xFF
        self.buf[off + 0] = b
        self.buf[off + 1] = g
        self.buf[off + 2] = r
        self.buf[off + 3] = 255

    def hline(
        self,
        x0: int,
        x1: int,
        y: int,
        color: int
            ) -> None:
        if x0 > x1:
            x0, x1 = x1, x0
        for x in range(x0, x1 + 1):
            self.put_pixel(x, y, color)

    def vline(
        self,
        x: int,
        y0: int,
        y1: int,
        color: int
            ) -> None:
        if y0 > y1:
            y0, y1 = y1, y0
        for yy in range(y0, y1 + 1):
            self.put_pixel(x, yy, color)

    def fill_rect(
        self,
        x: int,
        y: int,
        w: int,
        h: int,
        fill_color: int | None = None,
        border_color: int | None = None,
            ) -> None:
        if fill_color is not None:
            for yy in range(y, y + h):
                self.hline(x, x + w - 1, yy, fill_color)
        if border_color is not None:
            self.hline(x, x + w - 1, y, border_color)
            self.hline(x, x + w - 1, y + h - 1, border_color)
            self.vline(x, y, y + h - 1, border_color)
            self.vline(x + w - 1, y, y + h - 1, border_color)
