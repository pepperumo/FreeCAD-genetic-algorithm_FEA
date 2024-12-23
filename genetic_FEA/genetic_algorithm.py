import sys
import os
import time  # Add this for timing
from os import path
import random
from tqdm import tqdm  # Add tqdm for the progress bar

# Add FreeCAD Python libraries to sys.path dynamically
FREECAD_PATH = "C:/Program Files/FreeCAD 0.21/bin"  # Adjust this if your FreeCAD installation is elsewhere
if FREECAD_PATH not in sys.path:
    sys.path.append(FREECAD_PATH)

import pandas as pd
import FreeCAD
from deap import base, creator, tools, algorithms
from FreecadParametricFEA.parametric_analysis import ParametricAnalysis
from FreecadParametricFEA.variable import Variable
from FreecadParametricFEA.output import Output

class GeneticAlgorithm:
    def __init__(self, freecad_path, model_file, population_size=2, generations=1):
        self.freecad_path = freecad_path
        self.model_file = model_file
        self.population_size = population_size
        self.generations = generations
        

    def get_spreadsheet_data(self, spreadsheet, row):
        object_name = spreadsheet.get(f'A{row}')
        constraint_name = spreadsheet.get(f'B{row}')
        min_value = float(spreadsheet.get(f'C{row}'))
        max_value = float(spreadsheet.get(f'D{row}'))
        step = int(spreadsheet.get(f'E{row}'))
        unit = spreadsheet.get(f'F{row}')
        constraint_name_with_unit = f"{constraint_name} [{unit}]"
        return object_name, constraint_name, constraint_name_with_unit, min_value, max_value

    def save_best_model(self, doc, best_values, constraint_names_with_units):
        """Save the best model and dynamically name it based on constraints."""
        # Check if lengths match
        if len(best_values) != len(constraint_names_with_units):
            print(f"Error: Mismatch between the number of best values ({len(best_values)}) and constraint names with units ({len(constraint_names_with_units)}).")
            return  # Exit the function to avoid further errors

        # Build the filename from constraints and values
        filename_parts = []
        for i, value in enumerate(best_values):
            constraint_name = constraint_names_with_units[i].split(" [")[0]  # Remove units for the filename
            filename_parts.append(f"{constraint_name}_{round(value, 3)}")

        # Join the parts to create a filename
        filename = "_".join(filename_parts) + "_GA.fcstd"

        # Save the FreeCAD document with the best result
        results_folder = path.join(path.dirname(self.model_file), "results")
        if not os.path.exists(results_folder):
            os.makedirs(results_folder)
        best_model_path = path.join(results_folder, filename)
        doc.saveAs(best_model_path)

        print(f"Best model saved as {best_model_path}")


    def genetic_algorithm_fitness(self, individual, variables):
        analysis = ParametricAnalysis(self.freecad_path, self.model_file)
        for variable, value in zip(variables, individual):
            variable.constraint_values = [value]
            analysis.add_variable(variable)
        output1 = Output("vonMises", max)
        analysis.add_output(output1)

        # Run the analysis with a delay
        results = analysis.run_analysis()
        time.sleep(1)  # Add a delay to ensure the FEA completes
        
        return results["max(vonMises)"].min(),  # Assuming von Mises stress is in max(vonMises)

    def run(self):
        doc = FreeCAD.openDocument(self.model_file)
        spreadsheet = None
        for obj in doc.Objects:
            if obj.Label == "Spreadsheet":
                spreadsheet = obj
                break

        variables = []
        min_values = []
        max_values = []
        constraint_names_with_units = []

        for row in range(2, spreadsheet.get('G2') + 1):
            object_name, original_constraint_name, constraint_name_with_unit, min_value, max_value = self.get_spreadsheet_data(spreadsheet, row)
            variable = Variable(object_name, original_constraint_name, [min_value, max_value])
            variables.append(variable)
            min_values.append(min_value)
            max_values.append(max_value)
            constraint_names_with_units.append(constraint_name_with_unit)

        # Genetic Algorithm setup
        creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMin)

        toolbox = base.Toolbox()

        # Initialize individuals within the [min_value, max_value] range
        def init_individual():
            return [random.uniform(min_v, max_v) for min_v, max_v in zip(min_values, max_values)]

        toolbox.register("individual", tools.initIterate, creator.Individual, init_individual)
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)
        toolbox.register("evaluate", self.genetic_algorithm_fitness, variables=variables)
        toolbox.register("mate", tools.cxBlend, alpha=0.5)
        toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=1, indpb=0.2)
        toolbox.register("select", tools.selBest)

        population = toolbox.population(n=self.population_size)
        N_generations = self.generations
        
        # DataFrame to collect results
        all_results = pd.DataFrame()

        # Total calculations for progress bar: generations * population size
        total_calculations = self.generations * self.population_size

        # Progress bar to track genetic algorithm progress
        with tqdm(total=total_calculations, desc="Genetic Algorithm Progress", ncols=100) as pbar:
            # Run genetic algorithm and collect results for each generation
            for gen in range(1, N_generations + 1):
                population = algorithms.varAnd(population, toolbox, cxpb=0.7, mutpb=0.3)
                fitnesses = list(map(toolbox.evaluate, population))

                generation_results = []
                for ind, fitness in zip(population, fitnesses):
                    # Collect individual's data and add generation info
                    individual_data = {constraint_names_with_units[i]: val for i, val in enumerate(ind)}
                    individual_data['vonMises [MPa]'] = fitness[0]
                    individual_data['generation'] = f'gen {gen}'

                    # Add this individual's data to the generation results list
                    generation_results.append(individual_data)

                    # Update the progress bar for each individual evaluated
                    pbar.update(1)

                # Append generation results to the all_results DataFrame
                all_results = pd.concat([all_results, pd.DataFrame(generation_results)], ignore_index=True)

                # Assign fitness to individuals after the evaluation
                for ind, fit in zip(population, fitnesses):
                    ind.fitness.values = fit

                # Select the next generation
                population = toolbox.select(population, len(population))

        # Move 'vonMises [MPa]' column to the last position
        if 'vonMises [MPa]' in all_results.columns:
            cols = [col for col in all_results.columns if col != 'vonMises [MPa]'] + ['vonMises [MPa]']
            all_results = all_results[cols]

        # Create a folder for results if it doesn't exist
        results_folder = path.join(path.dirname(self.model_file), "results")
        if not os.path.exists(results_folder):
            os.makedirs(results_folder)

        # Save results to CSV
        all_results.to_csv(path.join(results_folder, "ga_results.csv"), index=False)

        print(f"Results saved to {path.join(results_folder, 'ga_results.csv')}")

        # Find the row with the minimum von Mises stress
        best_row = all_results.loc[all_results['vonMises [MPa]'].idxmin()]

        # Extract the best values from the row
        best_values = best_row[:-2].values  # Exclude von Mises and generation columns from the best values
        
        # Save the best model with a dynamic filename
        self.save_best_model(doc, best_values, constraint_names_with_units)

        print("Run all analysis completed, results saved, and best model saved.")
