#ifndef G1TFILE_H
#define G1TFILE_H

#include "DdsFile.h"

#define G1T_SIGNATURE   0x47315447

#define G1T_FLAG_STANDARD_FLAGS 0x000000011200ULL // Flags that are commonly set
#define G1T_FLAG_EXTENDED_DATA  0x000000000001ULL // Set if the texture has local data in the texture entry.
#define G1T_FLAG_SRGB           0x000000002000ULL // Set if the texture uses sRGB
#define G1T_FLAG_DOUBLE_HEIGHT  0x001000000000ULL // Some textures need to be doubled in height
#define G1T_FLAG_NORMAL_MAP     0x030000000000ULL // Usually set for normal maps (but not always)
#define G1T_FLAG_SURFACE_TEX    0x000000000001ULL // Set for textures that appear on a model's surface
#define G1T_FLAG_TEXTURE_ARRAY  0x0000F00F0000ULL
// This one is not used in G1Ts, but only in this application
#define G1T_FLAG_CUBE_MAP       0x000100000000ULL

#ifdef _MSC_VER
#pragma pack(push,1)
#endif

struct PACKED AocG1THeader
{
    uint32_t    magic;      // 0
    uint32_t    version;    // 0x4
    uint32_t    total_size; // 0x8
    uint32_t    header_size;// 0xC
    uint32_t    nb_textures;// 0x10
    uint32_t    platform;   // 0x14 0xA = PC
    uint32_t    extra_size; // 0x18
};
CHECK_STRUCT_SIZE(AocG1THeader, 28);

struct PACKED G1THeader
{
    uint32_t signature; // 0
    uint32_t version; // 4
    uint32_t file_size; // 8
    uint32_t table_offset; // 0xC
    uint32_t num_textures; // 0x10
    uint32_t plattform; // 0x14 - 0xA = PC
    uint32_t unk_data_size; // 0x18 If not 0, there are this X bytes after the offset table until the first texture header
    uint32_t unk_1C; // ?
};
CHECK_STRUCT_SIZE(G1THeader, 0x20);

struct PACKED AocG1tTexHeader
{
    uint8_t     z_mipmaps : 4;
    uint8_t     mipmaps : 4;
    uint8_t     type;
    uint8_t     dx : 4;
    uint8_t     dy : 4;
    uint8_t     flags[5];
};
CHECK_STRUCT_SIZE(AocG1tTexHeader, 0x8);

struct PACKED G1TEntryHeader
{
    uint8_t mip_sys; // 0-3: text sys; 4-7: mip maps count. Game check text sys to be between 0-4
    uint8_t format;
    uint8_t dxdy; // 0-3: width; 4-7: height
    uint8_t unk_3[4];
    uint8_t extra_header_version; // 7
};
CHECK_STRUCT_SIZE(G1TEntryHeader, 0x8);

struct PACKED G1TEntryHeader2
{
    uint32_t size; // 0 - Size of this. Usually either 0xC or 0x14
    uint32_t unk_04; // Is always zero?
    uint8_t array_other; // 8 - Bits 5-7 are num of interleaved images. Bits 0-3: unknown.
    uint8_t unk_09[3];

    // Only when size > C
    uint32_t width;
    uint32_t height;
};
CHECK_STRUCT_SIZE(G1TEntryHeader2, 0x14);

#ifdef _MSC_VER
#pragma pack(pop)
#endif

struct G1tTexture
{
    uint32_t width;
    uint32_t height;
    uint8_t format;
    uint8_t sys;
    uint8_t mips;
    uint8_t unk_3[4];
    uint8_t extra_header_version;

    uint8_t array_size;

    std::vector<uint8_t> image_data;
    std::vector<uint8_t> extra_header;
    AocG1tTexHeader *aochdr;
    uint8_t flags[5];
    int IdealMipsCount() const;
};

// class G1tFile : public BaseFile
class G1tFile 
{
    protected:
        bool big_endian;
        uint32_t val32(uint32_t val) const;
        
        uint8_t *GetOffsetPtr(const void *base, uint32_t offset, bool native=false) const;
        uint8_t *GetOffsetPtr(const void *base, const uint32_t *offsets_table, uint32_t idx, bool native=false) const;
private:

    size_t CalculateFileSize() const;

protected:

    void Reset();

public:
    const G1THeader *hdr;
    AocG1THeader *aohdr;
    std::vector<G1tTexture> textures;

    std::vector<uint8_t> extra_header;
    std::vector<uint8_t> unk_data;

    uint32_t version;
    uint32_t plattform;
    uint32_t unk_1C;

    G1tFile();
    virtual ~G1tFile() ;

    std::string GetMetadataCsv() const;

    virtual bool Load(const uint8_t *buf, size_t size) ;
    virtual uint8_t *Save(size_t *psize) ;

    inline size_t GetNumTextures() const { return textures.size(); }    

    static uint32_t *Decode(const uint8_t *buf, size_t buf_size, uint32_t width, uint32_t height, uint8_t g1t_format, bool *alpha, bool show_error);
    static uint32_t *Decode(const G1tTexture &tex, bool *alpha, bool show_error);
    uint32_t *Decode(size_t idx, bool *alpha, bool show_error) const;

    static DdsFile *ToDDS(const G1tTexture &tex);
    DdsFile *ToDDS(size_t idx) const;

    static bool FromDDS(G1tTexture &tex, const DdsFile &dds, uint8_t *fmt=nullptr, uint8_t *prev_fmt=nullptr);
    bool FromDDS(size_t idx, const DdsFile &dds, uint8_t *fmt=nullptr, uint8_t *prev_fmt=nullptr);

    static size_t CalculateTextureSize(const G1tTexture &tex, int override_levels=-1);
    size_t CalculateTextureSize(size_t idx, int override_levels=-1) const;

    bool IsArrayTexture(size_t idx) const;
    bool DecomposeArrayTexture(size_t idx, std::vector<G1tTexture> &ret, bool only_firstlevel, bool show_error) const;
    bool DecomposeArrayTextureFast(size_t idx, std::vector<uint8_t *> &ret, bool show_error);

    static bool ComposeArrayTexture(G1tTexture &ret, const std::vector<G1tTexture> &textures, bool show_error);
    bool ComposeArrayTexture(size_t idx, const std::vector<G1tTexture> &textures, bool show_error);

    static bool ReduceMipsLevel(G1tTexture &tex, uint8_t levels);
    bool ReduceMipsLevel(size_t idx, uint8_t levels);

    inline std::vector<G1tTexture> &GetTextures() { return textures; }
    inline const std::vector<G1tTexture> &GetTextures() const { return textures; }

    inline G1tTexture &operator[](size_t n) { return textures[n]; }
    inline const G1tTexture &operator[](size_t n) const { return textures[n]; }

    inline std::vector<G1tTexture>::iterator begin() { return textures.begin(); }
    inline std::vector<G1tTexture>::iterator end() { return textures.end(); }

    inline std::vector<G1tTexture>::const_iterator begin() const { return textures.begin(); }
    inline std::vector<G1tTexture>::const_iterator end() const { return textures.end(); }

    static int G1tToDdsFormat(uint8_t g1t_fmt);
    static int DdsToG1tFormat(int dds_fmt);

    static int IdealMipsCount(int width, int height);
    std::string GetMetadataCsv();
    std::vector<uint8_t> ToBytes();
    std::string GetMetadataJson();
};

uint32_t swap_bytes(uint32_t value);

#endif // G1TFILE_H
