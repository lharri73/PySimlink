#include "model_interface.hpp"
#include "param_structs.hpp"
#include <pybind11/pybind11.h>

namespace py = pybind11;

PYBIND11_MODULE(model_interface_c, m) {
    py::class_<PYSIMLINK::Model>(m, "Model")
            .def(py::init<std::string>())
            .def("reset", &PYSIMLINK::Model::reset)
            .def("step_size", &PYSIMLINK::Model::step_size)
            .def("tFinal", &PYSIMLINK::Model::tFinal)
            .def("set_tFinal", &PYSIMLINK::Model::set_tFinal)
            .def("step", &PYSIMLINK::Model::step)
            .def("get_models", &PYSIMLINK::Model::get_models)
            .def("get_signal", &PYSIMLINK::Model::get_sig)
            .def("get_params", &PYSIMLINK::Model::get_params);

    py::class_<PYSIMLINK::BlockParam>(m, "BlockParam")
            .def_readonly("block_name", &PYSIMLINK::BlockParam::block_name)
            .def_readonly("block_param", &PYSIMLINK::BlockParam::block_param)
            .def_readonly("data_type", &PYSIMLINK::BlockParam::data_type);

    py::class_<PYSIMLINK::Signal>(m, "Signal")
            .def_readonly("block_name", &PYSIMLINK::Signal::block_name)
            .def_readonly("signal_name", &PYSIMLINK::Signal::signal_name)
            .def_readonly("data_type", &PYSIMLINK::Signal::data_type);

    py::class_<PYSIMLINK::ModelParam>(m, "ModelParam")
            .def_readonly("model_param", &PYSIMLINK::ModelParam::model_param)
            .def_readonly("data_type", &PYSIMLINK::ModelParam::data_type);
    
    py::class_<PYSIMLINK::ModelInfo>(m, "ModelInfo")
            .def_readonly("model_name", &PYSIMLINK::ModelInfo::model_name)
            .def_readonly("model_params", &PYSIMLINK::ModelInfo::model_params)
            .def_readonly("block_params", &PYSIMLINK::ModelInfo::block_params)
            .def_readonly("signals", &PYSIMLINK::ModelInfo::signals);
}
