#include "model_interface.hpp"
#include <cstdio>

using namespace PYSIMLINK;

namespace py = pybind11;

Model::Model(){
    initialized = false;
    memset(OverrunFlags, 0, sizeof(boolean_T)*NUMST);
    memset(eventFlags, 0, sizeof(boolean_T)*NUMST);
    printf("here constructor\n");
}

Model::~Model(){
    printf("Here destructor\n");
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
    mmi = &(rtmGetDataMapInfo(RT_MDL).mmi);

    initialized = true;
}

double Model::step_size() const{
    return RT_MDL->Timing.stepSize0;
}

void Model::print_params() const{
    if(!initialized){
        throw std::runtime_error("Model must be initialized before calling print_params. Call reset() first");
    }
    print_params_recursive(mmi);
}