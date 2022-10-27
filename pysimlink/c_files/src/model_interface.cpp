#include "model_interface.hpp"
#include <cstdio>

#ifdef _WIN32
#define NULL_FILE "NUL"
#else
#define NULL_FILE "/dev/null"
#endif

using namespace PYSIMLINK;

namespace py = pybind11;

Model::~Model(){
    if(initialized){
        terminate();
    }
}

Model::Model(std::string name){
    initialized = false;
    memset(OverrunFlags, 0, sizeof(boolean_T));
    memset(eventFlags, 0, sizeof(boolean_T));
    root_mmi = nullptr;
    mdl_name = name;
}

void Model::terminate(){
#ifdef rtmGetRTWLogInfo
    rt_StopDataLogging(NULL_FILE,rtmGetRTWLogInfo(RT_MDL));
#endif
    MODEL_TERMINATE();
}

void Model::reset(){
    // clear all model mapping information bc it may change
    // between runs (verify this)
    model_param.clear();
    sig_map.clear();
    block_map.clear();

    // clear loggind data
    if(initialized){
        terminate();
    }
    MODEL_INITIALIZE();

    // get the MMI
    root_mmi = &(rtmGetDataMapInfo(RT_MDL).mmi);

    mmi_map.insert(std::make_pair(mdl_name, root_mmi));
    discover_mmis(root_mmi);
    initialized = true;
}

double Model::step_size() {
    if(!initialized){
        throw std::runtime_error("Model must be initialized before calling step_size. Call `reset()` first!");
    }
    return RT_MDL->Timing.stepSize0;
}

std::vector<struct ModelInfo> Model::get_params() const{
    if(!initialized){
        throw std::runtime_error("Model must be initialized before calling print_params. Call `reset()` first!");
    }
    std::vector<struct ModelInfo> ret;
    ret.reserve(mmi_map.size());

    for(auto it : mmi_map){
        struct ModelInfo to_add;
        to_add.model_name = it.first;
        to_add.block_params = debug_block_param(it.second);
        to_add.model_params = debug_model_params(it.second);
        to_add.signals = debug_signals(it.second);
        ret.push_back(to_add);
    }
    return ret;
}

void Model::discover_mmis(const rtwCAPI_ModelMappingInfo *mmi){
    // go through all child mmis and insert them into the map.
    for(size_t i = 0; i < mmi->InstanceMap.childMMIArrayLen; i++){
        mmi_map.insert(std::make_pair(std::string(mmi->InstanceMap.childMMIArray[i]->InstanceMap.path), mmi->InstanceMap.childMMIArray[i]));
        discover_mmis(mmi->InstanceMap.childMMIArray[i]);
    }
}

void Model::step(int num_steps){
    assert(((void)"num_steps must be a positive number", num_steps>0));
    if(!initialized){
        throw std::runtime_error("Model must be initialized before calling step. Call `reset()` first!");
    }

    for(int cur_step=0; cur_step < num_steps; cur_step++){
        if (OverrunFlags[0]++)
            rtmSetErrorStatus(RT_MDL, "Overrun");

        if (rtmGetErrorStatus(RT_MDL) != NULL) {
            char buf[256];
            sprintf(buf, "Model is in errored state: %s", rtmGetErrorStatus(RT_MDL));
            throw std::runtime_error(buf);
        }

        MODEL_STEP();

        OverrunFlags[0]--;
    }
}

double Model::tFinal() {
    if(!initialized){
        throw std::runtime_error("Model must be initialized before calling tFinal. Call `reset()` first!");
    }
#ifndef rtmGetFinalTime
    throw std::runtime_error("Getting/Setting tFinal is not supported for this model.");
#else
    return rtmGetFinalTime(RT_MDL);
#endif
}

void Model::set_tFinal(float tFinal){
    if(!initialized){
        throw std::runtime_error("Model must be initialized before calling set_tFinal. Call `reset()` first!");
    }

#ifndef rtmSetTFinal
    throw std::runtime_error("Getting/Setting tFinal is not supported for this model.");
#else
    rtmSetTFinal(RT_MDL, tFinal);
#endif
}

std::vector<std::string> Model::get_models() const{
    if(!initialized){
        throw std::runtime_error("Model must be initialized before calling get_models. Call `reset()` first!");
    }
    std::vector<std::string> ret;
    ret.reserve(mmi_map.size());

    for(auto i : mmi_map){
        ret.push_back(i.first);
    }

    return ret;
}

PYSIMLINK::DataType Model::signal_info(const std::string &model, const std::string &block_path,
                                       const std::string &signal) {
    if(!initialized){
        throw std::runtime_error("Model must be initialized before calling get_sig. Call `reset()` first!");
    }

    if(block_path.empty())
        throw std::runtime_error("No path provided to get_sig!");
    if(model.empty())
        throw std::runtime_error("No model name provided to get_sig!");

    auto mmi_idx = mmi_map.find(model);
    if(mmi_idx == mmi_map.end()){
        char buf[256];
        sprintf(buf, "Cannot find model with name: %s", model.c_str());
        throw std::runtime_error(buf);
    }

    const char* sig_name = signal.empty() ? nullptr : signal.c_str();
    return PYSIMLINK::describe_signal(mmi_idx->second, block_path.c_str(), sig_name, sig_map);
}

py::array Model::get_sig(const std::string& model, const std::string& block_path, const std::string& sig_name_raw){
    if(!initialized){
        throw std::runtime_error("Model must be initialized before calling get_sig. Call `reset()` first!");
    }

    if(block_path.empty())
        throw std::runtime_error("No path provided to get_sig!");
    if(model.empty())
        throw std::runtime_error("No model name provided to get_sig!");

    auto mmi_idx = mmi_map.find(model);
    if(mmi_idx == mmi_map.end()){
        char buf[256];
        sprintf(buf, "Cannot find model with name: %s", model.c_str());
        throw std::runtime_error(buf);
    }


    const char* sig_name = sig_name_raw.empty() ? nullptr : sig_name_raw.c_str();
    struct PYSIMLINK::signal_info ret = PYSIMLINK::get_signal_val(mmi_idx->second, sig_map, block_path.c_str(), sig_name);
//    py::handle<PYSIMLINK::signal_info> tmp(ret);
    return py::array(*ret.data.arr);
}

py::array Model::get_block_param(const std::string& model, const std::string& block_path, const std::string& param){
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
    py::buffer_info ret = PYSIMLINK::get_block_param(mmi_idx->second, block_path.c_str(), param.c_str(), block_map);
    return py::array(ret);
}

struct PYSIMLINK::DataType Model::block_param_info(const std::string &model, const std::string& block_path, const std::string& param){
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
    return PYSIMLINK::describe_block_param(mmi_idx->second, block_path.c_str(), param.c_str());
}

py::array Model::get_model_param(const std::string &model, const std::string &param) {
    if(!initialized){
        throw std::runtime_error("Model must be initialized before calling get_block_param. Call `reset()` first!");
    }

    if(model.empty())
        throw std::runtime_error("No model name provided to get_model_param!");
    if(param.empty())
        throw std::runtime_error("No parameter provided to get_model_param!");

    auto mmi_idx = mmi_map.find(model);
    if(mmi_idx == mmi_map.end()){
        char buf[256];
        sprintf(buf, "Cannot find model with name: %s", model.c_str());
        throw std::runtime_error(buf);
    }
    py::buffer_info ret = PYSIMLINK::get_model_param(mmi_idx->second, param.c_str(), model_param);
    return py::array(ret);
}

struct PYSIMLINK::DataType Model::model_param_info(const std::string &model, const std::string &param) {
    if(!initialized){
        throw std::runtime_error("Model must be initialized before calling get_block_param. Call `reset()` first!");
    }

    if(model.empty())
        throw std::runtime_error("No model name provided to get_model_param!");
    if(param.empty())
        throw std::runtime_error("No parameter provided to get_model_param!");
    auto mmi_idx = mmi_map.find(model);
    if(mmi_idx == mmi_map.end()){
        char buf[256];
        sprintf(buf, "Cannot find model with name: %s", model.c_str());
        throw std::runtime_error(buf);
    }
    return PYSIMLINK::describe_model_param(mmi_idx->second, param.c_str());
}