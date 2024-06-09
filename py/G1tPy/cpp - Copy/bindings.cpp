// bindings.cpp
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>
// #include "../../../src/G1tFile.h"
// #include "../../../src/DdsFile.h"
#include <string.h>
#include <vector>
#include "G1tLib.h"

namespace py = pybind11;

// struct CResult {
//     char* metadata;
//     const uint8_t** dds_data;
//     size_t* dds_sizes;
//     size_t num_dds;
// };

// struct CBytes {
//     uint8_t* data;
//     size_t size;
// };

// CResult G1tDecompile(const uint8_t* g1t_data, size_t g1t_size) {
//     std::string metadata = "Gowno cpp";

//     CResult result;
//     result.metadata = strdup(metadata.c_str());
//     result.dds_data = nullptr;
//     result.dds_sizes = nullptr;
//     result.num_dds = 0;
//     return result;
// }

// void free_cresult(CResult result) {
//     if (result.metadata) {
//         free(result.metadata);
//     }
//     for (size_t i = 0; i < result.num_dds; ++i) {
//         delete[] result.dds_data[i];
//     }
//     delete[] result.dds_data;
//     delete[] result.dds_sizes;
// }

// CBytes G1tCompile(const uint8_t** dds_data, const size_t* dds_sizes, size_t num_dds) {
//     std::vector<uint8_t> bytes;
//     uint8_t* data = new uint8_t[bytes.size()];
//     std::copy(bytes.begin(), bytes.end(), data);
//     return {data, bytes.size()};
// }

// std::tuple<std::string, std::vector<std::vector<uint8_t>>> G1tDecompile(std::vector<uint8_t> g1t_data);
// std::vector<uint8_t> G1tCompile(std::vector<std::vector<uint8_t>> dds_data);

PYBIND11_MODULE(g1t_module, m) {
    m.doc() = "Python bindings for G1tDecompile and G1tCompile functions";

    // Expose G1tDecompile function
    m.def("G1tDecompile", [](py::bytes g1t_data) {
        auto g1t_vector = std::vector<uint8_t>(g1t_data.begin(), g1t_data.end());
        auto result = G1tDecompile(g1t_vector);
        return py::make_tuple(
            std::get<0>(result),
            std::get<1>(result)
        );
    }, "Decompile G1t data",
       py::arg("g1t_data"));

    // Expose G1tCompile function
    m.def("G1tCompile", [](std::vector<py::bytes> dds_data) {
        std::vector<std::vector<uint8_t>> dds_vector;
        for (const auto& dds : dds_data) {
            dds_vector.emplace_back(dds.begin(), dds.end());
        }
        return py::bytes(reinterpret_cast<const char*>(G1tCompile(dds_vector).data()), G1tCompile(dds_vector).size());
    }, "Compile G1t data from DDS data",
       py::arg("dds_data"));
}