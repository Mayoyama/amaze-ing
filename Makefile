.PHONY: install, run, debug, clean, lint, lint-strict

install:
	python3 -m venv maze_venv
	./maze_venv/bin/pip install --upgrade pip
	./maze_venv/bin/pip install mypy
	./maze_venv/bin/pip install mlx-2.2-py3-none-any.whl
	#  pip install ./MazeGenerator-1.0.0-py3-none-any.whl
	#  pip install mlx-2.2-py3-none-any.whl

run:
	python3 a_maze_ing.py
	# ./maze_venv/bin/python3 main.py

debug:
	python3 -m pdb a_maze_ing.py

clean:
	rm -rf __pycache__ .mypy_cache
	
lint:
	flake8 . 
	./maze_venv/bin/mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 . 
	./maze_venv/bin/mypy . --strict

