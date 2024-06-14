// #include "../../../src/G1tFile.h"
// #include "../../../src/DdsFile.h"
#include "G1tLib.h"
// #include "./eternity_common/DOA6/G1tFile.h"
// #include "./eternity_common/DdsFile.h"
#include <string.h>
#include <string>

std::tuple<std::string, std::vector<std::vector<uint8_t>>> G1tDecompile(std::vector<uint8_t>& g1t_data) {
    // G1tFile g1t;
    // std::vector<std::vector<uint8_t>> dds_data;
    // if (!g1t.Load(g1t_data, g1t_size)) {
    //     return {"Error: unable to load g1t data", nullptr, nullptr, 0};
    // }
    // auto textures = g1t.GetTextures();
    // for (const auto& tex : textures) {
    //     DdsFile* dds = G1tFile::ToDDS(tex);
    //     if (!dds) {
    //         return {"Error: unable to convert DDS file", nullptr, nullptr, 0};
    //     }
    //     dds_data.push_back(dds->ToBytes());
    //     delete dds;
    // }
    // std::string metadata = g1t.GetMetadataCsv();
    std::string metadata = "Gowno cpp";

    // Convert std::vector to C arrays
    // CResult result;
    // result.metadata = _strdup(metadata.c_str()); // Duplicate string for C usage
    // result.num_dds = dds_data.size();
    // result.dds_data = new uint8_t*[dds_data.size()];
    // result.dds_sizes = new size_t[dds_data.size()];
    // for (size_t i = 0; i < dds_data.size(); ++i) {
    //     result.dds_sizes[i] = dds_data[i].size();
    //     result.dds_data[i] = new uint8_t[result.dds_sizes[i]];
    //     std::copy(dds_data[i].begin(), dds_data[i].end(), result.dds_data[i]);
    // }
    std::vector<std::vector<uint8_t>> asdf;
    return std::make_tuple(metadata, asdf);
}

// void free_cresult(CResult result) {
//     if (result.metadata) {
//         free((void*)result.metadata);
//     }
//     for (size_t i = 0; i < result.num_dds; ++i) {
//         delete[] result.dds_data[i];
//     }
//     delete[] result.dds_data;
//     delete[] result.dds_sizes;
// }

std::vector<uint8_t> G1tCompile(std::vector<std::vector<uint8_t>>& dds_data) {
    // G1tFile g1t;
    // for (size_t i = 0; i < num_dds; ++i) {
    //     std::vector<uint8_t> dds_bytes(dds_data[i], dds_data[i] + dds_sizes[i]);
    //     DdsFile dds;
    //     if (!dds.Load(dds_bytes.data(), dds_bytes.size())) {
    //         return {nullptr, 0};
    //     }
    //     G1tTexture tex;
    //     if (!G1tFile::FromDDS(tex, dds, nullptr, nullptr)) {
    //         return {nullptr, 0};
    //     }
    //     g1t.textures.push_back(tex);
    // }
    // std::vector<uint8_t> bytes = g1t.ToBytes();
    std::vector<uint8_t> bytes;
    return bytes;
}
