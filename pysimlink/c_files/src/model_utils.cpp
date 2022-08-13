//
// Created by landon on 10/24/21.
//
#include "model_utils.hpp"
#include <cstring>
#include <memory>
#include <sstream>
#include <unordered_map>
#include <string>
#include <utility>
#include <tuple>
#include <cassert>

double PYSIMLINK::get_model_param(const rtwCAPI_ModelMappingInfo *mmi, const char *param,
                                  std::unordered_map<map_key_1s, size_t, pair_hash, Compare> &param_map) {
    if (param == nullptr)
        throw std::runtime_error("passed nullptr to get_model_param as search param");

    const rtwCAPI_ModelParameters *capiModelParams = rtwCAPI_GetModelParameters(mmi);


    int param_index = -1;
    std::unordered_map<map_key_1s, size_t, pair_hash, Compare>::const_iterator it;
    map_key_1s key{std::string(param), mmi};
    it = param_map.find(key);
    if (it == param_map.end()) {
        uint_T nParams = rtwCAPI_GetNumModelParameters(mmi);
        for (size_t i = 0; i < nParams; i++) {
            if (strcmp(capiModelParams[i].varName, param) == 0) {
                // correct param
                param_index = i;
                //std::string tmp = param;
                param_map[key] = i;
                break;
            }
        }
    } else {
        param_index = it->second;
    }

    if (param_index == -1) {
        // never found the parameter
        std::stringstream err("");
        err << "get_model_param: Parameter (" << param << ") does not exist in mmi";
        throw std::runtime_error(err.str().c_str());

        return 0;
    }

    validate_scalar(mmi, capiModelParams[param_index], "get_model_param", param);
    rtwCAPI_DataTypeMap dt = mmi->staticMap->Maps.dataTypeMap[rtwCAPI_GetModelParameterDataTypeIdx(capiModelParams,
                                                                                                   param_index)];
    void *addr = mmi->InstanceMap.dataAddrMap[rtwCAPI_GetModelParameterAddrIdx(capiModelParams, param_index)];
    double ret;
    if (strcmp(dt.cDataName, "int") == 0) {
        int tmp = *(int *) addr;
        ret = tmp;
    } else if (strcmp(dt.cDataName, "float") == 0) {
        float tmp = *(float *) addr;
        ret = tmp;
    } else if (strcmp(dt.cDataName, "double") == 0) {
        ret = *(double *) addr;
    } else {
        std::stringstream err("");
        err << "get_model_param: Parameter (" << param << ") has invalid cDataName(" << dt.cDataName;
        err << "). Can only handle [int,float,double]";
        throw std::runtime_error(err.str().c_str());
    }
    return ret;
}

py::buffer_info PYSIMLINK::get_block_param(const rtwCAPI_ModelMappingInfo *mmi, const char *block, const char *param,
                                           std::unordered_map<map_key_2s, size_t, pair_hash, Compare> &param_map) {
    std::unordered_map<map_key_2s, size_t, pair_hash, Compare>::const_iterator it;
    int param_iter = -1;

    const rtwCAPI_BlockParameters *capiBlockParameters = rtwCAPI_GetBlockParameters(mmi);
    uint_T nParams = rtwCAPI_GetNumBlockParameters(mmi);
    std::string first(block == nullptr ? "" : block);
    std::string second(param == nullptr ? "" : param);
    map_key_2s key{first, second, mmi};
    it = param_map.find(key);
    if (it == param_map.end()) {
        for (size_t i = 0; i < nParams; i++) {
            if (strcmp(block, capiBlockParameters[i].blockPath) == 0 &&
                strcmp(param, capiBlockParameters[i].paramName) == 0) {
                // correct param
                param_map[key] = i;
                param_iter = i;
                break;
            }
        }
    } else {
        param_iter = it->second;
    }

    if (param_iter == -1) {
        std::stringstream err("");
        err << "get_block_param: Parameter (" << block << ',' << param << ") does not exist in mmi";
        throw std::runtime_error(err.str().c_str());
    }

    rtwCAPI_DataTypeMap dt = mmi->staticMap->Maps.dataTypeMap[rtwCAPI_GetBlockParameterDataTypeIdx(capiBlockParameters,
                                                                                                   param_iter)];
    rtwCAPI_DimensionMap sigDim = rtwCAPI_GetDimensionMap(mmi)[rtwCAPI_GetBlockParameterDimensionIdx(
            capiBlockParameters, param_iter)];
    void *addr = mmi->InstanceMap.dataAddrMap[rtwCAPI_GetBlockParameterAddrIdx(capiBlockParameters, param_iter)];
    return PYSIMLINK::format_pybuffer(mmi, dt, sigDim, addr);
}

py::buffer_info PYSIMLINK::get_signal_val(const rtwCAPI_ModelMappingInfo *mmi,
                                          std::unordered_map<map_key_2s, size_t, pair_hash, Compare> &sig_map,
                                          const char *block, const char *sigName) {
    assert(mmi != nullptr);
    std::unordered_map<map_key_2s, size_t, pair_hash, Compare>::const_iterator it;

    if (block == nullptr && sigName == nullptr)
        throw std::runtime_error("get_signal_val: Must specify signal name or origin block to search for signal");
//    if(block == nullptr){
//        fprintf(stderr, "Warning: Searching for signal by signal name only. Signal names are not guaranteed unique!\n");
//    }

    uint_T numSigs = rtwCAPI_GetNumSignals(mmi);
    const rtwCAPI_Signals *capiSignals = rtwCAPI_GetSignals(mmi);

    int param_index = -1;

    std::string first(block == nullptr ? "" : block);
    std::string second(sigName == nullptr ? "" : sigName);
    map_key_2s key{first, second, mmi};
    it = sig_map.find(key);
    if (it == sig_map.end()) {

        for (size_t i = 0; i < numSigs; i++) {
            if ((sigName == nullptr && strcmp(block, rtwCAPI_GetSignalBlockPath(capiSignals, i)) == 0) ||
                (block == nullptr && strcmp(sigName, rtwCAPI_GetSignalName(capiSignals, i)) == 0) ||
                ((sigName != nullptr && block != nullptr) &&
                 (strcmp(rtwCAPI_GetSignalName(capiSignals, i), sigName) == 0 && strcmp(
                         rtwCAPI_GetSignalBlockPath(capiSignals, i), block) == 0))) {
                // signal match
                sig_map[key] = i;
                param_index = i;
                break;
            }
        }
    } else {
        param_index = it->second;
    }

    if (param_index == -1) {
        std::stringstream err("");
        err << "get_signal_val: Parameter (" << block << ',' << (sigName == nullptr ? "" : sigName)
            << ") does not exist in provided model";
        throw std::runtime_error(err.str().c_str());
    }


    rtwCAPI_DataTypeMap dt = rtwCAPI_GetDataTypeMap(mmi)[rtwCAPI_GetSignalDataTypeIdx(capiSignals, param_index)];
    rtwCAPI_DimensionMap sigDim = rtwCAPI_GetDimensionMap(mmi)[rtwCAPI_GetSignalDimensionIdx(capiSignals, param_index)];
    void *addr = rtwCAPI_GetDataAddressMap(mmi)[rtwCAPI_GetSignalAddrIdx(capiSignals, param_index)];
    return PYSIMLINK::format_pybuffer(mmi, dt, sigDim, addr);
}

py::buffer_info
PYSIMLINK::format_pybuffer(const rtwCAPI_ModelMappingInfo *mmi, rtwCAPI_DataTypeMap dt, rtwCAPI_DimensionMap sigDim,
                           void *addr) {
    py::buffer_info ret;
    ret.ptr = addr;
    ret.itemsize = dt.dataSize;

    if (strcmp(dt.cDataName, "int") == 0) {
        ret.format = py::format_descriptor<int>::format();
    } else if (strcmp(dt.cDataName, "float") == 0) {
        ret.format = py::format_descriptor<float>::format();
    } else if (strcmp(dt.cDataName, "double") == 0) {
        ret.format = py::format_descriptor<double>::format();
    } else if (strcmp(dt.cDataName, "char") == 0) {
        ret.format = py::format_descriptor<char>::format();
    } else if (strcmp(dt.cDataName, "short") == 0) {
        ret.format = py::format_descriptor<short>::format();
    } else if (strcmp(dt.cDataName, "unsigned short") == 0) {
        ret.format = py::format_descriptor<unsigned short>::format();
    } else if (strcmp(dt.cDataName, "long") == 0) {
        ret.format = py::format_descriptor<long>::format();
    } else if (strcmp(dt.cDataName, "unsigned int") == 0) {
        ret.format = py::format_descriptor<unsigned int>::format();
    } else if (strcmp(dt.cDataName, "unsigned long") == 0) {
        ret.format = py::format_descriptor<unsigned long>::format();
    } else {
        std::stringstream err("");
        err << "Parameter ( has invalid cDataName(" << dt.cDataName << ") (internal error)";
        throw std::runtime_error(err.str().c_str());
    }
    ret.ndim = sigDim.numDims;
    if (ret.ndim > 3) {
        throw std::runtime_error(
                "Cannot return values with more than 3 dimensions...yet. Fix the issue and open a pull request!");
    }
    for (size_t i = 0; i < ret.ndim; i++) {
        ssize_t dim_size = rtwCAPI_GetDimensionArray(mmi)[sigDim.dimArrayIndex + i];
        ret.shape.push_back(dim_size);
        switch (sigDim.orientation) {
            case rtwCAPI_Orientation::rtwCAPI_SCALAR:
            case rtwCAPI_Orientation::rtwCAPI_VECTOR:
                ret.strides.push_back(dt.dataSize);
                break;
            case rtwCAPI_Orientation::rtwCAPI_MATRIX_COL_MAJOR:
                if (i == 1)
                    ret.strides.push_back(dt.dataSize * dim_size);
                else
                    ret.strides.push_back(dt.dataSize);
                break;
            case rtwCAPI_Orientation::rtwCAPI_MATRIX_COL_MAJOR_ND:
                // this does not generalize beyond 3 dimensions
                if (i == 0)
                    ret.strides.push_back(dt.dataSize * rtwCAPI_GetDimensionArray(mmi)[sigDim.dimArrayIndex + 1] *
                                          rtwCAPI_GetDimensionArray(mmi)[sigDim.dimArrayIndex + 2]);
                else if (i == 1)
                    ret.strides.push_back(dt.dataSize);
                else
                    ret.strides.push_back(dt.dataSize * dim_size);
                break;
            case rtwCAPI_Orientation::rtwCAPI_MATRIX_ROW_MAJOR:
                if (i == 0)
                    ret.strides.push_back(dt.dataSize * dim_size);
                else
                    ret.strides.push_back(dt.dataSize);
                break;
            case rtwCAPI_Orientation::rtwCAPI_MATRIX_ROW_MAJOR_ND:
                throw std::runtime_error(
                        "ND matrices not supported in row major orientation. Use column major for 3-dim matrices");
                break;
            default:
                throw std::runtime_error("Invalid/Unknown orientation for parameter (internal error)");
        }
    }
    ret.readonly = true;
    return ret;
}

void PYSIMLINK::set_block_param(const rtwCAPI_ModelMappingInfo *mmi, const char *block, const char *param, py::array value) {
    // TODO: cache the param index here
    const rtwCAPI_BlockParameters *capiBlockParameters = rtwCAPI_GetBlockParameters(mmi);
    uint_T nParams = rtwCAPI_GetNumBlockParameters(mmi);
    for (size_t i = 0; i < nParams; i++) {
        if (strcmp(block, capiBlockParameters[i].blockPath) == 0 &&
            strcmp(param, capiBlockParameters[i].paramName) == 0) {
//            validate_scalar(mmi, capiBlockParameters[i], "set_block_parameter", block);

            rtwCAPI_DataTypeMap dt = rtwCAPI_GetDataTypeMap(mmi)[rtwCAPI_GetBlockParameterDataTypeIdx(
                    capiBlockParameters, i)];
            rtwCAPI_DimensionMap blockDim = rtwCAPI_GetDimensionMap(mmi)[rtwCAPI_GetBlockParameterDimensionIdx(
                    capiBlockParameters, i)];
            void *addr = rtwCAPI_GetDataAddressMap(mmi)[rtwCAPI_GetBlockParameterAddrIdx(capiBlockParameters, i)];

            PYSIMLINK::fill_from_buffer(mmi, dt, blockDim, addr, value);
            return;
        }
    }
    std::stringstream err("");
    err << "set_block_param: Parameter (" << block << ',' << param << ") does not exist in mmi";
    throw std::runtime_error(err.str().c_str());

}

std::vector<struct PYSIMLINK::ModelParam> PYSIMLINK::debug_model_params(const rtwCAPI_ModelMappingInfo *mmi) {
    uint_T numParams = rtwCAPI_GetNumModelParameters(mmi);
    const rtwCAPI_ModelParameters *capiModelParams = rtwCAPI_GetModelParameters(mmi);
    std::vector<struct PYSIMLINK::ModelParam> ret;
    ret.reserve(numParams);
    for (size_t i = 0; i < numParams; i++) {
        struct PYSIMLINK::ModelParam to_add;
        to_add.model_param = capiModelParams[i].varName;
        to_add.data_type = PYSIMLINK::populate_dtype(mmi, capiModelParams[i]);
        ret.push_back(to_add);
    }
    return ret;
}

std::vector<struct PYSIMLINK::BlockParam> PYSIMLINK::debug_block_param(const rtwCAPI_ModelMappingInfo *mmi) {
    const rtwCAPI_BlockParameters *capiBlockParams = rtwCAPI_GetBlockParameters(mmi);
    uint_T nParams = rtwCAPI_GetNumBlockParameters(mmi);
    std::vector<struct PYSIMLINK::BlockParam> ret;
    ret.reserve(nParams);

    for (size_t i = 0; i < nParams; i++) {
        struct PYSIMLINK::BlockParam to_add;
        to_add.block_name = capiBlockParams[i].blockPath;
        to_add.block_param = capiBlockParams[i].paramName;
        to_add.data_type = PYSIMLINK::populate_dtype(mmi, capiBlockParams[i]);
        ret.push_back(to_add);
    }
    return ret;
}

std::vector<struct PYSIMLINK::Signal> PYSIMLINK::debug_signals(const rtwCAPI_ModelMappingInfo *mmi) {
    uint_T numSigs = rtwCAPI_GetNumSignals(mmi);
    const rtwCAPI_Signals *capiSignals = rtwCAPI_GetSignals(mmi);

    std::vector<struct PYSIMLINK::Signal> ret;
    ret.reserve(numSigs);
    for (size_t i = 0; i < numSigs; i++) {
        struct PYSIMLINK::Signal to_add;
        to_add.block_name = PYSIMLINK::safe_string(capiSignals[i].blockPath);
        to_add.signal_name = PYSIMLINK::safe_string(capiSignals[i].signalName);
        to_add.data_type = PYSIMLINK::populate_dtype(mmi, capiSignals[i]);
        ret.push_back(to_add);
    }
    return ret;
}

PYSIMLINK::ModelInfo PYSIMLINK::debug_model_info(const rtwCAPI_ModelMappingInfo *mmi) {
    struct PYSIMLINK::ModelInfo ret;
    ret.model_name = mmi->InstanceMap.path == nullptr ? "root" : std::string(mmi->InstanceMap.path);
    ret.block_params = debug_block_param(mmi);
    ret.model_params = debug_model_params(mmi);
    ret.signals = debug_signals(mmi);

    return ret;
}

void
PYSIMLINK::fill_from_buffer(const rtwCAPI_ModelMappingInfo *mmi, rtwCAPI_DataTypeMap dt, rtwCAPI_DimensionMap blockDim,
                            void *addr, py::array value) {
    // data type check
    std::string dtype_raw = repr(PYBIND11_STR_TYPE(value.dtype()));
    auto cit = PYSIMLINK::c_python_dtypes.find(dt.cDataName);
    if (cit == PYSIMLINK::c_python_dtypes.end()) {
        std::stringstream ss;
        ss << "Unknown C datatype. Not present in datatype map. ";
        ss << "Got " << dt.cDataName;
        throw std::runtime_error(ss.str());
    }

    if (strncmp(cit->second.c_str(), dtype_raw.c_str(), strlen(cit->second.c_str())) == 0 ||
        dt.dataSize != value.itemsize()) {
        std::stringstream ss;
        ss << "Datatype of array does not match datatype of Parameter. ";
        ss << "Expected " << cit->second.c_str() << " got dtype " << dtype_raw.c_str();
        throw std::runtime_error(ss.str());
    }

    // dimension check
    if (blockDim.numDims != value.ndim()) {
        std::stringstream ss;
        ss << "Dimension mismatch. ";
        ss << "Expected " << blockDim.numDims << " got " << value.ndim();
        throw std::runtime_error(ss.str());
    }

    switch (blockDim.orientation) {
        case rtwCAPI_MATRIX_COL_MAJOR_ND:
            if (blockDim.numDims > 3)
                throw std::runtime_error(
                        "Cannot change parameters with more than 3 dimensions...yet. Open a pull request!");
            break;
        case rtwCAPI_MATRIX_ROW_MAJOR_ND:
            throw std::runtime_error("Row major orientation for nd matrices not supported...yet.");
            break;
        default:
            break;
    }

    // perform the actual copy
    memcpy(addr, value.data(), value.nbytes());
}

std::string PYSIMLINK::translate_c_type_name(const std::string& c_name, bool should_throw) {
    auto finder = PYSIMLINK::c_python_dtypes.find(c_name);
    if(finder == PYSIMLINK::c_python_dtypes.end()){
        if(should_throw){
            std::stringstream ss;
            ss << "could not find matching python dtype for " << c_name;
            throw std::runtime_error(ss.str());
        }else{
            return "void";
        }
    }else{
        return finder->second;
    }
}

struct PYSIMLINK::DataType PYSIMLINK::describe_block_param(const rtwCAPI_ModelMappingInfo *mmi, const char *block_path,
                                                           const char *param) {
    const rtwCAPI_BlockParameters *capiBlockParameters = rtwCAPI_GetBlockParameters(mmi);
    uint_T nParams = rtwCAPI_GetNumBlockParameters(mmi);
    for (size_t i = 0; i < nParams; i++) {
        if (strcmp(block_path, capiBlockParameters[i].blockPath) == 0 &&
            strcmp(param, capiBlockParameters[i].paramName) == 0) {
            return PYSIMLINK::populate_dtype(mmi, capiBlockParameters[i]);
        }
    }
}

