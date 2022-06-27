import os
# import zipfile
import re

from .utils.file_utils import get_other_in_dir

class Compiler:
    model_folder: str    ## The root folder that contains 2 directories, the model_name and a MAtlAB or R202XX folder
    model_name: str      ## The name of the simulink model
    path_to_model: str            ## path to the directory containing {root_model, slprj}
    def __init__(self, model_name, path_to_model, compile_type='grt', suffix='rtw'):
        self.model_name = model_name
        self.model_folder = path_to_model
        self.compile_type = compile_type
        self.suffix = suffix
        self._validate_root(model_name)


    def compile(self):
        self._build_deps_tree()


    def _validate_root(self, model_name):
        ## Validate that this is a real model
        assert os.path.exists(self.model_folder), \
            f"Model path does not exists: {self.model_folder}"

        self.simulink_native = get_other_in_dir(self.model_folder, self.model_name)
        self.path_to_model = os.path.join(self.model_folder, model_name)
        root_model_raw = get_other_in_dir(self.path_to_model, 'slprj')
        self.slprj = os.path.join(self.path_to_model, 'slprj')
        self.path_to_root = os.path.join(self.path_to_model, root_model_raw)
        
        sub_idx = root_model_raw.find("_"+self.compile_type+"_"+self.suffix)
        self.root_model = root_model_raw[:sub_idx]
        

    def _build_deps_tree(self):
        deps_root = self._get_deps(self.path_to_root, self.root_model)
        pass

    def _get_deps(self, path, model_name):
        deps = []
        with open(os.path.join(path, model_name+".h")) as f:
            regex = re.compile('^#include "(.*?)"')
            end = re.compile('^typedef')
            for line in f.readlines():
                inc_test = re.match(regex, line)
                if inc_test:
                    dep = inc_test.groups()[0]
                    suffix_idx = dep.find('.h')
                    deps.append(dep[:suffix_idx])
                    continue
                elif re.match(end, line):
                    break
        print(deps)
