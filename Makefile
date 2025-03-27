.PHONY: clean install dev test lint format build docs docker docker-run

# Variables
PYTHON := python3
PIP := $(PYTHON) -m pip
BUILD_DIR := build
DIST_DIR := dist
TEST_ARGS := -v
DOCKER_IMAGE := llamavault
DOCKER_TAG := latest
DOCKER_PORT := 5000

# Default target
all: clean install test

# Clean build artifacts
clean:
	rm -rf $(BUILD_DIR) $(DIST_DIR) .coverage .pytest_cache *.egg-info

# Install package
install:
	$(PIP) install -e .

# Install development dependencies
dev:
	$(PIP) install -e ".[dev]"

# Install web interface dependencies
web:
	$(PIP) install -e ".[web]"

# Run tests
test:
	pytest $(TEST_ARGS)

# Check code quality with flake8
lint:
	flake8 src tests

# Format code with black
format:
	black src tests examples

# Check type annotations with mypy
typecheck:
	mypy src

# Run all quality checks
check: lint typecheck test

# Build package
build:
	$(PYTHON) -m build

# Build documentation
docs:
	cd docs && make html

# Build Docker image
docker:
	docker build -t $(DOCKER_IMAGE):$(DOCKER_TAG) .

# Run Docker container
docker-run:
	docker run -p $(DOCKER_PORT):5000 -v llamavault-data:/data $(DOCKER_IMAGE):$(DOCKER_TAG)

# Run package directly
run:
	$(PYTHON) -m llamavault

# Run web interface
web-serve:
	FLASK_APP=llamavault.web.app FLASK_DEBUG=1 flask run

help:
	@echo "Available targets:"
	@echo "  clean      - Remove build artifacts"
	@echo "  install    - Install package"
	@echo "  dev        - Install development dependencies"
	@echo "  web        - Install web interface dependencies"
	@echo "  test       - Run tests"
	@echo "  lint       - Check code quality with flake8"
	@echo "  format     - Format code with black"
	@echo "  typecheck  - Check type annotations with mypy"
	@echo "  check      - Run all quality checks"
	@echo "  build      - Build package"
	@echo "  docs       - Build documentation"
	@echo "  docker     - Build Docker image"
	@echo "  docker-run - Run Docker container"
	@echo "  run        - Run package directly"
	@echo "  web-serve  - Run web interface in debug mode" 