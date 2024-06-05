#ifndef FILESOPERATIONS_H
#define FILESOPERATIONS_H


#include <iostream>
#include <filesystem>
#include <vector>
#include <string>

std::vector<std::string> listDir(const std::string& path);
bool StringToFile(const std::string& path, const std::string& content);

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


#endif // FILESOPERATIONS_H