import json
import tkinter as tk
from tkinter import filedialog
from pathlib import Path
import os, sys, struct, io
from Ktid import *
from KidsOb import *
import shutil

hashes_to_ext = {
    "8ab68b3f": "g1m",
    "ad260326": "sid",
    #"2b6eb4f6": "kidsobjdb",
    "3bbfd9a5": "grp",
    "7f0de9a3": "mtl",
    "b4840aca": "swg",
    "8dfd0584": "oidex",
    "1b4ff321": "rigbin"

}
#f92c5190 KTID

def remove_dir_if_exists(p):
    x = Path(p)
    if x.exists() and x.is_dir():
        shutil.rmtree(x)

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
    
    def swap_model(self, g1m_1, g1m_2, mod_path, extended=False):
        g1_path = self.find_g1m(g1m_1)
        g2_path = self.find_g1m(g1m_2)
        files_path = mod_path / "data"
        files_path.mkdir(parents=True, exist_ok=True)
        g1m_sourcepath = Path(g2_path)
        g1m_destpath = files_path / g1_path.name
        mod_path = Path(mod_path)
        shutil.copyfile(g1m_sourcepath, g1m_destpath)
        if g1m_1 == g1m_2:
            print(f"Just copy g1m: {g1m_1}")
            return
        # if mod_path.exists():
        #     shutil.rmtree(str(mod_path))
        
        g1_ktid = self.g1ms[g1m_1]["g1t"]
        g1_kidsob = self.g1ms[g1m_1]["kidsobjdb"]
        g2_ktid = self.g1ms[g1m_2]["g1t"]
        g2_kidsob = self.g1ms[g1m_2]["kidsobjdb"]
        
        g1_ktid_path = self.find_ktid(g1_ktid)
        g2_ktid_path = self.find_ktid(g2_ktid)
        
        ktid_sourcepath = Path(g2_ktid_path)
        ktid_destpath = files_path / g1_ktid_path.name
        shutil.copyfile(ktid_sourcepath, ktid_destpath)
        
        print(g1m_sourcepath, g1m_destpath)
        print(ktid_sourcepath, ktid_destpath)
        
        #return
        #rest
        if not extended:
            return
        for ext in hashes_to_ext.values():
            if ext in ["g1m","kidsobjdb"]:
                continue
            g1_item = self.g1ms[g1m_1].get(ext)
            g2_item = self.g1ms[g1m_2].get(ext)
            if g1_item and g2_item:
                if g1_item==g2_item:
                    print(f"{g1_item}.{ext} is the same for {g1m_1} and {g1m_2}, skipping")
                    continue
                g1_item_p = self.find_file(g1_item, f".{ext}", ext)
                g2_item_p = self.find_file(g2_item, f".{ext}", ext)
                if g1_item_p and g2_item_p:
                    g1_item_sourcepath = Path(g2_item_p)
                    g2_item_destpath = files_path / g1_item_p.name
                    print(f"{ext}: {g1_item_sourcepath.stem} -> {g2_item_destpath.stem}")
                    shutil.copyfile(g1_item_sourcepath, g2_item_destpath)
                    #shutil.copyfile(g1_item_sourcepath, g2_item_destpath)
               
            
        
    
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

def update_json():
    p = Path('G1M_to_G1T_pairs.json')
    p1 = Path('G1M_to_G1T_pairs1.json')
    data = json.loads(p.read_text())
    kids = json.loads(Path(r"W:\coding\AOC_tools\py\KidsObPy\CharacterEditor.json").read_text())
    g1m_col_hash = [e for e,v in hashes_to_ext.items() if v=="g1m"][0]
    for ob in kids["objects"]:
        tmp = next((c for c in ob["columns"] if c.get("name", "")==g1m_col_hash), None)
        if tmp is None or not tmp.get("vals",[]):
            continue
        g1m = tmp["vals"][0]
        if g1m not in data:
            data[g1m] = {}
        if "g1t" not in data[g1m]:
            tmp1 = next((c for c in ob["columns"] if c.get("name","")=="f92c5190"), None)
            ktid_main_hash = None
            if tmp1 is not None and tmp1.get("vals",[]):
                ktid_main_hash = tmp1["vals"][0]
            if ktid_main_hash is not None:
                tmp2 = next((o for o in kids["objects"] if o.get("name","")==ktid_main_hash), None)
                if tmp2:
                    tmp3 = next((c for c in tmp2["columns"] if c.get("vals", ["00000000"])[0] != "00000000"), None   )
                    if tmp3:
                        data[g1m]["g1t"] = tmp3["vals"][0]
        for col in ob["columns"]:
            ext = hashes_to_ext.get(col.get("name", ""))
            if ext is None or not col.get("vals", []):
                continue
            if g1m not in data:
                data[g1m] = {"kidsobjdb": "CharacterEditor.kidssingletondb"}
            if col["vals"][0] != "00000000":
                data[g1m][ext] = col["vals"][0]
    
    p1.write_text(json.dumps(data, indent=4))
    sys.exit(0)

        


if __name__ == "__main__":
    #update_json()
    # folder = select_folder("Select folder with AOC dumped files")
    # print(folder)
    aoc = AocSwap()
    yuzu_mods = Path(r"W:\AOC_modding\_MODS")
    #aoc.swap_model("cd4ed2ed", "26a3f1f2", yuzu_mods / "Swap_gerudovai_to_royalguard")
    #aoc.swap_model("e2211005", "26a3f1f2", yuzu_mods / "Swap_gerudovai_to_royalguard")
    #aoc.swap_model("c63f1322", "7e52fec7", yuzu_mods / "tree_branch_test")
    #aoc.swap_model("b4736804", "b5e9b96d", yuzu_mods / "Archaic_set_over_Snowquill")
    #aoc.swap_model("cd4ed2ed", "b5e9b96d", yuzu_mods / "Archaic_set_over_Snowquill")
    #aoc.swap_model("b4736804", "bd554845", yuzu_mods / "Archaic_set_over_Snowquill")
    #aoc.swap_model("cd4ed2ed", "bd554845", yuzu_mods / "Archaic_set_over_Snowquill")
    #aoc.swap_model("862e7830", "e70352c8", yuzu_mods / "Hollow_Revali", extended=True)
    #aoc.swap_model("c7794a38", "68dd50eb", yuzu_mods / "Hollow_Daruk", extended=True)
    #aoc.swap_model("bae054b7", "68dd50eb", yuzu_mods / "Hollow_Daruk", extended=True)
    
    
    #aoc.swap_model("231ccec8", "231ccec8", yuzu_mods / "impa_uchiha", extended=True)
    #aoc.swap_model("d9dddb97", "d9dddb97", yuzu_mods / "impa_uchiha", extended=True)
    #aoc.swap_model("f23c0538", "f23c0538", yuzu_mods / "impa_uchiha", extended=True)
    #aoc.swap_model("72194cb8", "72194cb8", yuzu_mods / "impa_uchiha", extended=True)
    
    aoc.swap_model("4327965f", "6b243a38", yuzu_mods / "impa_uchiha_weapon_default", extended=True)
    #aoc.swap_model("231ccec8", "231ccec8", yuzu_mods / "impa_uchiha", extended=True)
    #aoc.swap_model("d9dddb97", "231ccec8", yuzu_mods / "impa_uchiha_swapped", extended=False)
    #aoc.swap_model("f23c0538", "231ccec8", yuzu_mods / "impa_uchiha_swapped", extended=True)
    #aoc.swap_model("51abfcbb", "231ccec8", yuzu_mods / "impa_uchiha_swapped", extended=True)
    #aoc.swap_model("9bdd95fc", "231ccec8", yuzu_mods / "impa_uchiha_swapped", extended=True)
    #aoc.swap_model("72194cb8", "231ccec8", yuzu_mods / "impa_uchiha_swapped", extended=True)
    
    #aoc.swap_model("c63f4cbe", "bc3c0a6d", yuzu_mods / "Battle_tested_guardian_electric", extended=True)
    #riju
    ##aoc.swap_model("7cb53ec4", "b9ec07ee", yuzu_mods / "TEST_Astor_over_Monk", extended=True)
    #aoc.swap_model("ad960854", "b9ec07ee", yuzu_mods / "TEST_Astor_over_Monk", extended=True)
    #mipha
    #aoc.swap_model("68d7e5d9", "b9ec07ee", yuzu_mods / "TEST_Astor_over_Monk", extended=True)
    #aoc.swap_model("5c3ef058", "b9ec07ee", yuzu_mods / "TEST_Astor_over_Monk", extended=True)
    #impa
    #aoc.swap_model("231ccec8", "b9ec07ee", yuzu_mods / "TEST_Astor_over_Monk", extended=True)
    #aoc.swap_model("d9dddb97", "b9ec07ee", yuzu_mods / "TEST_Astor_over_Monk", extended=True)
    #aoc.swap_model("f23c0538", "b9ec07ee", yuzu_mods / "TEST_Astor_over_Monk", extended=True)
    #robbie
    #aoc.swap_model("a07fc6ef", "b9ec07ee", yuzu_mods / "TEST_Astor_over_Monk", extended=True)
    #aoc.swap_model("40820d63", "b9ec07ee", yuzu_mods / "TEST_Astor_over_Monk", extended=True)
    #aoc.swap_model("a7026e3d", "b9ec07ee", yuzu_mods / "TEST_Astor_over_Monk", extended=True)
    #aoc.swap_model("8b238949", "b9ec07ee", yuzu_mods / "TEST_Astor_over_Monk", extended=True)
    
    
    #p = yuzu_mods / "Ancient_battle_axe_over_royal_g"
    #aoc.swap_model("fd071de1", "20b87366", p, extended=True)
    
    
    #p = yuzu_mods / "TEST_OOT_cap_over_hylian"
    #remove_dir_if_exists(p)
    #aoc.swap_model("17307cde", "65109a64", p, extended=True)
    #aoc.swap_model("2c19451f", "65109a64", p, extended=True)
    
    #p = yuzu_mods / "TEST_OOT_tunic_over_hylian"
    #aoc.swap_model("ecd2e63b", "dd404403", p, extended=True)
    
    #p = yuzu_mods / "TEST_OOT_pants_over_hylian"
    #aoc.swap_model("a110af7a", "308d5102", p, extended=True)
    #aoc.swap_model("e2211005", "308d5102", p)
    
    #aoc.swap_model("2de346c6", "dd404403", p)
    #aoc.swap_model("ecd2e63b", "dd404403", p)
    
    #aoc.swap_model("2c19451f", "65109a64", p)
    #aoc.swap_model("17307cde", "65109a64", p)
    #aoc.swap_model("02f788e7", "65109a64", p)
    
    #p = yuzu_mods / "TEST_hollow_link"
    #remove_dir_if_exists(p)
    #aoc.swap_model("308d5102", "3ea21ccb", p, extended=True)
    #aoc.swap_model("96666440", "3ea21ccb", p, extended=True)
    #aoc.swap_model("97130fdf", "3ea21ccb", p, extended=True)
    
    
    #p = yuzu_mods / "Malice_master_sword_TEST"
    #remove_dir_if_exists(p)
    #aoc.swap_model("ef2a56a2", "284d5f1e", p)
    #aoc.swap_model("08483492", "416b3d0e", p)
    
    #aoc.swap_model("48269de7", "5a8295eb", p)
    
    
    #aoc.swap_model("2ab808da", "1fe001d9", yuzu_mods / "Vagrant_King")
    #aoc.swap_model("7a7742f6", "1fe001d9", yuzu_mods / "Vagrant_King")
    #aoc.swap_model("9bafb4d8", "1fe001d9", yuzu_mods / "Vagrant_King")
    #aoc.swap_model("2ab808da", "1fe001d9", yuzu_mods / "Vagrant_King")
    
    
    #aoc.swap_model("9a9e9a45", "c5468f47", yuzu_mods / "Hollow_Terrako", extended=True)
    #aoc.swap_model("a5df5a3e", "c5468f47", yuzu_mods / "Hollow_Terrako", extended=True)
    #aoc.swap_model("0967ca97", "c5468f47", yuzu_mods / "Hollow_Terrako", extended=True)
    #aoc.swap_model("212454e4", "c5468f47", yuzu_mods / "Hollow_Terrako", extended=True)
    #aoc.swap_model("c5468f47", "212454e4", yuzu_mods / "Hollow_Terrako", extended=True)
    #aoc.swap_model("8d932507", "c5468f47", yuzu_mods / "Hollow_Terrako", extended=True) #cutscene, breaks
    
    # aoc.swap_model("9a9e9a45", "1418dfa6", yuzu_mods / "Broken_Terrako")
    # aoc.swap_model("a5df5a3e", "1418dfa6", yuzu_mods / "Broken_Terrako")
    # aoc.swap_model("0967ca97", "1418dfa6", yuzu_mods / "Broken_Terrako")
    # aoc.swap_model("212454e4", "1418dfa6", yuzu_mods / "Broken_Terrako")
    # aoc.swap_model("40bfc628", "4d58bba9", "Zelda_dress_over_white_dress")
    #4d58bba9