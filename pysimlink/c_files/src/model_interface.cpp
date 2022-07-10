#include "model_interface.hpp"
#include <cstdio>

using namespace PYSIMLINK;

namespace py = pybind11;

Model::Model(){
    initialized = false;
    memset(OverrunFlags, 0, sizeof(boolean_T)*NUMST);
    memset(eventFlags, 0, sizeof(boolean_T)*NUMST);
}

Model::~Model(){
    if(initialized){
        rt_StopDataLogging("/dev/null",rtmGetRTWLogInfo(RT_MDL));
        MODEL_TERMINATE();
    }
}

void Model::reset(){
    // clear all model mapping information bc it may change
    // between runs (verify this)
    model_param.clear();
    sig_map.clear();
    block_map.clear();

    // clear loggind data
    if(initialized){
        rt_StopDataLogging("/dev/null",rtmGetRTWLogInfo(RT_MDL));
        MODEL_TERMINATE();
    }
    MODEL_INITIALIZE();

    // get the MMI
    root_mmi = &(rtmGetDataMapInfo(RT_MDL).mmi);

    mmi_map.insert(std::make_pair("root", root_mmi));
    discover_mmis(root_mmi);
    initialized = true;
}

double Model::step_size() const{
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
        mmi_map.insert(std::make_pair(mmi->InstanceMap.childMMIArray[i]->InstanceMap.path, mmi->InstanceMap.childMMIArray[i]));
        discover_mmis(mmi->InstanceMap.childMMIArray[i]);
    }
}