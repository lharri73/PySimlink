import os
import sys

import numpy as np

from pysimlink.lib.model_paths import ModelPaths
from pysimlink.utils import annotation_utils as anno
from pysimlink.lib.model_types import DataType, ModelInfo


class Model:
    """
    Instance of the simulink mode. This class compiles and imports
    the model once built. You can have multiple instances of the same
    model in one python runtime (although multithreading *compiling* is not tested).
    """

    _model_paths: "anno.ModelPaths"
    _compiler: "anno.Compiler"

    def __init__(  # pylint: disable=R0913
        self,
        model_name: str,
        path_to_model: str,
        compile_type: str = "grt",
        suffix: str = "rtw",
        tmp_dir: "anno.Optional[str]" = None,
        force_rebuild: bool = False,
    ):
        """
        Args:
            model_name (str): name of the root simulink model
            path_to_model (str): path to the directory containing code generated from the Simulink Coder *or* the packaged zip file
            compile_type (str): Makefile template used to generate code from Simulink Coder. Only GRT is supported.
            suffix (str): Simulink Coder folders are almost always suffixed with rtw (real time workshop).
            tmp_dir (Optional[str]): Path to the directory that will be used to build the model. Defaults to :file:`__pycache__/{model_name}`
            force_rebuild (bool): force pysimlink to recompile the model from the source located at :code:`path_to_model`. Removes all build artifacts.

        Attributes:
            orientations: enumeration describing matrix orientations (row major, column major, etc.). This enumeration is
                likely the same among all models, but could change across MATLAB versions.
        """

        self._model_paths = ModelPaths(path_to_model, model_name, compile_type, suffix, tmp_dir)
        self._compiler = self._model_paths.compiler_factory()

        ## Check need to compile
        if force_rebuild or self._compiler.needs_to_compile():
            ## Need to compile
            self._compiler.compile()

        for dir, _, _ in os.walk(os.path.join(self._model_paths.tmp_dir, "build", "out", "library")):
            sys.path.append(dir)

        import model_interface_c  # pylint: disable=C0415,E0401

        self._model = model_interface_c.Model(self._model_paths.root_model_name)
        self.orientations = model_interface_c.rtwCAPI_Orientation

    def __len__(self):
        """
        Get the total number of steps this model can run
        """
        return self.step_size() * self.tFinal()

    def get_params(self) -> "list[anno.ModelInfo]":
        """
        Return an instance of all parameters, blocks, and signals in the _model

        See :func:`pysimlink.print_all_params` for iterating and printing the contents of this object

        Returns:
            list[:class:`pysimlink.types.ModelInfo`]: List of model info, one for each model (if reference models present). One ModelInfo if no reference models
        """
        return list(map(ModelInfo, self._model.get_params()))

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
                :code:`model.step(10)` is equivalent to calling :code:`for _ range(10): model.step(1)` functionally, but compiled.

        Raises:
            RuntimeError: If the model encounters an error (these will be raised from simulink). Most commonly, this
                will be `simulation complete`.

        """
        self._model.step(iterations)

    def tFinal(self) -> float:
        """
        Get the final timestep of the model.

        Returns:
            float: Final timestep of the model (seconds from zero).
        """
        return self._model.tFinal()

    def step_size(self) -> float:
        """
        Get the step size of the model

        Returns:
            float: step size of the fixed step solver.
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

    def get_signal(self, block_path, model_name=None, sig_name="") -> "np.ndarray":
        """
        Get the value of a signal

        Args:
            block_path: Path to the originating block
            model_name: Name of the model provided by :func:`pysimlink.print_all_params`. None if there are no model
                references (using :code:`None` will retrieve from the root model).
            sig_name: Name of the signal

        Returns:
            Value of the signal at the current timestep
        """
        model_name = self._model_paths.root_model_name if model_name is None else model_name
        return self._model.get_signal(model_name, block_path, sig_name)

    def get_block_param(self, block_path, param, model_name=None) -> "np.ndarray":
        """
        Get the value of a block parameter

        Args:
            block_path: Path the block within the model
            param: Name of the parameter to retrieve
            model_name: Name of the model provided by :func:`pysimlink.print_all_params`. None if there are no model references.

        Returns:
            np.ndarray with the value of the parameter
        """

        model_name = self._model_paths.root_model_name if model_name is None else model_name
        return self._model.get_block_param(model_name, block_path, param)

    def get_models(self) -> "list[str]":
        """
        Gets a list of all reference models (and the root model) in this model.

        Returns:
            list of paths, one for each model
        """
        return self._model.get_models()

    def set_block_param(self, block: str, param: str, value: "anno.ndarray", model_name: "anno.Union[str,None]" = None):
        """
        Set the parameter of a block within the model.

        Args:
            block: Path to the block within the model
            param: Name of the parameter to change
            value: new value of the parameter
            model_name: Name of the model provided by :func:`pysimlink.print_all_params`. None if there are no model references.
        Raises:
            RuntimeError: If the value array is not the correct shape or orientation as the parameter to change
        """
        model_name = self._model_paths.root_model_name if model_name is None else model_name
        info = self._model.block_param_info(model_name, block, param)
        dtype = DataType(info)
        if dtype.orientation in [self.orientations.col_major_nd, self.orientations.col_major]:
            value = np.asfortranarray(value)
        elif dtype.orientation in [self.orientations.row_major_nd, self.orientations.row_major]:
            value = np.ascontiguousarray(value)
        self._model.set_block_param(model_name, block, param, value)
