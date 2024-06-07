#include <iostream>
#include "../eternity_common/DOA6/G1mFile.h"
#include "G1tFile.h"
#include "../eternity_common/DdsFile.h"
#include "../eternity_common/tinyxml/tinyxml.h"
#include "../eternity_common/Utils.h"
// #include "../DirectXTex/DirectXTex/DirectXTex.h"
#include <filesystem>

void print_usage(char *argv[])
{
    std::cout << "Usage: " << argv[0] << " <input.g1m/.xml> <bones_file.oid> <output.xml/.g1m>" << std::endl;
}

int process_g1m(std::string &file1, std::string &oid_file, std::string &file2, G1mFile &g1m, bool var1)
{
    std::cout << "Loading file " << file1 << std::endl;
    std::string destfile = file1 + ".xml";
    if (!g1m.SmartLoad(file1))
    {
        std::cerr << "Failed to load file " << file1 << std::endl;
        return 1;
    }
    std::cout << "Loaded file " << file1 << std::endl;
    std::cout << "Setting default bones names set " << std::endl;
    g1m.SetDefaultBoneNames();
    std::cout << "Default bones names set " << std::endl;
    // var3 = g1m.SmartSave(file2, true, true);
    if (!g1m.SmartSave(destfile, true, false)) {
        
        std::cerr << "Failed to save file " << destfile << std::endl;
        return 1;
    }
    
    return 0;
}

int main(int argc, char *argv[])
{
    if (argc < 4)
    {
        print_usage(argv);
        return 1;
    }
    G1mFile g1m;
    bool var1 = true;
    std::string file1(argv[1]);
    std::string oid_file(argv[2]);
    std::string file2(argv[3]);

    if (file1.find(".g1m") != std::string::npos)
    {
        process_g1m(file1, oid_file, file2, g1m, var1);
    }
    else if (file1.find(".xml") != std::string::npos){}
    else if (file1.find(".g1t") != std::string::npos)
    {
        G1tFile g1t;
        std::cout << "Loading file " << file1 << std::endl;
        var1 &= g1t.SmartLoad(file1, true, false);

        std::cout << "extra_header: ";
        for (auto b : g1t.extra_header) {
            std::cout << std::hex << (int)b << " ";
        }
        std::cout << std::endl ;

        std::cout << "unk_data: ";
        for (auto b : g1t.unk_data) {
            std::cout << std::hex << (int)b << " ";
        }
        std::cout << std::endl ;

        std::cout << "version: " << g1t.version << std::endl;
        std::cout << "plattform: " << g1t.plattform << std::endl;
        std::cout << "unk_1C: " << g1t.unk_1C << std::endl;

        std::vector<G1tTexture> textures = g1t.GetTextures();
        int i = 0;
        for (auto tex: textures) {
            std::cout << "Texture id: " << i++ << " size: " << tex.image_data.size() << " extra_header size " << tex.extra_header.size() << std::endl;
        }
        std::string dirr = file1.substr(0, file1.size() - 4);
        if (!Utils::DirExists(dirr)) 
            Utils::CreatePath(dirr, true);
        i = 0;
        for (auto tex: textures) {
            std::string tex_name = dirr + "/" + std::to_string(i) + ".dds";
            DdsFile *dds = G1tFile::ToDDS(tex);
            std::cout << "Saving texture " << i << ".dds " << dds->GetWidth() << "x" << dds->GetHeight() << " format: " << dds->GetFormatName() << " mips: " << dds->GetMips() << std::endl;
            var1 &= dds->SaveToFile(tex_name, true, true);
            // var1 &= Utils::WriteFileBool(tex_name, dds., tex.image_data.size(), true, true);
            if (!var1)
            {
                std::cerr << "Failed to save texture " << tex_name << std::endl;
                return 1;
            }
            i++;
        }
        // G1tFile::FromDDS()

    }
    else
    {
        std::cout << "Invalid file extension" << std::endl;
        print_usage(argv);
        return 1;
    }

    if (var1)
    {
        std::cout << "Success" << std::endl;
    }
    else
    {
        std::cout << "Failure" << std::endl;
    }

    std::cout << "Hello world" << std::endl;
    return 0;
}