import ctypes
import glob
import os

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
        lib = glob.glob(os.path.join(self.tmp_dir, 'build', 'libmodel_interface_c.*'))
        if force_rebuild or not lib:
            ## Need to compile
            self.compiler = Compiler(model_name, path_to_model, compile_type, suffix, tmp_dir)
            self.compiler.compile()

        lib = glob.glob(os.path.join(self.tmp_dir, 'build', 'libmodel_interface_c.*'))
        self.model = ctypes.CDLL(lib[0])

