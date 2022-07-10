#pragma once

#define NAN_CHECK(num) if(isnan(num)) num=0;

extern "C"{
#include "rtw_capi.h"
#include "rtw_modelmap_logging.h"
#include "rtw_matlogging.h"
#include "rtw_modelmap.h"
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
            Model();
            ~Model();

            std::vector<struct ModelInfo> get_params() const;
            double step_size() const;
            void reset();

        protected:
            bool initialized;
            //void step();
            //double tFinal() const;
            void discover_mmis(const rtwCAPI_ModelMappingInfo *mmi);

            rtwCAPI_ModelMappingInfo *root_mmi;
            boolean_T OverrunFlags[NUMST];    /* ISR overrun flags */
            boolean_T eventFlags[NUMST];      /* necessary for overlapping preemption */
            std::map<const char*,const rtwCAPI_ModelMappingInfo *> mmi_map;

            std::unordered_map<PYSIMLINK::map_key_1s,size_t,PYSIMLINK::pair_hash,PYSIMLINK::Compare> model_param;
            std::unordered_map<PYSIMLINK::map_key_2s,size_t,PYSIMLINK::pair_hash,PYSIMLINK::Compare> sig_map;
            std::unordered_map<PYSIMLINK::map_key_2s,size_t,PYSIMLINK::pair_hash,PYSIMLINK::Compare> block_map;
    };
};
