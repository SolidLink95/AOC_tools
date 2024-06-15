#include "FilesOperations.h"

#include <filesystem>
#include <unordered_map>
#include <sstream>
#include <cstdio>
#include <iostream>
#include "../eternity_common/DOA6/KidsObjDBFile.h"
#include "../eternity_common/DOA6/KtidFile.h"
#include "../eternity_common/DOA6/MtlFile.h"
// #include "../eternity_common/DOA6/SrsaFile.h"
// #include "../eternity_common/DOA6/SrstFile.h"
#include "FilesOperations.h"
#include "Utils.h"


std::string TiXmlDocumentToString(TiXmlDocument doc) {
    // Redirect stdout to a temporary file
    FILE* temp = tmpfile();
    if (temp == nullptr) {
        perror("tmpfile");
        exit(EXIT_FAILURE);
    }

    int stdout_fd = dup(STDOUT_FILENO);
    if (stdout_fd == -1) {
        perror("dup");
        exit(EXIT_FAILURE);
    }

    if (dup2(fileno(temp), STDOUT_FILENO) == -1) {
        perror("dup2");
        exit(EXIT_FAILURE);
    }

    // Example output to stdout
    doc.Print();

    // Restore stdout
    fflush(stdout);
    dup2(stdout_fd, STDOUT_FILENO);
    close(stdout_fd);

    // Read from the temporary file
    fseek(temp, 0, SEEK_SET);
    std::stringstream ss;
    char buffer[1024];
    while (fgets(buffer, sizeof(buffer), temp) != nullptr) {
        ss << buffer;
    }
    fclose(temp);

    return ss.str();
}


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

std::string KidsObToString(const std::vector<uint8_t> &data) {
    std::string res;
    KidsObjDBFile kdb;
    if (kdb.Load(data.data(), data.size())) {
        std::cout << "Loaded KDB file " << std::endl;
        TiXmlDocument *doc = kdb.Decompile();
        if (doc) {
            res = TiXmlDocumentToString(*doc);
            delete doc; // Ensure proper cleanup
        } else {
            std::cerr << "Failed to decompile KDB file" << std::endl;
        }
        if (!res.empty()) {
            std::cout << "Converted KDB" << std::endl;
            return res;
        } else {
            std::cerr << "Failed to save KDB to string" << std::endl;
        }
    }
    return res;
}

std::string KtidToString(const std::vector<uint8_t> &data) {
    std::string res;
    KtidFile ktid;
    if (ktid.Load(data.data(), data.size()))
    {
        std::cout << "Loaded KTID file" << std::endl;
        TiXmlDocument *doc = ktid.Decompile();
        if (doc) {
            res = TiXmlDocumentToString(*doc);
            delete doc; // Ensure proper cleanup
        } else {
            std::cerr << "Failed to decompile KTID file" << std::endl;
        }
        if (!res.empty()) {
            std::cout << "Converted KTID" << std::endl;
            return res;
        } else {
            std::cerr << "Failed to save KTID to string" << std::endl;
        }
    }
    return res;
}

std::string MtlToString(const std::vector<uint8_t> &data) {
    std::string res;
    MtlFile mtl;
    if (mtl.Load(data.data(), data.size()))
    {
        std::cout << "Loaded MTL file" << std::endl;
        TiXmlDocument *doc = mtl.Decompile();
        if (doc) {
            res = TiXmlDocumentToString(*doc);
            delete doc; // Ensure proper cleanup
        } else {
            std::cerr << "Failed to decompile MTL file" << std::endl;
        }
        if (!res.empty()) {
            std::cout << "Converted MTL" << std::endl;
            return res;
        } else {
            std::cerr << "Failed to save MTL to string" << std::endl;
        }
    }
    return res;
}

// std::string SrsaToString(const std::vector<uint8_t> &data) {
//     std::string res;
//     SrsaFile srsa;
//     if (srsa.Load(data.data(), data.size()))
//     {
//         std::cout << "Loaded SRSA file" << std::endl;
//         TiXmlDocument *doc = srsa.Decompile();
//         if (doc) {
//             res = TiXmlDocumentToString(*doc);
//             delete doc; // Ensure proper cleanup
//         } else {
//             std::cerr << "Failed to decompile SRSA file" << std::endl;
//         }
//         if (!res.empty()) {
//             std::cout << "Converted SRSA" << std::endl;
//             return res;
//         } else {
//             std::cerr << "Failed to save SRSA to string" << std::endl;
//         }
//     }
//     return res;
// }

// std::string SrstToString(const std::vector<uint8_t> &data) {
//     std::string res;
//     SrstFile srst;
//     if (srst.Load(data.data(), data.size()))
//     {
//         std::cout << "Loaded SRST file" << std::endl;
//         TiXmlDocument *doc = srst.Decompile();
//         if (doc) {
//             res = TiXmlDocumentToString(*doc);
//             delete doc; // Ensure proper cleanup
//         } else {
//             std::cerr << "Failed to decompile SRST file" << std::endl;
//         }
//         if (!res.empty()) {
//             std::cout << "Converted SRST" << std::endl;
//             return res;
//         } else {
//             std::cerr << "Failed to save SRST to string" << std::endl;
//         }
//     }
//     return res;
// }

std::string BinaryToText(const std::vector<uint8_t> &data, const std::string &path)
{
    std::string res = KidsObToString(data);
    if (!res.empty()) return res;
    res = KtidToString(data);
    if (!res.empty()) return res;
    res = MtlToString(data);
    if (!res.empty()) return res;
    // res = SrsaToString(data);
    // if (!res.empty()) return res;
    // res = SrstToString(data);

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
    if (Utils::EndsWith(Utils::ToLowerCase(path), ".xml") || Utils::EndsWith(Utils::ToLowerCase(path), ".txt"))
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