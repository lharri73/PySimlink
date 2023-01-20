import glob
import os

from pysimlink.lib import cmake_gen
from pysimlink.lib.compilers.compiler import Compiler
from pysimlink.utils import annotation_utils as anno


class NoRefCompiler(Compiler):
    """
    Compiler for a model that does not use model references
    """

    def __init__(self, model_paths: "anno.ModelPaths"):
        super().__init__(model_paths)
        self.model_srcs = []
        self.model_incs = []

    def compile(self):
        self.clean()
        self._get_simulink_deps()
        self._gen_custom_srcs()
        self._gen_model_deps()
        self._gen_cmake()
        self._build()

    def _gen_model_deps(self):
        self.model_srcs = glob.glob(self.model_paths.root_model_path + "/**/*.c", recursive=True)
        self.model_incs = []
        for dir_name in os.walk(self.model_paths.root_model_path, followlinks=False):
            for file in dir_name[2]:
                if ".h" in file:
                    self.model_incs.append(dir_name[0])
                    break

    def _gen_cmake(self):
        includes = [self.custom_includes] + self.model_incs
        for dir_name in os.walk(self.model_paths.simulink_native, followlinks=False):
            for file in dir_name[2]:
                if ".h" in file:
                    includes.append(dir_name[0])
                    break
        maker = cmake_gen.CmakeTemplate(
            self.model_paths.root_model_name.replace(" ", "_").replace("-", "_").lower()
        )
        cmake_text = maker.header()
        cmake_text += maker.set_includes(includes)

        cmake_text += maker.add_library(self.model_paths.root_model_name, self.model_srcs)
        cmake_text += maker.add_library("shared_utils", self.simulink_deps_src)
        cmake_text += maker.add_custom_libs(self.custom_sources)
        cmake_text += maker.set_lib_props()

        dep_map = {self.model_paths.root_model_name: ["shared_utils"]}
        cmake_text += maker.add_link_libs(dep_map)
        cmake_text += maker.add_private_link(self.model_paths.root_model_name)
        cmake_text += maker.set_lib_props()
        cmake_text += maker.add_compile_defs(self.defines)

        cmake_text += maker.footer()

        with open(
            os.path.join(self.model_paths.tmp_dir, "CMakeLists.txt"), "w", encoding="utf-8"
        ) as f:
            f.write(cmake_text)

    def gather_types(self):
        types_files = glob.glob(self.model_paths.root_model_path + "/*_types.h")

        for file in types_files:
            with open(file, "r") as f:
                lines = f.readlines()

            self._read_types_single_file(lines)

        return self._gen_types()
