import hashlib
from io import BytesIO
import os
import shutil
import sys
import json
from pathlib import Path
import bpy
import math
from copy import deepcopy
from mathutils import Quaternion, Vector, Euler
# from tkinter import filedialog


def update_vgs_for_meshes(arm):
    #call after renaming bones to AOC bones
    print(arm, "metadata" in arm)
    metadata = json.loads(arm["metadata"])
    print(metadata.keys())
    skel_data = json.loads(arm["skeleton"])
    meshes = [o for o in bpy.data.objects if o.type=="MESH" and o.parent == arm]
    for mesh in meshes:
        update_vgs_for_mesh(mesh, metadata, skel_data)
    arm["metadata"] = json.dumps(metadata)
    
def get_section(metadata, ttype):
    for i, section in enumerate(metadata['sections']):
        if section['type'] == ttype:
            return i, section
    raise ValueError(f"Section {ttype} not found in metadata!")


def update_vgs_for_mesh(mesh,  metadata, skel_data):
    #call after renaming bones to AOC bones
    try:
        ind = int(mesh.name.split(".")[0]) if "." in mesh.name else int(mesh.name)
    except:
        print(f"transformed or drivermesh, skip it: {mesh.name}")
        return # transformed or drivermesh, skip it
    bnp_index, bonepalettes = get_section(metadata, "JOINT_PALETTES")
    sbm_index, submeshes = get_section(metadata, "SUBMESH")
    submesh_data = submeshes["data"][ind]
    bone_palette = bonepalettes["data"][submesh_data["bonePaletteIndex"]]
    bone_palette_id = bone_palette["block_id_referenceonly"]
    vgmap = dict(mesh["3DMigoto:VGMap:"])
    mis_vgs = [vg for vg in mesh.vertex_groups if vg.name not in vgmap.keys()]
    if not mis_vgs:
        return # mesh is correct
    for vg in mis_vgs:
        bone_id = vg.name.split("_")[-1] if "_" in vg.name else vg.name
        try:
            bone_id_int = int(bone_id)
        except:
            print(f"ERROR: Bone {bone_id} Cannot be converted to int!")
            raise ValueError("")
        bone_data = next((e for e in skel_data["boneList"] if e["bone_id"] == vg.name), None)
        if not bone_data:
            print(f"ERROR: Bone {vg.name} not found in skeleton data!")
            raise ValueError("")
        bone_n = next((k for k, v in skel_data["boneToBoneID"].items() if v==bone_id_int), None)
        if not bone_n:
            print(f"ERROR: Bone {bone_id} not found in boneToBoneID dict!")
            raise ValueError("")
        if is_bone_in_bonepalette(metadata, submesh_data["bonePaletteIndex"], int(bone_n)):
            continue
        new_joint = find_joint_palette_for_bone(metadata, int(bone_n))
        if not new_joint:
            print(f"ERROR: Bone {bone_n} not found in any joint palettes!")
            raise ValueError("")
        new_joint["id_referenceonly"] = int(bone_palette["joint_count"])
        bone_palette["joint_count"] += 1
        bone_palette["joints"].append(new_joint)
        print(f"INFO: Added {vg.name} to joint palette for mesh {mesh.name}")
        print(new_joint)
        metadata['sections'][bnp_index]["data"][submesh_data["bonePaletteIndex"]] = bone_palette
        for i in range(len(bone_palette['joints'])):
            if bone_palette["joints"][i]["id_referenceonly"] == new_joint["id_referenceonly"]:
                vgmap[vg.name] = i * 3
                print(f"INFO: Added {vg.name} to VGMap for mesh {mesh.name}")
                break
        mesh["3DMigoto:VGMap:"] = vgmap
    return metadata
        

def is_bone_in_bonepalette(metadata, bonepalette_index, bone_n):
    
    bnp_index, bonepalettes = get_section(metadata, "JOINT_PALETTES")
    for joint in bonepalettes["data"][bonepalette_index]["joints"]:
        if joint["jointIndex"] == bone_n:
            return True
    return False
    
    
def find_joint_palette_for_bone(metadata, bone_n):
    
    bnp_index, bonepalettes = get_section(metadata, "JOINT_PALETTES")
    for bonepalette in bonepalettes["data"]:
        for joint in bonepalette["joints"]:
            if joint["jointIndex"] == bone_n:
                return deepcopy(joint)
    return None
        

        
        
        
        
    

    
    
    # arm["metadata"] = json.dumps(metadata)


def generate_textures_for_material(mat, alb=None, emm=None, nrm=None, spm=None):
        im_alb = import_dds(alb)
        im_emm = import_dds(emm)
        im_nrm = import_dds(nrm)
        im_spm = import_dds(spm)
        """Alb"""
        if im_alb:
            mat.use_nodes = True
            bsdf = mat.node_tree.nodes["Principled BSDF"]
            texImage = mat.node_tree.nodes.new('ShaderNodeTexImage')
            # texImage.image = bpy.data.images.load(str(self.alb))
            texImage.image = im_alb
            mat.node_tree.links.new(bsdf.inputs['Base Color'], texImage.outputs['Color'])
        else:
            return 
        """Emmision"""
        if im_emm:
            texImage = mat.node_tree.nodes.new('ShaderNodeTexImage')
            # texImage.image = bpy.data.images.load(str(self.emm))
            texImage.image = im_emm
            mat.node_tree.links.new(bsdf.inputs['Emission'], texImage.outputs['Color'])
            
        """Normal"""
        if im_nrm:
            texImage = mat.node_tree.nodes.new('ShaderNodeTexImage')
            # texImage.image = bpy.data.images.load(str(self.nrm))
            texImage.image = im_nrm
            mat.node_tree.links.new(bsdf.inputs['Normal'], texImage.outputs['Color'])
        else:
            normNode = mat.node_tree.nodes.new('ShaderNodeNormalMap')
            mat.node_tree.links.new(bsdf.inputs['Normal'], normNode.outputs['Normal'])
        """Specular"""
        if im_spm:
            texImage = mat.node_tree.nodes.new('ShaderNodeTexImage')
            # texImage.image = bpy.data.images.load(str(self.spm))
            texImage.image = im_spm
            mat.node_tree.links.new(bsdf.inputs['Specular'], texImage.outputs['Color'])

def duplicate_object(ob):
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = ob
    ob.select_set(True)

    bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'}, TRANSFORM_OT_translate={"value":(0, 0, 0), "orient_type":'GLOBAL', "orient_matrix":((0, 0, 0), (0, 0, 0), (0, 0, 0)), "orient_matrix_type":'GLOBAL', "constraint_axis":(False, False, False), "mirror":False, "use_proportional_edit":False, "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "use_proportional_connected":False, "use_proportional_projected":False, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "cursor_transform":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False, "use_accurate":False, "use_automerge_and_split":False})
    return bpy.context.view_layer.objects.active


def keys_to_ints(d):
    return {k.isdecimal() and int(k) or k:v for k,v in d.items()}
def keys_to_strings(d):
    return {str(k):v for k,v in d.items()}

def update_vgmap_for_ob(obj, vg_step=1):
    vgmaps = {k:keys_to_ints(v) for k,v in obj.items() if k.startswith('3DMigoto:VGMap:')}
    if not vgmaps:
        raise Exception('Selected object has no 3DMigoto vertex group maps')
    for (suffix, vgmap) in vgmaps.items():
        highest = max(vgmap.values())
        for vg in obj.vertex_groups.keys():
            if vg.isdecimal():
                continue
            if vg in vgmap:
                continue
            highest += vg_step
            vgmap[vg] = highest
            print('Assigned named vertex group %s = %i' % (vg, vgmap[vg]))
        obj[suffix] = vgmap

def update_vgmap(operator, context, vg_step=1):
    if not context.selected_objects:
        raise Exception('No object selected')

    for obj in context.selected_objects:
        vgmaps = {k:keys_to_ints(v) for k,v in obj.items() if k.startswith('3DMigoto:VGMap:')}
        if not vgmaps:
            raise Exception('Selected object has no 3DMigoto vertex group maps')
        for (suffix, vgmap) in vgmaps.items():
            highest = max(vgmap.values())
            for vg in obj.vertex_groups.keys():
                if vg.isdecimal():
                    continue
                if vg in vgmap:
                    continue
                highest += vg_step
                vgmap[vg] = highest
                operator.report({'INFO'}, 'Assigned named vertex group %s = %i' % (vg, vgmap[vg]))
            obj[suffix] = vgmap

def duplicate_g1m_object(arm, ob):
    meshes = [o for o in bpy.data.objects if o.type=="MESH" and o.parent == arm]
    metadata = json.loads(arm["metadata"])
    subm_ind, submeshes = get_section(metadata, "SUBMESH")
    new_ind = int(submeshes["count"])
    new_name = f"{new_ind}.vb"
    g1m_hash = arm.name
    index = ob.name.split(".")[0] if "." in ob.name else ob.name
    index = int(index)

    new_ob = duplicate_object(ob)
    # new_ob = ob.copy()
    # new_ob.data = ob.data.copy()
    new_ob.name = new_name
    new_ob.data.name = new_name
    # collection = bpy.context.collection
    # collection.objects.link(new_ob)
    for s, section in enumerate(metadata.get("sections", [])):
        ttype = section.get("type", "")
        if ttype == "SUBMESH":
            section["count"] += 1
            new_submesh = deepcopy(section["data"][index])
            new_submesh["id_referenceonly"] = new_ind
            section["data"].append(new_submesh)
        elif ttype == "MESH_LOD":
            for i, elem in enumerate(section["data"]):
                for k, lod in enumerate(elem["lod"]):
                    if index in lod["indices"]:
                        metadata["sections"][s]["data"][i]["lod"][k]["indices"].append(new_ind)
                        metadata["sections"][s]["data"][i]["lod"][k]["indexCount"] += 1
                        break

    
    tex_dir = Path(arm["tex_dir"])
    json_path = tex_dir / f"metadata_{arm.name}.json"
    if  tex_dir.exists() and json_path.exists():
        json_path.write_text(json.dumps(metadata, indent=4))

    arm["metadata"] = json.dumps(metadata)


def update_meshes_from_metadata(meshes, metadata):
    for mesh in meshes:
        try:
            ind = int(mesh.name.split(".")[0]) if "." in mesh.name else int(mesh.name)
        except:
            print(f"transformed or drivermesh, skip it: {mesh.name}")
            continue
        for section in metadata.get("sections", []):
            ttype = section.get("type", "")
            if ttype == "SUBMESH":
                submesh_data = section["data"][ind]
                mesh["materialIndex"] = int(submesh_data["materialIndex"])
                mesh["shaderParamIndex"] = int(submesh_data["shaderParamIndex"])
                mesh["bonePaletteIndex"] = int(submesh_data["bonePaletteIndex"])
        new_mat_name = f"{mesh.parent.name}_{mesh['materialIndex']}"
        new_mat = bpy.data.materials.get(new_mat_name)
        if new_mat and mesh.material_slots:
            mesh.material_slots[0].material = new_mat
            


def update_materials_after_index_update(arm):
    g1m_hash = arm.name
    metadata = json.loads(arm["metadata"])
    meshes = [o for o in bpy.data.objects if o.type=="MESH" and o.parent == arm]
    for m in meshes:
        index = m.name.split(".")[0] if "." in m.name else m.name
        try:
            index = int(index)
        except:
            continue
        for section in metadata.get("sections", []):
            ttype = section.get("type", "")
            if ttype == "SUBMESH":
                section["count"] = len(section["data"])
                section["data"][index]["materialIndex"] = int(m["materialIndex"])
                section["data"][index]["shaderParamIndex"] = int(m["shaderParamIndex"])
                section["data"][index]["bonePaletteIndex"] = int(m["bonePaletteIndex"])
        if m.material_slots:
            mat_name = f"{g1m_hash}_{m['materialIndex']}"
            mat = bpy.data.materials.get(mat_name)
            if mat:
                m.material_slots[0].material = mat
            else:
                print(f"ERROR: Material {mat_name} not found for mesh {m.name}!")
    
    arm["metadata"] = json.dumps(metadata)

def reload_images(arm):
    meshes = [o for o in bpy.data.objects if o.type=="MESH" and o.parent == arm]
    for obj in meshes:
        for material_slot in obj.material_slots:
            mat = material_slot.material
            if mat and mat.use_nodes:
                for node in mat.node_tree.nodes:
                    if node.type == 'TEX_IMAGE':
                        if node.image:
                            if "dds_path" in node.image:
                                dds_path = str(node.image["dds_path"])
                                bpy.data.images.remove(node.image)
                                new_im = import_dds(dds_path, is_overwrite=True)
                                node.image = new_im

    for im in bpy.data.images:
        if "dds_path" in im:
            dds_path = str(im["dds_path"])
            new_im = import_dds(dds_path, is_overwrite=True)

def revert_after_export(arm, g1m):
    meshes = [o for o in bpy.data.objects if o.type=="MESH" and o.parent == arm]
    arm.scale = (0.01, 0.01,0.01)
    rotate_object_X_quat(arm, 90)
    apply_transforms([arm])
    apply_transforms(meshes)
    if arm["renamed_bones"]:
        rename_bones(arm, g1m.botw_bones)
        for ob in meshes:
            for vg in ob.vertex_groups:
                vg.name = g1m.botw_bones.get(vg.name, vg.name)

    for ob in meshes:
        ob["uvs"] = {}
        for i, uvmap in enumerate(ob.data.uv_layers):
            ob["uvs"][str(i)] = str(uvmap.name)
            uvmap.name = 'UVMap'

def prepare_for_export(arm, g1m):
    bpy.ops.object.mode_set(mode='OBJECT')
    meshes = [o for o in bpy.data.objects if o.type=="MESH" and o.parent == arm]
    arm.scale = (100.0,100.0,100.0)
    rotate_object_X_quat(arm, -90)
    apply_transforms([arm])
    apply_transforms(meshes)
    if arm["renamed_bones"]:
        rename_bones(arm, g1m.botw_bones_rev)
        for ob in meshes:
            for vg in ob.vertex_groups:
                vg.name = g1m.botw_bones_rev.get(vg.name, vg.name)
    for ob in meshes:
        for i, uvmap in enumerate(ob.data.uv_layers):
            # uvmap.name = 'TEXCOORD.xy'
            uvmap.name = ob["uvs"][str(i)]

# from tqdm import tk
def is_vgmap_correct(ob, vgmap):
    for vg in ob.vertex_groups:
        if vg.name not in vgmap.keys():
            return False
    return True

def generate_vgmap(ob, vgmaps):
    res = {}
    for vg in ob.vertex_groups:
        if vg.name in vgmaps.keys():
            res[vg.name] = vgmaps[vg.name]
    return res

def rotate_object_X_quat(obj, angle):
    euler_rotation = Euler((math.radians(angle), 0, 0), 'XYZ')
    quaternion_rotation = euler_rotation.to_quaternion()
    obj.rotation_quaternion = quaternion_rotation @ obj.rotation_quaternion
    bpy.context.view_layer.update()

def add_armature_modifier(mesh_object, armature_object):
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = mesh_object
    mesh_object.select_set(True)
    modifier = mesh_object.modifiers.new(name="Armature", type='ARMATURE')
    modifier.object = armature_object
    modifier.use_vertex_groups = True
    
def apply_transforms(objs):
    if not objs: return
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = objs[0]
    for obj in objs:
        obj.select_set(True)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    
    

def import_armature_from_gltf(gltf_path):
    objs_save = list(bpy.data.objects)
    try:
        bpy.ops.import_scene.gltf(filepath=str(gltf_path))
    except:
        pass
    new_objs = [o for o in bpy.data.objects if o not in objs_save]
    arm = next((o for o in new_objs if o.type == "ARMATURE"), None)
    for o in [o for o in new_objs if o != arm]:
        bpy.data.objects.remove(o)
    return arm

def u32_to_hex(u32):
    return hex(u32)[2:].zfill(8)


def md5_bytes(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()

def file_md5(filename: str) -> str:
    with open(filename, "rb") as f:
        return md5_bytes(f.read())
    
def get_aoc_files_path_str():
    tmp = get_aoc_files_path()
    return "NONE" if tmp is None else tmp

def save_aoc_files_path(p):
    res = {"aoc_path": str(p)}
    json_path = Path(os.path.expandvars("%localappdata%/AgeOfCalamity/aoc_config.json"))
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(res, indent=4))

    
def get_aoc_files_path():
    json_path = Path(os.path.expandvars("%localappdata%/AgeOfCalamity/aoc_config.json"))
    try:
        if json_path.exists():
            with open(json_path, "r") as f:
                data = json.load(f)
            if "aoc_path" in data.keys():
                return Path(data["aoc_path"])
    except:
        pass
    # json_path.parent.mkdir(parents=True, exist_ok=True)
    # folder = select_folder("Select folder with AOC dumped files")
    # dirr = Path(folder)
    # if not (dirr / "CharacterEditor").exists():
    #     # raise FileNotFoundError("CharacterEditor folder not found")
    #     print("Invalid folder selected: CharacterEditor folder not found {}".format(dirr / "CharacterEditor"))
    #     return None
    # res = {"aoc_path": str(folder)}
    # json_path.write_text(json.dumps(res, indent=4))
    return None

def update_json_file_metadata_from_scene(arm):
    tex_dir = Path(arm["tex_dir"])
    json_path = tex_dir / f"metadata_{arm.name}.json"
    if not tex_dir.exists() or not json_path.exists():
        return #nothing to update
    metadata = json.loads(arm["metadata"])
    json_path.write_text(json.dumps(metadata, indent=4))
    

def is_name_duplicate(name):
    size = len(name)
    if size <5:
        return False
    if name[-4] != ".":
        return False
    if not name[-3].isdigit() or not name[-2].isdigit() or not name[-1].isdigit():
        return False
    
    
    return True


class StringBytesIO(BytesIO):
    def write(self, data):
        if isinstance(data, str):
            data = data.encode()
        super().write(data)


def create_armature_from_bone_list(skel_data):
    # Create a new armature and object
    bpy.ops.object.armature_add()
    armature_obj = bpy.context.object
    armature = armature_obj.data
    if skel_data is None:
        return armature_obj
    return armature_obj
    
       # Switch to Edit mode to add bones
    bpy.ops.object.mode_set(mode='EDIT')
    
    bone_map = {}  # To keep track of bones and their names
    
    for bone_data in skel_data['boneList']:
        bone_id = bone_data["bone_id"]
        parent_id = bone_data["parentID"]
        
        # Create a new bone
        bone = armature.edit_bones.new(bone_id)
        head_pos = Vector(bone_data["pos_xyz"])
        # head_pos = Vector([e*10.0 for e in bone_data["pos_xyz"]])
        bone.head = head_pos
        
        # Make bones visually 5 times bigger by setting the tail
        bone.tail = head_pos + Vector((0, 0, 25))
        
        # If bone has a parent, set the parent
        if parent_id != -1:
            parent_bone_id = skel_data['boneList'][parent_id]["bone_id"]
            bone.parent = armature.edit_bones[parent_bone_id]
        
        # Store bone reference in the map
        bone_map[bone_id] = bone
    
    # Switch back to Object mode
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Apply rotation and scale to bones
    for bone_data in skel_data['boneList']:
        bone_id = bone_data["bone_id"]
        bone = armature_obj.pose.bones[bone_id]
        
        # Set rotation
        rotation_q = Quaternion(bone_data["q_wxyz"])
        bone.rotation_quaternion = rotation_q
        
        # Set scale
        scale = Vector(bone_data["scale"])
        bone.scale = scale
    
    # Return the created armature object
    # armature_obj.show_names = True
    return armature_obj

def remove_dir_if_exists(dirr):
    dirr = Path(dirr)
    if dirr.exists():
        shutil.rmtree(dirr)
        

def rename_bones(arm, data):
    for bone in arm.pose.bones:
        if bone.name in data.keys():
            bone.name = data[bone.name]
            

def import_dds(dds_path, is_overwrite=False):
    banned_hashes = ["333fb7ce492025ef14da0287ae535f52","0f20b8b67d52522ca70e61765e6e9b74"]
    if dds_path is None or not Path(dds_path).exists():
        return None
    try:
        dds_path = Path(dds_path)
        if md5_bytes(dds_path.read_bytes()) in banned_hashes:
            #some garbage dds file
            return None
        
        filepath = str(dds_path)
        pos_im = bpy.data.images.get(dds_path.stem)
        if pos_im and is_overwrite:
            pos_im["dds_path"] = str(dds_path)
            return bpy.data.images[dds_path.stem]
        bpy.ops.dds.import_dds(filepath=filepath, files=[{"name":dds_path.name, "name":dds_path.name}], directory=str(dds_path.parent))
        im = bpy.data.images[dds_path.stem]
        im["dds_path"] = str(dds_path)
        return im
    except:
        return None


botw_bones = {
	"bone_623": "Ankle_Assist_R",
	"bone_622": "Ankle_Assist_L",
	"bone_809": "Skirt_1_BC_Armor",
	"bone_821": "Skirt_2_BC_Armor",
	"bone_810": "Skirt_1_BL_Armor",
	"bone_822": "Skirt_2_BL_Armor",
	"bone_811": "Skirt_1_BR_Armor",
	"bone_823": "Skirt_2_BR_Armor",
	"bone_806": "Skirt_1_FC_Armor",
	"bone_818": "Skirt_2_FC_Armor",
	"bone_808": "Skirt_1_FR_Armor",
	"bone_820": "Skirt_2_FR_Armor",
	"bone_831": "Skirt_2_R_Armor",
	"bone_827": "Skirt_1_R_Armor",
	"bone_830": "Skirt_2_L_Armor",
	"bone_826": "Skirt_1_L_Armor",
	"bone_822": "Skirt_2_BL_Armor",
	"bone_810": "Skirt_1_BL_Armor",
	"bone_819": "Skirt_2_FL_Armor",
	"bone_807": "Skirt_1_FL_Armor",
	"bone_606": "Elbow_L",
	"bone_607": "Elbow_R",
	"bone_644": "Clavicle_Assist_L",
	"bone_645": "Clavicle_Assist_R",
	"bone_233": "Chin",
	"bone_0": "Root",
	"bone_2": "Waist",
	"bone_3": "Leg_1_L",
	"bone_4": "Leg_1_R",
	"bone_5": "Leg_2_L",
	"bone_6": "Leg_2_R",
	"bone_7": "Ankle_L",
	"bone_8": "Ankle_R",
	"bone_9": "Toe_L",
	"bone_10": "Toe_R",
	"bone_15": "Spine_1",
	"bone_16": "Spine_2",
	"bone_20": "Neck",
	"bone_22": "Head",
	"bone_25": "Clavicle_L",
	"bone_26": "Clavicle_R",
	"bone_27": "Arm_1_L",
	"bone_28": "Arm_1_R",
	"bone_29": "Arm_2_L",
	"bone_30": "Arm_2_R",
	"bone_31": "Wrist_L",
	"bone_32": "Wrist_R",
	"bone_40": "Finger_A_1_L",
	"bone_41": "Finger_A_1_R",
	"bone_42": "Finger_A_2_L",
	"bone_43": "Finger_A_2_R",
	"bone_44": "Finger_A_3_L",
	"bone_45": "Finger_A_3_R",
	"bone_46": "Finger_B_1_L",
	"bone_47": "Finger_B_1_R",
	"bone_48": "Finger_B_2_L",
	"bone_49": "Finger_B_2_R",
	"bone_50": "Finger_B_3_L",
	"bone_51": "Finger_B_3_R",
	"bone_52": "Finger_C_1_L",
	"bone_53": "Finger_C_1_R",
	"bone_54": "Finger_C_2_L",
	"bone_55": "Finger_C_2_R",
	"bone_56": "Finger_C_3_L",
	"bone_57": "Finger_C_3_R",
	"bone_58": "Finger_D_1_L",
	"bone_59": "Finger_D_1_R",
	"bone_60": "Finger_D_2_L",
	"bone_61": "Finger_D_2_R",
	"bone_62": "Finger_D_3_L",
	"bone_63": "Finger_D_3_R",
	"bone_64": "Finger_E_1_L",
	"bone_65": "Finger_E_1_R",
	"bone_66": "Finger_E_2_L",
	"bone_67": "Finger_E_2_R",
	"bone_68": "Finger_E_3_L",
	"bone_69": "Finger_E_3_R",
	# "bone_600": "Clavicle_Assist_L",
	# "bone_601": "Clavicle_Assist_R",
	"bone_602": "Arm_1_Assist_L",
	"bone_603": "Arm_1_Assist_R",
	"bone_608": "Wrist_Assist_L",
	"bone_609": "Wrist_Assist_R",
	"bone_620": "Knee_L",
	"bone_621": "Knee_R",
	"bone_801": "Waist_Assist",
	"bone_803": "Leg_2_Assist_L",
	"bone_805": "Leg_2_Assist_R"
}

botw_bones_rev = {v: k for k, v in botw_bones.items()}