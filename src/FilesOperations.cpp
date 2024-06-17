#include <filesystem>
#include <string>
#include <vector>
#include <fstream>
#include <sstream>
#include <algorithm>
#include "FilesOperations.h"
#include "Utils.h"
#include <cstdint>
#include <cctype>     // For std::tolower
#include <cstdarg>
#include <cstdio>

// int DebugPrintf(const char* fmt, ...) {
//     va_list args;
//     va_start(args, fmt);
//     int result = vprintf(fmt, args);
//     va_end(args);
//     return result;
// }

bool startsWith(const std::string& str, const std::string& prefix) {
    // Check if the prefix is longer than the string
    if (prefix.size() > str.size()) {
        return false;
    }
    // Compare the start of the string with the prefix
    return str.compare(0, prefix.size(), prefix) == 0;
}

std::string ToLowerCase(const std::string & str)
{
	std::string ret = str;
	
	for (char &c : ret)
	{
		if (c >= 'A' && c <= 'Z')
		{
			c = c + ('a' - 'A');
		}
	}
	
	return ret;
}

uint32_t GetShortVersion(uint32_t version)
{
    uint32_t result = 0;
    uint8_t *b = (uint8_t *)&version;

    uint32_t mult = 1;

    for (int i = 0; i < 4; i++)
    {
        if (b[i] >= '0' && b[i] <= '9')
        {
            result += (b[i] - '0') * mult;
            mult = mult*10;
        }
        else
            return 0xFFFFFFFF;
    }

    return result;
}


uint32_t GetLongVersion(uint32_t version)
{
    uint32_t result;

    if (version >= 10000)
        return 0xFFFFFFFF;

    uint32_t t = version / 1000;
    uint32_t h = (version / 100) % 10;
    uint32_t d = (version / 10) % 10;
    uint32_t u = version % 10;

    result = u + '0';
    result |= (d + '0') << 8;
    result |= (h + '0') << 16;
    result |= (t + '0') << 24;

    return result;
}


float HalfToFloat(uint16_t h)
{
    auto Mantissa = static_cast<uint32_t>(h & 0x03FF);

    uint32_t Exponent = (h & 0x7C00);
    if (Exponent == 0x7C00) // INF/NAN
    {
        Exponent = 0x8f;
    }
    else if (Exponent != 0)  // The value is normalized
    {
        Exponent = static_cast<uint32_t>((static_cast<int>(h) >> 10) & 0x1F);
    }
    else if (Mantissa != 0)     // The value is denormalized
    {
        // Normalize the value in the resulting float
        Exponent = 1;

        do
        {
            Exponent--;
            Mantissa <<= 1;
        } while ((Mantissa & 0x0400) == 0);

        Mantissa &= 0x03FF;
    }
    else                        // The value is zero
    {
        Exponent = static_cast<uint32_t>(-112);
    }

    uint32_t Result =
        ((static_cast<uint32_t>(h) & 0x8000) << 16) // Sign
        | ((Exponent + 112) << 23)                      // Exponent
        | (Mantissa << 13);                             // Mantissa

    return reinterpret_cast<float*>(&Result)[0];
}


bool BeginsWith(const std::string &str, const std::string &substr, bool case_sensitive)
{
    size_t len1 = str.length();
    size_t len2 = substr.length();

    if (len2 > len1)
        return false;

    if (case_sensitive)
        return (str.substr(0, len2) == substr);

    std::string lstr = ToLowerCase(str);
    std::string lsubstr = ToLowerCase(substr);

    return (lstr.substr(0, len2) == lsubstr);
}


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

void BytesToFile(const std::vector<uint8_t>& data, const std::string& filePath) {
    // Open the file in binary mode
    std::ofstream file(filePath, std::ios::binary);
    if (!file) {
        throw std::runtime_error("Unable to open file for writing: " + filePath);
    }

    // Write the data to the file
    file.write(reinterpret_cast<const char*>(data.data()), data.size());

    // Check if the write operation succeeded
    if (!file) {
        throw std::runtime_error("Error occurred while writing to the file: " + filePath);
    }

    // Close the file
    file.close();
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