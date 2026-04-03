VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
MAIN_SCRIPT := main.py
FILE :=

.PHONY: help venv install run clean lint lint-strict

help:
	@echo "Available targets:"
	@echo "  make venv       			- Create virtualenv using python3.13"
	@echo "  make install    			- Install dependencies from requirements.txt"
	@echo "  make run        			- Run the project (main.py)"
	@echo "  make clean      			- Remove $(VENV)"
	@echo "  make lint         			- Run flake8 and mypy with standard checks"
	@echo "  make lint-strict  			- Run flake8 and mypy with strict mode"

venv:
	@if [ -d "$(VENV)" ]; then \
		echo "Virtualenv exists at $(VENV)"; \
	else \
		python3.13 -m venv $(VENV) || python3 -m venv $(VENV); \
		$(PIP) install --upgrade pip setuptools wheel || true; \
	fi

debug:
	$(PYTHON) -m pdb $(MAIN_SCRIPT) $(FILE)

install: venv
	@if [ -f requirements.txt ]; then \
		$(PIP) install -r requirements.txt; \
	else \
		echo "No requirements.txt found; skipping."; \
	fi
	@echo "\nRun: source $(VENV)/bin/activate"

lint:
	flake8 . --exclude=.git,.venv,venv,env,test_vm,build,dist,.mypy_cache,.pytest_cache,__pycache__,dependencies,src,*.egg-info
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports \
		--disallow-untyped-defs --check-untyped-defs --exclude='(build|dist|venv|env|dependencies|src)'

lint-strict:
	flake8 . --exclude=.git,.venv,venv,env,test_vm,build,dist,.mypy_cache,.pytest_cache,__pycache__,dependencies,src,*.egg-info
	mypy . --strict --exclude='(build|dist|venv|env|dependencies|src)'

run:
	$(PYTHON) $(MAIN_SCRIPT) $(FILE)

clean:
	rm -rf $(VENV)
