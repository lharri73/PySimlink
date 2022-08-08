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

uint_T PYSIMLINK::get_num_model_params(const rtwCAPI_ModelMappingInfo *mmi){
    return rtwCAPI_GetNumModelParameters(mmi);
}

uint_T PYSIMLINK::get_num_block_params(const rtwCAPI_ModelMappingInfo *mmi) {
    return rtwCAPI_GetNumBlockParameters(mmi);
}

uint_T PYSIMLINK::get_num_signals(const rtwCAPI_ModelMappingInfo *mmi){
    return rtwCAPI_GetNumSignals(mmi);
}

void PYSIMLINK::print_model_params(const rtwCAPI_ModelMappingInfo *mmi){
    uint_T numParams = get_num_model_params(mmi);
    const rtwCAPI_ModelParameters* capiModelParams = rtwCAPI_GetModelParameters(mmi);
    printf("model params for %s\n", mmi->InstanceMap.path);
    for (size_t i=0; i < numParams; i++) {
        printf("\tname: %s\n", capiModelParams[i].varName);
    }
}

void PYSIMLINK::print_block_params(const rtwCAPI_ModelMappingInfo *mmi){
    const rtwCAPI_BlockParameters *capiBlockParams = rtwCAPI_GetBlockParameters(mmi);
    uint_T nParams = get_num_block_params(mmi);
    printf("Block params for %s\n", mmi->InstanceMap.path);
    for (size_t i=0; i < nParams; i++) {
        printf("\tBlock path: %-128s\tparam name: %s\n", capiBlockParams[i].blockPath, capiBlockParams[i].paramName);
    }
}

void PYSIMLINK::print_signals(const rtwCAPI_ModelMappingInfo *mmi){
    uint_T numSigs = get_num_signals(mmi);
    const rtwCAPI_Signals *capiSignals = rtwCAPI_GetSignals(mmi);
    printf("Signals for %s\n", mmi->InstanceMap.path);
    for(size_t i = 0; i < numSigs; i++){
        printf("\tBlock path: %-128s\tsignal_name: %s\n", capiSignals[i].blockPath, capiSignals[i].signalName);
    }
}

double PYSIMLINK::get_model_param(const rtwCAPI_ModelMappingInfo *mmi, const char* param, std::unordered_map<map_key_1s,size_t,pair_hash,Compare> &param_map){
    if(param == nullptr)
        throw std::runtime_error("passed nullptr to get_model_param as search param");

    const rtwCAPI_ModelParameters* capiModelParams = rtwCAPI_GetModelParameters(mmi);


    int param_index = -1;
    std::unordered_map<map_key_1s,size_t,pair_hash,Compare>::const_iterator it;
    map_key_1s key{std::string(param),mmi};
    it = param_map.find(key);
    if(it == param_map.end()){
        uint_T nParams = get_num_model_params(mmi);
        for(size_t i=0; i<nParams; i++){
            if(strcmp(capiModelParams[i].varName, param) == 0){
                // correct param
                param_index = i;
                //std::string tmp = param;
                param_map[key] = i;
                break;
            }
        }
    }else{
        param_index = it->second;
    }

    if(param_index == -1){
        // never found the parameter
        std::stringstream err("");
        err << "get_model_param: Parameter (" << param << ") does not exist in mmi";
        throw std::runtime_error(err.str().c_str());

        return 0;
    }

    validate_scalar(mmi, capiModelParams[param_index], "get_model_param", param);
    rtwCAPI_DataTypeMap dt = mmi->staticMap->Maps.dataTypeMap[rtwCAPI_GetModelParameterDataTypeIdx(capiModelParams, param_index)];
    void* addr = mmi->InstanceMap.dataAddrMap[rtwCAPI_GetModelParameterAddrIdx(capiModelParams, param_index)];
    double ret;
    if(strcmp(dt.cDataName, "int") == 0){
        int tmp = *(int*)addr;
        ret = tmp;
    }else if(strcmp(dt.cDataName, "float") == 0){
        float tmp = *(float*)addr;
        ret = tmp;
    }else if(strcmp(dt.cDataName, "double") == 0){
        ret = *(double*)addr;
    }else{
        std::stringstream err("");
        err << "get_model_param: Parameter (" << param << ") has invalid cDataName(" << dt.cDataName;
        err << "). Can only handle [int,float,double]";
        throw std::runtime_error(err.str().c_str());
    }
    return ret;
}

double PYSIMLINK::get_block_param(const rtwCAPI_ModelMappingInfo *mmi, const char* block, const char* param, std::unordered_map<map_key_2s,size_t,pair_hash,Compare> &param_map){
    std::unordered_map<map_key_2s,size_t,pair_hash,Compare>::const_iterator it;
    int param_iter = -1;

    const rtwCAPI_BlockParameters *capiBlockParameters = rtwCAPI_GetBlockParameters(mmi);
    uint_T nParams = get_num_block_params(mmi);
    std::string first(block == nullptr ? "" : block);
    std::string second(param == nullptr ? "" : param);
    map_key_2s key{first,second,mmi};
    it = param_map.find(key);
    if(it == param_map.end()){
        for(size_t i=0; i<nParams; i++){
            if(strcmp(block, capiBlockParameters[i].blockPath) == 0 &&
               strcmp(param, capiBlockParameters[i].paramName) == 0){
                // correct param
                param_map[key] = i;
                param_iter = i;
                break;
            }
        }
    }else{
        param_iter = it->second;
    }

    if(param_iter == -1){
        std::stringstream err("");
        err << "get_block_param: Parameter (" << block << ',' << param << ") does not exist in mmi";
        throw std::runtime_error(err.str().c_str());

        return 0;   // makes compiler happy
    }

    validate_scalar(mmi, capiBlockParameters[param_iter], "get_block_param", block);
    rtwCAPI_DataTypeMap dt = mmi->staticMap->Maps.dataTypeMap[rtwCAPI_GetBlockParameterDataTypeIdx(capiBlockParameters, param_iter)];
    void* addr = mmi->InstanceMap.dataAddrMap[rtwCAPI_GetBlockParameterAddrIdx(capiBlockParameters, param_iter)];
    double ret;
    if(strcmp(dt.cDataName, "int") == 0){
        int tmp = *(int*)addr;
        ret = tmp;
    }else if(strcmp(dt.cDataName, "float") == 0){
        float tmp = *(float*)addr;
        ret = tmp;
    }else if(strcmp(dt.cDataName, "double") == 0){
        ret = *(double*)addr;
    }else{
        std::stringstream err("");
        err << "get_block_param: Parameter (" << param << ") has invalid cDataName(" << dt.cDataName;
        err << "). Can only handle [int,float,double]";
        throw std::runtime_error(err.str().c_str());
    }
    return ret;
}

py::buffer_info PYSIMLINK::get_signal_val(const rtwCAPI_ModelMappingInfo *mmi, std::unordered_map<map_key_2s,size_t,pair_hash,Compare> &sig_map, const char* block, const char* sigName){
    assert(mmi != nullptr);
    std::unordered_map<map_key_2s,size_t,pair_hash,Compare>::const_iterator it;

    if(block == nullptr && sigName == nullptr)
        throw std::runtime_error("get_signal_val: Must specify signal name or origin block to search for signal");
//    if(block == nullptr){
//        fprintf(stderr, "Warning: Searching for signal by signal name only. Signal names are not guaranteed unique!\n");
//    }

    uint_T numSigs = get_num_signals(mmi);
    const rtwCAPI_Signals *capiSignals = rtwCAPI_GetSignals(mmi);

    int param_index = -1;

    std::string first(block == nullptr ? "" : block);
    std::string second(sigName == nullptr ? "" : sigName);
    map_key_2s key{first,second,mmi};
    it = sig_map.find(key);
    if(it == sig_map.end()){

        for(size_t i=0; i < numSigs; i++){
            if((sigName == nullptr && strcmp(block, rtwCAPI_GetSignalBlockPath(capiSignals, i)) == 0) ||
                    (block == nullptr && strcmp(sigName, rtwCAPI_GetSignalName(capiSignals, i)) == 0) ||
                    ((sigName != nullptr && block != nullptr) && (strcmp(rtwCAPI_GetSignalName(capiSignals, i), sigName)==0 && strcmp(
                            rtwCAPI_GetSignalBlockPath(capiSignals, i), block) == 0))){
                // signal match
                sig_map[key] = i;
                param_index = i;
                break;
            }
        }
    }else{
        param_index = it->second;
    }

    if(param_index == -1){
        std::stringstream err("");
        err << "get_signal_val: Parameter (" << block << ',' << (sigName == nullptr ? "" : sigName) << ") does not exist in mmi";
        throw std::runtime_error(err.str().c_str());

        return {};   // makes compiler happy
    }


//    validate_scalar(mmi, capiSignals[param_index], "get_signal_val", block);
    rtwCAPI_DataTypeMap dt = mmi->staticMap->Maps.dataTypeMap[capiSignals[param_index].dataTypeIndex];
    rtwCAPI_DimensionMap sigDim = mmi->staticMap->Maps.dimensionMap[capiSignals[param_index].dimIndex];
    void* addr = mmi->InstanceMap.dataAddrMap[capiSignals[param_index].addrMapIndex];

//    double ret;
    py::buffer_info ret;
    ret.ptr = addr;
    ret.itemsize = dt.dataSize;

    if(strcmp(dt.cDataName, "int") == 0){
        ret.format = py::format_descriptor<int>::format();
    }else if(strcmp(dt.cDataName, "float") == 0){
        ret.format = py::format_descriptor<float>::format();
    }else if(strcmp(dt.cDataName, "double") == 0) {
        ret.format = py::format_descriptor<double>::format();
    }else if(strcmp(dt.cDataName, "char") == 0) {
        ret.format = py::format_descriptor<char>::format();
    }else if(strcmp(dt.cDataName, "short") == 0) {
        ret.format = py::format_descriptor<short>::format();
    }else if(strcmp(dt.cDataName, "unsigned short") == 0) {
        ret.format = py::format_descriptor<unsigned short>::format();
    }else if(strcmp(dt.cDataName, "long") == 0) {
        ret.format = py::format_descriptor<long>::format();
    }else if(strcmp(dt.cDataName, "unsigned int") == 0) {
        ret.format = py::format_descriptor<unsigned int>::format();
    }else if(strcmp(dt.cDataName, "unsigned long") == 0) {
        ret.format = py::format_descriptor<unsigned long>::format();
    }else{
        std::stringstream err("");
        err << "get_signal_val: Parameter (" << block << ',' << sigName << ") has invalid cDataName(" << dt.cDataName;
        err << ". Type unknown";
        throw std::runtime_error(err.str().c_str());
    }
    ret.ndim = sigDim.numDims;
    for(size_t i = 0; i < ret.ndim; i++){
        ssize_t dim_size = mmi->staticMap->Maps.dimensionArray[sigDim.dimArrayIndex+i];
        ret.shape.push_back(dim_size);
        switch(sigDim.orientation){
            case rtwCAPI_Orientation::rtwCAPI_SCALAR:
            case rtwCAPI_Orientation::rtwCAPI_VECTOR:
                ret.strides.push_back(dt.dataSize);
                break;
            case rtwCAPI_Orientation::rtwCAPI_MATRIX_COL_MAJOR:
            case rtwCAPI_Orientation::rtwCAPI_MATRIX_COL_MAJOR_ND:
                if(i == 1) {
                    ret.strides.push_back(dt.dataSize * dim_size);
                }else{
                    ret.strides.push_back(dt.dataSize);
                }
                break;
            case rtwCAPI_Orientation::rtwCAPI_MATRIX_ROW_MAJOR:
            case rtwCAPI_Orientation::rtwCAPI_MATRIX_ROW_MAJOR_ND:
                if(i == 0) {
                    ret.strides.push_back(dt.dataSize * dim_size);
                }else{
                    ret.strides.push_back(dt.dataSize);
                }
                break;
            default:
                std::stringstream err("");
                err << "get_signal_val: Parameter (" << block << ',' << sigName << ") has invalid orientation";
                throw std::runtime_error(err.str().c_str());
                break;
        }
    }
    ret.readonly = true;
    return ret;
}

double PYSIMLINK::set_block_param(rtwCAPI_ModelMappingInfo *mmi, const char *block, const char *param, double value){
    const rtwCAPI_BlockParameters *capiBlockParameters = rtwCAPI_GetBlockParameters(mmi);
    uint_T nParams = get_num_block_params(mmi);
    for(size_t i=0; i<nParams; i++) {
        if (strcmp(block, capiBlockParameters[i].blockPath) == 0 &&
            strcmp(param, capiBlockParameters[i].paramName) == 0) {
            validate_scalar(mmi, capiBlockParameters[i], "set_block_parameter", block);

            rtwCAPI_DataTypeMap dt = mmi->staticMap->Maps.dataTypeMap[capiBlockParameters[i].dataTypeIndex];
            void* addr = mmi->InstanceMap.dataAddrMap[capiBlockParameters[i].addrMapIndex];

            double ret;
            if(strcmp(dt.cDataName, "int") == 0){
                int tmp = *(int*)addr;
                ret = tmp;
                tmp = value;
                memcpy(addr, &tmp, sizeof(int));
                return ret;
            }else if(strcmp(dt.cDataName, "float") == 0){
                float tmp = *(float*)addr;
                ret = tmp;
                tmp = value;
                memcpy(addr, &tmp, sizeof(float));
                return ret;
            }else if(strcmp(dt.cDataName, "double") == 0){
                ret = *(double*)addr;
                memcpy(addr, &value, sizeof(value));
                return ret;
            }else{
                std::stringstream err("");
                err << "get_signal_val: Parameter (" << block << ',' << param << ") has invalid cDataName(" << dt.cDataName;
                err << "). Can only handle [int,float,double]";
                throw std::runtime_error(err.str().c_str());
            }
        }
    }
    std::stringstream err("");
    err << "set_block_param: Parameter (" << block << ',' << param << ") does not exist in mmi";
    throw std::runtime_error(err.str().c_str());

    return 0.0;   // makes compiler happy
}

void PYSIMLINK::print_params_recursive(const rtwCAPI_ModelMappingInfo *child_mmi){
    print_model_params(child_mmi);
    print_block_params(child_mmi);
    print_signals(child_mmi);
    for(size_t i = 0; i < child_mmi->InstanceMap.childMMIArrayLen; i++){
        print_params_recursive(child_mmi->InstanceMap.childMMIArray[i]);
    }
}

std::vector<struct PYSIMLINK::ModelParam> PYSIMLINK::debug_model_params(const rtwCAPI_ModelMappingInfo *mmi){
    uint_T numParams = get_num_model_params(mmi);
    const rtwCAPI_ModelParameters* capiModelParams = rtwCAPI_GetModelParameters(mmi);
    std::vector<struct PYSIMLINK::ModelParam> ret;
    ret.reserve(numParams);
    for (size_t i=0; i < numParams; i++) {
        struct PYSIMLINK::ModelParam to_add;
        to_add.model_param = capiModelParams[i].varName;
        to_add.data_type = mmi->staticMap->Maps.dataTypeMap[capiModelParams[i].dataTypeIndex].cDataName;
        ret.push_back(to_add);
    }
    return ret;
}

std::vector<struct PYSIMLINK::BlockParam> PYSIMLINK::debug_block_param(const rtwCAPI_ModelMappingInfo *mmi) {
    const rtwCAPI_BlockParameters *capiBlockParams = rtwCAPI_GetBlockParameters(mmi);
    uint_T nParams = get_num_block_params(mmi);
    std::vector<struct PYSIMLINK::BlockParam> ret;
    ret.reserve(nParams);

    for (size_t i=0; i < nParams; i++) {
        struct PYSIMLINK::BlockParam to_add;
        to_add.block_name = capiBlockParams[i].blockPath;
        to_add.block_param = capiBlockParams[i].paramName;
        to_add.data_type = mmi->staticMap->Maps.dataTypeMap[capiBlockParams[i].dataTypeIndex].cDataName;
        ret.push_back(to_add);
    }
    return ret;
}

std::vector<struct PYSIMLINK::Signal> PYSIMLINK::debug_signals(const rtwCAPI_ModelMappingInfo *mmi) {
    uint_T numSigs = get_num_signals(mmi);
    const rtwCAPI_Signals *capiSignals = rtwCAPI_GetSignals(mmi);

    std::vector<struct PYSIMLINK::Signal> ret;
    ret.reserve(numSigs);
    for(size_t i = 0; i < numSigs; i++){
        struct PYSIMLINK::Signal to_add;
        to_add.block_name = PYSIMLINK::safe_string(capiSignals[i].blockPath);
        to_add.signal_name = PYSIMLINK::safe_string(capiSignals[i].signalName);
        to_add.data_type =  mmi->staticMap->Maps.dataTypeMap[capiSignals[i].dataTypeIndex].cDataName;
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