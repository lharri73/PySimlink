//
// Created by landon on 8/8/22.
//
#include "dev_tools.hpp"

#if false
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


void PYSIMLINK::print_params_recursive(const rtwCAPI_ModelMappingInfo *child_mmi){
    print_model_params(child_mmi);
    print_block_params(child_mmi);
    print_signals(child_mmi);
    for(size_t i = 0; i < child_mmi->InstanceMap.childMMIArrayLen; i++){
        print_params_recursive(child_mmi->InstanceMap.childMMIArray[i]);
    }
}

#endif