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

namespace PYSIMLINK{

    class map_key_2s{
        public:
        std::string a;
        std::string b;
        const rtwCAPI_ModelMappingInfo *c;
        bool operator==(const map_key_2s &other) const{
            if(c != other.c) return false;

            return ((a == other.a) && (b == other.b));
        }
    };
    class map_key_1s{
        public:
        std::string a;
        const rtwCAPI_ModelMappingInfo *c;
        bool operator==(const map_key_1s &other) const{
            if(c != other.c) return false;
            return (a == other.a);
        }
    };

    struct pair_hash{
        std::size_t operator()(const map_key_2s &p) const;
        std::size_t operator()(const map_key_1s &p) const;
    };
    struct Compare{
        bool operator()(const map_key_2s &lhs, const map_key_2s &rhs) const;
        bool operator()(const map_key_1s &lhs, const map_key_1s &rhs) const;
    };

    uint_T get_num_model_params(const rtwCAPI_ModelMappingInfo *mmi);
    double get_model_param(const rtwCAPI_ModelMappingInfo *mmi, const char *param, std::unordered_map<map_key_1s,size_t,pair_hash,Compare> &model_params);

    uint_T get_num_block_params(const rtwCAPI_ModelMappingInfo *mmi);
    double get_block_param(const rtwCAPI_ModelMappingInfo *mmi, const char *block, const char *param, std::unordered_map<map_key_2s,size_t,pair_hash,Compare> &block_map);
    double set_block_param(rtwCAPI_ModelMappingInfo *mmi, // returns the original value
                         const char *block,
                         const char *param,
                         double value);

    uint_T get_num_signals(const rtwCAPI_ModelMappingInfo *mmi);
    double get_signal_val(const rtwCAPI_ModelMappingInfo *mmi, std::unordered_map<map_key_2s,size_t,pair_hash,Compare> &sig_map, const char* block=nullptr, const char* signNam=nullptr);

    void print_model_params(const rtwCAPI_ModelMappingInfo *mmi);
    void print_block_params(const rtwCAPI_ModelMappingInfo *mmi);
    void print_signals(const rtwCAPI_ModelMappingInfo *mmi);

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

};
