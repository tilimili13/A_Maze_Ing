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


## TODO
<input type="checkbox" checked> console mode working<br/>
<input type="checkbox" checked> mlx mode working<br/>
<input type="checkbox" checked> makefile<br/>
<input type="checkbox" checked> utils<br/>
<input type="checkbox"> README.md<br/>
<input type="checkbox"> ??? refactoring (do we sill need?) - 50% done<br/>
<input type="checkbox" checked> interactive in console mode<br/>
<input type="checkbox"> make all importable (put in one class)<br/>