from abc import abstractmethod
import glob
import os
import shutil
from datetime import datetime
from subprocess import Popen, PIPE

import cmake

from pysimlink.utils import annotation_utils as anno
from pysimlink.utils.model_utils import infer_defines, sanitize_model_name
from pysimlink.lib.exceptions import GenerationError, BuildError


class Compiler:
    """
    Base class to discover sources and compile a model
    """

    simulink_deps: "set[str]"  ## All header files created in the simulink common directory
    simulink_deps_path: "list[str]"  ## Path to the header files created in the simulink common dir
    simulink_deps_src: "list[str]"  ## Path to all source files created in the simulink common dir
    model_paths: "anno.ModelPaths"  ## Instance of the ModelPaths containing information about the directory structure
    defines: "list[str]"  ## All defines that should be set during _model compilation
    custom_includes: str  ## Include files directory defined by this python module
    custom_sources: str  ## Source files directory defined by this python module

    def __init__(self, model_paths: "anno.ModelPaths"):
        self.model_paths = model_paths

    def clean(self):
        """
        Remove all files from the temporary directory
        """
        shutil.rmtree(self.model_paths.tmp_dir, ignore_errors=True)

    def compile(self):
        """
        Builds the cmake file, calls cmake, and builds the extension.
        """
        raise NotImplementedError

    def needs_to_compile(self) -> bool:
        """
        check if the model extension exists.

        Returns:
            bool: True if the model needs to be compiled, False otherwise
        """
        if os.name == "nt":
            lib = glob.glob(
                os.path.join(
                    self.model_paths.tmp_dir,
                    "build",
                    "out",
                    "library",
                    "Debug",
                    self.model_paths.module_name + ".*"
                )
            )
        else:
            lib = glob.glob(
                os.path.join(
                    self.model_paths.tmp_dir, "build", "out", "library", self.model_paths.module_name + ".*"
                )
            )
        return len(lib) == 0

    def _get_simulink_deps(self):
        """
        Generates a list of all simulink dependencies and their paths
        """
        files = glob.glob(self.model_paths.simulink_native + "/**/*.h", recursive=True)

        self.simulink_deps = {os.path.basename(f).split(".")[0] for f in files}
        self.simulink_deps_path = files

        simulink_deps = glob.glob(self.model_paths.simulink_native + "/**/*.c", recursive=True)
        rt_main = None
        for file in simulink_deps:
            if os.path.basename(file) in ["rt_main.c", "classic_main.c"]:
                rt_main = file
                break
        if rt_main is not None:
            simulink_deps.remove(rt_main)

        self.simulink_deps_src = simulink_deps

    def _gen_custom_srcs(self):
        """
        Moves all custom mixin source files to the temporary directory and makes appropriate replacements
        in the source files
        """
        shutil.rmtree(
            os.path.join(self.model_paths.tmp_dir, "c_files"),
            ignore_errors=True,
        )
        shutil.copytree(
            os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "c_files")),
            os.path.join(self.model_paths.tmp_dir, "c_files"),
        )
        self.custom_includes = os.path.join(self.model_paths.tmp_dir, "c_files", "include")
        self.custom_sources = os.path.join(self.model_paths.tmp_dir, "c_files", "src")

        replacements = {
            "<<ROOT_MODEL>>": self.model_paths.root_model_name + ".h",
            "<<ROOT_MODEL_PRIVATE>>": self.model_paths.root_model_name + "_private.h",
            "<<MODEL_INTERFACE_C>>": self.model_paths.module_name,
            "<<ROOT_MODEL_NAME>>": sanitize_model_name(self.model_paths.root_model_name)
        }
        self._replace_macros(os.path.join(self.custom_includes, "model_utils.hpp"), replacements)
        self._replace_macros(
            os.path.join(self.custom_includes, "model_interface.hpp"), replacements
        )
        self._replace_macros(os.path.join(self.custom_sources, "bindings.cpp"), replacements)

        defines = os.path.join(self.model_paths.root_model_path, "defines.txt")
        if os.path.exists(defines):
            with open(defines, "r", encoding="utf-8") as f:
                self.defines = [line.strip() for line in f.readlines()]
        else:
            self.defines = infer_defines(self.model_paths)

    def _build(self):
        """
        Cals cmake to configure and build the extension. Writes errors to the current working directory
        in a log file.
        """
        build_dir = os.path.join(self.model_paths.tmp_dir, "build")

        with Popen(
            [
                os.path.join(cmake.CMAKE_BIN_DIR, "cmake"),
                "-S",
                self.model_paths.tmp_dir,
                "-DCMAKE_BUILD_TYPE=Release",
                "-B",
                build_dir,
            ],
            stdout=PIPE,
            stderr=PIPE,
        ) as p:
            (output1, err1) = p.communicate()
            build = p.wait()

        if build != 0:
            now = datetime.now()
            err_file = os.path.join(
                os.getcwd(),
                now.strftime("%Y-%m-%d_%H-%M-%S_PySimlink_Generation_Error.log"),
            )
            with open(err_file, "w", encoding="utf-8") as f:
                f.write(output1.decode() if output1 else "")
                f.write(err1.decode() if err1 else "")
            raise GenerationError(
                err_file, os.path.join(self.model_paths.tmp_dir, "CMakeLists.txt")
            )

        with Popen(
            [os.path.join(cmake.CMAKE_BIN_DIR, "cmake"), "--build", build_dir],
            stdout=PIPE,
            stderr=PIPE,
        ) as p:
            (output2, err2) = p.communicate()
            make = p.wait()

        if make != 0:
            now = datetime.now()
            err_file = os.path.join(
                os.getcwd(),
                now.strftime("%Y-%m-%d_%H-%M-%S_PySimlink_Build_Error.log"),
            )
            with open(err_file, "w", encoding="utf-8") as f:
                f.write(output2.decode() if output2 else "")
                f.write(err2.decode() if err2 else "")

            raise BuildError(err_file, os.path.join(self.model_paths.tmp_dir, "CMakeLists.txt"))

    @staticmethod
    def _replace_macros(path: str, replacements: "dict[str, str]"):
        """
        Replaces strings in a file

        Args:
            path: path to file to replace strings in
            replacements: dictionary of replacements

        """
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        for i, line in enumerate(lines):
            for key, val in replacements.items():
                lines[i] = lines[i].replace(str(key), str(val))

        with open(path, "w", encoding="utf-8") as f:
            f.writelines(lines)
