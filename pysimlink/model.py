import ctypes
import glob
import os
import platform
import sys

from pysimlink.lib.compilers.model_ref_compiler import Compiler
from pysimlink.utils.model_utils import ModelPaths


class Model:
    model_paths: ModelPaths
    compiler: Compiler
    model: ctypes.CDLL

    def __init__(self, 
            model_name, 
            path_to_model, 
            compile_type='grt', 
            suffix='rtw', 
            tmp_dir=None,
            force_rebuild=False):
        
        self.model_paths = ModelPaths(path_to_model, model_name, compile_type, suffix, tmp_dir)
        self.compiler = self.model_paths.compiler_factory()

        ## Check need to compile
        if force_rebuild or self.compiler.needs_to_compile():
            ## Need to compile
            self.compiler.compile()

        sys.path.append(os.path.join(self.model_paths.tmp_dir, 'build'))
        import model_interface_c
        self.model = model_interface_c.Model()


    def print_params(self):
        return self.model.print_params()

    def reset(self):
        self.model.reset()