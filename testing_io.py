# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    testing_io.py                                      :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: albezbor <albezbor@student.42tokyo.jp>     +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/02/20 21:08:32 by albezbor          #+#    #+#              #
#    Updated: 2026/02/20 21:08:32 by albezbor         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

from utils.io_utils import dump_maze, load_maze
from utils.maze_types import Direction

def demo_dump() -> None:
    start, finish = (1, 1), (19, 14)
    maze = load_maze("maze.txt")

    path_raw = "SWSESWSESWSSSEESEEENEESESEESSSEEESSSEEENNENEE"
    path = list(map(Direction.from_str, path_raw))

    dump_maze(maze, start, finish, path, "out.txt")

if __name__ == "__main__":
    demo_dump()
