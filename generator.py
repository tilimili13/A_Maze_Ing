from utils import Maze, Direction, Point, CLOSED_CELL
import random

# "42" pattern
_DIGIT_4: list[list[int]] = [
    [1, 0, 0],
    [1, 0, 0],
    [1, 1, 1],
    [0, 0, 1],
    [0, 0, 1],
]
_DIGIT_2: list[list[int]] = [
    [1, 1, 1],
    [0, 0, 1],
    [1, 1, 1],
    [1, 0, 0],
    [1, 1, 1],
]

_PATTERN_HEIGHT = 5
_DIGIT_WIDTH = 3
_GAP = 1
_PATTERN_WIDTH = _DIGIT_WIDTH * 2 + _GAP  # 7


def _pattern_42_cells(ox: int, oy: int) -> set[Point]:
    cells: set[Point] = set()
    for dy in range(_PATTERN_HEIGHT):
        for dx in range(_DIGIT_WIDTH):
            if _DIGIT_4[dy][dx]:
                cells.add((ox + dx, oy + dy))
            if _DIGIT_2[dy][dx]:
                cells.add((ox + _DIGIT_WIDTH + _GAP + dx, oy + dy))
    return cells


def _find_42_position(
    width: int,
    height: int,
    entry: Point,
    exit_: Point,
    rng: random.Random,
) -> tuple[int, int]:
    max_x = width - _PATTERN_WIDTH - 1
    max_y = height - _PATTERN_HEIGHT - 1
    min_x = 1
    min_y = 1

    if max_x < min_x or max_y < min_y:
        print(
            f"Maze too small ({width}x{height}) to fit the '42' pattern "
            f"(needs at least {_PATTERN_WIDTH + 2}x{_PATTERN_HEIGHT + 2})"
        )
        return -1, -1

    for _ in range(200):
        ox = rng.randint(min_x, max_x)
        oy = rng.randint(min_y, max_y)
        cells = _pattern_42_cells(ox, oy)
        if entry not in cells and exit_ not in cells:
            return ox, oy

    # fallback: try all positions
    for oy in range(min_y, max_y + 1):
        for ox in range(min_x, max_x + 1):
            cells = _pattern_42_cells(ox, oy)
            if entry not in cells and exit_ not in cells:
                return ox, oy
    print("Cannot place '42' pattern without overlapping entry/exit")
    return -1, -1


def _remove_wall(maze: Maze, x: int, y: int, d: Direction) -> None:
    maze[y][x] &= ~d
    dx, dy = d.delta
    nx, ny = x + dx, y + dy
    w, h = len(maze[0]), len(maze)
    if 0 <= nx < w and 0 <= ny < h:
        maze[ny][nx] &= ~d.opposite


def _would_create_3x3_open(maze: Maze, x: int, y: int, d: Direction) -> bool:
    width, height = len(maze[0]), len(maze)
    dx, dy = d.delta
    nx, ny = x + dx, y + dy
    for ay in range(
        max(0, max(y, ny) - 2), min(height - 2, min(y, ny)) + 1
    ):
        for ax in range(
            max(0, max(x, nx) - 2), min(width - 2, min(x, nx)) + 1
        ):
            if _is_open_3x3(maze, ax, ay, skip_edge=(x, y, d)):
                return True
    return False


def _is_open_3x3(
    maze: Maze,
    ax: int,
    ay: int,
    skip_edge: tuple[int, int, Direction] | None = None,
) -> bool:
    for dy in range(3):
        for dx in range(3):
            cx, cy = ax + dx, ay + dy
            if dx < 2:
                if not _pair_open(maze, cx, cy, Direction.EAST, skip_edge):
                    return False
            if dy < 2:
                if not _pair_open(maze, cx, cy, Direction.SOUTH, skip_edge):
                    return False
    return True


def _pair_open(
    maze: Maze,
    x: int,
    y: int,
    d: Direction,
    skip_edge: tuple[int, int, Direction] | None,
) -> bool:
    if skip_edge is not None:
        sx, sy, sd = skip_edge
        ddx, ddy = d.delta
        if (x == sx and y == sy and d == sd):
            return True
        if (x + ddx == sx and y + ddy == sy and d.opposite == sd):
            return True
    return not (maze[y][x] & d)


def generate_maze(
    width: int,
    height: int,
    entry: Point,
    exit_: Point,
    perfect: bool = True,
    seed: int | None = None,
) -> Maze:
    _validate_points(width, height, entry, exit_)
    rng = random.Random(seed)
    maze: Maze = [[int(CLOSED_CELL)] * width for _ in range(height)]
    ox, oy = _find_42_position(width, height, entry, exit_, rng)
    if ox > -1 and oy > -1:
        pattern_cells = _pattern_42_cells(ox, oy)
    else:
        pattern_cells = []
    _backtracking(maze, width, height, entry, pattern_cells, rng)
    if not perfect:
        _add_extra_passages(maze, width, height, pattern_cells, rng)
    _enforce_borders(maze, width, height)
    for px, py in pattern_cells:
        maze[py][px] = int(CLOSED_CELL)
        for d in Direction:
            ddx, ddy = d.delta
            nnx, nny = px + ddx, py + ddy
            if 0 <= nnx < width and 0 <= nny < height:
                maze[nny][nnx] |= d.opposite
    return maze


def get_pattern_cells(maze: Maze) -> set[Point]:
    width, height = len(maze[0]), len(maze)
    return {
        (x, y)
        for y in range(height)
        for x in range(width)
        if maze[y][x] == int(CLOSED_CELL)
    }


def _validate_points(
    width: int, height: int, entry: Point, exit_: Point
) -> None:
    ex, ey = entry
    xx, xy = exit_
    if not (0 <= ex < width and 0 <= ey < height):
        raise ValueError(f"Entry {entry} is out of bounds ({width}x{height})")
    if not (0 <= xx < width and 0 <= xy < height):
        raise ValueError(f"Exit {exit_} is out of bounds ({width}x{height})")
    if entry == exit_:
        raise ValueError("Entry and exit must be different")


def _backtracking(
    maze: Maze,
    width: int,
    height: int,
    start: Point,
    blocked: set[Point],
    rng: random.Random,
) -> None:
    visited: set[Point] = set(blocked)
    visited.add(start)
    stack: list[Point] = [start]
    directions = list(Direction)
    while stack:
        x, y = stack[-1]
        rng.shuffle(directions)
        carved = False
        for d in directions:
            ddx, ddy = d.delta
            nx, ny = x + ddx, y + ddy
            if nx < 0 or nx >= width or ny < 0 or \
                    ny >= height or (nx, ny) in visited:
                continue
            _remove_wall(maze, x, y, d)
            visited.add((nx, ny))
            stack.append((nx, ny))
            carved = True
            break
        if not carved:
            stack.pop()


def _add_extra_passages(
    maze: Maze,
    width: int,
    height: int,
    blocked: set[Point],
    rng: random.Random,
    ratio: float = 0.08,
) -> None:
    candidates: list[tuple[int, int, Direction]] = []
    for y in range(height):
        for x in range(width):
            if (x, y) in blocked:
                continue
            for d in (Direction.EAST, Direction.SOUTH):
                ddx, ddy = d.delta
                nx, ny = x + ddx, y + ddy
                if nx < 0 or nx >= width or ny < 0 or ny >= height:
                    continue
                if (nx, ny) in blocked:
                    continue
                if maze[y][x] & d:          # wall is currently closed
                    candidates.append((x, y, d))
    rng.shuffle(candidates)
    target = max(1, int(len(candidates) * ratio))
    removed = 0
    for cx, cy, cd in candidates:
        if removed >= target:
            break
        if not _would_create_3x3_open(maze, cx, cy, cd):
            _remove_wall(maze, cx, cy, cd)
            removed += 1


def _enforce_borders(maze: Maze, width: int, height: int) -> None:
    for x in range(width):
        maze[0][x] |= Direction.NORTH
        maze[height - 1][x] |= Direction.SOUTH
    for y in range(height):
        maze[y][0] |= Direction.WEST
        maze[y][width - 1] |= Direction.EAST
