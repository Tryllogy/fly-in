SHELL := /bin/zsh
VENV := .venv
PY := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

.PHONY: help venv install run activate clean rebuild

help:
	@echo "Available targets:"
	@echo "  make venv       Create virtualenv using python3.13"
	@echo "  make install    Install dependencies from requirements.txt"
	@echo "  make run        Run the project (main.py)"
	@echo "  make activate   Print activation command for the venv"
	@echo "  make clean      Remove $(VENV)"
	@echo "  make rebuild    Recreate venv and reinstall deps"

venv:
	@if [ -d "$(VENV)" ]; then \
		echo "Virtualenv exists at $(VENV)"; \
	else \
		python3.13 -m venv $(VENV) || python3 -m venv $(VENV); \
		$(PIP) install --upgrade pip setuptools wheel || true; \
	fi

install: venv
	@if [ -f requirements.txt ]; then \
		$(PIP) install -r requirements.txt; \
	else \
		echo "No requirements.txt found; skipping."; \
	fi

run: venv
	$(PY) main.py

activate:
	@echo "Run: source $(VENV)/bin/activate"

clean:
	rm -rf $(VENV)

rebuild: clean venv install
