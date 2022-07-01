import pybind11

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
        includes = [include.translate(self.space_trans) for include in includes]
        include_dirs = '\n    '.join(includes)
        return f"""
include_directories(
    {include_dirs}
    src/extern/include
    src/extern/src
    ${{pybind11_INCLUDE_DIR}}
    #${{PYTHON_INCLUDE_DIRS}}
)
"""

    def add_library(self, lib_name, sources):
        self.libs.append(lib_name)
        sources = [source.translate(self.space_trans) for source in sources]
        source_paths = '\n    '.join(sources)
        return f"""
add_library({lib_name}
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

"""

set_target_properties(
    sharedUtils_PID 
    rtw_PID 
    Blazer_Plant_Model_PID 
    SiEngineController_PID 
    SiMappedEngine_PID 
    TransmissionController_PID 
    DrivetrainHevP4_PID 
    BattHev_PID 
    MotMapped_PID 
    StarterSystemP2_PID 
    HSC_Model_PID 
    Blazer_MiL_Model_PID 
    sharedUtils_RL 
    rtw_RL 
    Blazer_Plant_Model_RL 
    SiEngineController_RL 
    SiMappedEngine_RL 
    TransmissionController_RL 
    DrivetrainHevP4_RL 
    BattHev_RL 
    MotMapped_RL 
    StarterSystemP2_RL 
    HSC_Model_RL 
    Blazer_MiL_Model_RL 
        PROPERTIES C_STANDARD 90)

pybind11_add_module(
    blazer_model_c
    #src/extern/src/model_interface_common.cpp
        #src/extern/src/model_interface_rl.cpp
        #src/extern/src/model_interface_pid.cpp
        #src/extern/src/model_utils.cpp
        #src/extern/src/hash.cpp
        src/extern/src/bindings.cpp
)
target_include_directories(
    blazer_model_c
        PRIVATE ${rl_includes}
        PRIVATE ${pid_includes}
)
add_library(
    traffic_light STATIC
        src/extern/src/intersection.cpp
)
target_include_directories(traffic_light PRIVATE src/extern/include)

add_library(
    rl_model_interface STATIC
        src/extern/src/model_interface_common.cpp
        src/extern/src/model_interface_rl.cpp
        src/extern/src/model_utils.cpp
        src/extern/src/hash.cpp
)
add_library(
    pid_model_interface STATIC
        src/extern/src/model_interface_common.cpp
        src/extern/src/model_interface_pid.cpp
        src/extern/src/model_utils.cpp
        src/extern/src/hash.cpp
)

target_compile_definitions(rl_model_interface PRIVATE NAMESPACE_PID=RL)
target_compile_definitions(pid_model_interface PRIVATE NAMESPACE_PID=PID PID_INC=1)

target_include_directories(pid_model_interface PRIVATE ${pid_includes})
target_include_directories(rl_model_interface PRIVATE ${rl_includes})

target_link_libraries(traffic_light PRIVATE pybind11::module pybind11::lto)


target_link_libraries(
    Blazer_MiL_Model_RL
        HSC_Model_RL
        Blazer_Plant_Model_RL
        rtw_RL
        sharedUtils_RL
)

target_link_libraries(
    Blazer_MiL_Model_PID
        HSC_Model_PID
        Blazer_Plant_Model_PID
        sharedUtils_PID
        rtw_PID
)

target_link_libraries(
    Blazer_Plant_Model_PID
        StarterSystemP2_PID
        MotMapped_PID
        BattHev_PID
        DrivetrainHevP4_PID
        TransmissionController_PID
        SiMappedEngine_PID
        SiEngineController_PID
)

target_link_libraries(
    Blazer_Plant_Model_RL
        StarterSystemP2_RL
        MotMapped_RL
        BattHev_RL
        DrivetrainHevP4_RL
        TransmissionController_RL
        SiMappedEngine_RL
        SiEngineController_RL
)

target_link_libraries(
    rl_model_interface
        Blazer_MiL_Model_RL
        traffic_light
        #pybind11::module pybind11::lto
)

target_link_libraries(
    pid_model_interface
        Blazer_MiL_Model_PID
        traffic_light
        #pybind11::module pybind11::lto
)


## Must be private because pybind11 already uses the 
#  target_link_libraries command
target_link_libraries(
    blazer_model_c PRIVATE
        rl_model_interface
        pid_model_interface
)


# EXAMPLE_VERSION_INFO is defined by setup.py and passed into the C++ code as a
# define (VERSION_INFO) here.
target_compile_definitions(blazer_model_c PRIVATE VERSION_INFO=${EXAMPLE_VERSION_INFO} NAMESPACE_PID=PID)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fPIC")
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -fPIC")
set_property(TARGET
        blazer_model_c
        rl_model_interface
        pid_model_interface
        traffic_light
    PROPERTY 
        CXX_STANDARD 
        11
)
set(CMAKE_BUILD_TYPE Debug)

"""
