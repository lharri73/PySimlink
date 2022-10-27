import os
import re
import glob
import warnings

from pysimlink.lib.dependency_graph import DepGraph
from pysimlink.lib.cmake_gen import CmakeTemplate
from pysimlink.lib.compilers.compiler import Compiler
from pysimlink.utils import annotation_utils as anno
from pysimlink.lib.struct_parser import parse_struct


class ModelRefCompiler(Compiler):
    """
    Compiler for a model that do use model references
    """

    def __init__(self, model_paths: "anno.ModelPaths"):
        super().__init__(model_paths)
        self.models = None

    def compile(self):
        self.clean()
        self._get_simulink_deps()
        self._build_deps_tree()
        self._gen_custom_srcs()
        self._gen_cmake()
        self.gather_types()
        self._build()

    def _build_deps_tree(self):
        """
        Get the dependencies for this model and all child models recursively,
        starting at the root model.

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
            return

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
        """Get all dependencies of a model

        Args:
            path: Path to the _model (including it's name). Must contain
                {model_name}.h
            model_name: Name of the _model. path must contain {model_name}.h

        Returns:
            deps: list of dependencies for this _model.
        """
        deps = set()
        with open(os.path.join(path, model_name + ".h"), encoding="utf-8") as f:
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
                if re.match(end, line):
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
        for dir_name in os.walk(self.model_paths.root_dir, followlinks=False):
            for file in dir_name[2]:
                if ".h" in file:
                    includes.append(dir_name[0])
                    break

        maker = CmakeTemplate(
            self.model_paths.root_model_name.replace(" ", "_").replace("-", "_").lower()
        )
        cmake_text = maker.header()
        cmake_text += maker.set_includes(includes)

        for lib in self.models.dep_map:
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

        with open(
            os.path.join(self.model_paths.tmp_dir, "CMakeLists.txt"), "w", encoding="utf-8"
        ) as f:
            f.write(cmake_text)

    @property
    def _module_name(self):
        return super()._module_name

    def gather_types(self):
        types_files = []
        for lib in self.models.dep_map:
            if lib == self.model_paths.root_model_path:
                files = glob.glob(self.model_paths.root_model_path + "/*_types.h")
            else:
                files = glob.glob(os.path.join(self.model_paths.slprj_dir, lib) + "/*_types.h")

            types_files += files

        for file in types_files:
            with open(file, "r") as f:
                lines = f.readlines()

            define_re = re.compile(r"^#define DEFINED_TYPEDEF")
            endif = re.compile(r"^#endif")
            pairs = []
            cur = None
            for i, line in enumerate(lines):
                test1 = re.search(define_re, line)
                test2 = re.search(endif, line)
                if test1 is not None:
                    if cur is not None:
                        warnings.warn("types file malformed")
                    else:
                        cur = i
                    continue
                if test2 is not None:
                    if cur is not None:
                        pairs.append((cur, i))
                        cur = None

            for pair in pairs:
                new_struct = parse_struct(lines[pair[0]+2:pair[1]-1])
                for struct in self.types:
                    ## Prevent duplicate types
                    if struct.name == new_struct.name:
                        break
                else:
                    self.types.append(new_struct)

        ret = []
        for type in self.types:
            ret += [f'    py::class_<{type.name}>(m, "{type.name}", py::module_local())']
            for field in type.fields:
                ret += [f'            .def_readonly("{field.name}", &{type.name}::{field.name})']
            ret[-1] += ';'
            ret.append('')

        return '\n'.join(ret)

    def get_type_names(self):
        ret = []
        for struct in self.types:
            ret.append(f"{struct.name} {struct.name}_obj;")

        return '\n        '.join(ret)
