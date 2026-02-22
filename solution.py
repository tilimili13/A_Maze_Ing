from collections import deque
from typing import Sequence
from utils import Maze, Point, Direction, CLOSED_CELL


def maze_dims(maze: Maze) -> tuple[int, int]:
    height = len(maze)
    width = len(maze[0]) if height else 0
    return width, height


def in_bounds(x: int, y: int, width: int, height: int) -> bool:
    return 0 <= x < width and 0 <= y < height


def can_move(maze: Maze, x: int, y: int, direction: Direction) -> bool:
    width, height = maze_dims(maze)
    if not in_bounds(x, y, width, height):
        return False

    if maze[y][x] & direction:
        return False

    dx, dy = direction.delta
    nx, ny = x + dx, y + dy

    if not in_bounds(nx, ny, width, height):
        return False

    if maze[ny][nx] & direction.opposite:
        return False

    return True


def get_neighbors(
    maze: Maze,
    x: int,
    y: int
) -> list[tuple[int, int, Direction]]:
    result: list[tuple[int, int, Direction]] = []
    for d in Direction:
        if can_move(maze, x, y, d):
            dx, dy = d.delta
            result.append((x + dx, y + dy, d))
    return result


def solve(
    maze: Maze,
    start: Point,
    end: Point,
) -> list[Direction]:
    if start == end:
        return []

    width, height = maze_dims(maze)
    sx, sy = start
    ex, ey = end

    visited: dict[Point, tuple[Point, Direction] | None] = {start: None}
    queue: deque[Point] = deque([start])

    while queue:
        cx, cy = queue.popleft()
        for nx, ny, d in get_neighbors(maze, cx, cy):
            if (nx, ny) not in visited:
                visited[(nx, ny)] = ((cx, cy), d)
                if (nx, ny) == end:
                    return _reconstruct_path(visited, end)
                queue.append((nx, ny))


def _reconstruct_path(
    visited: dict[Point, tuple[Point, Direction] | None],
    end: Point,
) -> list[Direction]:
    path: list[Direction] = []
    cur = end
    while (node_info := visited[cur]) is not None:
        prev, d = node_info
        path.append(d)
        cur = prev
    path.reverse()
    return path


def path_to_str(path: Sequence[Direction]) -> str:
    """Convert a list of Direction to the compact N/E/S/W string."""
    return "".join(str(d) for d in path)
