# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    maze_types.py                                      :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: albezbor <albezbor@student.42tokyo.jp>     +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/02/20 21:07:39 by albezbor          #+#    #+#              #
#    Updated: 2026/02/20 21:07:39 by albezbor         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

from __future__ import annotations

from enum import IntFlag, auto
from typing import TypeAlias


Maze: TypeAlias = list[list[int]]
Point: TypeAlias = tuple[int, int]


class Direction(IntFlag):
    """Cardinal directions with bit flags for wall encoding."""
    NORTH = auto()
    EAST = auto()
    SOUTH = auto()
    WEST = auto()

    def __str__(self) -> str:
        if self.name:
            return self.name[0]
        return str(self.value)

    @property
    def opposite(self) -> Direction:
        return {
            Direction.NORTH: Direction.SOUTH,
            Direction.SOUTH: Direction.NORTH,
            Direction.EAST: Direction.WEST,
            Direction.WEST: Direction.EAST,
        }[self]

    @property
    def delta(self) -> tuple[int, int]:
        return {
            Direction.NORTH: (0, -1),
            Direction.EAST: (1, 0),
            Direction.SOUTH: (0, 1),
            Direction.WEST: (-1, 0),
        }[self]

    @classmethod
    def from_str(cls, value: str) -> Direction:
        value = value.upper()
        for member in cls:
            if member.name.startswith(value):
                return member
        raise ValueError(f"Invalid direction: {value}")


CLOSED_CELL = (
    Direction.NORTH
    | Direction.EAST
    | Direction.SOUTH
    | Direction.WEST
)

EMPTY_CELL = Direction(0)
