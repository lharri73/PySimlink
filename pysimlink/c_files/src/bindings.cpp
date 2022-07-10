#include "model_interface.hpp"
#include <pybind11/pybind11.h>

namespace py = pybind11;

PYBIND11_MODULE(model_interface_c, m) {
    py::class_<PYSIMLINK::Model>(m, "Model")
            .def(py::init<>())
            .def("reset", &PYSIMLINK::Model::reset)
            .def("step_size", &PYSIMLINK::Model::step_size)
            .def("print_params", &PYSIMLINK::Model::print_params);
}