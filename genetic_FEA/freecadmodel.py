import os
import contextlib
from .loghandler import logger
from .register_freecad import register_freecad
from typing import Tuple
import numpy as np

class FreecadModel:
    """FreecadModel class"""

    def __init__(self, document_path: str, freecad_path: str = "") -> None:
        """initialises a FreecadModel object

        Args:
            document_path (str): path to the FreeCAD file
            freecad_path (str): path to the FreeCAD Python libraries
        """
        self.filename = document_path

        global FreeCAD, femtools, vtkResults
        (FreeCAD, femtools, vtkResults) = register_freecad(freecad_path=freecad_path)

        self.model = FreeCAD.open(document_path)
        logger.debug(f"Opened FreeCAD model {document_path}")

        self.solver_name = ""
        self.fea_results_name = ""
        # TODO: error handling

    def change_parameter(
        self, object_name: str, constraint_name: str, target_value: float
    ):
        """changes a parameter (e.g. a named constraint) inside a freecad
        document. Currently works if the constraint is inside the driving
        sketch of the referenced object (e.g. a pocket)

        Args:
            object_name (str): name of the Freecad object containing the
                sketch containing the constraint
            constraint_name (str): name of the constraint to modify
            target_value (float): target value for the constraint
        """

        target_object = self.model.getObjectsByLabel(object_name)
        if not target_object:
            try:
                raise KeyError(f"Unable to find object {object_name} in the model")
            except KeyError as e:
                logger.exception(str(e))
                raise

        try:
            target_str = str(target_object[0])

            # sketcher objects need obj.getDatum / obj.setDatum
            if target_str == "<Sketcher::SketchObject>":
                target_object[0].setDatum(constraint_name, target_value)

            # generic objects need setattr(obj, attr, value)
            else:
                setattr(target_object[0], constraint_name, target_value)

        except (NameError, IndexError):
            logger.exception(
                f"Invalid constraint name {constraint_name} in object {object_name}"
            )
            raise

        logger.debug(f"Set {object_name}.{constraint_name} to {target_value}")
        # apply changes and recompute
        self.model.recompute()
        logger.debug("Model recomputed")
        # TODO: check for model errors here

    def run_fea(self, max_retries=3):
        """runs a FEA analysis in the specified freecad document

        Args:
            solver_name (str): name of the solver (e.g. SolverCcxTools)
            fea_results_name (str): name of the FEA results container (e.g.
                CCX_Results)

        Returns:
            fea object: a FreeCAD object containing the FEA results
        """
        if self.solver_name == "":
            self._find_solver_result_names()

        solver_object = self.model.getObject(self.solver_name)

        fea = femtools.ccxtools.FemToolsCcx(solver=solver_object)
        fea.purge_results()
        fea.reset_all()
        fea.update_objects()
        logger.debug(f"Prepared solver {solver_object.Name}")

        # Retry logic for FEA
        retries = 0
        von_mises_stress = 0
        while retries < max_retries:
            # there should be some error handling here
            fea.check_prerequisites()
            logger.debug("Checked FEA prerequisites")

            # Patch to redirect output from Calculix
            with open(os.devnull, "w", encoding="utf8") as devnull:
                with contextlib.redirect_stdout(devnull):
                    fea.run()

            if fea.results_present:
                logger.debug("FEA results generated")
                von_mises_stress = np.max(self.model.getObject(self.fea_results_name).vonMises)

                if von_mises_stress == 0:
                    retries += 1
                    logger.warning(f"Von Mises stress is zero, retrying {retries}/{max_retries}...")
                else:
                    return self.model.getObject(self.fea_results_name)
            else:
                retries += 1
                logger.warning(f"FEA failed, retrying {retries}/{max_retries}...")

        if retries == max_retries:
            logger.error(f"FEA analysis failed after {max_retries} retries. Von Mises stress is zero.")
            raise RuntimeError("FEA analysis failed. Von Mises stress is zero.")

    def export_fea_results(self, filename: str, export_format: str = "vtk"):
        """exports the results of a analysis to various mesh formats

        Args:
            filename (str): path to the output file
            export_format (str, optional): output format. Defaults to "vtk".

        Raises:
            NotImplementedError: if the output format specified is not available
        """

        if export_format == "vtk":
            objects = []
            objects.append(self.model.getObject(self.fea_results_name))
            vtkResults.importVTKResults.export(objects, filename)
            logger.info(f"Exporting VTK file {filename}")
            del objects
        else:
            try:
                raise NotImplementedError(
                    f"Export method {export_format} not available"
                )
            except NotImplementedError as e:
                logger.exception(str(e))
                raise

    def _find_solver_result_names(self) -> Tuple[str, str]:
        # do stuff...
        solver_name = ""
        fea_results_name = ""

        for el in self.model.Objects:
            if str(el) == "<Fem::FemSolverObjectPython object>":
                solver_name = el.Name
            if str(el) == "<Fem::FemResultObjectPython object>":
                fea_results_name = el.Name

        if "" in (solver_name, fea_results_name):
            try:
                raise NameError(
                    "FEA solver or results not found, consider "
                    "specifying manually using parametric.setup_fea()"
                )
            except NameError as e:
                logger.exception(str(e))
                raise

        logger.debug(f"Found solver name: {solver_name}")
        logger.debug(f"Found FEA results name: {fea_results_name}")

        self.solver_name = solver_name
        self.fea_results_name = fea_results_name
        return (self.solver_name, self.fea_results_name)
