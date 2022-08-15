//
// Created by landon on 10/24/21.
//
#pragma once
extern "C"{
#include "<<ROOT_MODEL>>"
#include "rtw_capi.h"
#include "rtw_modelmap_logging.h"
#include "rtw_matlogging.h"
#include "rtw_modelmap.h"
}
#include <sstream>
#include <stdexcept>
#include <unordered_map>
#include <vector>
#include "pybind11/pybind11.h"
#include "pybind11/numpy.h"
#include "pybind11/stl.h"

#include "containers.hpp"
#include "safe_utils.hpp"

namespace py = pybind11;

namespace PYSIMLINK{

    const std::map<std::string,std::string> c_python_dtypes = {
            {"char", "int8"},
            {"unsigned char", "uint8"},
            {"short", "int16"},
            {"unsigned short", "uint16"},
            {"int", "int32"},
            {"unsigned int", "uint32"},
            {"float", "float32"},
            {"double", "float64"}
    };

    std::string translate_c_type_name(const std::string& c_name, bool should_throw=false);

    py::buffer_info get_model_param(const rtwCAPI_ModelMappingInfo *mmi, const char *param, std::unordered_map<map_key_1s,size_t,pair_hash,Compare> &model_params);
    void set_model_param(const rtwCAPI_ModelMappingInfo *mmi,
                         const char* param,
                         py::array value);

    py::buffer_info get_block_param(const rtwCAPI_ModelMappingInfo *mmi, const char *block, const char *param, std::unordered_map<map_key_2s,size_t,pair_hash,Compare> &block_map);
    void set_block_param(const rtwCAPI_ModelMappingInfo *mmi,
                         const char *block,
                         const char *param,
                         py::array value);

    py::buffer_info get_signal_val(const rtwCAPI_ModelMappingInfo *mmi, std::unordered_map<map_key_2s,size_t,pair_hash,Compare> &sig_map, const char* block=nullptr, const char* signNam=nullptr);

    py::buffer_info
    format_pybuffer(const rtwCAPI_ModelMappingInfo *mmi, rtwCAPI_DataTypeMap dt, rtwCAPI_DimensionMap sigDim, void *addr);
    void fill_from_buffer(const rtwCAPI_ModelMappingInfo *mmi, rtwCAPI_DataTypeMap dt, rtwCAPI_DimensionMap blockDim, void* addr, py::array value);

    struct PYSIMLINK::DataType describe_block_param(const rtwCAPI_ModelMappingInfo *mmi, const char *block_path, const char *param);
    struct PYSIMLINK::DataType describe_model_param(const rtwCAPI_ModelMappingInfo *mmi, const char *param);

    std::vector<struct PYSIMLINK::ModelParam> debug_model_params(const rtwCAPI_ModelMappingInfo *mmi);
    std::vector<struct PYSIMLINK::BlockParam> debug_block_param(const rtwCAPI_ModelMappingInfo *mmi);
    std::vector<struct PYSIMLINK::Signal> debug_signals(const rtwCAPI_ModelMappingInfo *mmi);
    PYSIMLINK::ModelInfo debug_model_info(const rtwCAPI_ModelMappingInfo *mmi);


    template <typename T>
    void validate_scalar(const rtwCAPI_ModelMappingInfo *mmi, T param, const char* funcName, const char* identifier){
        rtwCAPI_DimensionMap sigDim = mmi->staticMap->Maps.dimensionMap[param.dimIndex];
        rtwCAPI_DataTypeMap dt = mmi->staticMap->Maps.dataTypeMap[param.dataTypeIndex];

        if(sigDim.orientation != rtwCAPI_Orientation::rtwCAPI_SCALAR){
            std::stringstream err("");
            err << funcName << ": signal (" << identifier << ") has too many dimensions(" << (int)sigDim.numDims;
            err << ") or is not a scalar(" << sigDim.orientation << ")";
            throw std::runtime_error(err.str().c_str());
        }
        if(dt.isPointer){
            std::stringstream err("");
            err << funcName << ": Cannot read value from pointer (isPointer=True) for parameter (" << identifier << ")";
            throw std::runtime_error(err.str().c_str());
        }
    }
    template <typename T>
    struct DataType populate_dtype(const rtwCAPI_ModelMappingInfo *mmi, T capi_struct){
        struct DataType ret;
        ret.cDataType = rtwCAPI_GetDataTypeMap(mmi)[capi_struct.dataTypeIndex].cDataName;
        ret.pythonType = PYSIMLINK::translate_c_type_name(ret.cDataType);
        ret.orientation = rtwCAPI_GetDimensionMap(mmi)[capi_struct.dimIndex].orientation;
        for(size_t j = 0; j < rtwCAPI_GetDimensionMap(mmi)[capi_struct.dimIndex].numDims; j++){
            ret.dims.push_back(rtwCAPI_GetDimensionArray(mmi)[rtwCAPI_GetDimensionMap(mmi)[capi_struct.dimIndex].dimArrayIndex + j]);
        }
        return ret;
    }
};
