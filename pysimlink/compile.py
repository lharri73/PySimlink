import os
import re
import glob

from .utils.file_utils import get_other_in_dir
from .lib.dependency_graph import DepGraph
from .lib.cmake_gen import cmake_template

class Compiler:
    model_folder: str    ## The root folder that contains 2 directories, the model_name and a MAtlAB or R202XX folder
    model_name: str      ## The name of the simulink model
    path_to_model: str            ## path to the directory containing {root_model, slprj}
    def __init__(self, model_name, path_to_model, compile_type='grt', suffix='rtw', tmp_dir=None):
        self.model_name = model_name
        self.model_folder = path_to_model
        self.compile_type = compile_type
        self.suffix = suffix
        self.tmp_dir = tmp_dir
        self._validate_root(model_name)


    def compile(self):
        self._get_simulink_deps()
        self._build_deps_tree()
        self._gen_cmake()
        with open('CMakeLists.txt', 'w') as f:
            f.write(self.cmake_text)


    def _validate_root(self, model_name):
        ## Validate that this is a real model
        assert os.path.exists(self.model_folder), \
            f"Model path does not exists: {self.model_folder}"

        self.simulink_native = os.path.join(self.model_folder, get_other_in_dir(self.model_folder, self.model_name))
        self.path_to_model = os.path.join(self.model_folder, model_name)
        root_model_raw = get_other_in_dir(self.path_to_model, 'slprj')
        self.slprj = os.path.join(self.path_to_model, 'slprj', self.compile_type)
        self.path_to_root = os.path.join(self.path_to_model, root_model_raw)
        
        sub_idx = root_model_raw.find("_"+self.compile_type+"_"+self.suffix)
        self.root_model = root_model_raw[:sub_idx]
        

    def _build_deps_tree(self):
        """
        Get the dependencies for this model and all child models recursively,
        starting at the root model. 
        
        """
        self.models = DepGraph()
        self.update_recurse(self.root_model, self.models, is_root=True)
        

    def update_recurse(self, 
                       model_name: str, 
                       models: DepGraph, 
                       is_root=False):
        """
        Recursively gathers dependencies for a model and adds them to the
        dependency graph. 
        Argument:
            model_name: Name of the model. This is used to locate the model in
                the slprj/{compile_type} folder
            models: An instance of the dependency graph
            is_root: Since the root model is in a different place, we handle the
                path differently. This is set to true only when processing the
                root model
        Returns:
            None: always
        """
        if model_name in models: return None

        model_path = self.path_to_root if is_root else os.path.join(self.slprj, model_name)
        deps = self._get_deps(model_path, model_name)
        models.add_dependency(model_name, deps)
        for dep in deps:
            self.update_recurse(dep, models)
        


    def _get_deps(self, path, model_name):
        """Get all dependencies of a model

        Args:
            path: Path to the model (including it's name). Must contain
                {model_name}.h
            model_name: Name of the model. path must contain {model_name}.h
        
        Returns:
            deps: list of dependencies for this model. 
        """
        deps = set()
        with open(os.path.join(path, model_name+".h")) as f:
            regex = re.compile('^#include "(.*?)"')
            end = re.compile('^typedef')
            for line in f.readlines():
                inc_test = re.match(regex, line)
                if inc_test:
                    dep = inc_test.groups()[0]
                    ## Could probably replace this with .split('.')[0] but can model names have a '.'?
                    suffix_idx = dep.find('.h')
                    deps.add(dep[:suffix_idx])
                    continue
                elif re.match(end, line):
                    break
        this_deps = deps.difference(self.simulink_deps)
        to_remove = [dep for dep in this_deps if dep.startswith(model_name)]
        return this_deps.difference(to_remove)

    def _get_simulink_deps(self):
        files = glob.glob(self.simulink_native + '/**/*.h', recursive=True)
        files2 = glob.glob(os.path.join(self.path_to_model, 'slprj', self.compile_type, '_sharedutils') + '/**/*.h', recursive=True)
        files += files2
        
        iter = lambda file: os.path.basename(file).split('.')[0]
        self.simulink_deps = set(map(iter, files))
        self.simulink_deps_path = files

    def _gen_cmake(self):
        includes = []
        for dir in os.walk(self.model_folder, followlinks=False):
            for file in dir[2]:
                if ".h" in file:
                    includes.append(dir[0])
                    break

        maker = cmake_template(self.model_name.replace(' ', '_').replace('-', '_').lower())
        cmake_text = maker.header()
        cmake_text += maker.set_includes(includes)

        for lib in self.models.dep_map.keys():
            if lib == self.root_model:
                files = glob.glob(self.path_to_root + "/*.c")
            else:
                files = glob.glob(os.path.join(self.slprj, lib) + "/*.c")
            cmake_text += maker.add_library(lib, files)

        cmake_text += maker.set_lib_props()
        self.cmake_text = cmake_text
