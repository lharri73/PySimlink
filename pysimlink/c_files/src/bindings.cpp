#include <pybind11/pybind11.h>
#include "model_interface.hpp"

namespace py = pybind11;

PYBIND11_MODULE(blazer_model_c, m) {
    py::class_<PYSMINLIBK::Model>(m, "pid_model")
            .def(py::init<>())
            .def("reset", &PYSMINLIBK::Model::reset)
            .def("step", &PYSMINLIBK::Model::iter)
            .def("num_steps", &PYSMINLIBK::Model::num_steps)
            .def("step_size", &PYSMINLIBK::Model::step_size)
            .def("debug", &PYSMINLIBK::Model::debug_params)
}
