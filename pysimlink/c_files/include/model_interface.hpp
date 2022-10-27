#pragma once

#define NAN_CHECK(num) if(isnan(num)) num=0;

extern "C"{
#include "rtw_capi.h"
#include "rtw_modelmap_logging.h"
#include "rtw_matlogging.h"
#include "rtw_modelmap.h"
#include "<<ROOT_MODEL>>"
#include "<<ROOT_MODEL_PRIVATE>>"
}

#include <string>
#include "model_utils.hpp"
#include <math.h>
#include <stdexcept>
#include <vector>
#include <unordered_map>

#include "pybind11/pybind11.h"
#include "pybind11/numpy.h"
#include "pybind11/stl.h"

/* create generic macros that work with any model */
# define EXPAND_CONCAT(name1,name2) name1 ## name2
# define CONCAT(name1,name2) EXPAND_CONCAT(name1,name2)
# define MODEL_INITIALIZE CONCAT(MODEL,_initialize)
# define MODEL_STEP       CONCAT(MODEL,_step)
# define MODEL_TERMINATE  CONCAT(MODEL,_terminate)
# define RT_MDL           CONCAT(MODEL,_M)

namespace py = pybind11;

namespace PYSIMLINK{
    class Model{
        public:
            Model(std::string name);
            ~Model();

            void step(int num_steps);
            void reset();

            std::vector<struct ModelInfo> get_params() const;
            py::array get_sig(const std::string& model, const std::string& path, const std::string& sig_name);
            PYSIMLINK::all_dtypes get_sig_union(const std::string &model, const std::string &path, const std::string &sig_name);
            py::array get_block_param(const std::string& model, const std::string& block_path, const std::string& param);
            py::array get_model_param(const std::string& model, const std::string& param);

            template <typename T>
            void set_block_param(const std::string& model, const std::string &block_path, const std::string &param, py::array_t<T> value);

            template <typename T>
            void set_model_param(const std::string& model, const std::string &param, py::array_t<T> value);

            struct PYSIMLINK::DataType block_param_info(const std::string &model, const std::string& block_path, const std::string& param);
            struct PYSIMLINK::DataType model_param_info(const std::string &model, const std::string& param);
            struct PYSIMLINK::DataType signal_info(const std::string &model, const std::string &block_path, const std::string &signal);

            double step_size();
            double tFinal();
            void set_tFinal(float);
            std::vector<std::string> get_models() const;

        protected:
            bool initialized;
            void discover_mmis(const rtwCAPI_ModelMappingInfo *mmi);
            static void terminate();
            std::string mdl_name;

            rtwCAPI_ModelMappingInfo *root_mmi;
            boolean_T OverrunFlags[1];    /* ISR overrun flags */
            boolean_T eventFlags[1];      /* necessary for overlapping preemption */
            std::map<std::string,const rtwCAPI_ModelMappingInfo *> mmi_map;

            std::unordered_map<PYSIMLINK::map_key_1s,size_t, PYSIMLINK::pair_hash,PYSIMLINK::Compare> model_param;
            std::unordered_map<PYSIMLINK::map_key_2s,size_t, PYSIMLINK::pair_hash,PYSIMLINK::Compare> sig_map;
            std::unordered_map<PYSIMLINK::map_key_2s,size_t, PYSIMLINK::pair_hash,PYSIMLINK::Compare> block_map;
    };
    template <typename T>
    void Model::set_block_param(const std::string &model, const std::string &block_path, const std::string &param,
                                py::array_t<T> value) {
        if(!initialized){
            throw std::runtime_error("Model must be initialized before calling get_block_param. Call `reset()` first!");
        }
        if(block_path.empty())
            throw std::runtime_error("No path provided to get_block_param!");
        if(model.empty())
            throw std::runtime_error("No model name provided to get_block_param!");
        if(param.empty())
            throw std::runtime_error("No parameter provided to get_block_param!");
        auto mmi_idx = mmi_map.find(model);
        if(mmi_idx == mmi_map.end()){
            char buf[256];
            sprintf(buf, "Cannot find model with name: %s", model.c_str());
            throw std::runtime_error(buf);
        }
        PYSIMLINK::set_block_param(mmi_idx->second, block_path.c_str(), param.c_str(), value);
    }

    template <typename T>
    void Model::set_model_param(const std::string &model, const std::string &param, py::array_t<T> value) {
        if(!initialized){
            throw std::runtime_error("Model must be initialized before calling get_block_param. Call `reset()` first!");
        }
        if(model.empty())
            throw std::runtime_error("No model name provided to get_block_param!");
        if(param.empty())
            throw std::runtime_error("No parameter provided to get_block_param!");
        auto mmi_idx = mmi_map.find(model);
        if(mmi_idx == mmi_map.end()){
            char buf[256];
            sprintf(buf, "Cannot find model with name: %s", model.c_str());
            throw std::runtime_error(buf);
        }
        PYSIMLINK::set_model_param(mmi_idx->second, param.c_str(), value);
    }
};
