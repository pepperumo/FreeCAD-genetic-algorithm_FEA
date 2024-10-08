.PHONY: init add lint run clean update

# Initialize the project by installing dependencies
init:
	poetry install

# Add a new dependency (usage: make add package=<package-name>)
add:
	poetry add $(package)

# Lint the code using flake8
lint:
	poetry run flake8 src/

# Run the main script
run:
	poetry run python src/freecad_genetic_algorithm/main.py

# Clean up generated files
clean:
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete

# Update all dependencies
update:
	poetry update
