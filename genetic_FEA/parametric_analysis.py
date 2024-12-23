# parametric_analysis.py

from FreecadParametricFEA import parametric as pfea
from FreecadParametricFEA.variable import Variable
from FreecadParametricFEA.output import Output

class ParametricAnalysis:
    def __init__(self, freecad_path, model_file):
        """
        Initializes the ParametricAnalysis object.

        Parameters:
        - freecad_path (str): Path to FreeCAD executable directory.
        - model_file (str): Path to the FreeCAD model file (.fcstd).
        """
        self.fea = pfea(freecad_path=freecad_path)
        self.fea.set_model(model_file)
        self.variables = []  # List to store Variable objects
        self.outputs = []  # List to store Output objects

    def add_variable(self, variable):
        """
        Adds a Variable object to the analysis.

        Parameters:
        - variable (Variable): A Variable object to add.
        """
        self.variables.append(variable)

    def add_output(self, output):
        """
        Adds an Output object to the analysis.

        Parameters:
        - output (Output): An Output object to add.
        """
        self.outputs.append(output)

    def run_analysis(self):
        """
        Runs the parametric analysis and returns the results.
        
        Returns:
        - results (dict): Dictionary containing the results of the parametric analysis.
        """
        # Convert variables to the required format and set them
        variable_dicts = [var.to_dict() for var in self.variables]
        self.fea.set_variables(variable_dicts)

        # Convert outputs to the required format and set them
        output_dicts = [output.to_dict() for output in self.outputs]
        self.fea.set_outputs(output_dicts)

        self.fea.setup_fea(fea_results_name="CCX_Results", solver_name="SolverCcxTools")
        results = self.fea.run_parametric(export_results=False) #set to False so that the results are not exported 
        #self.fea.plot_fea_results()
        return results
