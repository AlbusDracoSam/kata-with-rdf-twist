.EXPORT_ALL_VARIABLES:

# Virtual Environment variables
SHELL = /bin/bash
PYTHON_VERSION = 3.13
PY = python3
VENV = .venv
BIN=$(VENV)/bin

export BASH_ENV=$(VENV)/bin/activate

.PHONY: help test test-python lint lint-fix format format-check coverage coverage-term coverage-html coverage-xml coverage-check clean type-check check install pre-commit-install pre-commit pre-commit-update pre-commit-clean

help: ## Show this help message
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

$(VENV): pyproject.toml
	@uv self update || true
	@uv venv --python ${PYTHON_VERSION} --python-fetch automatic --python-preference only-managed --link-mode=copy -q
	@uv sync --all-groups --link-mode=copy

install: $(VENV) ## Install/update dependencies
	@echo "Dependencies installed in $(VENV)"

test: test-python ## run all tests

test-python: $(VENV) ## run python tests
	@$(BIN)/pytest python/tests/ -v

lint: $(VENV) ## Linting - only report issues, don't fix
	@echo "Running ruff..."
	@$(BIN)/ruff check python/ || true
	@echo "\nRunning flake8..."
	@$(BIN)/flake8 python/ || true
	@echo "\nRunning pylint..."
	@$(BIN)/pylint python/*.py python/tests/*.py || true

lint-fix: $(VENV) ## Auto-fix linting issues where possible
	@echo "Fixing with ruff..."
	@$(BIN)/ruff check --fix python/
	@echo "Fixing with autopep8..."
	@$(BIN)/autopep8 --in-place --recursive --aggressive --aggressive python/

format: $(VENV) ## Format code with black and isort
	@echo "Formatting with black..."
	@$(BIN)/black python/
	@echo "Sorting imports with isort..."
	@$(BIN)/isort python/

format-check: $(VENV) ## Check if code is formatted correctly (CI-friendly)
	@echo "Checking black formatting..."
	@$(BIN)/black --check python/ || (echo "Code is not formatted with black. Run 'make format' to fix." && exit 1)
	@echo "Checking isort formatting..."
	@$(BIN)/isort --check-only python/ || (echo "Imports are not sorted. Run 'make format' to fix." && exit 1)
	@echo "All formatting checks passed!"

coverage: coverage-term coverage-html coverage-xml ## Run tests with all coverage reports

coverage-term: $(VENV) ## Run tests with terminal coverage report
	@$(BIN)/pytest python/tests/ --cov=python --cov-report=term-missing --cov-report=term

coverage-html: $(VENV) ## Generate HTML coverage report
	@$(BIN)/pytest python/tests/ --cov=python --cov-report=html
	@echo "\n📊 HTML coverage report generated: htmlcov/index.html"
	@echo "   Open htmlcov/index.html in your browser to view the report"

coverage-xml: $(VENV) ## Generate XML coverage report (for CI integration)
	@$(BIN)/pytest python/tests/ --cov=python --cov-report=xml
	@echo "\n📄 XML coverage report generated: coverage.xml"

coverage-check: $(VENV) ## Check coverage thresholds (fails if below minimum)
	@$(BIN)/pytest python/tests/ --cov=python --cov-report=term-missing --cov-report=term --cov-fail-under=80
	@echo "\n✅ Coverage check passed!"

type-check: $(VENV) ## Run type checking with mypy
	@$(BIN)/mypy python/ --ignore-missing-imports

clean: ## Remove generated files and caches
	@echo "Cleaning up..."
	@rm -rf $(VENV)
	@rm -rf .pytest_cache
	@rm -rf .mypy_cache
	@rm -rf .ruff_cache
	@rm -rf htmlcov
	@rm -rf .coverage
	@rm -rf coverage.xml
	@rm -rf dist
	@rm -rf build
	@rm -rf *.egg-info
	@find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@echo "Clean complete!"

pre-commit-install: $(VENV) ## Install pre-commit hooks
	@$(BIN)/pre-commit install
	@echo "\n✅ Pre-commit hooks installed!"
	@echo "   Hooks will run automatically on git commit"
	@echo "   Run 'make pre-commit' to test hooks manually"

pre-commit: $(VENV) ## Run pre-commit hooks on all files
	@$(BIN)/pre-commit run --all-files

pre-commit-update: $(VENV) ## Update pre-commit hooks to latest versions
	@$(BIN)/pre-commit autoupdate
	@echo "\n✅ Pre-commit hooks updated!"

pre-commit-clean: $(VENV) ## Remove pre-commit hooks
	@$(BIN)/pre-commit uninstall || true
	@echo "Pre-commit hooks removed"

check: format-check lint type-check test ## Run all checks (format, lint, type-check, tests)
	@echo "\n✅ All checks passed!"
