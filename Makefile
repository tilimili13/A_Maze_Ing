VENV = .venv
VENV_PYTHON = $(VENV)/bin/python
VENV_PIP = $(VENV)/bin/pip

all: install run

install:
	python3 -m venv .venv
	$(VENV_PIP) install flake8 mypy
	$(VENV_PIP) install libs/mlx-2.2-py3-none-any.whl

run:
	$(VENV_PYTHON) a_maze_ing.py config.txt

debug:
	$(VENV_PYTHON) -m pdb a_maze_ing.py config.txt

clean:
	find ./ -name "__pycache__" -type d -exec rm -rf {} +
	rm -rf .mypy_cache

lint: clean
	$(VENV_PYTHON) -m flake8 . --exclude $(VENV)
	$(VENV_PYTHON) -m mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

fclean: clean
	rm -rf $(VENV)