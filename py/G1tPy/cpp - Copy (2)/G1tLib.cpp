// #include "../../../src/G1tFile.h"
// #include "../../../src/DdsFile.h"
#include "G1tLib.h"
// #include "./eternity_common/DOA6/G1tFile.h"
// #include "./eternity_common/DdsFile.h"
#include <string.h>
#include <string>

std::tuple<std::string, std::vector<std::vector<uint8_t>>> G1tDecompile(std::vector<uint8_t>& g1t_data) {
   
    std::string metadata = "Gowno cpp";

    
    std::vector<std::vector<uint8_t>> asdf;
    return std::make_tuple(metadata, asdf);
}

std::vector<uint8_t> G1tCompile(std::vector<std::vector<uint8_t>>& dds_data) {
    std::vector<uint8_t> bytes;
    return bytes;
}
