#include "model_interface.hpp"

using namespace PYSIMLINK;

namespace py = pybind11;

Model::Model(){
    initialized = false;
    memset(OverrunFlags, 0, sizeof(boolean_T)*NUMST);
    memset(eventFlags, 0, sizeof(boolean_T)*NUMST);
}

Model::~Model(){

}

double Model::step_size() const{
    return RT_MDL->Timing.stepSize0;
}

void print_params(const rtwCAPI_ModelMappingInfo *mmi){

}
