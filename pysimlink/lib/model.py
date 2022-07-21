import os
import sys

from pysimlink.lib.model_paths import ModelPaths
from pysimlink.utils import annotation_utils as anno


class Model:
    """
    Instance of the simulink mode. This class compiles and imports
    the model once built. You can have multiple instances of the same
    model in one python runtime (although multithreaded *compiling* is not tested).
    """

    model_paths: "anno.ModelPaths"
    compiler: "anno.Compiler"

    def __init__(  # pylint: disable=R0913
        self,
        model_name: str,
        path_to_model: str,
        compile_type: str = "grt",
        suffix: str = "rtw",
        tmp_dir: str = None,
        force_rebuild: bool = False,
    ):

        self.model_paths = ModelPaths(path_to_model, model_name, compile_type, suffix, tmp_dir)
        self.compiler = self.model_paths.compiler_factory()

        ## Check need to compile
        if force_rebuild or self.compiler.needs_to_compile():
            ## Need to compile
            self.compiler.compile()

        sys.path.append(os.path.join(self.model_paths.tmp_dir, "build"))

        import model_interface_c  # pylint: disable=C0415,E0401

        self._model = model_interface_c.Model()

    def get_params(self) -> "anno.ModelInfo":
        """
        Return an instance of all parameters, blocks, and signals in the _model

        See `lib.model_utils.print_all_params` for iterating and printing the contents of this object
        Returns:
            ModelInfo
        """
        return self._model.get_params()

    def reset(self):
        """
        Reset the simulink model. This clears all signal values and reinstantiates the model.
        """
        self._model.reset()

    def step(self, iterations: int = 1):
        """
        Step the simulink model


        Args:
            iterations: Number of timesteps to step internally.
                `model.step(10)` is equivalent to calling `for _ range(10): model.step(1)` functionally, but compiled.

        Raises:
            RuntimeError: If the model encounters an error (these will be raised from simulink). Most commonly, this
                will be `simulation complete`.

        """
        self._model.step(iterations)

    def tFinal(self) -> float:
        """
        Get the final timestep of the model.

        Returns:
            tFinal: Final timestep of the model (seconds from zero).
        """
        return self._model.tFinal()

    def step_size(self) -> float:
        """
        Get the step size of the model

        Returns:
            step_size: step size of the fixed step solver.
        """
        return self._model.step_size()

    def set_tFinal(self, tFinal: float):
        """
        Change the final timestep of the model

        Args:
            tFinal: New final timestep of the model (seconds from zero).

        Raises:
            ValueError: if tFinal is <= 0
        """
        if tFinal <= 0:
            raise ValueError("new tFinal must be > 0")
        self._model.set_tFinal(tFinal)
