import configparser
from dataclasses import dataclass

@dataclass
class Config:
    width: int
    height: int
    entry: tuple[int, int]
    exit: tuple[int, int]
    perfect: bool
    output_file: str = "maze.txt"
    algorithm: str = "backtracking"
    seed: int | None = None
    # colour settings (0xRRGGBB)
    color_wall: int = 0xFFFFFF
    color_path: int = 0x00FF00
    color_entry: int = 0x00AAFF
    color_exit: int = 0xFF3333
    color_pattern42: int = 0xFFAA00
    color_background: int = 0x000000
    # display mode
    display: str = "ascii"   # "ascii", "mlx", or "both"


def _parse_point(value: str) -> tuple[int, int]:
    parts = value.split(",")
    if len(parts) != 2:
        raise ValueError(f"Invalid point: {value!r} (expected 'x,y')")
    x = int(parts[0].strip())
    y = int(parts[1].strip())
    return (x, y)

def _parse_color(value: str) -> int:
    value = value.strip().lstrip("#")
    if value.lower().startswith("0x"):
        return int(value, 16)
    # try hex if it looks like hex (6 chars, all hex digits)
    if len(value) == 6:
        try:
            return int(value, 16)
        except ValueError:
            pass
    return int(value)


def load_config(filename: str = "default.cfg") -> Config:
    parser = configparser.ConfigParser()

    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()

    filtered = "\n".join(
        line for line in content.splitlines()
        if not line.strip().startswith("#")
    )

    parser.read_string("[DEFAULT]\n" + filtered)
    d = parser["DEFAULT"]

    return Config(
        width=d.getint("WIDTH", fallback=20),
        height=d.getint("HEIGHT", fallback=15),
        entry=_parse_point(d.get("ENTRY", "0,0").strip()),
        exit=_parse_point(d.get("EXIT", "0,0").strip()),
        output_file=d.get("OUTPUT_FILE", "maze.txt").strip(),
        perfect=d.getboolean("PERFECT", fallback=True),
        algorithm=d.get("ALGORITHM", "backtracking").strip(),
        seed=d.getint("SEED", fallback=None),
        color_wall=_parse_color(d.get("COLOR_WALL", "0xFFFFFF")),
        color_path=_parse_color(d.get("COLOR_PATH", "0x00FF00")),
        color_entry=_parse_color(d.get("COLOR_ENTRY", "0x00AAFF")),
        color_exit=_parse_color(d.get("COLOR_EXIT", "0xFF3333")),
        color_pattern42=_parse_color(d.get("COLOR_PATTERN42", "0xFFAA00")),
        color_background=_parse_color(d.get("COLOR_BACKGROUND", "0x000000")),
        display=d.get("DISPLAY", "ascii").strip().lower(),
    )
