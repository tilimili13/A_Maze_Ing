maze_types.py<br>
Defines the fundamental maze data model: <br>
* Direction enum <br>
* Walls (N, E, S, W as bit flags) <br>
* Maze type alias <br>
* Point type alias <br>

io_utils.py<br>
Handles reading and writing maze files: <br>
* load_maze() → Reads maze grid from text file <br>
* dump_maze() → Writes: grid, entry point, exit point, path.

ui_mlx.pu<br>
Handles graphical display using MiniLibX (Python wrapper): <br>
* Loads maze from file <br>
* Draws walls pixel-by-pixel<br>
* Opens MLX window<br>
* Handles ESC / window close<br>
* Runs MLX loop<br>
