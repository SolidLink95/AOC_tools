#include "FilesOperations.h"

#include <filesystem>
#include <unordered_map>
#include <sstream>
#include <cstdio>
#include <iostream>
#include "../eternity_common/DOA6/KidsObjDBFile.h"
#include "KtidFile.h"
#include "MtlFile.h"
#include "FilesOperations.h"
#include "Utils.h"

bool TextToBinary(const std::string& path) {
    std::vector<uint8_t> res;
    std::string dest_file;
    if (path.size() > 5) {
        dest_file = path.substr(0, path.size() - 4);
    } else {
        dest_file = path + ".bin";
    }
    KidsObjDBFile kdb;
    if (kdb.LoadFromFile(path)) {
        std::cout << "Loaded KDB file" << std::endl;
        if (kdb.SaveToFile(dest_file, true, false)) {
            return true;
        }
    }
    KtidFile ktid;
    if (ktid.LoadFromFile(path)) {
        std::cout << "Loaded KTID file" << std::endl;
        if (ktid.SaveToFile(dest_file)) {
            return true;
        }
    }
    MtlFile mtl;
    if (mtl.LoadFromFile(path)) {
        std::cout << "Loaded MTL file" << std::endl;
        if (mtl.SaveToFile(dest_file)) {
            return true;
        }
    }
    return false;

}

std::string BinaryToText(const std::vector<uint8_t> &data, const std::string &path)
{
    std::string res;
    KidsObjDBFile kdb;
    if (kdb.Load(data.data(), data.size())) {
        std::cout << "Loaded KDB file " << std::endl;
        TiXmlDocument *doc = kdb.Decompile();
        if (doc != nullptr){
            if (doc->SaveFile((path + ".xml").c_str())) {
                std::cout << "Saved KDB to XML" << std::endl;
                exit(0);
            }
        }
        else {
            std::cerr << "Failed to decompile KDB file" << std::endl;
        }
    }
    KtidFile ktid;
    if (ktid.Load(data.data(), data.size()))
    {
        std::cout << "Loaded KTID file" << std::endl;
        if (ktid.SaveToString(res, path, nullptr, false)) {
            return res;
        }
        else {
            std::cerr << "Failed to save KTID to string" << std::endl;
        }
    }
    MtlFile mtl;
    if (mtl.Load(data.data(), data.size()))
    {
        std::cout << "Loaded MTL file" << std::endl;
        if (mtl.SaveToString(res, path, nullptr, false)){
            return res;
        }
        else {
            std::cerr << "Failed to save MTL to string" << std::endl;
        }
    }

    return res;
}

int main(int argc, char *argv[])
{
    if (argc < 2)
    {
        std::cerr << "Usage: " << argv[0] << " <input file>" << std::endl;
        return 1;
    }
    std::string mode;
    if (argc > 2) {
        mode = argv[2];
    }
    std::string path = argv[1];
    std::vector<uint8_t> data = FileToBytes(path);
    if (Utils::EndsWith(Utils::ToLowerCase(path), ".xml"))
    {
        if (TextToBinary(path)) {
            std::cout << "Success" << std::endl;
            return 0;
        }
        else {
            std::cerr << "Failure" << std::endl;
            return 1;
        }
    }
    std::string res = BinaryToText(data, path);
    if (res.empty()) {
        std::cout << "Failure: unable to convert binary to text" << std::endl;
    } else {
        StringToFile(path + ".xml", res);
    }

    return 0;
}