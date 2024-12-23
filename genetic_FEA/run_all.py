import sys
import os
import time  # Import the time module for adding delay
from os import path
import numpy as np

# Add FreeCAD Python libraries to sys.path dynamically
FREECAD_PATH = "C:/Program Files/FreeCAD 0.21/bin"  # Adjust this if your FreeCAD installation is elsewhere
if FREECAD_PATH not in sys.path:
    sys.path.append(FREECAD_PATH)

# Now import FreeCAD after adding the path
import FreeCAD
import pandas as pd
from FreecadParametricFEA.parametric_analysis import ParametricAnalysis
from FreecadParametricFEA.variable import Variable
from FreecadParametricFEA.output import Output

class RunAllAnalysis:
    def __init__(self, freecad_path, model_file):
        self.freecad_path = freecad_path
        self.model_file = model_file

    def get_spreadsheet_data(self, spreadsheet, row):
        object_name = spreadsheet.get(f'A{row}')
        constraint_name = spreadsheet.get(f'B{row}')
        min_value = float(spreadsheet.get(f'C{row}'))
        max_value = float(spreadsheet.get(f'D{row}'))
        steps = int(spreadsheet.get(f'E{row}'))
        unit = spreadsheet.get(f'F{row}')  
        constraint_name_with_unit = f"{constraint_name} [{unit}]"
        return object_name, constraint_name, min_value, max_value, steps, unit

    def save_best_model(self, doc, best_values, constraint_names_with_units):
        """Save the best model and dynamically name it based on constraints."""
        # Build the filename from constraints and values
        filename_parts = []
        for i, value in enumerate(best_values):
            constraint_name = constraint_names_with_units[i].split(" [")[0]  # Remove units for the filename
            filename_parts.append(f"{constraint_name}_{round(value, 3)}")

        # Join the parts to create a filename
        filename = "_".join(filename_parts) + "_run_all.fcstd"

        # Save the FreeCAD document
        results_folder = path.join(path.dirname(self.model_file), "results")
        if not os.path.exists(results_folder):
            os.makedirs(results_folder)
        best_model_path = path.join(results_folder, filename)
        doc.saveAs(best_model_path)

        print(f"Best model saved as {best_model_path}")

    def run(self):
        doc = FreeCAD.openDocument(self.model_file)
        spreadsheet = None
        for obj in doc.Objects:
            if obj.Label == "Spreadsheet":
                spreadsheet = obj
                break

        variables = []
        constraint_names_with_units = []  # Store the constraint names with units

        for row in range(2, spreadsheet.get('G2') + 1):
            # Get the data from the spreadsheet, including units
            object_name, constraint_name, min_value, max_value, steps, unit = self.get_spreadsheet_data(spreadsheet, row)
            
            # Generate the values between min_value and max_value using steps
            if steps > 1:
                values = np.linspace(min_value, max_value, steps)
            else:
                values = [min_value, max_value]  # Default to just min and max if no steps are defined

            # Create the variable with the generated values
            variable = Variable(object_name, constraint_name, values)
            variables.append(variable)
            
            # Store constraint names with units (e.g., 'S [mm]')
            constraint_name_with_unit = f"{constraint_name} [{unit}]"
            constraint_names_with_units.append(constraint_name_with_unit)

        output1 = Output("vonMises", max)

        analysis = ParametricAnalysis(self.freecad_path, self.model_file)
        for variable in variables:
            analysis.add_variable(variable)
        analysis.add_output(output1)

        # Run the analysis
        results = analysis.run_analysis()

        # Add a delay to ensure FreeCAD has fully processed the analysis
        time.sleep(1)  # Wait 2 seconds

        # Rename 'max(vonMises)' to 'vonMises [MPa]' for clarity
        if "max(vonMises)" in results.columns:
            results = results.rename(columns={"max(vonMises)": "vonMises [MPa]"})
        else:
            raise KeyError("Expected 'max(vonMises)' not found in the results.")

        # Exclude 'Msg' and 'FEA_Runtime' columns
        columns_to_exclude = ['Msg', 'FEA_Runtime']
        results = results.drop(columns=[col for col in columns_to_exclude if col in results.columns])

        # Move 'vonMises [MPa]' column to the last position
        if 'vonMises [MPa]' in results.columns:
            cols = [col for col in results.columns if col != 'vonMises [MPa]'] + ['vonMises [MPa]']
            results = results[cols]
        else:
            raise KeyError("'vonMises [MPa]' column not found after renaming.")

        # Create the renaming map that includes the constraint names with units
        rename_mapping = {results.columns[i]: constraint_names_with_units[i] for i in range(len(constraint_names_with_units))}
        
        # Apply the renaming
        results = results.rename(columns=rename_mapping)

        # Save the results to CSV
        results_folder = path.join(path.dirname(self.model_file), "results")
        if not os.path.exists(results_folder):
            os.makedirs(results_folder)
        results.to_csv(path.join(results_folder, "results.csv"), index=False)

        # Find the row with the minimum von Mises stress
        best_row = results.loc[results['vonMises [MPa]'].idxmin()]

        # Extract the best values from the row
        best_values = best_row[:-1].values  # Exclude von Mises from the best values
        
        # Save the best model with a dynamic filename
        self.save_best_model(doc, best_values, constraint_names_with_units)

        print("Run all analysis completed, results saved, and best model saved.")
