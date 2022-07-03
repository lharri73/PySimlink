import os
import glob
from .compile import Compiler
import ctypes

class Model:
    def __init__(self, 
        model_name, 
        path_to_model, 
        compile_type='grt', 
        suffix='rtw', 
        tmp_dir=None,
        force_rebuild=False):
        self.model_name = model_name
        self.path_to_model = path_to_model
        self.compile_type = compile_type
        self.suffix = suffix

        if tmp_dir is None:
            import sys
            self.tmp_dir = os.path.join(os.path.dirname(sys.argv[0]), "__pycache__", "pysimlink", self.model_name)
        else:
            self.tmp_dir = os.path.join(tmp_dir, model_name)

        ## Check need to compile
        lib = glob.glob(os.path.join(self.tmp_dir, 'build', 'libmodel_interface_c.*'))
        if force_rebuild or not lib:
            ## Need to compile
            self.compiler = Compiler(model_name, path_to_model, compile_type, suffix, tmp_dir)
            self.compiler.compile()

        lib = glob.glob(os.path.join(self.tmp_dir, 'build', 'libmodel_interface_c.*'))
        self.model = ctypes.CDLL(lib[0])

