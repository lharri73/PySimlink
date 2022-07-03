import pybind11
import os
import glob

class cmake_template:
    def __init__(self, model_name):
        self.model_name = model_name
        self.space_trans = str.maketrans({' ': r'\ '})
        self.libs = []

    def header(self):
        return f"""cmake_minimum_required(VERSION 3.4)
project({self.model_name})
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
find_package(pybind11 PATHS {pybind11.get_cmake_dir()})"""
#find_package(Python3 REQUIRED)"""


    def set_includes(self, includes):
        ## Add the include path for model runner code

        includes = [include.translate(self.space_trans) for include in includes]
        include_dirs = '\n    '.join(includes)
        return f"""
include_directories(
    {include_dirs}
    ${{pybind11_INCLUDE_DIRS}}
    #${{PYTHON_INCLUDE_DIRS}}
)
"""

    def add_library(self, lib_name, sources):
        self.libs.append(lib_name)
        sources = [source.translate(self.space_trans) for source in sources]
        source_paths = '\n        '.join(sources)
        return f"""
add_library(
    {lib_name}
        {source_paths}
)        
"""

    def set_lib_props(self):
        libs = '\n    '.join(self.libs)
        return f"""
set_target_properties(
    {libs}
        PROPERTIES C_STANDARD 90
)        
"""

    def add_custom_libs(self, sources):
        sources = glob.glob(sources + "/*.cpp")
        sources = [source.translate(self.space_trans) for source in sources]
        source_paths = '\n        '.join(sources)
        return f"""
add_library(
    model_interface_c SHARED
        {source_paths}
)        
"""

    def add_link_libs(self, dep_map):
        ret = ""
        for dep, deps in dep_map.items():
            if len(deps) == 0: continue
            deps_exp = '\n        '.join(deps)
            ret += f"""
target_link_libraries(
    {dep}
        {deps_exp}
)
"""
        return ret

    def footer(self):
        return f"""
set(CMAKE_CXX_FLAGS "${{CMAKE_CXX_FLAGS}} -fPIC")
set(CMAKE_C_FLAGS "${{CMAKE_C_FLAGS}} -fPIC")
"""

    def add_compile_defs(self, defines):
        defines = '\n    '.join(defines)
        return f"""
add_compile_definitions(
    {defines}
)        
"""
