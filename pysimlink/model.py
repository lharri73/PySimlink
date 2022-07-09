import ctypes
import glob
import os
import platform

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

        lib = glob.glob(os.path.join(self.model_paths.tmp_dir, 'build', 'libmodel_interface_c.*'))
        self.model_lib = ctypes.CDLL(lib[0])

        ## set up the arguments and return types for all function parameters
        #  in the dll
        self.setup_types(self.model_lib.new_model, ctypes.c_void_p, [])
        self.setup_types(self.model_lib.delete_model, None, [ctypes.c_void_p])
        self.setup_types(self.model_lib.call_reset, None, [ctypes.c_void_p])
        self.setup_types(self.model_lib.call_print_params, None, [ctypes.c_void_p])

        self.model = self.model_lib.new_model()

    @staticmethod
    def setup_types(func, ret_type, arg_types):
        """Set up the function return and argument types

        :param func: ctypes
        :param ret_type:
        :param arg_types:
        :return:
        """
        assert isinstance(arg_types, list), "argTypes should be a list of argument types"
        if ret_type is not None:
            func.restype = ret_type
        func.argtypes = arg_types


    def print_params(self):
        self.model_lib.call_print_params(self.model)

    def reset(self):
        self.model_lib.call_reset(self.model)

    def __del__(self):
        self.model_lib.delete_model(self.model)