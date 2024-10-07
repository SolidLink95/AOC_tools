import os
import json
import sys
import shutil
import subprocess
from pathlib import Path
# from PIL import Image

def remove_dir_if_exists(path):
    x = Path(path)
    if x.exists() and x.is_dir():
        shutil.rmtree(x)

class G1T_Emm_Converter():
    def __init__(self) -> None:
        self.tmp = Path(os.path.expandvars("%TEMP%/aoctemp"))
        remove_dir_if_exists(self.tmp)
        self.root_path = Path(os.path.expandvars("%LOCALAPPDATA%/AgeOfCalamity"))
        self.gust = self.root_path / "gust_g1t.exe"
        self.texconv = self.root_path / "texconv.exe"
        self.texassemble = self.root_path / "texassemble.exe"
        self.nvtt_export = Path(r"C:\Program Files\NVIDIA Corporation\NVIDIA Texture Tools\nvtt_export.exe")
        self.aoc_path = None
        self.get_aoc_path()
    
    def get_aoc_path(self):
        try:
            json_path = self.root_path / "aoc_config.json"
            with open(json_path, "r") as f:
                data = json.loads(f.read())
            self.aoc_path = Path(data["aoc_path"])
        except:
            pass
        

    def is_valid(self):
        return self.gust.exists() and self.texconv.exists() and self.texassemble.exists() and self.nvtt_export.exists() and self.aoc_path is not None
    
    def get_g1t_path(self, g1t_hash):
        return self.aoc_path / "MaterialEditor/g1t" / f"{g1t_hash}.g1t"
    
    def run(self, command, check=True):
        c = [str(e) for e in command]
        p = subprocess.run(c, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=check)
        # p = subprocess.run(c,  check=check)
        return p.returncode

    def convert_to_black_png(self, input_image, output_image):
        input_image = Path(input_image)
        shutil.copyfile(input_image, output_image)
        return
        
        tmp = Path(os.path.expandvars("%TEMP%/texconv"))
        remove_dir_if_exists(tmp)
        
        # texconv command to convert the image to pitch black (0,0,0) pixels
        command = [
            self.texconv,            # Path to texconv executable
            "-ft", "png",         # Convert to PNG format
            "-o", tmp,  # Output directory
            # "-px", "black_",      # Prefix for the output file
            input_image           # Input image
        ]

        self.run(command)
        result_file = tmp / (input_image.stem + ".png")
        shutil.move(result_file, output_image)
        remove_dir_if_exists(tmp)

    def dds_to_png(self, dds, dest_path):
        dds = Path(dds)
        if dds.name.lower().endswith(".png"):
            shutil.copyfile(dds, dest_path)
            return
        tmp = Path(os.path.expandvars("%TEMP%/texconv"))
        remove_dir_if_exists(tmp)
        tmp.mkdir(parents=True, exist_ok=True)
        command = [
            self.texconv,      # texconv executable (make sure it's in your system PATH)
            "-ft", "png",   # Specifies output format as PNG
            "-o", tmp,  # Output directory
            dds      # Input .dds file
        ]
        self.run(command)
        png = tmp / (dds.stem + ".png")
        shutil.move(png, dest_path)
        remove_dir_if_exists(tmp)

    def is_g1t_dds_arr(self, g1t_path):
        g1t_path = Path(g1t_path)
        clean_g1t_path = self.get_g1t_path(g1t_path.stem)
        if not clean_g1t_path.exists():
            return False
        self.tmp.mkdir(parents=True, exist_ok=True)
        tmp_g1t = self.tmp / g1t_path.name
        shutil.copy(clean_g1t_path, tmp_g1t)
        code = self.run([self.gust, tmp_g1t], check=False)
        if code != 0: #not a g1t
            return False
        json_path = tmp_g1t.parent / tmp_g1t.stem / "g1t.json"
        try:
            with open(json_path, "r") as f:
                rawdata = f.read()
            if not "TEXTURE_ARRAY" in rawdata.upper():
                remove_dir_if_exists(self.tmp)
                return False
        except:
            return False
        remove_dir_if_exists(self.tmp)
        return True

    def convert_g1t_from_image(self, im_path, g1t, destfile):
        remove_dir_if_exists(self.tmp)
        self.tmp.mkdir(parents=True, exist_ok=True)
        if len(str(g1t)) != 8:
            g1t_hash = Path(g1t).stem
        else:
            g1t_hash = g1t
        clean_g1t_path = self.get_g1t_path(g1t_hash)
        if isinstance(im_path, bytes):
            rawdata = bytes(im_path)
            im_path = self.tmp / "new.dds"
            im_path.write_bytes(rawdata)
        im_path = Path(im_path)
        if im_path.name.lower().endswith(".dds"):
            slice1 = self.tmp / "new.png"
            self.dds_to_png(im_path, slice1)
        else:
            slice1 = im_path
        
        #create slice2
        print("Creating slice2")
        slice2 = str(self.tmp / "slice2.png")
        self.convert_to_black_png(slice1, slice2)
        # with Image.open(slice1) as im1:
        #     w, h = im1.size
        #     im2 = Image.new("RGB", (w, h), (0, 0, 0))
        #     im2.save(slice2)

        #run gust
        g1t_path = self.tmp / clean_g1t_path.name
        g1t_dir = self.tmp / g1t_hash
        shutil.copyfile(clean_g1t_path, self.tmp / g1t_path.name)
        self.run([self.gust, g1t_path])
        clean_dds = self.tmp / g1t_hash / "000.dds"
        tmp_arr_dds = self.tmp / "arr.dds"
        tmp_arr_mips_dds = self.tmp / "arr_mips.dds"

            
        #Create array
        print("Creating array")
        command = [
            self.texassemble, 
            'array', 
            '-y', 
            '-o', tmp_arr_dds, 
            slice1, 
            slice2
        ]
        self.run(command, check=True)
        #Generate mips
        print("Generate mips")
        command = [
            self.nvtt_export, 
            '-f', 'bc7', 
            '--extract-from-atlas', 
            '--atlas-elements', '2', 
            '--mips', 
            '--num-mips-in-atlas', '8', 
            '-o', tmp_arr_mips_dds, 
            tmp_arr_dds
        ]
        self.run(command, check=True)
        shutil.copyfile(tmp_arr_mips_dds, clean_dds)
        #Convert g1t back
        self.run([self.gust, g1t_dir], check=True)

        shutil.copyfile(g1t_path, destfile)

        remove_dir_if_exists(self.tmp)

def main():
    os.system("cls")
    dds = "emm_0_00648a45_17.dds"
    tool = G1T_Emm_Converter()
    if not tool.is_valid():
        print("Invalid tool setup")
        return
    g1t = "00648a45"
    g1t_path = tool.get_g1t_path(g1t)
    if not tool.is_g1t_dds_arr(g1t_path):
        print("Not a valid g1t dds array")
        return
    tool.convert_g1t_from_image(dds, g1t, "new.g1t")


if __name__ == "__main__":
    main()
        

        
            
    


