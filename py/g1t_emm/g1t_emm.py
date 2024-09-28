import subprocess
import sys
import os
from pathlib import Path
import shutil
from PIL import Image

NVIDIA_TOOLS_PATH = r"C:\Program Files\NVIDIA Corporation\NVIDIA Texture Tools\nvtt_export.exe"

def remove_dir_if_exists(dirr):
    x = Path(dirr)
    if x.exists() and x.is_dir():
        shutil.rmtree(x)

def main():
    if len(sys.argv) < 2:
        input("No file to process")
        return
    g1t_file = Path(sys.argv[1])
    if not (g1t_file.name.lower().endswith(".g1t") or g1t_file.name.lower().endswith(".gt1")):
        input(f"Invalid extension, exiting")
        return
    
    gust_g1t = "gust_g1t.exe"
    tmp = Path("tmp")
    remove_dir_if_exists(tmp)
    tmp.mkdir(exist_ok=True)
    #shutil.copyfile("new.png", tmp / "new.png")
    #slice1 = str(tmp / "new.png")
    slice1 = "new.png"
    slice2 = str(tmp / "slice2.png")
    im1 = Image.open(slice1)
    w, h = im1.size
    im2 = Image.new("RGB", (w,h), (0,0,0))
    im2.save(slice2)
    dirr = g1t_file.parent / g1t_file.stem
    remove_dir_if_exists(dirr)
    subprocess.run([gust_g1t, str(g1t_file)], check=True)
    clean_dds = str(dirr / "000.dds")
    tmp_arr_dds = str(tmp / "arr.dds")
    tmp_arr_mips_dds = str(tmp / "arr_mips.dds")
    #Create array
    command = [
        'texassemble.exe', 
        'array', 
        '-y', 
        '-o', tmp_arr_dds, 
        slice1, 
        slice2
    ]
    subprocess.run(command, check=True)
    #Generate mips
    command = [
        NVIDIA_TOOLS_PATH, 
        '-f', 'bc7', 
        '--extract-from-atlas', 
        '--atlas-elements', '2', 
        '--mips', 
        '--num-mips-in-atlas', '8', 
        '-o', tmp_arr_mips_dds, 
        tmp_arr_dds
    ]
    subprocess.run(command, check=True)
    shutil.copyfile(tmp_arr_mips_dds, clean_dds)
    #Convert g1t back
    subprocess.run(["gust_g1t.exe", str(dirr)], check=True)
    
    
    remove_dir_if_exists(dirr)
    remove_dir_if_exists(tmp)
    
try:
    main()
except Exception as e:
    print(e)
    input("\n")