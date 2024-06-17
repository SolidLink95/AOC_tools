#include <cstdint>
#include "Utils.h"
#include <algorithm>  // For std::transform
#include <cctype>     // For std::tolower
#include <cstdarg>
#include <cstdio>


void AesEcbDecrypt(void *, size_t, const uint8_t *, int)
{
    // DPRINTF("%s: Crypto is not enabled.\n", FUNCNAME);
}

void AesEcbEncrypt(void *, size_t, const uint8_t *, int)
{
    // DPRINTF("%s: Crypto is not enabled.\n", FUNCNAME);
}

bool HasOnlyDigits(const std::string &str)
{
    for (char c: str)
    {
        bool ok = false;

        if (c >= '0' && c <= '9')
        {
            ok = true;
        }

        if (!ok)
            return false;
    }

    return true;
}


size_t GetFileSize(const std::string &path)
{
#ifdef UTILS_UTF8
    return GetFileSize(Utf8ToUcs2(path));
#else
    struct stat info;

    if (stat(path.c_str(), &info) != 0)
        return (size_t)-1;

    return (size_t)info.st_size;
#endif
}

size_t GetFileSize(const std::u16string &path)
{
    struct _stat info;

    if (_wstat((const wchar_t *)path.c_str(), &info) != 0)
        return (size_t)-1;

    return (size_t)info.st_size;
}


uint32_t GetUnsigned(const std::string &str, uint32_t default_value)
{
	uint32_t ret = 0;
    size_t len = str.length();
	
	if (len == 0)
	{
        //DPRINTF("WARNING: length of integer string = 0 (param \"%s\"), setting value to 0.\n", param_name.c_str());
        return default_value;
	}
	
	if (str[0] == '0')
	{
		if (len == 1)
			return 0;
		
		if (str[1] != 'x')
		{
            /*DPRINTF("WARNING: Integer format error on \"%s\". "
							"Value must be decimal values without any 0 on the left, or hexadecimal values with 0x prefix. "
							"Octal values not allowed (offending_string = %s). "
                            "Setting value to 0.\n", param_name.c_str(), str.c_str());*/
							
            for (size_t i = 1; i < str.length(); i++)
            {
                if (str[i] != '0')
                {
                    if (sscanf_s(str.c_str()+i, "%u", &ret) != 1)
                        return default_value;

                    return ret;
                }
            }

            return default_value;
		}
		
		if (len == 2)
		{
            //DPRINTF("WARNING: nothing on the right of hexadecimal prefix (on param \"%s\"). Setting value to 0.\n", param_name.c_str());
            return default_value;
		}
		
        if (sscanf_s(str.c_str()+2, "%x", &ret) != 1)
		{
            //DPRINTF("sscanf_s failed on param \"%s\", offending string = \"%s\"\n. Setting value to 0.", param_name.c_str(), str.c_str());
            return default_value;
		}
	}
	else
	{
        if (sscanf_s(str.c_str(), "%u", &ret) != 1)
		{
            //DPRINTF("sscanf_s failed on param \"%s\", offending string = \"%s\"\n. Setting value to 0.", param_name.c_str(), str.c_str());
            return default_value;
		}
	}
	
	return ret;
}


uint8_t *ReadFile(const std::string &path, size_t *psize, bool show_error)
{
    FILE *f = fopen(path.c_str(), "rb");
	if (!f)
	{
		if (show_error)
        {
            DPRINTF("Cannot open file \"%s\" for reading.\n"
                    "Error given by the system: %s\n", path.c_str(), strerror(errno));
        }
		
        return nullptr;
	}
	
	size_t size, rd;
    uint8_t *buf;
	
	fseeko64(f, 0, SEEK_END);
    size = (size_t)ftello64(f);
    fseeko64(f, 0, SEEK_SET);

    buf = new uint8_t[size];
	rd = fread(buf, 1, size, f);
	fclose(f);
	
	if (rd != size)
	{
		if (show_error)
            DPRINTF("Read failure on file \"%s\"\n", path.c_str());
		
		delete[] buf;
        return nullptr;
	}
	
	*psize = size;
	return buf;
}



#ifdef __GNUC__
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wformat"
#endif

std::string U64ToString(uint64_t value, bool hexadecimal)
{
	char temp[16];
	std::string str;
	
	if (hexadecimal)
	{
        sprintf_s(temp, "0x%I64x", value);
	}
	else
	{
        sprintf_s(temp, "%I64u", value);
	}
	
	str = temp;
	return str;
}

#ifdef __GNUC__
#pragma GCC diagnostic pop
#endif

std::string U8ToHexString(uint8_t value, bool zeropad, bool prefix)
{
    char temp[16];
    std::string str;

    if (!zeropad)
    {
        if (prefix)
            sprintf_s(temp, "0x%x", value);
        else
            sprintf_s(temp, "%x", value);
    }
    else
    {
        if (prefix)
            sprintf_s(temp, "0x%02x", value);
        else
            sprintf_s(temp, "%02x", value);
    }

    str = temp;
    return str;
}

std::string U16ToHexString(uint16_t value, bool zeropad, bool prefix)
{
    char temp[16];
    std::string str;

    if (!zeropad)
    {
        if (prefix)
            sprintf_s(temp, "0x%x", value);
        else
            sprintf_s(temp, "%x", value);
    }
    else
    {
        if (prefix)
            sprintf_s(temp, "0x%04x", value);
        else
            sprintf_s(temp, "%04x", value);
    }

    str = temp;
    return str;
}

std::string U32ToHexString(uint32_t value, bool zeropad, bool prefix)
{
    char temp[16];
    std::string str;

    if (!zeropad)
    {
        if (prefix)
            sprintf_s(temp, "0x%x", value);
        else
            sprintf_s(temp, "%x", value);
    }
    else
    {
        if (prefix)
            sprintf_s(temp, "0x%08x", value);
        else
            sprintf_s(temp, "%08x", value);
    }

    str = temp;
    return str;
}

#ifdef __GNUC__
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wformat"
#pragma GCC diagnostic ignored "-Wformat-extra-args"
#endif

std::string U64ToHexString(uint64_t value, bool zeropad, bool prefix)
{
    char temp[20];
    std::string str;

    if (!zeropad)
    {
        if (prefix)
            sprintf_s(temp, "0x%I64x", value);
        else
            sprintf_s(temp, "%I64x", value);
    }
    else
    {
        if (prefix)
            sprintf_s(temp, "0x%16I64x", value);
        else
            sprintf_s(temp, "%16I64x", value);
    }

    str = temp;
    return str;
}



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