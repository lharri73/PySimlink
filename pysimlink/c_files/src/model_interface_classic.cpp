#include "model_interface.hpp"
#include <cstdio>

using namespace PYSIMLINK;

namespace py = pybind11;

#ifdef CLASSIC_INTERFACE

Model::Model(){
    initialized = false;
    memset(OverrunFlags, 0, sizeof(boolean_T));
    memset(eventFlags, 0, sizeof(boolean_T));
}

void Model::terminate(){
    rt_StopDataLogging("/dev/null",rtmGetRTWLogInfo(RT_MDL));
#ifdef CLASSIC_INTERFACE

    if (GBLbuf.errmsg) {
        (void)fprintf(stderr,"%s\n",GBLbuf.errmsg);
        exit(EXIT_FAILURE);
    }

    if (rtmGetErrorStatus(S) != NULL) {
        (void)fprintf(stderr,"ErrorStatus set: \"%s\"\n", rtmGetErrorStatus(S));
        exit(EXIT_FAILURE);
    }

    if (GBLbuf.isrOverrun) {
        (void)fprintf(stderr,
                      "%s: ISR overrun - base sampling rate is too fast\n",
                      QUOTE(MODEL));
        exit(EXIT_FAILURE);
    }

    MdlTerminate();
    rtExtModeShutdown(rtmGetNumSampleTimes(S));
#else
    MODEL_TERMINATE();
#endif
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

    mmi_map.insert(std::make_pair("root", root_mmi));
    discover_mmis(root_mmi);
    initialized = true;
}

double Model::step_size() const{
    return RT_MDL->Timing.stepSize0;
}

void Model::discover_mmis(const rtwCAPI_ModelMappingInfo *mmi){
    // go through all child mmis and insert them into the map.
    for(size_t i = 0; i < mmi->InstanceMap.childMMIArrayLen; i++){
        mmi_map.insert(std::make_pair(mmi->InstanceMap.childMMIArray[i]->InstanceMap.path, mmi->InstanceMap.childMMIArray[i]));
        discover_mmis(mmi->InstanceMap.childMMIArray[i]);
    }
}

void Model::step(int num_steps){
    assert(((void)"num_steps must be a positive number", num_steps>0));

    for(int cur_step=0; cur_step < num_steps; cur_step++){
        if (OverrunFlags[0]++)
            rtmSetErrorStatus(RT_MDL, "Overrun");

        if (rtmGetErrorStatus(RT_MDL) != NULL) {
            char buf[256];
            sprintf(buf, "Model is in errored state: %s", rtmGetErrorStatus(RT_MDL));
            throw std::runtime_error(buf);
            return;
        }

        MODEL_STEP();

        OverrunFlags[0]--;
    }
}

double Model::tFinal() const{
    return rtmGetFinalTime(RT_MDL);
}

void Model::set_tFinal(float tFinal){
    rtmSetTFinal(RT_MDL, tFinal);
}

void classic_step(){
    /****************************
     * Initialize global memory *
     ****************************/
    (void)memset(&GBLbuf, 0, sizeof(GBLbuf));

    /************************
     * Initialize the model *
     ************************/

    S = MODEL();
    if (rtmGetErrorStatus(S) != NULL) {
        (void)fprintf(stderr,"Error during model registration: %s\n",
                      rtmGetErrorStatus(S));
        exit(EXIT_FAILURE);
    }
    if (finaltime >= 0.0 || finaltime == RUN_FOREVER) rtmSetTFinal(S,finaltime);

    MdlInitializeSizes();
    MdlInitializeSampleTimes();

    status = rt_SimInitTimingEngine(rtmGetNumSampleTimes(S),
                                    rtmGetStepSize(S),
                                    rtmGetSampleTimePtr(S),
                                    rtmGetOffsetTimePtr(S),
                                    rtmGetSampleHitPtr(S),
                                    rtmGetSampleTimeTaskIDPtr(S),
                                    rtmGetTStart(S),
                                    &rtmGetSimTimeStep(S),
                                    &rtmGetTimingData(S));

    if (status != NULL) {
        (void)fprintf(stderr,
                      "Failed to initialize sample time engine: %s\n", status);
        exit(EXIT_FAILURE);
    }
    rt_CreateIntegrationData(S);

#ifdef UseMMIDataLogging
    rt_FillStateSigInfoFromMMI(rtmGetRTWLogInfo(S),&rtmGetErrorStatus(S));
#endif
    GBLbuf.errmsg = rt_StartDataLogging(rtmGetRTWLogInfo(S),
                                        rtmGetTFinal(S),
                                        rtmGetStepSize(S),
                                        &rtmGetErrorStatus(S));
    if (GBLbuf.errmsg != NULL) {
        (void)fprintf(stderr,"Error starting data logging: %s\n",GBLbuf.errmsg);
        return(EXIT_FAILURE);
    }

    rtExtModeCheckInit(rtmGetNumSampleTimes(S));
    rtExtModeWaitForStartPkt(rtmGetRTWExtModeInfo(S),
                             rtmGetNumSampleTimes(S),
                             (boolean_T *)&rtmGetStopRequested(S));

    (void)printf("\n** starting the model **\n");

    MdlStart();
    if (rtmGetErrorStatus(S) != NULL) {
        GBLbuf.stopExecutionFlag = 1;
    }

    /*************************************************************************
     * Execute the model.  You may attach rtOneStep to an ISR, if so replace *
     * the call to rtOneStep (below) with a call to a background task        *
     * application.                                                          *
     *************************************************************************/
    if (rtmGetTFinal(S) == RUN_FOREVER) {
        printf ("\n**May run forever. Model stop time set to infinity.**\n");
    }

    while (!GBLbuf.stopExecutionFlag &&
           (rtmGetTFinal(S) == RUN_FOREVER ||
            rtmGetTFinal(S)-rtmGetT(S) > rtmGetT(S)*DBL_EPSILON)) {

        rtExtModePauseIfNeeded(rtmGetRTWExtModeInfo(S),
                               rtmGetNumSampleTimes(S),
                               (boolean_T *)&rtmGetStopRequested(S));

        if (rtmGetStopRequested(S)) break;
        /* external mode */
        rtExtModeOneStep(rtmGetRTWExtModeInfo(S),
                         rtmGetNumSampleTimes(S),
                         (boolean_T *)&rtmGetStopRequested(S));

        rt_OneStep(S);
    }

    if (!GBLbuf.stopExecutionFlag && !rtmGetStopRequested(S)) {
        /* external mode */
        rtExtModeOneStep(rtmGetRTWExtModeInfo(S),
                         rtmGetNumSampleTimes(S),
                         (boolean_T *)&rtmGetStopRequested(S));

        /* Execute model last time step */
        rt_OneStep(S);
    }

    /********************
     * Cleanup and exit *
     ********************/

    return(EXIT_SUCCESS);

}

#endif