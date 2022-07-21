import ctypes
import os
import sys

from pysimlink.lib.model_paths import ModelPaths
from pysimlink.lib.compilers import compiler


class Model:
    model_paths: ModelPaths
    compiler: compiler.Compiler

    def __init__(
        self,
        model_name,
        path_to_model,
        compile_type="grt",
        suffix="rtw",
        tmp_dir=None,
        force_rebuild=False,
    ):

        self.model_paths = ModelPaths(path_to_model, model_name, compile_type, suffix, tmp_dir)
        self.compiler = self.model_paths.compiler_factory()

        ## Check need to compile
        if force_rebuild or self.compiler.needs_to_compile():
            ## Need to compile
            self.compiler.compile()

        sys.path.append(os.path.join(self.model_paths.tmp_dir, "build"))
        import model_interface_c

        self.model = model_interface_c.Model()

    def get_params(self):
        return self.model.get_params()

    def reset(self):
        self.model.reset()

    def step(self):
        self.model.step()

    def tFinal(self):
        return self.model.tFinal()

    def step_size(self):
        return self.model.step_size()

    def set_tFinal(self, tFinal):
        if tFinal <= 0:
            raise ValueError("new tFinal must be > 0")
        self.model.set_tFinal(tFinal)