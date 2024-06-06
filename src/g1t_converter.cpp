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
#include "../stb/stb_image.h"


struct G1tRecord
{
    std::string name;
    int width;
    int height;
    std::string formatStr;
    int format;
    int mips;
};

void print_usage(char *argv[])
{
    std::cout << "Usage: " << argv[0] << " <input.g1t> to extract all textures" << std::endl;
    std::cout << "       " << argv[0] << " <input directory> to pack all textures into g1t file" << std::endl;
}

std::unordered_map<std::string, G1tRecord> parseG1tCsv(const std::string &path)
{
    std::unordered_map<std::string, G1tRecord> records;
    std::vector<std::string> lines = ReadFileLines(path);
    for (const auto &line : lines)
    {
        std::vector<std::string> parts = SplitString(line, ';');
        if (parts.size() != 6)
        {
            std::cerr << "Invalid g1t.txt line elements count: " << line << " size: " << parts.size() << " expected: 6" << std::endl;
            continue;
        }
        if (!(isNumeric(parts[1]) && isNumeric(parts[2]) && isNumeric(parts[4]) && isNumeric(parts[5])))
        {
            std::cerr << "Invalid g1t.txt line, some elements are non integers: " << line << std::endl;
            continue;
        }
        G1tRecord rec = {
            parts[0],
            std::stoi(parts[1]),
            std::stoi(parts[2]),
            parts[3],
            std::stoi(parts[4]),
            std::stoi(parts[5])};

        records[rec.name] = rec;
    }
    return records;
}

bool extractG1tFile(const std::string &path)
{
    if (path.size() < 5)
    {
        std::cerr << "Invalid path: " << path << std::endl;
        return false;
    }
    if (!std::filesystem::exists(path))
    {
        std::cerr << "File not found: " << path << std::endl;
        return false;
    }
    if (!Utils::EndsWith(Utils::ToLowerCase(path), ".g1t"))
    {
        std::cerr << "Not a G1T file: " << path << std::endl;
        return false;
    }

    G1tFile g1t;
    if (!g1t.SmartLoad(path))
    {
        std::cerr << "Failed to load G1T file: " << path << std::endl;
        return false;
    }
    std::string dest_dir = path.substr(0, path.size() - 4);
    if (!Utils::Mkdir(dest_dir))
    {
        std::cerr << "Failed to create directory: " << dest_dir << std::endl;
        return false;
    }
    int i = 0;
    std::string g1t_csv;
    std::string d(";");
    std::vector<G1tTexture> textures = g1t.GetTextures();
    for (auto tex : textures)
    {
        DdsFile *dds = G1tFile::ToDDS(tex);
        std::cout << "Saving texture " << i << ".dds " << dds->GetWidth() << "x" << dds->GetHeight() << " format: " << dds->GetFormatName() << " mips: " << dds->GetMips() << std::endl;
        // g1t_csv += std::to_string(i) + d + std::to_string(tex.width) + d + std::to_string(tex.height) + d + std::to_string(tex.format) + d;
        g1t_csv += std::to_string(i) + d + std::to_string(tex.width) + d + std::to_string(tex.height) + d + dds->GetFormatName() + d;
        g1t_csv += std::to_string(dds->GetFormat()) + d + std::to_string(dds->GetMips()) + d + "\n";
        if (!dds)
        {
            std::cerr << "Failed to convert texture " << i << " to DDS" << std::endl;
            return false;
        }
        std::string out_path = dest_dir + "/" + std::to_string(i) + ".dds";
        if (!dds->SaveToFile(out_path, true, false))
        {
            std::cerr << "Failed to save texture " << out_path << " to DDS" << std::endl;
            return false;
        }
        delete dds;
        i++;
    }
    if (!StringToFile(dest_dir + "/g1t.txt", g1t_csv))
    {
        std::cerr << "Failed to save g1t.txt" << std::endl;
        return false;
    }
    return true;
}

bool dirToG1t(const std::string &path)
{
    std::vector<std::string> files = listDir(path);
    if (files.empty())
    {
        std::cerr << "Directory is empty: " << path << std::endl;
        return false;
    }
    G1tFile g1t;
    std::string g1t_csv_path = path + "\\g1t.txt";
    if (!std::filesystem::exists(g1t_csv_path))
    {
        std::cerr << "g1t.txt not found in directory: " << path << std::endl;
        return false;
    }
    std::unordered_map<std::string, G1tRecord> records = parseG1tCsv(g1t_csv_path);
    
    if (records.empty())
    {
        std::cerr << "g1t.txt is empty or couldn't be parsed: " << g1t_csv_path << std::endl;
        return false;
    }

    for (const auto &file : files)
    {
        if (strcmp(file.c_str(), g1t_csv_path.c_str()) == 0) continue;
        std::vector<uint8_t> rawdata;
        if (isValidImagePath(file)) {
            rawdata = FileToBytes(file);
        } else {
            std::cerr << "Invalid file, not png nor dds: " << file << std::endl;
            continue;
        }
        std::string key = getBaseNameWithoutExtension(file);
        if (key.empty()) {
            std::cerr << "Invalid file name, empty name: " << file << std::endl;
            continue;
        }
        if (records.find(key) != records.end()) {
            G1tRecord rec = records[key];
            if (isPngFile(file))
                rawdata = createDdsDataFromPngData(rawdata, rec.mips, rec.format);
            // DdsFile dds(rec.format, rec.width, rec.height, rec.mips, rawdata.data(), rawdata.size());
            DdsFile dds;
            // dds.LoadFromFile(file);
            if (!dds.Load(rawdata.data(), rawdata.size())) {
                std::cerr << "Failed to load dds/png file: " << file << std::endl;
                continue;
            }
            std::cout << "Adding dds: " << dds.GetWidth() << "x" << dds.GetHeight() << " format: " << dds.GetFormatName() << " mips: " << dds.GetMips() << std::endl; 
            G1tTexture tex;
            if (!G1tFile::FromDDS(tex, dds, nullptr, nullptr)) {
                std::cerr << "Failed to convert: " << std::endl;
                // dds.DisplayInfo();
                continue;
            }
            g1t.textures.push_back(tex);
            
            //found key
        } else {
            std::cout << "Key not found in g1t.txt, skipping: " << key << std::endl;
        }
    }
    if (g1t.textures.empty()) {
        std::cerr << "No textures could be added to g1t file: "  << std::endl;
        return false;
    }
    std::string out_path = path + ".g1t";
    if (!g1t.SaveToFile(out_path, true, false)) {
        std::cerr << "Failed to save g1t file: " << out_path << std::endl;
        return false;
    }

    return true;
}

int main(int argc, char *argv[])
{
    if (argc < 2)
    {
        print_usage(argv);
        // for (const auto &file : listDir("./8279b3ed"))
        // {
        //     std::cout << file << std::endl;
        // }
        return 1;
    }
    std::string path = argv[1];

    if (Utils::EndsWith(Utils::ToLowerCase(path), ".g1t"))
    {
        if (!extractG1tFile(path))
        {
            std::cout << "Failure" << std::endl;
            return 1;
        }
        else
        {
            std::cout << "Success" << std::endl;
            return 0;
        }
    }
    else if (std::filesystem::is_directory(path))
    {
        std::cout << "Packing directory" << std::endl;
        if (!dirToG1t(path)) {
            std::cout << "Failure" << std::endl;
            return 1;
        }
        else
        {
            std::cout << "Success" << std::endl;
            return 0;
        }
    }
    else
    {
        std::cerr << "Invalid argument, not g1t file nor directory (or directory empty): " << std::endl
                  << path << std::endl;
        return 1;
    }

    return 0;
}