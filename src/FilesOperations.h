#ifndef FILESOPERATIONS_H
#define FILESOPERATIONS_H


#include <iostream>
#include <filesystem>
#include <vector>
#include <string>
#include <cstdint>
#include <cstdarg>
#include <cstdio> 

std::vector<std::string> listDir(const std::string& path);
bool StringToFile(const std::string& path, const std::string& content);
bool startsWith(const std::string& str, const std::string& prefix);
std::string FileToString(const std::string& path);
std::vector<std::string> ReadFileLines(const std::string& path);
bool naturalCompare(const std::string& a, const std::string& b);
std::vector<std::string> SplitString(const std::string& str, char delimiter);
bool isDdsFile(const std::string& path);
bool isPngFile(const std::string& path);
bool isValidImagePath(const std::string& path);
std::vector<uint8_t> FileToBytes(const std::string& path);
bool isNumeric(const std::string& s);
std::string getBaseNameWithoutExtension(const std::string& path);
void BytesToFile(const std::vector<uint8_t>& data, const std::string& filePath);


#define DPRINTF DebugPrintf

// Correct the declaration of DebugPrintf
int DebugPrintf(const char* fmt, ...);

std::string ToLowerCase(const std::string & str);
uint32_t GetShortVersion(uint32_t version);
uint32_t GetLongVersion(uint32_t version);
float HalfToFloat(uint16_t h);
bool BeginsWith(const std::string &str, const std::string &substr, bool case_sensitive);

#endif // FILESOPERATIONS_H