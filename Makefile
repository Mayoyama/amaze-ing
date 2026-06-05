.PHONY: install, run, debug, clean, lint, lint-strict

install:
	python3 -m venv maz_venv
	source maze_venv/bin/activate
	pip install ./MazeGenerator-1.0.0-py3-none-any.whl
	pip install mlx-2.2-py3-ubuntu-any.whl

run:
	python3 a_maze_ing.py

debug:
	python3 -m pdb a_maze_ing.py

clean:
	rm -rf __pycache__ .mypy_cache
	
lint:
	flake8 . 
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 . 
	mypy . --strict

