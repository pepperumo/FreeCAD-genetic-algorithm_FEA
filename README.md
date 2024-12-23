# Differential Self-Driving Robot (BumperBot)
[![LinkedIn][linkedin-shield]][linkedin-url]
[![Udemy][udemy-shield]][udemy-url]
# FreeCAD Genetic Algorithm FEA

This repository contains scripts and utilities to run parametric and genetic algorithm-based finite element analysis (FEA) using FreeCAD. The project is designed to automate the exploration of optimized designs by sweeping parameter values or employing a genetic algorithm to minimize von Mises stress.

## Features

- **Parametric FEA**: Automate parameter sweeps to run FEA on multiple design configurations and analyze the results.
- **Genetic Algorithm**: Leverage a genetic algorithm to optimize designs based on von Mises stress results.
- **FreeCAD Integration**: Scripts dynamically interact with FreeCAD, utilizing its Python API for CAD model manipulation and FEA.
- **CSV Output**: Results are saved in CSV format, including von Mises stress and the corresponding parameters for easy post-analysis.
- **Logging**: Comprehensive logging to help monitor progress and debug issues.

## Requirements

- Python 3.8+
- FreeCAD 0.21+
  
The project uses Poetry and Pipenv for dependency management. You can choose either to manage the dependencies.

## Setup with Poetry

1. Install [Poetry](https://python-poetry.org/docs/):
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. Clone this repository:
   ```bash
   git clone https://github.com/pepperumo/FreeCAD-genetic-algorithm_FEA.git
   cd FreeCAD-genetic-algorithm_FEA
   ```

3. Install dependencies using Poetry:
   ```bash
   poetry install
   ```

4. Activate the environment:
   ```bash
   poetry shell
   ```

## Setup with Pipenv

1. Install [Pipenv](https://pipenv.pypa.io/en/latest/):
   ```bash
   pip install pipenv
   ```

2. Install dependencies using Pipenv:
   ```bash
   pipenv install
   ```

3. Activate the environment:
   ```bash
   pipenv shell
   ```

## Running the Project

1. Adjust the `FREECAD_PATH` in the scripts (`run_all.py`, `genetic_algorithm.py`, etc.) to point to your FreeCAD installation path.
   
2. To run a parametric analysis or genetic algorithm, execute:
   ```bash
   python main.py
   ```
   Choose between `RunAll` or `GeneticAlgorithm` methods when prompted.

### Parametric Analysis

The parametric analysis will sweep through all specified parameter ranges and save the results to a CSV file.

### Genetic Algorithm

The genetic algorithm will iterate over generations to minimize von Mises stress, saving the best model configuration and results at the end.

## Project Structure

- `main.py`: Entry point to choose between parametric analysis and genetic algorithm.
- `run_all.py`: Runs the parametric FEA analysis over a range of parameters.
- `genetic_algorithm.py`: Implements the genetic algorithm for design optimization.
- `parametric.py`: Handles high-level parametric FEA functions.
- `freecadmodel.py`: Manages interaction with FreeCAD, including model parameter changes and FEA execution.
- `loghandler.py`: Configures logging.
- `Makefile`: Makefile for automating common tasks.
- `pyproject.toml`: Defines the project's dependencies and setup for Poetry.
- `Pipfile` and `Pipfile.lock`: Define dependencies for Pipenv.


<!-- MARKDOWN LINKS & IMAGES -->
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=flat-square&logo=linkedin&colorB=555
[linkedin-url]: https://www.linkedin.com/in/pepperumo/
[udemy-shield]: https://img.shields.io/badge/-Udemy-black.svg?style=flat-square&logo=udemy&colorB=555
[udemy-url]: https://www.udemy.com/course/self-driving-and-ros-2-learn-by-doing-odometry-control/?referralCode=50BCC4E84DB2DB09BFB3
All logs are stored in `freecadparametricfea.log` for debugging and tracking execution. Ensure you check this log if any issues arise during the execution of FEA or genetic algorithm runs.

## License

This project is licensed under the MIT License. See the `LICENSE.md` file for more details.
