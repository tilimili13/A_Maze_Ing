from __future__ import annotations

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


def _parse_point(value: str) -> tuple[int, int]:
    parts = value.split(",")
    if len(parts) != 2:
        raise ValueError(f"Invalid point: {value!r} (expected 'x,y')")
    x = int(parts[0].strip())
    y = int(parts[1].strip())
    return (x, y)


def load_config(filename: str = "default.cfg") -> Config:
    parser = configparser.ConfigParser()

    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()

    parser.read_string("[DEFAULT]\n" + content)
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
    )
