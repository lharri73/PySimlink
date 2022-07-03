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
#include "defines.hpp"

namespace py = pybind11;

namespace PYSIMLINK{
    class Model{
        public:
            Model(bool v2x, bool automatic_control, double alt, int ni);
            ~Model();

            void debug_params();
            double step_size() const;

        protected:
            bool initialized;
            void print_params(const rtwCAPI_ModelMappingInfo *mmi);
            void common_reset();
            virtual void step() = 0;
            virtual double tFinal() const = 0;

            rtwCAPI_ModelMappingInfo *mmi;
            boolean_T OverrunFlags[NUMST];    /* ISR overrun flags */
            boolean_T eventFlags[NUMST];      /* necessary for overlapping preemption */
            std::unordered_map<PYSIMLINK::map_key_1s,size_t,PYSIMLINK::pair_hash,PYSIMLINK::Compare> model_param;
            std::unordered_map<PYSIMLINK::map_key_2s,size_t,PYSIMLINK::pair_hash,PYSIMLINK::Compare> sig_map;
            std::unordered_map<PYSIMLINK::map_key_2s,size_t,PYSIMLINK::pair_hash,PYSIMLINK::Compare> block_map;
    };
};
