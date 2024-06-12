import cpp.g1t_module as g1t_module
from pathlib import Path
from G1t import G1T, fileToMd5
import os
import Dds_rs
import sys
# print(dir(Dds_rs))
import qui
from PIL import Image
from pydirectxtex import DirectXTex, DDS_HEADER_FLAGS_VOLUME

# Load PNG using Pillow
img = Image.open('"cpp/tmp/0.png"')
img = img.convert('RGBA')

# Convert to DDS with BC7_UNORM using DirectXTex
tex = DirectXTex.from_pillow_image(img)
tex.generate_mipmaps(8)
tex.save_dds('cpp/tmp/0_rust.dds', compression='BC7_UNORM')


sys.exit()
van = Path("0cc1a2b4_bak.g1t")
modd = Path("0cc1a2b4.g1t")
destpath = Path("0cc1a2b4_patched.g1t")


# g1t = G1T(van)
# g1t.extract_to_dir("tmp")
png_data = Path("cpp/tmp/0.png").read_bytes()
van_dds_data = Path("cpp/tmp/0.dds").read_bytes()

dds_data = Dds_rs.dds_to_dds(van_dds_data, "BC7_UNORM", 0, 512, 512)

Path("cpp/tmp/0_rust.dds").write_bytes(bytes(dds_data))














# vb = van.read_bytes()
# mb = modd.read_bytes()

# working_hdr = vb[:0x38]
# print(hex(vb[0x38]))
# print(hex(working_hdr[-1]))

# x = mb[0x2C:]

# destpath.write_bytes(working_hdr + x)

# print(fileToMd5(van))
# print(fileToMd5(modd))
# print(fileToMd5(destpath))
# p = "W:/coding/AOC_tools/test_data/0cc1a2b4.g1t"

# print("Extracting modded")
# g1t_modded = G1T("0cc1a2b4.g1t")
# print("Extracting vanila")
# g1t_vanila = G1T("0cc1a2b4_bak.g1t")
# g1t_vanila.save_file("0cc1a2b4.g1t")
# g1t_modded.extract_to_dir(r"W:\coding\AOC_tools\tmp\temp")
# g1t_vanila.extract_to_dir(r"W:\coding\AOC_tools\tmp\temp")
# g1t = G1T(p)
# g1t.extract_to_dir("tmp")

# g1t_1 = G1T("test_g1t_data")
# print(g1t_1.metadata)
# g1t_1.save_file("test_g1t_data_1.g1t")
# g1t_data = Path(p).read_bytes()
# metadata, dds_data = g1t_module.G1tDecompile(g1t_data)
# print(metadata)
