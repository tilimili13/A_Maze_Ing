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
        width=int(d.get("WIDTH", "20")),
        height=int(d.get("HEIGHT", "15")),
        entry=_parse_point(d.get("ENTRY", "0,0")),
        exit=_parse_point(d.get("EXIT", "0,0")),
        output_file=d.get("OUTPUT_FILE", "maze.txt"),
        perfect=d.getboolean("PERFECT", fallback=True),
        algorithm=d.get("ALGORITHM", "backtracking").strip,
        seed=(int(d["SEED"]) if "SEED" in d else None),
    )
