#include <iostream>
// #include "../eternity_common/DOA6/G1mFile.h"
#include "G1tFile.h"
#include "DdsFile.h"
#include "../eternity_common/tinyxml/tinyxml.h"
#include "Utils.h"
#include "FilesOperations.h"
// #include "../DirectXTex/DirectXTex/DirectXTex.h"
#include <filesystem>
#include <unordered_map>
#include <json/json.h>
#include "../stb/stb_image.h"

struct DecompiledG1t {
    std::string metadata;
    std::vector<std::vector<uint8_t>> dds_data;
};


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
    for (auto& texture_data : data["textures"]) {
        std::vector<std::string> texture_keys = {"extra_header_version", "flags", "extra_header", "name"};
        for( const auto& key : texture_keys ) {
            if (!texture_data.isMember(key)) {
                std::cerr << "Invalid key in texture json: " << key << std::endl;
                return false;
            }
        }
    }
    
    return true;
}


// Forward declare the functions
DecompiledG1t G1tDecompile(std::vector<uint8_t> &g1t_data) {
    G1tFile g1t;
    std::vector<std::vector<uint8_t>> dds_data;
    if (!g1t.Load(g1t_data.data(), g1t_data.size())) {
        return DecompiledG1t{"Error loading g1t data", dds_data};
    }
    // printf("Loaded unk_1c: 0x%X\n", g1t.unk_1C);

    size_t i = 0;
    size_t size = g1t.GetNumTextures();
    while (i < size) {
        // DdsFile* dds = G1tFile::ToDDS(tex);
        DdsFile* dds = g1t.ToDDS(i);
        if (!dds) {
            return DecompiledG1t{"Error loading dds data", dds_data};
        }
        dds_data.push_back(dds->ToBytes());
        delete dds;
        i++;
    }
    std::string metadata = g1t.GetMetadataJson();
    return DecompiledG1t{metadata, dds_data};
}

std::vector<uint8_t> G1tCompile(const std::string& path, const std::string& metadata) {
    // std::cout << "G1tCompile metadata: " << metadata << std::endl;
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
    g1t.plattform = json_data["platform"].asUInt(); 
    g1t.unk_1C = json_data["unk_1C"].asUInt(); 
    g1t.version = json_data["version"].asUInt();
    // if (dds_data.size() != json_data["textures"].size()) {
    //     std::cerr << "Mismatch between number of textures and dds data" << std::endl;
    //     return std::vector<uint8_t>();
    // }
    int i = 0;
    std::stringstream ss;
    std::cout << "parsing textures..." << std::endl;
    // for (auto& dds_bytes: dds_data) {
    while (i < (int)json_data["textures"].size()) {
        Json::Value texture_data = json_data["textures"][i];
        std::string name = texture_data["name"].asString();
        std::string dds_path = path + "/" + name;
        if (!Utils::FileExists(dds_path)) {
            std::cerr << "File not found: " << dds_path << std::endl;
            return std::vector<uint8_t>();
        }
        std::vector<uint8_t> dds_bytes = FileToBytes(dds_path);

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
        for (auto& x : texture_data["extra_header"]) {
            uint8_t val = static_cast<uint8_t>(x.asUInt());
            printf("extra_header: 0x%X\n", val);
            tex.extra_header.push_back(val);
        }
        
        size_t size = texture_data["flags"].size();
        std::cout << "flags is an array size: " << size << std::endl;
        int k = 0;
        for (auto& flag : texture_data["flags"]) {
            uint8_t flag_val = static_cast<uint8_t>(flag.asUInt());
            if (k == 4) {
            } else {
                tex.unk_3[k] = flag_val;
            } 
            k++;
        }
        
        uint8_t extra_header_version = (uint8_t)(texture_data["extra_header_version"].asUInt());
        tex.extra_header_version = extra_header_version;

        g1t.textures.push_back(tex);
        i++;
    }

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

void print_usage(char *argv[])
{
    std::cout << "Usage: " << argv[0] << " <input.g1t> to extract all textures" << std::endl;
    std::cout << "       " << argv[0] << " <input directory> to pack all textures into g1t file" << std::endl;
}

int main(int argc, char *argv[])
{
    if (argc < 2)
    {
        print_usage(argv);
        return 1;
    }
    std::string path = argv[1];

    if (Utils::EndsWith(path, ".g1t", false))
    {
        std::vector<uint8_t> g1t_data = FileToBytes(path);
        DecompiledG1t res = G1tDecompile(g1t_data);
        if (startsWith(res.metadata, "Error")) {
            std::cerr << res.metadata << std::endl;
            return 1;
        }
        std::string dest_dir = path.substr(0, path.size() - 4);
        if (!Utils::DirExists(dest_dir)) {
            if (!Utils::Mkdir(dest_dir)) {
                std::cerr << "Failed to create directory: " << dest_dir << std::endl;
                return 1;
            }
        }
        if (!StringToFile(dest_dir + "/g1t.json", res.metadata)) {
            std::cerr << "Failed to save metadata to g1t.json" << std::endl;
            return 1;
        }
        for (size_t i = 0; i < res.dds_data.size(); i++) {
            std::string out_path = dest_dir + "/" + std::to_string(i) + ".dds";
            BytesToFile(res.dds_data[i], out_path);
        }


    }
    else if (std::filesystem::is_directory(path))
    {
      std::string json_path = path + "/g1t.json";
      if (!Utils::FileExists(json_path)) {
          std::cerr << "g1t.json not found in directory: " << path << std::endl;
          return 1;
      }
        std::string metadata = FileToString(json_path);
        std::vector<uint8_t> g1t_data = G1tCompile(path, metadata);
        if (g1t_data.empty()) {
            std::cerr << "Failed to compile g1t data" << std::endl;
            return 1;
        }
        std::string out_path = path + ".g1t";
        BytesToFile(g1t_data, out_path);
    }
    else
    {
        std::cerr << "Invalid argument, not g1t file nor directory (or directory empty): " << std::endl
                  << path << std::endl;
        return 1;
    }

    return 0;
}