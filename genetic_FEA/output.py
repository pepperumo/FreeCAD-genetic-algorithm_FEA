# output.py

class Output:
    def __init__(self, output_var, reduction_fun):
        """
        Initializes an Output object.

        Parameters:
        - output_var (str): The name of the output variable.
        - reduction_fun (callable): The function to reduce the output (e.g., np.max).
        """
        self.output_var = output_var
        self.reduction_fun = reduction_fun

    def to_dict(self):
        """Converts the Output object to a dictionary format for FEA."""
        return {
            "output_var": self.output_var,
            "reduction_fun": self.reduction_fun,
        }
