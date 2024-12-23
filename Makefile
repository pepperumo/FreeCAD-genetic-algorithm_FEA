.PHONY: init add lint run clean update install-dependencies docs

# Initialize the project by installing dependencies
init:
	poetry install


# Add a new dependency (usage: make add package=<package-name>)
add:
	poetry add $(package)

# Lint the code using flake8
lint:
	poetry run flake8 genetic_FEA/

# Run the main script
run:
	poetry run python genetic_FEA/main.py

# Clean up generated files
clean:
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete

# Update all dependencies
update:
	poetry update

# Build Sphinx documentation
docs:
	sphinx-build -b html docs/ docs/_build/html

format:
	poetry run black genetic_FEA/

# Run tests using pytest
test:
	poetry run pytest tests/

