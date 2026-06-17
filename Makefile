VENV = maze_venv
VENV_BIN = $(VENV)/bin
PYTHON = $(VENV_BIN)/python3
PIP = $(VENV_BIN)/pip
CONFIG_TOML = pyproject.toml
# Local wheel — not on PyPI, installed explicitly below
MLX_WHL = Rendering/mlx-2.2-py3-none-any.whl
VENV_ANCHOR = $(VENV)/.anchor

.PHONY: install run debug clean lint lint-strict build uninstall

install: $(VENV_ANCHOR)

$(VENV_ANCHOR): $(CONFIG_TOML)
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install .[dev]
	@if [ ! -f "$(MLX_WHL)" ]; then echo "Missing $(MLX_WHL)"; exit 1; fi
	$(PIP) install $(MLX_WHL)
	@touch $(VENV_ANCHOR)

run: $(VENV_ANCHOR)
	$(PYTHON) a_maze_ing.py config.txt

debug: $(VENV_ANCHOR)
	$(PYTHON) -m pdb a_maze_ing.py

clean:
	find . -not -path './$(VENV)/*' -type d \( -name "__pycache__" -o -name "*.egg-info" \
	    -o -name ".mypy_cache" -o -name "build" -o -name "dist" \) -exec rm -rf {} +
	find . -type f \( -name "*.pyc" -o -name "*.pyo" -o -name "*~" \) -delete

lint: $(VENV_ANCHOR)
	$(VENV_BIN)/flake8 . --exclude=maze_venv/,misc_files/ || true
	$(VENV_BIN)/mypy --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs --exclude 'maze_venv' .

lint-strict: $(VENV_ANCHOR)
	$(VENV_BIN)/flake8 . --exclude=maze_venv/,misc_files/ || true
	$(VENV_BIN)/mypy . --strict --exclude 'maze_venv'

build: $(VENV_ANCHOR)
	$(PYTHON) -m build mazegen

uninstall: clean
	@if python3 -c "import sys; print(sys.prefix != sys.base_prefix)" | grep -q True; then \
		echo "ERROR: maze_venv is currently active..."; \
	else \
		rm -rf maze_venv; echo "VENV: maze_venv successfully removed"; \
	fi
