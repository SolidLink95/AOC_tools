#ifndef UTILS_H
#define UTILS_H

#include <string>
#include <cstdint>
#include <cstdarg>
#include <cstdio>  // Include cstdio for printf-related functions

#define DPRINTF DebugPrintf

// Correct the declaration of DebugPrintf
int DebugPrintf(const char* fmt, ...);

std::string ToLowerCase(const std::string & str);
uint32_t GetShortVersion(uint32_t version);
uint32_t GetLongVersion(uint32_t version);
float HalfToFloat(uint16_t h);
bool BeginsWith(const std::string &str, const std::string &substr, bool case_sensitive);

#endif // UTILS_H
