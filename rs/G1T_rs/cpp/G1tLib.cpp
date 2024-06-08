#include "../../../src/G1tFile.h"

std::tuple<std::string, std::vector<std::vector<uint8_t>>> G1tDecompile(std::vector<uint8_t> g1t_data) {
    std::string metadata;
    std::vector<std::vector<uint8_t>> dds_data;
    G1tFile g1t;
    if (!g1t.Load(g1t_data.data(), g1t.size())) {
        return std::make_tuple("Error: unable to load g1t data", dds_data);
    }
    

}