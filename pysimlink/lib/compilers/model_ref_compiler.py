import os
import re
import glob

from pysimlink.lib.dependency_graph import DepGraph
from pysimlink.lib.cmake_gen import CmakeTemplate
from pysimlink.lib.compilers.compiler import Compiler
from pysimlink.utils import annotation_utils as anno


class ModelRefCompiler(Compiler):
    def __init__(self, model_paths: "anno.ModelPaths"):
        super().__init__(model_paths)

    def compile(self):
        self._get_simulink_deps()
        self._build_deps_tree()
        self._gen_custom_srcs()
        self._gen_cmake()
        self._build()

    def _build_deps_tree(self):
        """
        Get the dependencies for this _model and all child models recursively,
        starting at the root _model.

        """
        self.models = DepGraph()
        self.update_recurse(self.model_paths.root_model_name, self.models, is_root=True)

    def update_recurse(self, model_name: str, models: "anno.DepGraph", is_root=False):
        """
        Recursively gathers dependencies for a _model and adds them to the
        dependency graph.
        Argument:
            model_name: Name of the _model. This is used to locate the _model in
                the slprj/{compile_type} folder
            models: An instance of the dependency graph
            is_root: Since the root _model is in a different place, we handle the
                path differently. This is set to true only when processing the
                root _model
        Returns:
            None: always
        """
        if model_name in models:
            return None

        model_path = (
            self.model_paths.root_model_path
            if is_root
            else os.path.join(self.model_paths.slprj_dir, model_name)
        )
        deps = self._get_deps(model_path, model_name)
        models.add_dependency(model_name, deps)
        for dep in deps:
            self.update_recurse(dep, models)

    def _get_deps(self, path, model_name):
        """Get all dependencies of a _model

        Args:
            path: Path to the _model (including it's name). Must contain
                {model_name}.h
            model_name: Name of the _model. path must contain {model_name}.h

        Returns:
            deps: list of dependencies for this _model.
        """
        deps = set()
        with open(os.path.join(path, model_name + ".h")) as f:
            regex = re.compile('^#include "(.*?)"')
            end = re.compile("^typedef")
            for line in f.readlines():
                inc_test = re.match(regex, line)
                if inc_test:
                    dep = inc_test.groups()[0]
                    ## Could probably replace this with .split('.')[0] but can _model names have a '.'?
                    suffix_idx = dep.find(".h")
                    deps.add(dep[:suffix_idx])
                    continue
                elif re.match(end, line):
                    break
        this_deps = deps.difference(self.simulink_deps)
        to_remove = [dep for dep in this_deps if dep.startswith(model_name)]
        return this_deps.difference(to_remove)

    def _get_simulink_deps(self):
        super()._get_simulink_deps()
        _shared_utils = glob.glob(
            os.path.join(self.model_paths.slprj_dir, "_sharedutils") + "/**/*.c",
            recursive=True,
        )
        self.simulink_deps_src += _shared_utils

        _shared_utils = glob.glob(
            os.path.join(self.model_paths.slprj_dir, "_sharedutils") + "/**/*.h",
            recursive=True,
        )
        self.simulink_deps = self.simulink_deps.union(
            [os.path.basename(f).split(".")[0] for f in _shared_utils]
        )

    def _gen_cmake(self):
        includes = [self.custom_includes]
        for dir in os.walk(self.model_paths.root_dir, followlinks=False):
            for file in dir[2]:
                if ".h" in file:
                    includes.append(dir[0])
                    break

        maker = CmakeTemplate(
            self.model_paths.root_model_name.replace(" ", "_").replace("-", "_").lower()
        )
        cmake_text = maker.header()
        cmake_text += maker.set_includes(includes)

        for lib in self.models.dep_map.keys():
            if lib == self.model_paths.root_model_name:
                files = glob.glob(self.model_paths.root_model_path + "/*.c")
            else:
                files = glob.glob(os.path.join(self.model_paths.slprj_dir, lib) + "/*.c")
            cmake_text += maker.add_library(lib, files)

        cmake_text += maker.add_library("shared_utils", self.simulink_deps_src)
        ## the custom code depends on the root _model.
        self.models.add_dependency(self.model_paths.root_model_name, ["shared_utils"])

        cmake_text += maker.add_custom_libs(self.custom_sources)
        cmake_text += maker.add_private_link(self.model_paths.root_model_name)
        cmake_text += maker.set_lib_props()
        cmake_text += maker.add_link_libs(self.models.dep_map)
        cmake_text += maker.add_compile_defs(self.defines)
        cmake_text += maker.footer()

        with open(os.path.join(self.model_paths.tmp_dir, "CMakeLists.txt"), "w") as f:
            f.write(cmake_text)
