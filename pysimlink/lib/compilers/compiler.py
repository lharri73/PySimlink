from pysimlink.utils.model_utils import ModelPaths
class Compiler:
    def __init__(self, model_paths: ModelPaths):
        self.model_paths = model_paths

    def compile(self):
        raise NotImplementedError


    def check_up_to_date(self):
        raise NotImplementedError
