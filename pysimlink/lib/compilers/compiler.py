from pysimlink.utils.model_utils import ModelPaths, infer_defines
import glob
import os
import shutil
import cmake
from subprocess import Popen, PIPE


class Compiler:
    simulink_deps: set[str]         ## All header files created in the simulink common directory
    simulink_deps_path: list[str]   ## Path to the header files created in the simulink common dir
    simulink_deps_src: list[str]    ## Path to all source files created in the simulink common dir
    model_paths: ModelPaths         ## Instance of the ModelPaths containing information about the directory structure
    defines: list[str]              ## All defines that should be set during model compilation
    custom_includes: str            ## Include files directory defined by this python module
    custom_sources: str             ## Source files directory defined by this python module
    
    def __init__(self, model_paths: ModelPaths):
        self.model_paths = model_paths

    def clean(self):
        shutil.rmtree(self.model_paths.tmp_dir)

    def compile(self):
        raise NotImplementedError

    def needs_to_compile(self):
        lib = glob.glob(os.path.join(self.model_paths.tmp_dir, 'build', 'libmodel_interface_c.*'))
        return len(lib) != 0

    def _get_simulink_deps(self):
        files = glob.glob(self.model_paths.simulink_native + '/**/*.h', recursive=True)

        self.simulink_deps = set([os.path.basename(f).split('.')[0] for f in files])
        self.simulink_deps_path = files

        simulink_deps = glob.glob(self.model_paths.simulink_native + '/**/*.c', recursive=True)
        rt_main = None
        for file in simulink_deps:
            if os.path.basename(file) == "rt_main.c":
                rt_main = file
                break
        if rt_main is not None:
            simulink_deps.remove(rt_main)

        self.simulink_deps_src = simulink_deps 

    def _gen_custom_srcs(self):
        shutil.rmtree(os.path.join(self.model_paths.tmp_dir, 'c_files'), ignore_errors=True)
        shutil.copytree(
                os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..','c_files')),
                os.path.join(self.model_paths.tmp_dir, 'c_files')
        )
        self.custom_includes = os.path.join(self.model_paths.tmp_dir, 'c_files', 'include')
        self.custom_sources = os.path.join(self.model_paths.tmp_dir, 'c_files', 'src')
        
        with open(os.path.join(self.custom_includes, 'model_utils.hpp'), 'r') as f:
            model_utils = f.readlines()

        model_utils = [line.replace("<<ROOT_MODEL>>", self.model_paths.root_model_name +".h") for line in model_utils]

        with open(os.path.join(self.custom_includes, 'model_utils.hpp'), 'w') as f:
            f.writelines(model_utils)

        defines = os.path.join(self.model_paths.root_model_path, "defines.txt")
        if os.path.exists(defines):
            with open(defines, 'r') as f:
                self.defines = [line.strip() for line in f.readlines()]
        else:
            self.defines = infer_defines(self.model_paths)

    def _build(self):
        build_dir = os.path.join(self.model_paths.tmp_dir, "build")
        process = Popen([os.path.join(cmake.CMAKE_BIN_DIR, "cmake"), "-S", self.model_paths.tmp_dir, "-B", build_dir], stdout=PIPE, stderr=PIPE)
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