#ifndef UTILS_H
#define UTILS_H

#include <string>
#include <cstdint>
#include <cstdarg>
#include <cstdio>  // Include cstdio for printf-related functions

#ifdef  _MSC_VER
#define fseeko fseek
#define ftello ftell
#define fseeko64 _fseeki64
#define ftello64 _ftelli64
#define off64_t int64_t
#endif

#define DPRINTF DebugPrintf
void AesEcbDecrypt(void *buf, size_t size, const uint8_t *key, int key_size);
void AesEcbEncrypt(void *buf, size_t size, const uint8_t *key, int key_size);
bool HasOnlyDigits(const std::string &str);
size_t GetFileSize(const std::string &path);
size_t GetFileSize(const std::u16string &path);
uint32_t GetUnsigned(const std::string &str, uint32_t default_value=0);
uint8_t *ReadFile(const std::string &path, size_t *psize, bool show_error = false);

std::string U8ToHexString(uint8_t value, bool zeropad, bool prefix=true);
std::string U16ToHexString(uint16_t value, bool zeropad, bool prefix=true);
std::string U32ToHexString(uint32_t value, bool zeropad, bool prefix=true);
std::string U64ToHexString(uint64_t value, bool zeropad, bool prefix=true);
// Correct the declaration of DebugPrintf
int DebugPrintf(const char* fmt, ...);

std::string ToLowerCase(const std::string & str);
uint32_t GetShortVersion(uint32_t version);
uint32_t GetLongVersion(uint32_t version);
float HalfToFloat(uint16_t h);
bool BeginsWith(const std::string &str, const std::string &substr, bool case_sensitive);

#endif // UTILS_H
