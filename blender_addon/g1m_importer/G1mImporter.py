import os
import subprocess
import sys
from pathlib import Path
#sys.path.append(str(Path(os.getcwd()) / "g1m_exporter"))
import json
from g1m_importer.G1t import G1T
from g1m_importer.g1m_exporter.g1m_export_meshes import *
import hashlib
from g1m_importer.util import *
from g1m_importer.G1M_to_G1T_hashes import *
from g1m_importer.KtidsKidsobs import *
import shutil
import struct
import io, bpy


class G1Mmodel():
    def __init__(self) -> None:
        self.path: Path = None
        self.g1m_hash = None
        self.g1m_data = None
        self.ktid_name = "file"
        self.ktid_dict = {}
        self.kidsob_dict = {}
        self.metadata = {}
        self.g1ts = {}
        self.files = {}
        self.grouped_files = {}
        self.skeleton = {}
        self.vgmaps = {}
        self.curr_index = 0
        self.botw_bones = botw_bones
        self.botw_bones_rev = botw_bones_rev
        self.arm = None
        self.meshes= []
        self.dump_path = get_aoc_files_path()
        # try:
        # except:
        #     pass
        # self.skip_textures = False
    
    def get_g1t_data_from_dump(self,g1ts=[]):
        print("Ktid dict size: ", len(self.ktid_dict.keys()))
        print("Kidsob dict size: ", len(self.kidsob_dict.keys()))
        # self.dump_path = get_aoc_files_path()
        if self.dump_path is None:
            print("AOC path not found")
            return
        print(f"Using AOC path: {self.dump_path}")
        i = 0
        for ind, ktid_hash in self.ktid_dict.items():
            # print(f"Processing KTID: {ind}")
            g1t_hash = self.get_g1t_hash_from_ktid_hash(ktid_hash, ind)
            if g1t_hash is not None:
                g1t_path = next((e for e in g1ts if g1t_hash.lower() == e.stem.lower()), None)
                g1t_path = self.find_g1t(g1t_hash) if g1t_path is None else g1t_path
                if g1t_path:
                    # print(f"Found G1T file: {g1t_hash}")
                    g1t = G1T(g1t_path)
                    self.g1ts[str(ind)] = {"g1t": g1t, "dds_name": f""}
                else:
                    print(f"G1T file not found: {g1t_hash}")
            else:
                print(f"G1T hash  not found for KTID: {ktid_hash}")
    
        
    def prepare_meshes_for_export(self, vgmaps):
        print("\n\n Preparing meshes for export\n\n")
        for m in self.meshes:
            is_updated = False
            vgmap = m["3DMigoto:VGMap:"]
            for vg in m.vertex_groups:
                if vg.name not in vgmap:
                    print(f"Vg {vg.name} missing in {m.name}, attempting to fix...")
                    if vg.name not in vgmaps.keys():
                        e = f"Vg {vg.name} not found in vgmaps"
                        raise ValueError(e)
                    vgmap[vg.name] = vgmaps[vg.name]
                    is_updated = True
            if is_updated:
                m["3DMigoto:VGMap:"] = vgmap

    def tex_ktid_index_to_str_name(self, ktid_ind):
        int_ktid_ind = int(ktid_ind)
        for section in self.metadata.get("sections", []):
            if section.get("type", "") == "MATERIALS":
                for i, tex_elem in enumerate(section.get("data", [])):
                    # if tex_elem.get("id_referenceonly", -1) == mesh_ind:
                    for tex in tex_elem.get("textures", []):
                        if tex.get("id", -1) == int_ktid_ind:
                            if tex.get("type", -1) == 1 and tex.get("subtype", -1) == 1:
                                return "alb"
                            if tex.get("type", -1) == 3 and tex.get("subtype", -1) == 8:
                                return "nrm"
                            # if tex.get("type", -1) == 66 and tex.get("subtype", -1) == 66:
                            if tex.get("type", -1) == 37 and tex.get("subtype", -1) == 37:
                                return "spm"
                            if tex.get("type", -1) == 19 and tex.get("subtype", -1) == 0:
                                return "emm"
                            if tex.get("type", -1) == 5 and tex.get("subtype", -1) == 5:
                                return "aoo"
        return "tex"
                  
    def pack_g1ts(self, tex_dir, dest_dir):
        tex_dir = Path(tex_dir)
        dest_dir = Path(dest_dir)
        json_md5 = json.loads((tex_dir / "md5.json").read_text())
        for dds_file in tex_dir.glob("*dds"):
            dds_data = dds_file.read_bytes()
            md5 = md5_bytes(dds_data)
            if md5 != json_md5.get(dds_file.name, ""):
                ttype, ind, g1t_hash, ktid_ind = dds_file.stem.split("_")
                g1t_path = self.find_g1t(g1t_hash)
                if g1t_path is None:
                    print("G1T file not found: ", g1t_hash)
                else:
                    try:
                        g1t = G1T(g1t_path)
                        g1t.dds[int(ind)] = dds_data
                        dest_dir.mkdir(parents=True, exist_ok=True)
                        g1t.save_file(dest_dir / f"{g1t_hash}.g1t")
                    except:
                        print(f"Error processing: {dds_file.name}")
                    
        
            
    
    def extract_g1t_textures(self, dirr):
        dirr = Path(dirr)
        dirr.mkdir(parents=True, exist_ok=True)
        res = {}
        md5s = {}
        for ind, g1t_params in self.g1ts.items():
            g1t = g1t_params["g1t"]
            for i, rawdata in enumerate(g1t.dds):
                pref = self.tex_ktid_index_to_str_name(ind)
                file_name = f"{pref}_{i}_{g1t.Hash}_{ind}.dds"
                self.g1ts[ind]["dds_name"] = file_name
                dest_path = dirr / file_name
                dest_path.write_bytes(rawdata)
                res[str(g1t.Hash)] = g1t.metadata
                md5s[file_name] = md5_bytes(rawdata)
        json_path = dirr / "g1t.json"
        json_path_md5 = dirr / "md5.json"
        json_path.write_text(json.dumps(res, indent=4))
        json_path_md5.write_text(json.dumps(md5s, indent=4))
        #extract materials
        mat_dir = dirr / "materials"
        mat_dir.mkdir(parents=True, exist_ok=True)
        for section in self.metadata.get("sections", []):
            section_type = section.get("type", "")
            if section_type == "MATERIALS":
                for i, mat_info in enumerate(section.get("data", [])):
                    mat_name = f"material_{self.g1m_hash}_{mat_info.get('id_referenceonly', i)}"
                    mat_path = mat_dir / f"{mat_name}.json"
                    mat_path.write_text(json.dumps(mat_info, indent=4))
            elif section_type == "SHADER_PARAMS":
                for i, shader_info in enumerate(section.get("data", [])):
                    shader_name = f"shader_{self.g1m_hash}_{shader_info.get('id_referenceonly', i)}"
                    shader_path = mat_dir / f"{shader_name}.json"
                    shader_path.write_text(json.dumps(shader_info, indent=4))

        
    
    def collect_g1t_textures(self, dirr, dest_dir):
        dirr = Path(dirr)
        dest_dir = Path(dest_dir)
        res = {}
        for file in dirr.glob("*.dds"):
            if file.stem.count("_") != 3:
                print(f"Invalid file name: {file.name}")
                continue
            rawdata = file.read_bytes()
            pref, ind, file_hash, ktid_ind = file.stem.split("_")
            index = int(ind)
            g1t = self.g1ts[ktid_ind]["g1t"]
            md5_hash = md5_bytes(rawdata)
            van_hash = g1t.metadata["textures"][index]["MD5"]
            if md5_hash != van_hash: #save only changed textures
                g1t.dds[index] = rawdata
                res[file_hash] = g1t
        dest_dir.mkdir(parents=True, exist_ok=True)
        for file_hash, g1t in res.items():
            g1t_path = dest_dir / f"{file_hash}.g1t"
            g1t.save_file(g1t_path)
                
            
            
        
    
    def find_ktid(self, ktid_name):
        return self.find_file(ktid_name, ".ktid", "ktid")
    
    def find_g1t(self, g1t_name):
        return self.find_file(g1t_name, ".g1t", "g1t")
    
    def find_g1m(self, g1m_name):
        return self.find_file(g1m_name, ".g1m", "g1m")
    
    def find_kidsob(self, kname):
        if "CharacterEditor" in kname:
            kname = kname.split(".")[0] if "." in kname else kname
            k2 =  self.find_file(kname, ".kidssingletondb", "kidsobjdb")
            if k2 is not None:
                return k2
        return self.find_file(kname, ".kidsobjdb", "kidsobjdb")
    
    def find_file(self, file_name, ext, emb_dir):
        folders = [e for e in self.dump_path.glob("*") if e.is_dir()]
        for folder in folders:
            file = folder / emb_dir / f"{file_name}{ext}"
            # print(folder, file)
            if file.exists():
                return file
        return None
    
    def generate_materials(self, tex_dir, isemm=False, isnrm=True, isspm=True):
        tex_dir = Path(tex_dir)
        
        mesh_to_mat_index = {}
        for section in self.metadata.get("sections", []):
            if section.get("type", "") == "SUBMESH":
                for i, tex_elem in enumerate(section.get("data", [])):
                    # if tex_elem.get("id_referenceonly", -1) == mesh_ind:
                    mesh_to_mat_index[str(i)] = tex_elem["materialIndex"]
        meshes = [G1mMesh(g1m_hash=self.g1m_hash ,ob=ob,isemm=isemm, isnrm=isnrm, isspm=isspm) for ob in self.meshes]
        for m in meshes:
            print(m.index)
            try:
                index = int(m.index)
            except:
                continue
            for section in self.metadata.get("sections", []):
                if section.get("type", "") == "MATERIALS":
                    mat_index = mesh_to_mat_index[m.index]
                    tex_elem = section["data"][mat_index]
                    # for i, tex_elem in enumerate(section.get("data", [])):
                        # if tex_elem.get("id_referenceonly", -1) == mesh_ind:
                        
                        # if tex_elem.get("id_referenceonly", -1) == index:
                    for tex in tex_elem.get("textures", []):
                        id = str(tex.get("id", -1))
                        if id in self.g1ts:
                            g1t = self.g1ts[id]
                            if tex.get("type", -1) == 1 and tex.get("subtype", -1) == 1:
                                m.alb = tex_dir / g1t["dds_name"]
                            if tex.get("type", -1) == 3 and tex.get("subtype", -1) == 8:
                                m.nrm = tex_dir / g1t["dds_name"]
                            if tex.get("type", -1) == 37 and tex.get("subtype", -1) == 37:
                                m.spm = tex_dir / g1t["dds_name"]
                            if tex.get("type", -1) == 19 and tex.get("subtype", -1) == 0:
                                m.emm = tex_dir / g1t["dds_name"]
                            if tex.get("type", -1) == 5 and tex.get("subtype", -1) == 5:
                                m.ao = tex_dir / g1t["dds_name"]
                    # print(index, str(m.alb))
                    # break
        for m in meshes:
            m.generate_material()     
        
        
        for section in self.metadata.get("sections", []):
            if section.get("type", "") == "MATERIALS":
                for i, mat_info in enumerate(section.get("data", [])):
                    mat_name = f"{self.g1m_hash}_{mat_info.get('id_referenceonly', i)}"
                    prob_mat = bpy.data.materials.get(mat_name)
                    if prob_mat:
                        continue
                    mat = bpy.data.materials.new(mat_name)
                    if mat is None:
                        continue
                    mat.use_nodes = True
                    bsdf = mat.node_tree.nodes["Principled BSDF"]
                    for tex in tex_elem.get("textures", []):
                        id = str(tex.get("id", -1))
                        if id in self.g1ts:
                            g1t = self.g1ts[id]
                            if tex.get("type", -1) == 1 and tex.get("subtype", -1) == 1:
                                dds = import_dds(tex_dir / g1t["dds_name"])
                                if dds:
                                    texImage = mat.node_tree.nodes.new('ShaderNodeTexImage')
                                    texImage.image = dds
                                    mat.node_tree.links.new(bsdf.inputs['Base Color'], texImage.outputs['Color'])
                                    break
                break
    
    def set_mesh_properties(self):
        for m in self.meshes:
            index = m.name.split(".")[0] if "." in m.name else m.name
            try:
                index = int(index)
            except:
                continue
            for section in self.metadata.get("sections", []):
                ttype = section.get("type", "")
                if ttype == "SUBMESH":
                    m["materialIndex"] = section["data"][index]["materialIndex"]
                    m["shaderParamIndex"] = section["data"][index]["shaderParamIndex"]
                elif ttype == "MATERIALS":
                    self.arm["materials_count"] = str(section.get("count", len(section.get("data", []))))
                elif ttype == "SHADER_PARAMS":
                    self.arm["shaderParams_count"] = str(section.get("count", len(section.get("data", []))))

    
    def update_metadata_from_scene(self):
        for m in self.meshes:
            index = m.name.split(".")[0] if "." in m.name else m.name
            try:
                index = int(index)
            except:
                continue
            for section in self.metadata.get("sections", []):
                ttype = section.get("type", "")
                if ttype == "SUBMESH":
                    section["data"][index]["materialIndex"] = int(m["materialIndex"])
                    section["data"][index]["shaderParamIndex"] = int(m["shaderParamIndex"])

    
    def get_ktid_hash_from_g1t_hash(self, g1t_hash):
        for main_hash, kidso_data in self.kidsob_dict.items():
            for pos_ktid_hash, tex_list in kidso_data.items():
                for tex_hash in tex_list:
                    if g1t_hash == tex_hash:
                        return main_hash
        return None
        
    def get_g1t_hash_from_ktid_hash(self, ktid_hash, ind):
        for main_hash, kidso_data in self.kidsob_dict.items():
            for pos_ktid_hash, tex_list in kidso_data.items():
                if ktid_hash == main_hash:
                    for tex_hash in tex_list:
                        if tex_hash != "00000000":
                            return tex_hash #assuming only 1 texture per ktid hash
        return None
    
    def update_ktid_from_path(self, ktidpath):
        if ktidpath is not None:
            self.ktid_dict = ktid_file_to_dict(ktidpath)
            self.ktid_name = Path(ktidpath).stem
        else:
            ktid_hash = g1m_to_g1t_hashes.get(self.g1m_hash, {}).get("g1t", None)
            if ktid_hash is not None:
                self.ktid_name = ktid_hash
                ktid_path = self.find_ktid(ktid_hash)
                if ktid_path is not None:
                    self.ktid_dict = ktid_file_to_dict(ktid_path)
            
        
    def update_kidsob_from_path(self, kidsobpath):
        if kidsobpath is not None:
            kidsob = KidsOb()
            kidsob.from_binary_file(kidsobpath)
            self.kidsob_dict = kidsob.to_dict()
        else:
            print("No kidsob path")
            kidsob_hash = g1m_to_g1t_hashes.get(self.g1m_hash, {}).get("kidsobjdb", None)
            # kidsob_hash = g1m_to_g1t_hashes[self.g1m_hash]["kidsobjdb"]
            if kidsob_hash is not None:
                print(f"Kidsob hash: {kidsob_hash}")
                kidsob_path = self.find_kidsob(kidsob_hash)
                if kidsob_path is not None:
                    print(f"Kidsob path: {kidsob_path}")
                    kidsob = KidsOb()
                    kidsob.from_binary_file(kidsob_path)
                    self.kidsob_dict = kidsob.to_dict()
                    return
            # raise Exception("No kidsob path")
            
    
    def skip_textures(self):
        return len(self.kidsob_dict.keys()) == 0 or len(self.ktid_dict.keys()) == 0
    
    def extract_to_temp(self, skip_drivermesh=False, skip_transformed=False):
        temp_path = Path(os.path.join(os.path.expandvars("%TEMP%"), self.path.stem))
        print(str(temp_path))
        remove_dir_if_exists(temp_path)
        temp_path.mkdir()
        for filename, data in self.files.items():
            if not ((skip_drivermesh and "drivermesh" in filename) or (skip_transformed and "transformed" in filename)):
                destpath =  temp_path / Path(filename).name 
                print(destpath.as_posix())
                destpath.write_bytes(data)
            if str(filename).lower().endswith(".vgmap"):
                json_data = json.loads(data)
                for key, value in json_data.items():
                    print(key, value)
                    self.vgmaps[key] = value
        return temp_path
    
    def trim_files_paths(self):
        self.files = {str(Path(fname).name): data for fname, data in self.files.items()}
        
    def pair_files_for_import(self):
        keys = [e.split(".")[0] for e in self.files.keys() if "." in e]
        res = {}
        for key in keys:
            res[key] = {}
            for k, item in self.files.items():
                if k.startswith(f"{key}."):
                    res[key][k] = item
        self.grouped_files = res
        return res
    
    def parse_skeleton(self):
        self.skeleton = parseSkelG1M(self.g1m_data)
        self.arm = create_armature_from_bone_list(self.skeleton)
        # rename_bones(self.arm, self.botw_bones)
    
    def process_objects(self, rename_bones_flag):
        col = bpy.data.collections.get("Collection")
        if col is None:
            col = next((c for c in bpy.data.collections), None)
        # col.objects.link(self.arm)
        apply_transforms([self.arm])
        apply_transforms(self.meshes)
        for ob in self.meshes:
            # col.objects.link(ob)
            add_armature_modifier(ob, self.arm)
            ob.parent = self.arm
            
            for uvmap in ob.data.uv_layers:
                uvmap.name = 'UVMap'
        self.arm.scale = (0.01, 0.01, 0.01)
        apply_transforms([self.arm])
        if rename_bones_flag:
            rename_bones(self.arm, self.botw_bones)
            for ob in self.meshes:
                for vg in ob.vertex_groups:
                    vg.name = self.botw_bones.get(vg.name, vg.name)
    
    def save_ktid(self, dest_dir, tex_dir):
        print(f"Saving KTID to {dest_dir}")
        path = tex_dir / "ktid.json"
        if not path.exists() or not tex_dir.exists():
            return
        ktid_dict = json.loads(path.read_text())
        res = {}
        for ind, g1t_hash in ktid_dict.items():
            pos_hash = self.get_ktid_hash_from_g1t_hash(g1t_hash)
            if pos_hash is None:
                print(f"KTID hash not found for G1T hash: {g1t_hash}, skipping ktid saving")
                return
            res[ind] = pos_hash
        destfile = dest_dir / f"{self.ktid_name}.ktid"
        dest_dir.mkdir(parents=True, exist_ok=True)
        print(res)
        with open(destfile, "wb") as f:
            f.write(ktid_dict_to_binary(res))

    
    def debug_print_g1ts(self, dest_dir):
        print("\n")
        res = {}
        for ind, ktid_hash in self.ktid_dict.items():
            res[ind] = {}
            for _, g1t in self.g1ts.items():
                _, _, g1t_hash, ktid_ind = g1t["dds_name"][:-4].split("_")
                if ktid_ind == ind:
                    print(f"KTID ind: {ind} hash {ktid_hash} G1T hash: {g1t_hash}")
                    res[ind] = g1t_hash
                    break
        with open(dest_dir / "ktid.json", "w") as f:
            f.write(json.dumps(res, indent=4))
                
    
    
    
class G1mMesh():
    def __init__(self, g1m_hash, ob=None, alb=None, nrm=None, spm=None, emm=None, isemm=False, isnrm=True, isspm=True) -> None:
        self.g1m_hash = g1m_hash
        self.ob = ob
        self.name = ob.name if ob else ""
        self.alb = alb
        self.nrm = nrm
        self.spm = spm
        self.emm = emm
        texconv = Path(os.path.expandvars("%localappdata%/AgeOfCalamity/texconv.exe"))
        self.texconv = texconv if texconv.exists() else None
        self.temp_path = Path(os.path.expandvars(f"%TEMP%/{g1m_hash}_png"))
        remove_dir_if_exists(self.temp_path)
        self.temp_path.mkdir(exist_ok=True, parents=True)
        self.isemm = isemm
        self.isnrm = isnrm
        self.isspm = isspm
        self.name = self.name[:-4] if is_name_duplicate(self.name) else self.name
        self.index = self.name.split(".")[0] if "." in self.name else None
    
    def generate_material(self):
        mat_index = self.ob["materialIndex"]
        # mat_name = f"{self.g1m_hash}_{self.name}"
        mat_name = f"{self.g1m_hash}_{mat_index}"
        pos_mat = bpy.data.materials.get(mat_name)
        if not pos_mat:
            pos_mat = bpy.data.materials.new(mat_name)
            # bpy.data.materials.remove(bpy.data.materials[mat_name])
        mat = pos_mat
        mat.use_nodes = True
        if self.ob.data.materials:
            self.ob.data.materials.clear()
        self.ob.data.materials.append(mat)
        im_alb = import_dds(self.alb)
        im_emm = import_dds(self.emm)
        im_nrm = import_dds(self.nrm)
        im_spm = import_dds(self.spm)
        """Alb"""
        if self.alb is not None and Path(self.alb).exists() and im_alb is not None:
            bsdf = mat.node_tree.nodes["Principled BSDF"]
            texImage = mat.node_tree.nodes.new('ShaderNodeTexImage')
            # texImage.image = bpy.data.images.load(str(self.alb))
            texImage.image = im_alb
            mat.node_tree.links.new(bsdf.inputs['Base Color'], texImage.outputs['Color'])
            """Emmision"""
            if self.isemm and self.emm is not None and Path(self.emm).exists() and im_emm is not None:
                texImage = mat.node_tree.nodes.new('ShaderNodeTexImage')
                # texImage.image = bpy.data.images.load(str(self.emm))
                texImage.image = im_emm
                mat.node_tree.links.new(bsdf.inputs['Emission'], texImage.outputs['Color'])
        else: #emmision as alb
            bsdf = mat.node_tree.nodes["Principled BSDF"]
            texImage = mat.node_tree.nodes.new('ShaderNodeTexImage')
            # texImage.image = bpy.data.images.load(str(self.alb))
            texImage.image = im_emm
            mat.node_tree.links.new(bsdf.inputs['Base Color'], texImage.outputs['Color'])
            
        """Normal"""
        if self.isnrm and self.nrm is not None and Path(self.nrm).exists() and im_nrm is not None:
            texImage = mat.node_tree.nodes.new('ShaderNodeTexImage')
            # texImage.image = bpy.data.images.load(str(self.nrm))
            texImage.image = im_nrm
            mat.node_tree.links.new(bsdf.inputs['Normal'], texImage.outputs['Color'])
        else:
            normNode = mat.node_tree.nodes.new('ShaderNodeNormalMap')
            mat.node_tree.links.new(bsdf.inputs['Normal'], normNode.outputs['Normal'])
        """Specular"""
        if self.isspm and self.spm is not None and Path(self.spm).exists() and im_spm is not None:
            texImage = mat.node_tree.nodes.new('ShaderNodeTexImage')
            # texImage.image = bpy.data.images.load(str(self.spm))
            texImage.image = im_spm
            mat.node_tree.links.new(bsdf.inputs['Specular'], texImage.outputs['Color'])
    
    def import_dds(self, dds_path, is_overwrite=False):
        banned_hashes = ["333fb7ce492025ef14da0287ae535f52","0f20b8b67d52522ca70e61765e6e9b74"]
        if dds_path is None or not Path(dds_path).exists():
            return None
        dds_path = Path(dds_path)
        if self.texconv is not None:
            c = [str(self.texconv), "-ft", "PNG", "-o", str(self.temp_path), str(dds_path)]
            p = subprocess.run(c, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if p.returncode == 0:
                png_path = self.temp_path / f"{dds_path.stem}.png"
                return bpy.data.images.load(str(png_path))
                
        try:
            if md5_bytes(dds_path.read_bytes()) in banned_hashes:
                #some garbage dds file
                return None
            
            filepath = str(dds_path)
            if bpy.data.images.get(dds_path.stem) and is_overwrite:
                return bpy.data.images[dds_path.stem]
            bpy.ops.dds.import_dds(filepath=filepath, files=[{"name":dds_path.name, "name":dds_path.name}], directory=str(dds_path.parent))
            im = bpy.data.images[dds_path.stem]
            im["dds_path"] = str(dds_path)
            return im
        except:
            return None



if __name__=="__main__":
    g1m = G1Mmodel()
    filename = r"W:\AOC_modding\coding\g1m_exporter_v1.3.8\1eab2c04.g1m"
    parseG1MFile(g1m, filename[:-4], overwrite = True,\
                write_buffers = True, cull_vertices = True,\
                transform_cloth = True, write_empty_buffers = False)
    
    g1m.files = {str(Path(fname).name): data for fname, data in g1m.files.items()}
        
        
    print(md5_bytes(g1m.g1m_data))
    print(g1m.files.keys())
    p = Path(r"W:\AOC_modding\coding\g1m_exporter_v1.3.8\1eab2c04")
    for filename, rawdata in g1m.files.items():
        Hash = md5_bytes(rawdata)
        Hash1 = file_md5(p / filename)
        if Hash != Hash1:
            print(f"Hashes do not match: {filename}")
            
        # else:
        # print(filename, md5_bytes(rawdata))
    
    for file in p.glob("*"):
        if file.name not in g1m.files:
            print(f"File not found: {file.name}")
        elif file_md5(str(file)) != md5_bytes(g1m.files[file.name]):
            print(f"Hashes do not match: {file.name}")
            
    print("\n\n")
    res = parseSkelG1M(r"E:\AOC\_extracted\CharacterEditor\g1m\0a47d2d8")
    with open("tmp.json", "w") as f:
        f.write(json.dumps(res, indent=4))
    # print(json.dumps(res, indent=4))