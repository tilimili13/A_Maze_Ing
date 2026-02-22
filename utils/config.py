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
    show_path: bool
    output_file: str = "maze.txt"
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

    @classmethod
    def load(cls, filename: str = "utils/default.cfg") -> Config:
        config = configparser.ConfigParser()
        content = ""
        try:
            with open(filename, "r", encoding="utf-8") as f:
                content = f.read()
        except:
            with open("utils/default.cfg", "r", encoding="utf-8") as f:
                content = f.read()

        filtered = "\n".join(
            line for line in content.splitlines()
            if not line.strip().startswith("#")
        )
        try:
            config.read_string("[DEFAULT]\n" + filtered)
        except configparser.ParsingError as e:
            msg: str = "Wrong format of config file:"
            for line_content in e.errors:
                msg += f" {line_content!r}"
            raise ValueError(msg)

        d = config["DEFAULT"]
        for option in ("WIDTH", "HEIGHT", "ENTRY", "EXIT", "PERFECT"):
            if not config.has_option("DEFAULT", option):
                raise ValueError(f"Key {option} is not set in config")
        width = cls._getint(d, "WIDTH")
        height = cls._getint(d, "HEIGHT")
        entry=cls._parse_point("ENTRY", d.get("ENTRY", fallback=None).strip())
        exit_=cls._parse_point("ENTRY", d.get("EXIT", fallback=None).strip())
        if width < 1:
            raise ValueError("Please set positive WIDTH value")
        if height < 1:
            raise ValueError("Please set positive HEIGHT value")
        if entry[0] < 0 or entry[0] >= width:
            raise ValueError("Entry point is out of width range")
        if entry[1] < 0 or entry[1] >= height:
            raise ValueError("Entry point is out of height range")
        if exit_[0] < 0 or exit_[0] >= width:
            raise ValueError("Exit point is out of width range")
        if exit_[1] < 0 or exit_[1] >= height:
            raise ValueError("Exit point is out of height range")
        try:
            perfect=d.getboolean("PERFECT")
        except:
            raise ValueError("Wrong format of PERFECT key")
        return cls(
            width=width,
            height=height,
            entry=entry,
            exit=exit_,
            output_file=d.get("OUTPUT_FILE", "maze.txt").strip(),
            perfect=perfect,
            seed=d.getint("SEED", fallback=None),
            show_path=d.getboolean("SHOW_PATH", fallback=True),
            color_wall=cls._parse_color(d.get("COLOR_WALL", "0xFFFFFF")),
            color_path=cls._parse_color(d.get("COLOR_PATH", "0x00FF00")),
            color_entry=cls._parse_color(d.get("COLOR_ENTRY", "0x00AAFF")),
            color_exit=cls._parse_color(d.get("COLOR_EXIT", "0xFF3333")),
            color_pattern42=cls._parse_color(d.get("COLOR_PATTERN42", "0xFFAA00")),
            color_background=cls._parse_color(d.get("COLOR_BACKGROUND", "0x000000")),
            display=d.get("DISPLAY", "ascii").strip().lower(),
    )

    @staticmethod
    def _getint(section: configparser.SectionProxy, name: str) -> int:
        try:
            val: int = int(section.get(name))
        except:
            raise(f"{name} should be integer")
        return val

    @staticmethod
    def _parse_point(name: str, value: str | None) -> tuple[int, int]:
        parts = value.split(",")
        if len(parts) != 2:
            raise ValueError(f"Invalid point {name}: {value!r} (expected 'x,y')")
        try:
            x = int(parts[0].strip())
            y = int(parts[1].strip())
        except:
            raise ValueError(f"Wrong format of {name}")
        return (x, y)

    @staticmethod
    def _parse_color(value: str) -> int:
        value = value.strip().lstrip("#")
        if value.lower().startswith("0x"):
            return int(value, 16)
        if len(value) == 6:
            try:
                return int(value, 16)
            except ValueError:
                pass
        return int(value)



