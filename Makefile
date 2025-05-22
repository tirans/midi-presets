.PHONY: help install install-dev test test-cov lint format clean build

help:		## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install:	## Install the package
	pip install -e .

install-dev:	## Install development dependencies
	pip install -e .[dev]
	pre-commit install

test:		## Run tests
	pytest

test-cov:	## Run tests with coverage
	pytest --cov=src/midi_presets --cov-report=term-missing --cov-report=html

lint:		## Run linting
	flake8 src tests
	mypy src

format:		## Format code
	black src tests scripts

clean:		## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build:		## Build the package
	python -m build

validate:	## Validate all device files
	python scripts/validate_presets.py devices/**/*.json

checksums:	## Generate repository checksums
	python scripts/generate_checksums.py --devices-folder devices
