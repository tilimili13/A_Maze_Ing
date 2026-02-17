class Button:
    x: int
    y: int
    w: int
    h: int
    label: str
    def __init__(self, label: str, x: int, y: int, w: int, h: int):
        self.label = label
        self.x = x
        self.y = y
        self.w = w
        self.h = h