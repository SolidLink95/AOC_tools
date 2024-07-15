import json
import tkinter as tk
from tkinter import filedialog
from pathlib import Path
import os, sys, struct, io
from Ktid import *
from KidsOb import *
import shutil

def select_folder(title="Select a folder"):
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    folder_selected = filedialog.askdirectory(title=title)  # Show the folder selection dialog
    root.destroy()  # Destroy the root window
    return folder_selected

class AocSwap():
    def __init__(self) -> None:
        self.aoc_dir = Path(get_aoc_files_path())
        self.g1ms = get_g1m_git_pairs()
    
    def find_file(self, file_name, ext, emb_dir):
        folders = [e for e in self.aoc_dir.glob("*") if e.is_dir()]
        for folder in folders:
            file = folder / emb_dir / f"{file_name}{ext}"
            if file.exists():
                return file
        return None
    
    def swap_model(self, g1m_1, g1m_2, mod_path):
        g1_path = self.find_g1m(g1m_1)
        g2_path = self.find_g1m(g1m_2)
        mod_path = Path(mod_path)
        # if mod_path.exists():
        #     shutil.rmtree(str(mod_path))
        files_path = mod_path / "romfs/asset/data"
        files_path.mkdir(parents=True, exist_ok=True)
        
        g1_ktid = self.g1ms[g1m_1]["g1t"]
        g1_kidsob = self.g1ms[g1m_1]["kidsobjdb"]
        g2_ktid = self.g1ms[g1m_2]["g1t"]
        g2_kidsob = self.g1ms[g1m_2]["kidsobjdb"]
        
        g1_ktid_path = self.find_ktid(g1_ktid)
        g2_ktid_path = self.find_ktid(g2_ktid)
        
        g1m_sourcepath = Path(g2_path)
        g1m_destpath = files_path / g1_path.name
        
        ktid_sourcepath = Path(g2_ktid_path)
        ktid_destpath = files_path / g1_ktid_path.name
        
        print(g1m_sourcepath, g1m_destpath)
        print(ktid_sourcepath, ktid_destpath)
        
        shutil.copyfile(g1m_sourcepath, g1m_destpath)
        shutil.copyfile(ktid_sourcepath, ktid_destpath)
        
        
    
    def find_ktid(self, ktid_name):
        return self.find_file(ktid_name, ".ktid", "ktid")
    
    def find_g1t(self, g1t_name):
        return self.find_file(g1t_name, ".g1t", "g1t")
    
    def find_g1m(self, g1m_name):
        return self.find_file(g1m_name, ".g1m", "g1m")
    
    def find_kidsob(self, kname):
        if "CharacterEditor" in kname:
            k2 =  self.find_file(kname, ".kidssingletondb", "kidsobjdb")
            if k2 is not None:
                return k2
        return self.find_file(kname, ".kidsobjdb", "kidsobjdb")

def get_g1m_git_pairs():
    json_path = Path(os.path.expandvars("%localappdata%/AgeOfCalamity/G1M_to_G1T_pairs.json"))
    return json.loads(json_path.read_text())
    

def get_aoc_files_path():
    json_path = Path(os.path.expandvars("%localappdata%/AgeOfCalamity/aoc_config.json"))
    try:
        if json_path.exists():
            with open(json_path, "r") as f:
                data = json.load(f)
            return data["aoc_path"]
    except:
        pass
    folder = select_folder("Select folder with AOC dumped files")
    dirr = Path(folder)
    if not (dirr / "CharacterEditor").exists():
        raise FileNotFoundError("CharacterEditor folder not found")
    res = {"aoc_path": str(folder)}
    json_path.write_text(json.dumps(res, indent=4))
    return folder



        


if __name__ == "__main__":
    # folder = select_folder("Select folder with AOC dumped files")
    # print(folder)
    aoc = AocSwap()
    yuzu_mods = Path(r"W:\AOC_modding\_MODS")
    #aoc.swap_model("cd4ed2ed", "26a3f1f2", yuzu_mods / "Swap_gerudovai_to_royalguard")
    #aoc.swap_model("e2211005", "26a3f1f2", yuzu_mods / "Swap_gerudovai_to_royalguard")
    aoc.swap_model("c63f1322", "7e52fec7", yuzu_mods / "tree_branch_test")
    #aoc.swap_model("b4736804", "b5e9b96d", yuzu_mods / "Archaic_set_over_Snowquill")
    #aoc.swap_model("cd4ed2ed", "b5e9b96d", yuzu_mods / "Archaic_set_over_Snowquill")
    #aoc.swap_model("b4736804", "bd554845", yuzu_mods / "Archaic_set_over_Snowquill")
    #aoc.swap_model("cd4ed2ed", "bd554845", yuzu_mods / "Archaic_set_over_Snowquill")
    #aoc.swap_model("862e7830", "e70352c8", yuzu_mods / "Hollow_Revali")
    #aoc.swap_model("c7794a38", "68dd50eb", yuzu_mods / "Hollow_Daruk")
    #aoc.swap_model("bae054b7", "68dd50eb", yuzu_mods / "Hollow_Daruk")
    
    
    #aoc.swap_model("9a9e9a45", "c5468f47", yuzu_mods / "Hollow_Terrako")
    #aoc.swap_model("a5df5a3e", "c5468f47", yuzu_mods / "Hollow_Terrako")
    #aoc.swap_model("0967ca97", "c5468f47", yuzu_mods / "Hollow_Terrako")
    #aoc.swap_model("212454e4", "c5468f47", yuzu_mods / "Hollow_Terrako")
    #aoc.swap_model("8d932507", "c5468f47", yuzu_mods / "Hollow_Terrako") #cutscene, breaks
    
    # aoc.swap_model("9a9e9a45", "1418dfa6", yuzu_mods / "Broken_Terrako")
    # aoc.swap_model("a5df5a3e", "1418dfa6", yuzu_mods / "Broken_Terrako")
    # aoc.swap_model("0967ca97", "1418dfa6", yuzu_mods / "Broken_Terrako")
    # aoc.swap_model("212454e4", "1418dfa6", yuzu_mods / "Broken_Terrako")
    # aoc.swap_model("40bfc628", "4d58bba9", "Zelda_dress_over_white_dress")
    #4d58bba9