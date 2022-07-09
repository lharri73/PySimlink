from pysimlink.lib.compilers.compiler import Compiler
from pysimlink.utils.model_utils import ModelPaths
from pysimlink.lib import cmake_gen
import glob
import os

class NoRefCompiler(Compiler):
    def __init__(self, model_paths: ModelPaths):
        super().__init__(model_paths)

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
        for dir in os.walk(self.model_paths.root_model_path, followlinks=False):
            for file in dir[2]:
                if ".h" in file:
                    self.model_incs.append(dir[0])
                    break

    def _gen_cmake(self):
        includes = [self.custom_includes] + self.model_incs
        for dir in os.walk(self.model_paths.simulink_native, followlinks=False):
            for file in dir[2]:
                if ".h" in file:
                    includes.append(dir[0])
                    break
        maker = cmake_gen.cmake_template(self.model_paths.root_model_name.replace(' ', '_').replace('-', '_').lower())
        cmake_text = maker.header()
        cmake_text += maker.set_includes(includes)

        cmake_text += maker.add_library(self.model_paths.root_model_name, self.model_srcs)
        cmake_text += maker.add_library('shared_utils', self.simulink_deps_src)
        cmake_text += maker.add_custom_libs(self.custom_sources)

        cmake_text += maker.set_lib_props()
        dep_map = {
                self.model_paths.root_model_name: ['shared_utils'],
                'model_interface_c': [self.model_paths.root_model_name]
        }
        cmake_text += maker.add_link_libs(dep_map)
        cmake_text += maker.add_compile_defs(self.defines)
        cmake_text += maker.footer()

        with open(os.path.join(self.model_paths.tmp_dir, "CMakeLists.txt"), "w") as f:
            f.write(cmake_text)