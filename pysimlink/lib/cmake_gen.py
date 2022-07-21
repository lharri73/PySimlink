import os
import glob

import pybind11


class CmakeTemplate:
    """
    Generates the CMakeLists.txt file that can be used to compile the model.

    The generated cmakelists.txt includes custom mixins and pybind bindings that
    allow a model to be imported in python.
    """

    def __init__(self, model_name):
        self.model_name = model_name
        self.space_trans = str.maketrans({" ": r"\ "})
        self.libs = []

    def header(self):
        """
        Create the header of the CMakeLists.txt

        Returns:
            str: header section for cmake
        """
        return f"""cmake_minimum_required(VERSION 3.4)
project({self.model_name})
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
find_package(pybind11 PATHS {pybind11.get_cmake_dir()})"""

    def set_includes(self, includes: list[str]):
        """
        Setup the includes directories for the model, custom mixins, and simulink files

        Args:
            includes: list of all include paths.

        Returns:
            str: include_directories directive
        """
        ## Add the include path for model runner code

        includes = [os.path.abspath(include).translate(self.space_trans) for include in includes]
        include_dirs = "\n    ".join(includes)
        return f"""
include_directories(
    {include_dirs}
    ${{pybind11_INCLUDE_DIRS}}
    #${{PYTHON_INCLUDE_DIRS}}
)
"""

    def add_library(self, lib_name: str, sources: list[str]):
        """
        Add a single library to be compiled

        Args:
            lib_name: Name of the library
            sources: list of all source files to compile into this library

        Returns:
            str: add_library cmake directive
        """
        self.libs.append(lib_name)
        sources = [os.path.abspath(source).translate(self.space_trans) for source in sources]
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

    def add_custom_libs(self, sources: list[str]):
        """
        Add the mixins library (created with pybind11)

        Args:
            sources: list of all source files part of the library

        Returns:
            str: pybind11_add_module cmake directive
        """
        sources = glob.glob(sources + "/*.cpp")
        sources = [os.path.abspath(source).translate(self.space_trans) for source in sources]
        source_paths = "\n        ".join(sources)
        return f"""
pybind11_add_module(
    model_interface_c
        {source_paths}
)        
"""

    def add_link_libs(self, dep_map: dict[str, list[str]]):
        """
        Link libraries according to the dependency map

        Args:
            dep_map: dictionary from the dependency_graph class

        Returns:
            str: all required target_link_libraries cmake directives
        """
        ret = ""
        for dep, deps in dep_map.items():
            if len(deps) == 0:
                continue
            deps_exp = "\n        ".join(deps)
            ret += f"""
target_link_libraries(
    {dep}
        {deps_exp}
)
"""
        return ret

    def add_private_link(self, root_model: str):
        """
        Link the custom mixins to the root model

        Args:
            root_model: name of the root model

        Returns:
            str: target_link_libraries directive, but as private link
        """
        return f"""
target_link_libraries(
    model_interface_c
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
set(CMAKE_CXX_FLAGS "${{CMAKE_CXX_FLAGS}} -fPIC")
set(CMAKE_C_FLAGS "${{CMAKE_C_FLAGS}} -fPIC")
"""

    def add_compile_defs(self, defines: list[str]):
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
