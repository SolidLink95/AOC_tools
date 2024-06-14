// bindings.cpp
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>
#include <vector>
#include <cstdint>
#include <string>
#include <iostream>
#include "G1tFile.h"
#include "DdsFile.h"
#include <thread>
#include <chrono>
#include <sstream>
#include <json/json.h>

namespace py = pybind11;

bool ValidateJsonData(Json::Value& data) {
    std::vector<std::string> keys = {"version", "platform", "textures"};
    for( const auto& key : keys ) {
        if (!data.isMember(key)) {
            std::cerr << "Invalid key in json: " << key << std::endl;
            return false;
        }
    }
    if (!data["textures"].isArray()) {
        std::cerr << "textures key is not an array" << std::endl;
        return false;
    }
    
    return true;
}


// Forward declare the functions
std::tuple<std::string, std::vector<std::vector<uint8_t>>> G1tDecompile(std::vector<uint8_t> &g1t_data) {
    G1tFile g1t;
    std::vector<std::vector<uint8_t>> dds_data;
    if (!g1t.Load(g1t_data.data(), g1t_data.size())) {
        return std::make_tuple("Error loading g1t data", dds_data);
    }
    
    // std::cout << "hdr->version: " << g1t.version << std::endl;
    // std::cout << "hdr->plattform: " << g1t.plattform << std::endl;

    size_t i = 0;
    size_t size = g1t.GetNumTextures();
    // auto textures = g1t.GetTextures();
    // for (const auto& tex : textures) {
    while (i < size) {
        // DdsFile* dds = G1tFile::ToDDS(tex);
        DdsFile* dds = g1t.ToDDS(i);
        if (!dds) {
            return std::make_tuple("Error loading dds data", dds_data);
        }
        dds_data.push_back(dds->ToBytes());
        delete dds;
        i++;
    }
    // std::string metadata = g1t.GetMetadataCsv();
    std::string metadata = g1t.GetMetadataJson();
    return std::make_tuple(metadata, dds_data);
}

std::vector<uint8_t> G1tCompile(std::vector<std::vector<uint8_t>> &dds_data, const std::string& metadata) {
    std::cout << "G1tCompile metadata: " << metadata << std::endl;
    Json::CharReaderBuilder builder;
    Json::CharReader* reader = builder.newCharReader();
    Json::Value json_data;
    std::string errs;
    bool parsingSuccess = reader->parse(metadata.c_str(), metadata.c_str() + metadata.size(), &json_data, &errs);
    delete reader;
    if (!parsingSuccess) {
        std::cerr << "Failed to parse metadata: " << errs << std::endl;
        return std::vector<uint8_t>();
    }
    if (!ValidateJsonData(json_data)) {
        return std::vector<uint8_t>();
    }


    G1tFile g1t;
    g1t.plattform = json_data["platform"].asUInt(); //Windows
    g1t.version = json_data["version"].asUInt();
    if (dds_data.size() != json_data["textures"].size()) {
        std::cerr << "Mismatch between number of textures and dds data" << std::endl;
        return std::vector<uint8_t>();
    }
    // g1t.version = 0x30303630;
    // std::vector<uint8_t> bytes;
    int i = 0;
    std::stringstream ss;
    std::cout << "parsing textures..." << std::endl;
    for (auto& dds_bytes: dds_data) {
        printf("asdf1\n");
        Json::Value texture_data = json_data["textures"][i];
        printf("asdf2\n");
        DdsFile dds;
        // printf("asdf3\n");
        if (!dds.Load(dds_bytes.data(), dds_bytes.size())) {
            std::cerr << "Failed to load dds data" << std::endl;
            return std::vector<uint8_t>();
        }
        G1tTexture tex;
        if (!G1tFile::FromDDS(tex, dds, nullptr, nullptr)) {
            std::cerr << "Failed to convert dds to g1t texture" << std::endl;
            return std::vector<uint8_t>();
        }
        tex.sys = static_cast<uint8_t>(texture_data["sys"].asUInt());
        // printf("asdf4\n");
        
        if (texture_data.isMember("flags")) {
            std::cout << "flags is an array size: " << texture_data["flags"].size() << std::endl;
            int k = 0;
            for (auto& flag : texture_data["flags"]) { 
                uint8_t flag_val = static_cast<uint8_t>(flag.asUInt());
                tex.flags[k] = flag_val;
                k++;
            }
        }
        printf("asdf5\n");

        g1t.textures.push_back(tex);
        // std::cout << "G1tCompile texture id: " << i << " sys: " << tex.sys  << std::endl;
        // ss << "G1tCompile texture id: " << i << " sys: " << tex.sys  << std::endl;
        i++;
    }
    std::cout << "Textures parsed "  << std::endl;

    //For some absurd reason this line along with stringstream operation must remain as is
    //in order to ensure the correct g1t bytes parsing
    // g1t.GetMetadataCsv();
    // std::this_thread::sleep_for(std::chrono::seconds(1));
    size_t size;
	
    uint8_t *buf = g1t.Save(&size);
	
	if (!buf) {
        std::cerr << "Failed to save g1t data (::Save function)" << std::endl;
		return std::vector<uint8_t>();
    }
	std::vector<uint8_t> res(buf, buf + size);
	delete[] buf;
    return res;
}

PYBIND11_MODULE(g1t_module, m) {
    m.doc() = "Python bindings for G1tDecompile and G1tCompile functions";

    // Expose G1tDecompile function
    m.def("G1tDecompile", [](py::bytes g1t_data) {
        // Convert py::bytes to std::vector<uint8_t>
        std::string g1t_str = g1t_data;  // convert py::bytes to std::string
        std::vector<uint8_t> g1t_vector(g1t_str.begin(), g1t_str.end());

        // Call the C++ function
        auto result = G1tDecompile(g1t_vector);
        std::string metadata = std::get<0>(result);
        std::vector<std::vector<uint8_t>> dds_data = std::get<1>(result);

        // Convert std::vector<std::vector<uint8_t>> to list of bytes
        py::list dds_list;
        for (const auto& dds : dds_data) {
            dds_list.append(py::bytes(reinterpret_cast<const char*>(dds.data()), dds.size()));
        }

        return py::make_tuple(metadata, dds_list);
    }, "Decompile G1t data", py::arg("g1t_data"));

    // Expose G1tCompile function
   m.def("G1tCompile", [](py::list dds_list, const std::string& metadata) {
        std::vector<std::vector<uint8_t>> dds_vector;
        for (auto item : dds_list) {
            py::bytes dds_data = item.cast<py::bytes>();
            std::string dds_str = dds_data;
            dds_vector.emplace_back(dds_str.begin(), dds_str.end());
        }

        std::vector<uint8_t> compiled_data = G1tCompile(dds_vector, metadata);

        return py::bytes(reinterpret_cast<const char*>(compiled_data.data()), compiled_data.size());
    }, "Compile G1t data from DDS data and metadata", py::arg("dds_data"), py::arg("metadata"));
}
