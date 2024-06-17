// #include "FilesOperations.h"
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <filesystem>
#include <unordered_map>
#include <sstream>
#include <cstdio>
#include <iostream>
#include <vector>
#include <string>
#include <json/json.h>
#ifdef _WIN32
    #include <io.h>       // Windows-specific functions
    #include <fcntl.h>    // File control options
    #include <windows.h>  // Windows API functions
#else
    #include <unistd.h>   // For dup, dup2, etc. (POSIX systems)
#endif
#include "AocKidsObjDBFile.h"
// #include "FilesOperations.h"
#include "../../G1tPy/cpp/Utils.h"



std::string KidsObToString(const std::vector<uint8_t> &data) {
    std::string res;
    KidsObjDBFile kdb;

    // Load the KDB file
    if (!kdb.Load(data.data(), data.size())) {
        std::cerr << "Failed to load KDB file " << std::endl;
        return res;
    }

    Json::Value json_data;

    // Iterate over objects in kdb
    for (auto& ob : kdb.objects) {
        Json::Value json_ob;
        Json::Value columns;
        std::string name = U32ToHexString(ob.name, true, false);

        // Populate json_ob fields
        json_ob["type"] = U32ToHexString(ob.type, true, false);
        json_ob["version"] = U32ToHexString(ob.version, true, false);

        // Iterate over columns in object
        for (auto& col : ob.columns) {
            Json::Value json_col;
            Json::Value json_rows;

            // Populate json_col fields
            json_col["name"] = U32ToHexString(col.name, true, false);
            json_col["type"] = U32ToHexString(col.type, true, false);

            // Iterate over rows in column
            for (auto& val : col.values32) {
                json_rows.append(U32ToHexString(val.u32, true, false));
            }

            json_col["rows"] = json_rows;
            columns.append(json_col);
        }

        json_ob["columns"] = columns;
        json_data[name] = json_ob;
    }

    // Use StreamWriterBuilder to serialize json_data to a string
    Json::StreamWriterBuilder writer;
    writer["indentation"] = "";  // Set indentation to empty for compact output
    res = Json::writeString(writer, json_data);

    return res;
}



namespace py = pybind11;

PYBIND11_MODULE(kidsob_module, m) {
    m.doc() = "Python bindings for parsing kidsobjdb/kidssingletondb binary data";

    m.def("KidsObToString", &KidsObToString, "Convert kidsobjdb/kidssingletondb binary data to xml string");
}