#include "debug.h"
#include <cstdarg>
#include <cstdio>

// Implementation of DebugPrintf
int DebugPrintf(const char* fmt, ...) {
    va_list args;
    va_start(args, fmt);
    int result = vprintf(fmt, args);
    va_end(args);
    return result;
}

// Implement other functions similarly if needed
int UserPrintf(const char* fmt, ...) {
    va_list args;
    va_start(args, fmt);
    int result = vprintf(fmt, args);
    va_end(args);
    return result;
}

int FilePrintf(const char* fmt, ...) {
    va_list args;
    va_start(args, fmt);
    int result = vprintf(fmt, args);
    va_end(args);
    return result;
}

int FatalPrintf(bool ask, const char* fmt, ...) {
    va_list args;
    va_start(args, fmt);
    int result = vprintf(fmt, args);
    va_end(args);
    if (ask) {
        fprintf(stderr, "Fatal error: ");
        vfprintf(stderr, fmt, args);
        exit(EXIT_FAILURE);
    }
    return result;
}

// Provide implementations for any other functions declared in debug.h as needed
