#include <filesystem>
#include <string>
#include <vector>
#include <fstream>
#include <sstream>
#include <algorithm>
#include "FilesOperations.h"
#include "Utils.h"


std::vector<std::string> listDir(const std::string& path) {
    std::vector<std::string> files;
    for (const auto& entry : std::filesystem::directory_iterator(path)) {
        std::filesystem::path entry_path = entry.path();
        if (std::filesystem::is_regular_file(entry_path)) {
            files.push_back(entry_path.string());
        }
    }
    std::sort(files.begin(), files.end(), naturalCompare);
    return files;
}

bool StringToFile(const std::string& path, const std::string& content) {
     std::ofstream out_file(path);

    if (!out_file) {
        return false;
    }

    out_file << content;

    out_file.close();

    return true;
}

std::string FileToString(const std::string& path) {
    // Create an input file stream (ifstream) object
    std::ifstream in_file(path);

    // Check if the file was successfully opened
    if (!in_file) {
        throw std::runtime_error("Could not open file");
    }

    // Use a string stream to read the entire file content
    std::stringstream buffer;
    buffer << in_file.rdbuf();

    // Close the file
    in_file.close();

    // Return the file content as a string
    return buffer.str();
}

std::vector<std::string> ReadFileLines(const std::string& path) {
    std::ifstream in_file(path);
    if (!in_file) {
        throw std::runtime_error("Could not open file");
    }
    std::vector<std::string> lines;
    std::string line;
    while (std::getline(in_file, line)) {
        lines.push_back(line);
    }
    in_file.close();
    return lines;
}

bool naturalCompare(const std::string& a, const std::string& b) {
    auto ait = a.begin();
    auto bit = b.begin();

    while (ait != a.end() && bit != b.end()) {
        if (std::isdigit(*ait) && std::isdigit(*bit)) {
            // Compare numbers
            std::string num1, num2;

            while (ait != a.end() && std::isdigit(*ait)) {
                num1 += *ait;
                ++ait;
            }
            while (bit != b.end() && std::isdigit(*bit)) {
                num2 += *bit;
                ++bit;
            }

            if (num1 != num2) {
                return std::stoi(num1) < std::stoi(num2);
            }
        } else {
            // Compare characters
            if (*ait != *bit) {
                return *ait < *bit;
            }
            ++ait;
            ++bit;
        }
    }

    return a.size() < b.size();
}

std::vector<std::string> SplitString(const std::string& str, char delimiter) {
    std::vector<std::string> tokens;
    std::string token;
    std::istringstream tokenStream(str);
    while (std::getline(tokenStream, token, delimiter)) {
        tokens.push_back(token);
    }
    return tokens;
}

bool isDdsFile(const std::string& path) {
    return Utils::EndsWith(Utils::ToLowerCase(path), ".dds");
}

bool isPngFile(const std::string& path) {
    return Utils::EndsWith(Utils::ToLowerCase(path), ".png");
}

bool isValidImagePath(const std::string& path) {
    return isDdsFile(path) || isPngFile(path);
}

std::vector<uint8_t> FileToBytes(const std::string& path) {
    std::ifstream in_file(path, std::ios::binary);
    if (!in_file) {
        throw std::runtime_error("Could not open file");
    }
    std::vector<uint8_t> buffer((std::istreambuf_iterator<char>(in_file)), std::istreambuf_iterator<char>());
    in_file.close();
    return buffer;
}

bool isNumeric(const std::string& s) {
    return !s.empty() && std::all_of(s.begin(), s.end(), ::isdigit);
}

std::string getBaseNameWithoutExtension(const std::string& path) {
    // Extract the base name
    std::string base_name = std::filesystem::path(path).filename().string();
    
    // Remove the last four characters (e.g., ".dds")
    if (base_name.size() > 4) {
        base_name = base_name.substr(0, base_name.size() - 4);
    }
    
    return base_name;
}