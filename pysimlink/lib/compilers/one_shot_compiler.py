from pysimlink.lib.compilers import Compiler
from pysimlink.utils.model_utils import ModelPaths

class NoRefCompiler(Compiler):
    def __init__(self, model_paths: ModelPaths):
        super().__init__(self, model_paths)

    def compile(self):
        pass
