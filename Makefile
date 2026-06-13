VENV = maze_venv
VENV_BIN = $(VENV)/bin
PYTHON = $(VENV_BIN)/python3
PIP = $(VENV_BIN)/pip
CONFIG_TOML = pyproject.toml
MLX_WHL = mlx-2.2-py3-none-any.whl
VENV_ANCHOR = $(VENV)/.anchor

.PHONY: install run debug clean lint lint-strict build uninstall

install: $(VENV_ANCHOR)

$(VENV_ANCHOR): $(CONFIG_TOML)
	@echo "Creating virtual environment..."
	python3 -m venv $(VENV)
	@echo "Installing dependencies directly from TOML..."
	$(PIP) install --upgrade pip
	$(PIP) install .[dev]
	@if [ ! -f "$(MLX_WHL)" ]; then \
	echo "Missing $(MLX_WHL)"; \
	exit 1; \
	fi
	@echo "Installing MLX..."
	$(PIP) install $(MLX_WHL)
	@touch $(VENV_ANCHOR)

run:
	$(PYTHON) a_maze_ing.py config.txt

debug:
	$(PYTHON) -m pdb a_maze_ing.py

clean:
	find . -type d \( -name "__pycache__" -o -name ".mypy_cache" \) -exec rm -rf {} +
	find . -type f \( -name "*.pyc" -o -name "*.pyo" -o -name "*~" \) -delete
	rm -rf build dist *.egg-info

lint:
	flake8 . --exclude=maze_venv/,misc_files/ || true
	$(PYTHON) -m mypy \
		--warn-return-any \
		--warn-unused-ignores \
		--ignore-missing-imports \
		--disallow-untyped-defs \
		--check-untyped-defs \
		--exclude 'maze_venv' .

lint-strict:
	flake8 . --exclude=maze_venv/,misc_files/ || true
	$(PYTHON) -m mypy . --strict --exclude 'maze_venv'

build:
	$(PYTHON) -m build

uninstall: clean
	@if python3 -c "import sys; print(sys.prefix != sys.base_prefix)" | grep -q True; then \
		echo "ERROR: maze_venv is currently active. Unable to remove maze_venv. Run 'deactivate' first."; \
		else \
			rm -rf maze_venv; \
			echo "VENV: maze_venv successfully removed"; \
	fi