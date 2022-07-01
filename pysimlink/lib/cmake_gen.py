import pybind11

class cmake_template:
    def __init__(self):
        pass

    def header(self, model_name):
        return f"""cmake_minimum_required(VERSION 3.4)
project({model_name})
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
find_package(pybind11 {pybind11.get_cmake_dir()})"""
#find_package(Python3 REQUIRED)"""


    def set_includes(self, includes):
        trans = str.maketrans({' ': r'\ '})
        includes = [include.translate(trans) for include in includes]
        include_dirs = '\n        '.join(includes)
        return f"""
set(
    includes
        {include_dirs}
        src/extern/include
        src/extern/src
        ${{pybind11_INCLUDE_DIR}}
        #${{PYTHON_INCLUDE_DIRS}}
)
"""

"""
set(
    pid_includes
        src/pid/MATLAB/rtw/c/src
        src/pid/MATLAB/rtw/c/src/ext_mode/common
        src/pid/MATLAB/simulink/include
        src/pid/MATLAB/extern/include
        src/pid/Model/slprj/grt/_sharedutils
        src/pid/Model/Blazer_MiL_Model_PID_grt_rtw
        src/pid/Model/slprj/grt/Blazer_Plant_Model
        src/pid/Model/slprj/grt/SiEngineController
        src/pid/Model/slprj/grt/SiMappedEngine
        src/pid/Model/slprj/grt/TransmissionController
        src/pid/Model/slprj/grt/DrivetrainHevP4
        src/pid/Model/slprj/grt/BattHev
        src/pid/Model/slprj/grt/MotMapped
        src/pid/Model/slprj/grt/StarterSystemP2
        src/pid/Model/slprj/grt/PID_HSC_Model
        src/extern/include
        src/extern/src
        ${pybind11_INCLUDE_DIR}
        ${PYTHON_INCLUDE_DIRS}
)

## Get's all of the matlab source files (all are c),
#  GLOB is usually bad practice, but here it's codegen so the number of files could change
file(GLOB shared_utils_RL_SRCS src/rl/Model/slprj/grt/_sharedutils/*.c)
file(GLOB rtw_RL_SRCS src/rl/MATLAB/rtw/c/src/*.c)
file(GLOB Blazer_MiL_Model_RL_SRCS src/rl/Model/Blazer_MiL_Model_grt_rtw/*.c)
file(GLOB Blazer_Plant_Model_RL_SRCS src/rl/Model/slprj/grt/Blazer_Plant_Model/*.c)
file(GLOB SiEngineController_RL_SRCS src/rl/Model/slprj/grt/SiEngineController/*.c)
file(GLOB SiMappedEngine_RL_SRCS src/rl/Model/slprj/grt/SiMappedEngine/*.c)
file(GLOB TransmissionController_RL_SRCS src/rl/Model/slprj/grt/TransmissionController/*.c)
file(GLOB DrivetrainHevP4_RL_SRCS src/rl/Model/slprj/grt/DrivetrainHevP4/*.c)
file(GLOB BattHev_RL_SRCS src/rl/Model/slprj/grt/BattHev/*.c)
file(GLOB MotMapped_RL_SRCS src/rl/Model/slprj/grt/MotMapped/*.c)
file(GLOB StarterSystemP2_RL_SRCS src/rl/Model/slprj/grt/StarterSystemP2/*.c)
file(GLOB HSC_Model_RL_SRCS src/rl/Model/slprj/grt/HSC_Model/*.c)
file(GLOB shared_utils_PID_SRCS src/pid/Model/slprj/grt/_sharedutils/*.c)
file(GLOB rtw_PID_SRCS src/pid/MATLAB/rtw/c/src/*.c)
file(GLOB Blazer_MiL_Model_PID_SRCS src/pid/Model/Blazer_MiL_Model_PID_grt_rtw/*.c)
file(GLOB Blazer_Plant_Model_PID_SRCS src/pid/Model/slprj/grt/Blazer_Plant_Model/*.c)
file(GLOB SiEngineController_PID_SRCS src/pid/Model/slprj/grt/SiEngineController/*.c)
file(GLOB SiMappedEngine_PID_SRCS src/pid/Model/slprj/grt/SiMappedEngine/*.c)
file(GLOB TransmissionController_PID_SRCS src/pid/Model/slprj/grt/TransmissionController/*.c)
file(GLOB DrivetrainHevP4_PID_SRCS src/pid/Model/slprj/grt/DrivetrainHevP4/*.c)
file(GLOB BattHev_PID_SRCS src/pid/Model/slprj/grt/BattHev/*.c)
file(GLOB MotMapped_PID_SRCS src/pid/Model/slprj/grt/MotMapped/*.c)
file(GLOB StarterSystemP2_PID_SRCS src/pid/Model/slprj/grt/StarterSystemP2/*.c)
file(GLOB HSC_Model_PID_SRCS src/pid/Model/slprj/grt/PID_HSC_Model/*.c)
#

## Each model (even reference) must be linked to the main binary. 
#  creating each model as a library is just easy for organization.
add_library(sharedUtils_PID STATIC ${shared_utils_PID_SRCS})
add_library(rtw_PID STATIC ${rtw_PID_SRCS})
add_library(Blazer_Plant_Model_PID STATIC ${Blazer_Plant_Model_PID_SRCS})
add_library(SiEngineController_PID STATIC ${SiEngineController_PID_SRCS})
add_library(SiMappedEngine_PID STATIC ${SiMappedEngine_PID_SRCS})
add_library(TransmissionController_PID STATIC ${TransmissionController_PID_SRCS})
add_library(DrivetrainHevP4_PID STATIC ${DrivetrainHevP4_PID_SRCS})
add_library(BattHev_PID STATIC ${BattHev_PID_SRCS})
add_library(MotMapped_PID STATIC ${MotMapped_PID_SRCS})
add_library(StarterSystemP2_PID STATIC ${StarterSystemP2_PID_SRCS})
add_library(HSC_Model_PID STATIC ${HSC_Model_PID_SRCS})
add_library(Blazer_MiL_Model_PID STATIC ${Blazer_MiL_Model_PID_SRCS})
add_library(sharedUtils_RL STATIC ${shared_utils_RL_SRCS})
add_library(rtw_RL STATIC ${rtw_RL_SRCS})
add_library(Blazer_Plant_Model_RL STATIC ${Blazer_Plant_Model_RL_SRCS})
add_library(SiEngineController_RL STATIC ${SiEngineController_RL_SRCS})
add_library(SiMappedEngine_RL STATIC ${SiMappedEngine_RL_SRCS})
add_library(TransmissionController_RL STATIC ${TransmissionController_RL_SRCS})
add_library(DrivetrainHevP4_RL STATIC ${DrivetrainHevP4_RL_SRCS})
add_library(BattHev_RL STATIC ${BattHev_RL_SRCS})
add_library(MotMapped_RL STATIC ${MotMapped_RL_SRCS})
add_library(StarterSystemP2_RL STATIC ${StarterSystemP2_RL_SRCS})
add_library(HSC_Model_RL STATIC ${HSC_Model_RL_SRCS})
add_library(Blazer_MiL_Model_RL STATIC ${Blazer_MiL_Model_RL_SRCS})
target_include_directories(sharedUtils_RL PRIVATE ${rl_includes})
target_include_directories(rtw_RL PRIVATE ${rl_includes})
target_include_directories(Blazer_Plant_Model_RL PRIVATE ${rl_includes})
target_include_directories(SiEngineController_RL PRIVATE ${rl_includes})
target_include_directories(SiMappedEngine_RL PRIVATE ${rl_includes})
target_include_directories(TransmissionController_RL PRIVATE ${rl_includes})
target_include_directories(DrivetrainHevP4_RL PRIVATE ${rl_includes})
target_include_directories(BattHev_RL PRIVATE ${rl_includes})
target_include_directories(MotMapped_RL PRIVATE ${rl_includes})
target_include_directories(StarterSystemP2_RL PRIVATE ${rl_includes})
target_include_directories(HSC_Model_RL PRIVATE ${rl_includes})
target_include_directories(Blazer_MiL_Model_RL PRIVATE ${rl_includes})
target_include_directories(sharedUtils_PID PRIVATE ${pid_includes})
target_include_directories(rtw_PID PRIVATE ${pid_includes})
target_include_directories(Blazer_Plant_Model_PID PRIVATE ${pid_includes})
target_include_directories(SiEngineController_PID PRIVATE ${pid_includes})
target_include_directories(SiMappedEngine_PID PRIVATE ${pid_includes})
target_include_directories(TransmissionController_PID PRIVATE ${pid_includes})
target_include_directories(DrivetrainHevP4_PID PRIVATE ${pid_includes})
target_include_directories(BattHev_PID PRIVATE ${pid_includes})
target_include_directories(MotMapped_PID PRIVATE ${pid_includes})
target_include_directories(StarterSystemP2_PID PRIVATE ${pid_includes})
target_include_directories(HSC_Model_PID PRIVATE ${pid_includes})
target_include_directories(Blazer_MiL_Model_PID PRIVATE ${pid_includes})

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
