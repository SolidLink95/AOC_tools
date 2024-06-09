// #include <pybind11/pybind11.h>
// #include <pybind11/stl.h>
// #include <pybind11/numpy.h>
// #include "../../../src/G1tFile.h"
// #include "../../../src/DdsFile.h"
#include <string.h>
#include <vector>
#include <cstdint>


std::tuple<std::string, std::vector<std::vector<uint8_t>>> G1tDecompile(std::vector<uint8_t> g1t_data);
std::vector<uint8_t> G1tCompile(std::vector<std::vector<uint8_t>> dds_data);

// 
