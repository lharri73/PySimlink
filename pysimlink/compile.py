import os
import re
import glob
from subprocess import Popen, PIPE
import cmake
import shutil

from .utils.file_utils import get_other_in_dir
from .lib.dependency_graph import DepGraph
from .lib.cmake_gen import cmake_template

class Compiler:
    model_folder: str    ## The root folder that contains 2 directories, the model_name and a MAtlAB or R202XX folder
    model_name: str      ## The name of the simulink model
    path_to_model: str            ## path to the directory containing {root_model, slprj}
    def __init__(self, model_name, path_to_model, compile_type='grt', suffix='rtw', tmp_dir=None):
        self.model_name = model_name
        self.model_folder = os.path.normpath(path_to_model)
        self.compile_type = compile_type
        self.suffix = suffix
        if tmp_dir is None:
            import sys
            self.tmp_dir = os.path.join(os.path.dirname(sys.argv[0]), "__pycache__", "pysimlink", self.model_name)
        else:
            self.tmp_dir = os.path.join(tmp_dir, model_name)
        os.makedirs(self.tmp_dir, exist_ok=True)
        self._validate_root(model_name)


    def compile(self):
        self._get_simulink_deps()
        self._build_deps_tree()
        self._gen_custom_srcs()
        self._gen_cmake()
        self._build()
        

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

        simulink_deps = glob.glob(self.simulink_native + '/**/*.c', recursive=True)
        print(simulink_deps)
        exit(1)
        try: 
            simulink_deps.remove('rt_main.c')
        except ValueError:
            pass
        _shared_utils = glob.glob(os.path.join(self.slprj, '_sharedutils') + '/**/*.c', recursive=True)
        self.shared_utils_sources = simulink_deps + _shared_utils

    def _gen_cmake(self):
        includes = [self.custom_includes]
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
        
        cmake_text += maker.add_library('shared_utils', self.shared_utils_sources)
        ## the custom code depends on the root model. 
        self.models.add_dependency("model_interface_c", [self.root_model])
        self.models.add_dependency(self.root_model, ['shared_utils'])

        cmake_text += maker.add_custom_libs(self.custom_sources)
        cmake_text += maker.set_lib_props()
        cmake_text += maker.add_link_libs(self.models.dep_map)
        cmake_text += maker.add_compile_defs(self.defines)
        cmake_text += maker.footer()

        with open(os.path.join(self.tmp_dir, 'CMakeLists.txt'), 'w') as f:
            f.write(cmake_text)

    def _build(self):
        build_dir = os.path.join(self.tmp_dir, "build")
        process = Popen([os.path.join(cmake.CMAKE_BIN_DIR, "cmake"), "-S", self.tmp_dir, "-B", build_dir], stdout=PIPE, stderr=PIPE)
        (output1, err1) = process.communicate()
        build = process.wait() 
        if build != 0:
            from datetime import datetime
            now = datetime.now()
            err_file = os.path.join(os.getcwd(), now.strftime("%Y-%m-%d_%H-%M-%S_PySimlink_Generation_Error.log"))
            with open(err_file, 'w') as f:
                f.write(output1.decode() if output1 else "")
                f.write(err1.decode() if err1 else "")
            raise Exception("Generating the CMakeLists for this model failed. This could be a c/c++/cmake setup issue, bad paths, or a bug!\n" 
                f"Output from CMake generation is in {err_file}")

        process = Popen([os.path.join(cmake.CMAKE_BIN_DIR, "cmake"), '--build', build_dir], stdout=PIPE, stderr=PIPE)
        (output2, err2) = process.communicate()
        make = process.wait() 
        if make != 0:
            from datetime import datetime
            now = datetime.now()
            err_file = os.path.join(os.getcwd(), now.strftime("%Y-%m-%d_%H-%M-%S_PySimlink_Build_Error.log"))
            with open(err_file, 'w') as f:
                f.write(output2.decode() if output2 else "")
                f.write(err2.decode() if err2 else "")

            raise Exception("Building the model failed. This could be a c/c++/cmake setup issue, bad paths, or a bug!\n" 
                f"Output from the build process is in {err_file}")

    def _gen_custom_srcs(self):
        shutil.rmtree(os.path.join(self.tmp_dir, 'c_files'), ignore_errors=True)
        shutil.copytree(os.path.abspath(os.path.join(os.path.dirname(__file__), 'c_files')), os.path.join(self.tmp_dir, 'c_files'))
        self.custom_includes = os.path.join(self.tmp_dir, 'c_files', 'include')
        self.custom_sources = os.path.join(self.tmp_dir, 'c_files', 'src')
        
        with open(os.path.join(self.custom_includes, 'model_utils.hpp'), 'r') as f:
            model_utils = f.readlines()
        repl = lambda f: f.replace("<<ROOT_MODEL>>", self.root_model+".h")
        model_utils = list(map(repl, model_utils))

        with open(os.path.join(self.custom_includes, 'model_utils.hpp'), 'w') as f:
            f.writelines(model_utils)

        defines = os.path.join(self.path_to_root, "defines.txt")
        assert os.path.exists(defines), "Cannot find `defines.txt` in your root model. Try using the grt template. "

        with open(defines, 'r') as f:
            self.defines = [line.strip() for line in f.readlines()]

        
