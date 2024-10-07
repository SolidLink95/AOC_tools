import os
import json
import sys
import shutil
import subprocess
from pathlib import Path

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
        return p.returncode

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
                if not "TEXTURE_ARRAY" in f.read().upper():
                    return False
        except:
            pass
        remove_dir_if_exists(self.tmp)
        return True

    


