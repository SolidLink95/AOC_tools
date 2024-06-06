#ifndef KTIDFILE_H
#define KTIDFILE_H

#include "../eternity_common/FixedBitStream.h"
#include "../eternity_common/FixedMemoryStream.h"

class KtidFile : public BaseFile
{
private:
    std::vector<std::pair<uint32_t, uint32_t>> textures;

protected:
    void Reset();

public:
    KtidFile();
    virtual ~KtidFile() override;

    virtual bool Load(const uint8_t *buf, size_t size) override;
    virtual uint8_t *Save(size_t *psize) override;

    bool LoadFromTextFile(const std::string &path);
    bool SaveToTextFile(const std::string &path, bool *crack_success, bool full_crack);

    bool SaveToString(std::string &output, const std::string &path, bool *crack_success, bool full_crack);
};

#endif // KTIDFILE_H
