import os
import glob
import re

import pybind11


from pysimlink.utils.model_utils import sanitize_model_name


class CmakeTemplate:
    """
    Generates the CMakeLists.txt file that can be used to compile the model.

    The generated cmakelists.txt includes custom mixins and pybind bindings that
    allow a model to be imported in python.
    """

    def __init__(self, model_name):
        self.model_name = model_name
        self.libs = []
        self.replacers = [(re.compile(r"(?<!\\) "), r"\ "), (re.compile(r"\\(?! )"), r"/")]

        self.sanitized_name = sanitize_model_name(model_name)

    def replacer(self, string):
        for search, rep in self.replacers:
            indices = list(re.finditer(search, string))
            for idx in reversed(indices):
                string = string[: idx.start(0)] + rep + string[idx.end(0) :]
        return string

    def header(self):
        """
        Create the header of the CMakeLists.txt

        Returns:
            str: header section for cmake
        """
        return f"""cmake_minimum_required(VERSION 3.5)
project({self.model_name})
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
find_package(pybind11 PATHS {self.replacer(pybind11.get_cmake_dir())})"""

    def set_includes(self, includes: "list[str]"):
        """
        Setup the includes directories for the model, custom mixins, and simulink files

        Args:
            includes: list of all include paths.

        Returns:
            str: include_directories directive
        """
        ## Add the include path for model runner code

        includes = [self.replacer(os.path.abspath(include)) for include in includes]
        include_dirs = "\n    ".join(includes)
        return f"""
include_directories(
    {include_dirs}
    ${{pybind11_INCLUDE_DIRS}}
    #${{PYTHON_INCLUDE_DIRS}}
)
"""

    def add_library(self, lib_name: str, sources: "list[str]"):
        """
        Add a single library to be compiled

        Args:
            lib_name: Name of the library
            sources: list of all source files to compile into this library

        Returns:
            str: add_library cmake directive
        """
        self.libs.append(lib_name)
        sources = [self.replacer(os.path.abspath(source)) for source in sources]
        source_paths = "\n        ".join(sources)
        return f"""
add_library(
    {lib_name}
        {source_paths}
)        
"""

    def set_lib_props(self):
        """
        Set all models to be compiled with c 90

        This is usually fine, even if the model was generated to use c89. Not the other way around though.

        Returns:
            str: set_target_properties cmake directive
        """
        libs = "\n    ".join(self.libs)
        return f"""
set_target_properties(
    {libs}
        PROPERTIES C_STANDARD 90
)        
"""

    def add_custom_libs(self, sources: "list[str]"):
        """
        Add the mixins library (created with pybind11)

        Args:
            sources: list of all source files part of the library

        Returns:
            str: pybind11_add_module cmake directive
        """
        sources = glob.glob(sources + "/*.cpp")

        sources = [self.replacer(os.path.abspath(source)) for source in sources]
        source_paths = "\n        ".join(sources)
        return f"""
pybind11_add_module(
    {self.sanitized_name}_interface_c
        {source_paths}
)        

set_target_properties(
    {self.sanitized_name}_interface_c PROPERTIES
        LIBRARY_OUTPUT_DIRECTORY ${{PROJECT_BINARY_DIR}}/out/library
)
"""

    def add_link_libs(self, dep_map: "dict[str, set[str]]"):
        """
        Link libraries according to the dependency map

        Args:
            dep_map: dictionary from the dependency_graph class

        Returns:
            str: all required target_link_libraries cmake directives
        """
        ret = ""
        for dep, deps in dep_map.items():
            deps = list(deps)
            if len(deps) == 0:
                continue
            if "math" in deps:
                midx = deps.index("math")
                if os.name == 'nt':
                    del deps[midx]
                else:
                    deps[midx] = "m"
            deps_exp = "\n        ".join(deps)
            ret += f"""
target_link_libraries(
    {dep}
        {deps_exp}
)
"""
        return ret

    def add_private_link(self, root_model: "str"):
        """
        Link the custom mixins to the root model

        Args:
            root_model: name of the root model

        Returns:
            str: target_link_libraries directive, but as private link
        """
        return f"""
target_link_libraries(
    {self.sanitized_name}_interface_c
        PRIVATE {root_model}
)        
"""

    def footer(self):
        """
        Set position independent code flag for all targets

        Returns:
            str: set directives for all targets
        """
        return """
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fPIC")
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -fPIC")
"""

    def add_compile_defs(self, defines: "list[str]"):
        """
        Set compile definitions from defines.txt or inference

        Args:
            defines: list of defines added to cmake

        Returns:
            str: add_compile_definitions cmake directive
        """
        defines = "\n    ".join(defines)
        return f"""
add_compile_definitions(
    {defines}
)        
"""
