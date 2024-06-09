#pragma once
#include <vector>
#include <string>
#include <cstdint>

extern "C" {

// Define a simple C-compatible struct
struct CResult {
    const char* metadata;
    uint8_t** dds_data;
    size_t* dds_sizes;
    size_t num_dds;
};

// Define C-compatible functions
CResult G1tDecompile(const uint8_t* g1t_data, size_t g1t_size);
void free_cresult(CResult result); // To free allocated memory

struct CBytes {
    const uint8_t* data;
    size_t size;
};

// Function to compile G1t data
CBytes G1tCompile(const uint8_t** dds_data, const size_t* dds_sizes, size_t num_dds);

}
