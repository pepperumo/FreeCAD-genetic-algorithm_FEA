import sys
import os
from FreecadParametricFEA.run_all import RunAllAnalysis
from FreecadParametricFEA.genetic_algorithm import GeneticAlgorithm

FREECAD_PATH = "C:/Program Files/FreeCAD 0.21/bin"
script_dir = os.path.dirname(os.path.realpath(__file__))  # Get the directory of the current script
FreeCad_Model = os.path.join(script_dir, "linkage.fcstd")  # Relative path to the notch model

import FreeCAD

def main():
    method = input("Choose the method (1 for RunAll, 2 for GeneticAlgorithm): ")

    if method == "1":
        analysis = RunAllAnalysis(FREECAD_PATH, FreeCad_Model)
        analysis.run()
    elif method == "2":
        analysis = GeneticAlgorithm(FREECAD_PATH, FreeCad_Model, population_size=2, generations=2)
        analysis.run()
    else:
        print("Invalid method chosen.")

if __name__ == "__main__":
    main()
