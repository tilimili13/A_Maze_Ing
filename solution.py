# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    solution.py                                        :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: albezbor <albezbor@student.42tokyo.jp>     +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/02/20 21:08:29 by albezbor          #+#    #+#              #
#    Updated: 2026/02/20 21:08:30 by albezbor         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

from collections import deque
from typing import Sequence

from utils.maze_types import Maze, Point, Direction, CLOSED_CELL

def maze_dims(maze: Maze) -> tuple[int, int]:
    height = len(maze)
    width = len(maze[0]) if height else 0
    return width, height


def in_bounds(x: int, y: int, width: int, height: int) -> bool:
    return 0 <= x < width and 0 <= y < height


def is_closed_cell(maze: Maze, x: int, y: int) -> bool:
    return maze[y][x] == int(CLOSED_CELL)


def can_move(maze: Maze, x: int, y: int, direction: Direction) -> bool:
    width, height = maze_dims(maze)
    if not in_bounds(x, y, width, height):
        return False

    # wall on departure side?
    if maze[y][x] & direction:
        return False

    dx, dy = direction.delta
    nx, ny = x + dx, y + dy

    if not in_bounds(nx, ny, width, height):
        return False

    # wall on arrival side?
    if maze[ny][nx] & direction.opposite:
        return False

    return True

def get_neighbors(maze: Maze, x: int, y: int) -> list[tuple[int, int, Direction]]:
    result: list[tuple[int, int, Direction]] = []
    for d in Direction:
        if can_move(maze, x, y, d):
            dx, dy = d.delta
            result.append((x + dx, y + dy, d))
    return result

def bfs_shortest_path(
    maze: Maze,
    start: Point,
    end: Point,
) -> list[Direction] | None:
    if start == end:
        return []

    width, height = maze_dims(maze)
    sx, sy = start
    ex, ey = end

    if not (in_bounds(sx, sy, width, height) and in_bounds(ex, ey, width, height)):
        return None

    visited: dict[Point, tuple[Point, Direction] | None] = {start: None}
    queue: deque[Point] = deque([start])

    while queue:
        cx, cy = queue.popleft()

        for nx, ny, d in get_neighbors(maze, cx, cy):
            if (nx, ny) not in visited:
                visited[(nx, ny)] = ((cx, cy), d)
                if (nx, ny) == end:
                    # reconstruct
                    return _reconstruct_path(visited, end)
                queue.append((nx, ny))

    return None  # unreachable

def _reconstruct_path(
    visited: dict[Point, tuple[Point, Direction] | None],
    end: Point,
) -> list[Direction]:
    path: list[Direction] = []
    cur = end
    while visited[cur] is not None:
        prev, d = visited[cur]
        path.append(d)
        cur = prev
    path.reverse()
    return path

def find_all_paths(
    maze: Maze,
    start: Point,
    end: Point,
    *,
    max_paths: int = 0,
) -> list[list[Direction]]:
    results: list[list[Direction]] = []
    visited: set[Point] = {start}
    stack: list[Direction] = []

    def _dfs(pos: Point) -> bool:
        if pos == end:
            results.append(list(stack))
            return max_paths > 0 and len(results) >= max_paths
        for nx, ny, d in get_neighbors(maze, pos[0], pos[1]):
            if (nx, ny) not in visited:
                visited.add((nx, ny))
                stack.append(d)
                if _dfs((nx, ny)):
                    return True
                stack.pop()
                visited.discard((nx, ny))
        return False

    _dfs(start)
    return results

def _flood_fill(maze: Maze, start: Point) -> set[Point]:
    visited: set[Point] = {start}
    queue: deque[Point] = deque([start])

    while queue:
        cx, cy = queue.popleft()
        for nx, ny, _ in get_neighbors(maze, cx, cy):
            if (nx, ny) not in visited:
                visited.add((nx, ny))
                queue.append((nx, ny))

    return visited

def find_closed_cells(maze: Maze) -> set[Point]:
    width, height = maze_dims(maze)
    return {
        (x, y)
        for y in range(height)
        for x in range(width)
        if is_closed_cell(maze, x, y)
    }

def check_connectivity(maze: Maze) -> tuple[bool, set[Point]]:
    width, height = maze_dims(maze)
    closed = find_closed_cells(maze)

    open_cells: set[Point] = {
        (x, y)
        for y in range(height)
        for x in range(width)
        if (x, y) not in closed
    }

    if not open_cells:
        return True, set()

    # start flood-fill from an arbitrary open cell
    seed = next(iter(open_cells))
    reachable = _flood_fill(maze, seed)

    unreachable = open_cells - reachable
    return len(unreachable) == 0, unreachable

def _count_open_edges(maze: Maze) -> int:
    width, height = maze_dims(maze)
    edges = 0
    for y in range(height):
        for x in range(width):
            if is_closed_cell(maze, x, y):
                continue
            # east
            if can_move(maze, x, y, Direction.EAST):
                edges += 1
            # south
            if can_move(maze, x, y, Direction.SOUTH):
                edges += 1
    return edges

def is_perfect_maze(maze: Maze) -> tuple[bool, str]:
    connected, unreachable = check_connectivity(maze)
    if not connected:
        return False, f"Maze is not connected: {len(unreachable)} unreachable cell(s)"

    closed = find_closed_cells(maze)
    width, height = maze_dims(maze)
    vertices = width * height - len(closed)
    edges = _count_open_edges(maze)

    if edges != vertices - 1:
        return False, (
            f"Not a perfect maze: {edges} edges for {vertices} vertices "
            f"(expected {vertices - 1})"
        )

    return True, "Perfect maze confirmed"

def solve(
    maze: Maze,
    start: Point,
    end: Point,
    *,
    perfect: bool = False,
) -> list[Direction] | None:
    return bfs_shortest_path(maze, start, end)

def validate_maze(
    maze: Maze,
    *,
    perfect: bool = False,
) -> tuple[bool, list[str]]:

    messages: list[str] = []

    connected, unreachable = check_connectivity(maze)
    if connected:
        messages.append("Connectivity: OK")
    else:
        messages.append(
            f"Connectivity: FAIL — {len(unreachable)} isolated cell(s): "
            + ", ".join(f"({x},{y})" for x, y in sorted(unreachable))
        )

    if perfect:
        ok, reason = is_perfect_maze(maze)
        messages.append(f"Perfect maze: {'OK' if ok else 'FAIL'} — {reason}")
        if not ok:
            return False, messages

    return connected, messages

def path_to_str(path: Sequence[Direction]) -> str:
    """Convert a list of Direction to the compact N/E/S/W string."""
    return "".join(str(d) for d in path)

def main() -> None:
    from io_utils import load_maze

    filename = "maze_output.txt"
    maze = load_maze(filename)

    width, height = maze_dims(maze)
    print(f"Loaded maze: {width}×{height}")

    # "42" pattern cells
    closed = find_closed_cells(maze)
    print(f"Closed ('42' pattern) cells: {len(closed)}")

    connected, unreachable = check_connectivity(maze)
    if connected:
        print("Connectivity: OK (all open cells are reachable)")
    else:
        print(f"Connectivity: FAIL — {len(unreachable)} isolated cell(s)")
        for p in sorted(unreachable):
            print(f"  unreachable: {p}")

    # perfect check
    ok, reason = is_perfect_maze(maze) 
    print(f"Perfect maze: {reason}")

    # solve
    start = (1, 1)
    end = (19, 14)
    path = bfs_shortest_path(maze, start, end)
    if path is None:
        print(f"No path from {start} to {end}")
    else:
        print(f"Shortest path ({len(path)} steps): {path_to_str(path)}")
