from io_utils import dump_maze, load_maze
from maze_types import Direction
from ui_mlx import display_maze

def demo_dump() -> None:
    start, finish = (1, 1), (19, 14)
    maze = load_maze("maze.txt")

    path_raw = "SWSESWSESWSSSEESEEENEESESEESSSEEESSSEEENNENEE"
    path = list(map(Direction.from_str, path_raw))

    dump_maze(maze, start, finish, path, "out.txt")

if __name__ == "__main__":
    demo_dump()