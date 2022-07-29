#include "model_interface.hpp"
#include <cstdio>

using namespace PYSIMLINK;

namespace py = pybind11;

Model::~Model(){
    if(initialized){
        terminate();
    }
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