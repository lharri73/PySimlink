#include "model_interface.hpp"
#include "containers.hpp"
#include <pybind11/pybind11.h>

#define NEW_TEMPLATE_FUNC(A,B) \
    .def(A, B<char>) \
    .def(A, B<unsigned char>) \
    .def(A, B<short>) \
    .def(A, B<unsigned short>) \
    .def(A, B<unsigned int>) \
    .def(A, B<int>) \
    .def(A, B<float>) \
    .def(A, B<double>)


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
            .def("get_block_param", &PYSIMLINK::Model::get_block_param)
            NEW_TEMPLATE_FUNC("set_block_param", &PYSIMLINK::Model::set_block_param)
            .def("get_params", &PYSIMLINK::Model::get_params)
            .def("block_param_info", &PYSIMLINK::Model::block_param_info);

    py::enum_<rtwCAPI_Orientation>(m, "rtwCAPI_Orientation")
            .value("vector", rtwCAPI_VECTOR)
            .value("scalar", rtwCAPI_SCALAR)
            .value("col_major_nd", rtwCAPI_MATRIX_COL_MAJOR_ND)
            .value("col_major", rtwCAPI_MATRIX_COL_MAJOR)
            .value("row_major_nd", rtwCAPI_MATRIX_ROW_MAJOR_ND)
            .value("row_major", rtwCAPI_MATRIX_ROW_MAJOR);

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

    py::class_<PYSIMLINK::DataType>(m, "DataType")
            .def_readonly("cDataType", &PYSIMLINK::DataType::cDataType)
            .def_readonly("pythonType", &PYSIMLINK::DataType::pythonType)
            .def_readonly("dims", &PYSIMLINK::DataType::dims)
            .def_readonly("orientation", &PYSIMLINK::DataType::orientation);
}
