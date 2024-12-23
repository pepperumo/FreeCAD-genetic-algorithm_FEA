# variable.py

import numpy as np

class Variable:
    def __init__(self, object_name, constraint_name, constraint_values):
        """
        Initializes a Variable object.

        Parameters:
        - object_name (str): The name of the object in FreeCAD.
        - constraint_name (str): The name of the constraint to modify.
        - constraint_values (array-like): The values to sweep through.
        """
        self.object_name = object_name
        self.constraint_name = constraint_name
        self.constraint_values = constraint_values

    def to_dict(self):
        """Converts the Variable object to a dictionary format for FEA."""
        return {
            "object_name": self.object_name,
            "constraint_name": self.constraint_name,
            "constraint_values": self.constraint_values,
        }
