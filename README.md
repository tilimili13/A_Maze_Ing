_This project has been created as part of the 42 curriculum by tnikitin, albezbor_

## Description

This project `a_maze_ing` generates random mazes, renders them in a terminal or using MiniLibX library, and exports them to a hex-encoded file along with entry/exit coordinates and a shortest path. 

The program generates maze and finds enter and exit using DFS algorithm. BFS algorithm is used for finding short path. Also, the program adds “42” engraving.

### Algorithms
1. DFS algorithm generates maze.
- Low memory usage. It stores the current path from the starting cell to the current cell (linear space complexity).
- Easy to implement.
- It always ensures that there is exit.

2. BFS searches shortest path.
- Finding shortest path is guaranteed.
- Easy to understand and implement.

## Instructions

### Install
Use Makefile to prepare run environment and run the program.<br/>
`make install` creates virtual environment and install `flake8`, `mypy` and `mlx` library.<br/>
Type `make run` to run the program.<br/>
Use `make lint` to check the code using `flake8` and `mypy`.<br/>
`make clean` removes all temporary python files, `make fclean` removes `.venv` directory as well.<br/>
To start debugging type `make debug`.<br/>
You can use `make` to install virtual environment and run the programm (same as `make install` + `make run`).

### Run the program

Make file runs program automatically. It's possible to change configurations in config.txt:

- `WIDTH`, `HEIGHT`: maze dimensions.
- `ENTRY`, `EXIT`: coordinates `x,y` inside bounds and distinct.
- `OUTPUT_FILE`: target maze file path.
- `PERFECT`: `True|False` to allow/forbid loops.
Optional keys:
- `SEED`: integer for reproducible generation.
- `DISPLAY`: `ascii|mlx` - displaying maze in terminal or using MiniLibX library.
- `COLOR_WALL`, `COLOR_PATH`, `COLOR_ENTRY`, `COLOR_EXIT`, `COLOR_PATTERN42`, `COLOR_BACKGROUND`: set color for maze objects.

### UI controls
In MLX window (if installed):
- `1`: new maze; `2`: hide and show path; `3`: change colors. Click x or esq for exit.
- Also it's possible to control maze by clicking on buttons in window.

In terminal:
After maze is generated terminal asks about next action:
>1. Re-generate a new maze\
>2. Show/Hide path from entry to exit\
>3. Change maze colors\
>4. Quit\
>Choice? (1-4)

## Resources

- [BFS tutorial for Python programming](https://csanim.com/tutorials/breadth-first-search-python-visualization-and-code)
- [BFS explanation](https://en.wikipedia.org/wiki/Breadth-first_search)


## Team management
tnikitin focused on the library connection, UI, MLX output, and utilities, while albezbor developed the terminal output, maze generator, and the program that finds and displays the path.

Plan:
First, tnikitin worked on utilities and MLX output, creating test programs with demo versions of mazes so we could verify that the real mazes were generated correctly.

After confirming that the output worked properly, albezbor implemented the maze generator and solver, as well as the terminal output.

During the later stages of development, tnikitin added additional features in MLX output (such as color change, hide/show path, regeneration). Also she buttons to the MLX window and reorganized the project files as an improvement. albezbor worked on fixing bugs and improving code.

To share files, we used a Git repository.

Tools: Python, MiniLibX, flake8, mypy, Git.


## TODO
O<input type="checkbox" checked> console mode working<br/>
O<input type="checkbox" checked> mlx mode working<br/>
O<input type="checkbox" checked> makefile<br/>
O<input type="checkbox" checked> utils<br/>
<input type="checkbox"> README.md<br/>   -  Dobav pro "which part of your code is reusable"
O<input type="checkbox"> ??? refactoring (do we sill need?) - 50% done<br/>
O<input type="checkbox" checked> interactive in console mode<br/>
?<input type="checkbox"> make all importable (put in one class)<br/>
