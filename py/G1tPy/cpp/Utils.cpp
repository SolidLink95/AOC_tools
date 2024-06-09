#include <cstdint>
#include "Utils.h"
#include <algorithm>  // For std::transform
#include <cctype>     // For std::tolower
#include <cstdarg>
#include <cstdio>

int DebugPrintf(const char* fmt, ...) {
    va_list args;
    va_start(args, fmt);
    int result = vprintf(fmt, args);
    va_end(args);
    return result;
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