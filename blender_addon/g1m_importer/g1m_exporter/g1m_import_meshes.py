# Mesh importer for G1M files.
#
# Based primarily off the work of GitHub/Joschuka, GitHub/three-houses-research-team,
# and GitHub/eterniti (G1M Tools), huge thank you!
#
# This code depends on g1m_export_meshes.py and lib_fmtibvb.py being in the same folder.
#
# Steps:
# 1. Run g1m_export_meshes.py
# 2. Edit meshes and metadata as desired.
# 3. Run this script (in the folder with the g1m file).
#
# For command line options:
# /path/to/python3 g1m_import_meshes.py --help
#
# GitHub eArmada8/gust_stuff

try:
    import glob, os, io, sys, struct, shutil, json
    from g1m_importer.g1m_exporter.lib_fmtibvb import *
    from g1m_importer.g1m_exporter.g1m_export_meshes import *
except ModuleNotFoundError as e:
    print("Python module missing! {}".format(e.msg))
    input("Press Enter to abort.")
    raise
from pathlib import Path
from g1m_importer.G1mImporter import G1Mmodel

def list_files_with_suffix(directory, suffix):
    return [str(path) for path in Path(directory).glob(f"*{suffix}")]

def strip_extension(file_name):
    return Path(file_name).stem

def parseG1MforG1MF(g1m_name):
    with open(g1m_name + '.g1m', "rb") as f:
        return parseG1MforG1MFbinary(f.read())
        
def parseG1MforG1MFbinary(data):
    # with open(g1m_name + '.g1m', "rb") as f:
    f = io.BytesIO(data)
    file = {}
    file["file_magic"], = struct.unpack(">I", f.read(4))
    if file["file_magic"] == 0x5F4D3147:
        e = '<' # Little Endian
    elif file["file_magic"] == 0x47314D5F:
        e = '>' # Big Endian
    else:
        print("not G1M!") # Figure this out later
        sys.exit()
    file["file_version"] = f.read(4).hex()
    file["file_size"], = struct.unpack(e+"I", f.read(4))
    chunks = {}
    chunks["starting_offset"], chunks["reserved"], chunks["count"] = struct.unpack(e+"III", f.read(12))
    chunks["chunks"] = []
    f.seek(chunks["starting_offset"])
    have_skeleton = False
    for i in range(chunks["count"]):
        chunk = {}
        chunk["start_offset"] = f.tell()
        chunk["magic"] = f.read(4).decode("utf-8")
        chunk["version"] = f.read(4).hex()
        chunk["size"], = struct.unpack(e+"I", f.read(4))
        chunks["chunks"].append(chunk)
        if chunk["magic"] in ['G1MF', 'FM1G']:
            f.seek(chunk["start_offset"],0)
            g1mf_stream = f.read(chunk["size"])
        else:
            f.seek(chunk["start_offset"] + chunk["size"],0) # Move to next chunk
        file["chunks"] = chunks
    return(g1mf_stream)

def parseG1MF(g1mf_stream,e):
    g1mf_section = {}
    with io.BytesIO(g1mf_stream) as f:
        g1mf_section["magic"] = f.read(4).decode("utf-8")
        g1mf_section["version"], g1mf_section["size"], = struct.unpack(e+"II", f.read(8))
        g1mf_section["unknown0"], g1mf_section["total_bones"], g1mf_section["total_g1ms_sections"],\
            g1mf_section["total_matrices"], g1mf_section["geom_socket_section_count"],\
            g1mf_section["material_section_count"], g1mf_section["shader_param_section_count"],\
            g1mf_section["total_shader_params"], g1mf_section["total_shader_params_name_len"],\
            g1mf_section["shader_section_size_minus_countX4_minus_12"], g1mf_section["vertex_buffer_section_count"],\
            g1mf_section["vertex_attr_section_count"], g1mf_section["unknownC"],\
            g1mf_section["joint_palette_section_count"], g1mf_section["total_joint_count"],\
            g1mf_section["index_buffer_section_count"], g1mf_section["submesh_section_count"],\
            g1mf_section["total_submesh_count"], g1mf_section["mesh_lod_section_count"],\
            g1mf_section["total_mesh_lod_group_count"], g1mf_section["total_mesh_lod_group_submesh_count"]\
            = struct.unpack(e+"21I", f.read(84))
        remaining_data_len = len(g1mf_stream) - f.tell()
        g1mf_section["rest_of_header"] = list(struct.unpack(e+"{0}I".format(int(remaining_data_len/4)), f.read(remaining_data_len)))
        return(g1mf_section)

# Only G1MG section data is rebuilt, everything else is copied over.
# Some of the data is probably not correct, we will not know without further experimentation.
def build_g1mf(new_g1mg_stream, g1m, e = '<'):
    g1m_name = str(g1m.temp_path)
    # Retrieve G1MF section from the current G1M file, as there will be sections we do not rebuild
    old_g1mf_data = parseG1MF(parseG1MforG1MFbinary(g1m.g1m_data), e)
    # Load the NEW metadata.  It's a little inefficient to do it this way, but parsing is very fast so it really doesn't matter.
    model_mesh_metadata = parseG1MG(new_g1mg_stream,e)
    # Rebuild G1MF.
    new_g1mf = old_g1mf_data["magic"].encode()
    new_g1mf += struct.pack(e+"2I", old_g1mf_data["version"], old_g1mf_data["size"])
    new_g1mf += struct.pack(e+"4I", old_g1mf_data["unknown0"], old_g1mf_data["total_bones"],\
        old_g1mf_data["total_g1ms_sections"], old_g1mf_data["total_matrices"])
    mkeys = {}
    for i in range(len(model_mesh_metadata["sections"])):
        mkeys[model_mesh_metadata["sections"][i]["type"]] = i
    new_g1mf += struct.pack(e+"2I", model_mesh_metadata["sections"][mkeys["GEOMETRY_SOCKETS"]]["count"],\
        model_mesh_metadata["sections"][mkeys["MATERIALS"]]["count"])
    total_shader_name_len = 0
    for i in range(len(model_mesh_metadata["sections"][mkeys["SHADER_PARAMS"]]["data"])):
        for j in range(len(model_mesh_metadata["sections"][mkeys["SHADER_PARAMS"]]["data"][i]['shader_block'])):
            namelen = len(model_mesh_metadata["sections"][mkeys["SHADER_PARAMS"]]["data"][i]['shader_block'][j]["name"])
            total_shader_name_len += namelen + (4 - namelen % 4)
    shader_section_size_minus_countX4_minus_12 = model_mesh_metadata["sections"][mkeys["SHADER_PARAMS"]]["size"]\
        - model_mesh_metadata["sections"][mkeys["SHADER_PARAMS"]]["count"] * 4 - 12
    new_g1mf += struct.pack(e+"4I", model_mesh_metadata["sections"][mkeys["SHADER_PARAMS"]]["count"],\
        sum([len(x['shader_block']) for x in model_mesh_metadata["sections"][mkeys["SHADER_PARAMS"]]["data"]]),\
        total_shader_name_len, shader_section_size_minus_countX4_minus_12)
    new_g1mf += struct.pack(e+"I", model_mesh_metadata["sections"][mkeys["VERTEX_BUFFERS"]]["count"])
    # Sum of buffer list is a completely wild guess for "unknownC"
    new_g1mf += struct.pack(e+"2I", model_mesh_metadata["sections"][mkeys["VERTEX_ATTRIBUTES"]]["count"],\
        sum([len(x["buffer_list"]) for x in model_mesh_metadata["sections"][mkeys["VERTEX_ATTRIBUTES"]]["data"]]))
    new_g1mf += struct.pack(e+"2I", model_mesh_metadata["sections"][mkeys["JOINT_PALETTES"]]["count"],\
        sum([len(x["joints"]) for x in model_mesh_metadata["sections"][mkeys["JOINT_PALETTES"]]["data"]]))
    new_g1mf += struct.pack(e+"I", model_mesh_metadata["sections"][mkeys["INDEX_BUFFER"]]["count"])
    # This can't be correct, perhaps the second value is total unknown2==1 or something like that??
    new_g1mf += struct.pack(e+"2I", model_mesh_metadata["sections"][mkeys["SUBMESH"]]["count"],\
        model_mesh_metadata["sections"][mkeys["SUBMESH"]]["count"])
    lod_group_submesh_count = 0
    for i in range(len(model_mesh_metadata["sections"][mkeys["MESH_LOD"]]["data"])):
        lod_group_submesh_count += sum([len(x["indices"]) for x\
            in model_mesh_metadata["sections"][mkeys["MESH_LOD"]]["data"][i]["lod"]])
    new_g1mf += struct.pack(e+"3I", model_mesh_metadata["sections"][mkeys["MESH_LOD"]]["count"],\
        sum([len(x["lod"]) for x in model_mesh_metadata["sections"][mkeys["MESH_LOD"]]["data"]]),\
        lod_group_submesh_count)
    new_g1mf += struct.pack(e+"{0}I".format(len(old_g1mf_data["rest_of_header"])), *old_g1mf_data["rest_of_header"])
    return(new_g1mf)

def parseG1MforG1MG(g1m_name):
    with open(g1m_name + '.g1m', "rb") as f:
        return parseG1MforG1MGbinary(f.read())
    
def parseG1MforG1MGbinary(rawdata):
    # with open(g1m_name + '.g1m', "rb") as f:
    f = io.BytesIO(rawdata)
    file = {}
    file["file_magic"], = struct.unpack(">I", f.read(4))
    if file["file_magic"] == 0x5F4D3147:
        e = '<' # Little Endian
    elif file["file_magic"] == 0x47314D5F:
        e = '>' # Big Endian
    else:
        print("not G1M!") # Figure this out later
        sys.exit()
    file["file_version"] = f.read(4).hex()
    file["file_size"], = struct.unpack(e+"I", f.read(4))
    chunks = {}
    chunks["starting_offset"], chunks["reserved"], chunks["count"] = struct.unpack(e+"III", f.read(12))
    chunks["chunks"] = []
    f.seek(chunks["starting_offset"])
    have_skeleton = False
    for i in range(chunks["count"]):
        chunk = {}
        chunk["start_offset"] = f.tell()
        chunk["magic"] = f.read(4).decode("utf-8")
        chunk["version"] = f.read(4).hex()
        chunk["size"], = struct.unpack(e+"I", f.read(4))
        chunks["chunks"].append(chunk)
        if chunk["magic"] in ['G1MG', 'GM1G']:
            f.seek(chunk["start_offset"],0)
            g1mg_stream = f.read(chunk["size"])
        else:
            f.seek(chunk["start_offset"] + chunk["size"],0) # Move to next chunk
        file["chunks"] = chunks
    return(g1mg_stream)

def build_composite_buffers(g1m_name, model_mesh_metadata, g1mg_stream, skel_data, e = '<'):
    subvbs = [x for x in model_mesh_metadata['sections'] if x['type'] == "SUBMESH"][0]
    mesh_with_subs = find_submeshes(model_mesh_metadata) #dict with key as mesh, value as submesh
    # Grab a list of intact meshes (has fmt/ib/vb)
    # meshfiles = [x[:-4] for x in glob.glob("*.fmt", root_dir=g1m_name) if (x[:-4] in \
    #     [x[:-3] for x in glob.glob("*.ib", root_dir=g1m_name)] and x[:-4] in \
    #     [x[:-3] for x in glob.glob("*.vb", root_dir=g1m_name)])]
    
    fmt_files = list_files_with_suffix(g1m_name, ".fmt")
    ib_files = list_files_with_suffix(g1m_name, ".ib")
    vb_files = list_files_with_suffix(g1m_name, ".vb")

    fmt_files_stripped = {strip_extension(file) for file in fmt_files}
    ib_files_stripped = {strip_extension(file) for file in ib_files}
    vb_files_stripped = {strip_extension(file) for file in vb_files}

    # Find common base names
    meshfiles = list(fmt_files_stripped & ib_files_stripped & vb_files_stripped)
    # Remove any empty mesh files from the list of intact meshes
    meshfiles = [x for x in meshfiles if os.path.getsize('{0}/{1}.ib'.format(g1m_name, x)) > 0]
    composite_vbs = []
    current_vbsub = 0
    for i in mesh_with_subs:
        # When processing each mesh, cull the submesh list of submeshes that have been deleted
        existing_submeshes = [x for x in mesh_with_subs[i] if str(x) in meshfiles]
        if len(existing_submeshes) > 0:
            try:
                fmt = read_fmt("{0}/{1}.fmt".format(g1m_name, existing_submeshes[0]))
                composite_vb = []
                composite_ib = []
                vbsub_info = {}
                for j in range(len(existing_submeshes)):
                    print("Processing submesh {0}...".format(existing_submeshes[j]))
                    # Do not process submesh if it does not match the existing format (set by the first submesh)
                    if fmt == read_fmt("{0}/{1}.fmt".format(g1m_name, existing_submeshes[j])):
                        vb = read_vb("{0}/{1}.vb".format(g1m_name, existing_submeshes[j]), fmt)
                        ib = read_ib("{0}/{1}.ib".format(g1m_name, existing_submeshes[j]), fmt)
                        if len(composite_vb) == 0:
                            composite_vb = vb
                            composite_ib = ib
                        else:
                            # Append the submesh to the mesh; indices need to be updated as vertices have moved in the buffer
                            ib_offset = len(composite_vb[0]['Buffer'])
                            for k in range(len(composite_vb)):
                                composite_vb[k]['Buffer'].extend(vb[k]['Buffer'])
                            for k in range(len(ib)):
                                for l in range(len(ib[k])):
                                    ib[k][l] += ib_offset
                            composite_ib.extend(ib)
                        # Vertex group sanity check, if vgmap available
                        if os.path.exists("{0}/{1}.vgmap".format(g1m_name, existing_submeshes[j])):
                            vgmap = read_struct_from_json("{0}/{1}.vgmap".format(g1m_name, existing_submeshes[j]))
                            # Proceed only if a complete skeleton is available
                            if skel_data['jointCount'] > 1 and not skel_data['boneList'][0]['parentID'] < -200000000:
                                # correct_vgmap = generate_vgmap(subvbs['data'][existing_submeshes[j]]['bonePaletteIndex'], model_mesh_metadata, skel_data)
                                correct_vgmap = vgmap
                                if 'BLENDINDICES' in [x['SemanticName'] for x in vb]:
                                    bl_idx = vb[[x['SemanticName'] for x in vb].index('BLENDINDICES')]['Buffer']
                                    used_bones = sorted(list(set([x for y in bl_idx for x in y])))
                                    rev_vgmap = {vgmap[x]:x for x in vgmap if vgmap[x] in used_bones}
                                    missing_bones = [x for x in rev_vgmap.values() if x not in correct_vgmap]
                                    if len(missing_bones) == 0:
                                        incorrect = [rev_vgmap[x] for x in rev_vgmap if not x == correct_vgmap[rev_vgmap[x]]]
                                        if len(incorrect) > 0:
                                            print("Warning, vertex group sanity check failed!  This model is very unlikely to correctly render.")
                                            print("Incorrect Mappings: {}".format(", ".join(incorrect)))
                                            input("Press Enter to continue.")
                                    else:
                                        print("Warning, vertex group sanity check failed!  This model is very unlikely to correctly render.")
                                        print("Missing bones: {}".format(", ".join(missing_bones)))
                                        # input("Press Enter to continue.")
                        # Determine indexBufferPrimType, which is set in submesh section instead of vertex attribute section
                        if fmt["topology"] == "trianglelist":
                            indexBufferPrimType = 3
                        elif fmt["topology"] == "trianglestrip":
                            indexBufferPrimType = 4
                        else:
                            indexBufferPrimType = 1
                        # Update submesh info with new offsets and counts
                        vbsub_info[existing_submeshes[j]] = {"submeshFlags": subvbs['data'][existing_submeshes[j]]['submeshFlags'],\
                            "vertexBufferIndex": i,\
                            "bonePaletteIndex": subvbs['data'][existing_submeshes[j]]['bonePaletteIndex'],\
                            "boneIndex": subvbs['data'][existing_submeshes[j]]['boneIndex'],\
                            "unknown": subvbs['data'][existing_submeshes[j]]['unknown'],\
                            "shaderParamIndex": subvbs['data'][existing_submeshes[j]]['shaderParamIndex'],\
                            "materialIndex": subvbs['data'][existing_submeshes[j]]['materialIndex'],\
                            "indexBufferIndex": i,\
                            "unknown2": subvbs['data'][existing_submeshes[j]]['unknown2'],\
                            "indexBufferPrimType": indexBufferPrimType,\
                            "vertexBufferOffset": len(composite_vb[0]['Buffer']) - len(vb[0]['Buffer']),\
                            "vertexCount": len(vb[0]['Buffer']),\
                            "indexBufferOffset": int((len(composite_ib) - len(ib)) * 3),\
                            "indexCount": int(len(ib) * 3)}
                    else:
                        pass # skip if fmt does not match the first
            except KeyError as e:
                print("KeyError: Missing value \"{0}\" detected in metadata while processing mesh {1} submesh {2}!".format(e.args[0], \
                    i, existing_submeshes[j]))
                input("Press Enter to abort.")
                raise
        else:
            try:
                # Cannot seem to delete entire meshes, so will generate a dummy mesh if all submeshes have been deleted
                original_fmts = generate_fmts(model_mesh_metadata) # A little inefficient to run JIT but very helpful with error checking
                fmt = original_fmts[i]
                composite_ib = generate_ib(i, g1mg_stream, model_mesh_metadata, original_fmts, e=e)
                composite_vb = generate_vb(i, g1mg_stream, model_mesh_metadata, original_fmts, e=e)
                # Place an empty submesh in the mesh
                vbsub_info = {mesh_with_subs[i][0]: {"submeshFlags": subvbs['data'][mesh_with_subs[i][0]]['submeshFlags'],\
                            "vertexBufferIndex": i,\
                            "bonePaletteIndex": subvbs['data'][mesh_with_subs[i][0]]['bonePaletteIndex'],\
                            "boneIndex": subvbs['data'][mesh_with_subs[i][0]]['boneIndex'],\
                            "unknown": subvbs['data'][mesh_with_subs[i][0]]['unknown'],\
                            "shaderParamIndex": subvbs['data'][mesh_with_subs[i][0]]['shaderParamIndex'],\
                            "materialIndex": subvbs['data'][mesh_with_subs[i][0]]['materialIndex'],\
                            "indexBufferIndex": i,\
                            "unknown2": subvbs['data'][mesh_with_subs[i][0]]['unknown2'],\
                            "indexBufferPrimType": subvbs['data'][mesh_with_subs[i][0]]['indexBufferPrimType'],\
                            "vertexBufferOffset": 0,\
                            "vertexCount": 0,\
                            "indexBufferOffset": 0,\
                            "indexCount": 0}}
            except KeyError as e:
                print("KeyError: Missing value \"{0}\" detected in metadata while processing mesh {1} submesh {2}!".format(e.args[0], \
                    i, mesh_with_subs[i][0]))
                input("Press Enter to abort.")
                raise
        composite_vbs.append({'original_vb_num': i, 'fmt': fmt, 'vb': composite_vb, 'ib': composite_ib, 'vbsub_info': vbsub_info})
    return(composite_vbs)

# This will not be accurate until 4D is implemented
def define_bounding_box(composite_vbs):
    # Initialize bounding box - I have no idea why this works, but it does.
    box = {'min_x': True, 'min_y': True, 'min_z': True, 'max_x': False, 'max_y': False, 'max_z': False}
    # Check every position coordinate and spread out
    for i in range(len(composite_vbs)):
        element = int([x['id'] for x in composite_vbs[i]['fmt']['elements'] if x['SemanticName'] == 'POSITION'][0])
        #if len(composite_vbs[i]['vb'][element]['Buffer']) > 0:
        for j in range(len(composite_vbs[i]['vb'][element]['Buffer'])):
            box['min_x'] = min(box['min_x'], composite_vbs[i]['vb'][element]['Buffer'][j][0])
            box['min_y'] = min(box['min_y'], composite_vbs[i]['vb'][element]['Buffer'][j][1])
            box['min_z'] = min(box['min_z'], composite_vbs[i]['vb'][element]['Buffer'][j][2])
            box['max_x'] = max(box['max_x'], composite_vbs[i]['vb'][element]['Buffer'][j][0])
            box['max_y'] = max(box['max_y'], composite_vbs[i]['vb'][element]['Buffer'][j][1])
            box['max_z'] = max(box['max_z'], composite_vbs[i]['vb'][element]['Buffer'][j][2])
    return(box)

def build_g1mg(g1m, skel_data, e = '<'):
    # Retrieve G1MG section from the current G1M file, as there will be sections we do not rebuild
    # g1mg_stream = parseG1MforG1MG(g1m_name)
    g1m_name = g1m.g1m_hash
    g1mg_stream = parseG1MforG1MGbinary(g1m.g1m_data)
    # Load the metadata - if it does not exist in JSON format, load from G1M instead
    # try:
    #     model_mesh_metadata = read_struct_from_json(g1m_name + "/mesh_metadata.json")
    # except:
    #     print("{0}/mesh_metadata.json missing or unreadable, reading data from {0}.g1m instead...".format(g1m_name))
        # model_mesh_metadata = parseG1MG(g1mg_stream,e)
    model_mesh_metadata = g1m.metadata
    #Load all the buffers, and combine submeshes into meshes
    composite_vbs = build_composite_buffers(str(g1m.temp_path), model_mesh_metadata, g1mg_stream, skel_data, e)
    bounding_box = define_bounding_box(composite_vbs)
    new_g1mg = bytes()
    with io.BytesIO(g1mg_stream) as f:
        try:
            for i in range(len(model_mesh_metadata['sections'])):
                if model_mesh_metadata['sections'][i]['type'] == 'GEOMETRY_SOCKETS':
                    socket_section = bytes()
                    for j in range(len(model_mesh_metadata['sections'][i]['data'])):
                        socket_section += struct.pack(e+"2h7f", model_mesh_metadata['sections'][i]['data'][j]['start']['bone_id'],\
                            model_mesh_metadata['sections'][i]['data'][j]['start']['unknown'],\
                            model_mesh_metadata['sections'][i]['data'][j]['start']['weight'],\
                            *model_mesh_metadata['sections'][i]['data'][j]['start']['scale'],\
                            *model_mesh_metadata['sections'][i]['data'][j]['start']['position'])
                        socket_section += struct.pack(e+"2h7f", model_mesh_metadata['sections'][i]['data'][j]['end']['bone_id'],\
                            model_mesh_metadata['sections'][i]['data'][j]['end']['unknown'],\
                            model_mesh_metadata['sections'][i]['data'][j]['end']['weight'],\
                            *model_mesh_metadata['sections'][i]['data'][j]['end']['scale'],\
                            *model_mesh_metadata['sections'][i]['data'][j]['end']['position'])
                    if len(model_mesh_metadata['sections'][i]['tail']) > 0:
                        socket_section += struct.pack(e+"{0}I".format(len(model_mesh_metadata['sections'][i]['tail'])),\
                            *model_mesh_metadata['sections'][i]['tail'])
                    new_g1mg += struct.pack(e+"3I", model_mesh_metadata['sections'][i]['magic'], len(socket_section)+12,\
                        len(model_mesh_metadata['sections'][i]['data'])) + socket_section
                elif model_mesh_metadata['sections'][i]['type'] == 'MATERIALS':
                    materials_section = bytes()
                    for j in range(len(model_mesh_metadata['sections'][i]['data'])):
                        materials_section += struct.pack(e+"4I", model_mesh_metadata['sections'][i]['data'][j]['unknown1'],\
                            len(model_mesh_metadata['sections'][i]['data'][j]['textures']),\
                            model_mesh_metadata['sections'][i]['data'][j]['unknown2'],\
                            model_mesh_metadata['sections'][i]['data'][j]['unknown3'])
                        for k in range(len(model_mesh_metadata['sections'][i]['data'][j]['textures'])):
                            materials_section += struct.pack(e+"6H", model_mesh_metadata['sections'][i]['data'][j]['textures'][k]['id'],\
                                model_mesh_metadata['sections'][i]['data'][j]['textures'][k]['layer'],\
                                model_mesh_metadata['sections'][i]['data'][j]['textures'][k]['type'],\
                                model_mesh_metadata['sections'][i]['data'][j]['textures'][k]['subtype'],\
                                model_mesh_metadata['sections'][i]['data'][j]['textures'][k]['tilemodex'],\
                                model_mesh_metadata['sections'][i]['data'][j]['textures'][k]['tilemodey'])
                    new_g1mg += struct.pack(e+"3I", model_mesh_metadata['sections'][i]['magic'], len(materials_section)+12,\
                        len(model_mesh_metadata['sections'][i]['data'])) + materials_section
                elif model_mesh_metadata['sections'][i]['type'] == 'SHADER_PARAMS':
                    shader_section = bytes()
                    for j in range(len(model_mesh_metadata['sections'][i]['data'])):
                        shader_section += struct.pack(e+"I", len(model_mesh_metadata['sections'][i]['data'][j]['shader_block']))
                        for k in range(len(model_mesh_metadata['sections'][i]['data'][j]['shader_block'])):
                            shader_name = model_mesh_metadata['sections'][i]['data'][j]['shader_block'][k]['name'].encode() + b'\x00'
                            while len(shader_name) % 4 > 0:
                                shader_name += b'\x00'
                            shader_section += struct.pack(e+"3I2H", model_mesh_metadata['sections'][i]['data'][j]['shader_block'][k]["size"],\
                                len(shader_name), model_mesh_metadata['sections'][i]['data'][j]['shader_block'][k]["unk1"],\
                                model_mesh_metadata['sections'][i]['data'][j]['shader_block'][k]["buffer_type"],\
                                model_mesh_metadata['sections'][i]['data'][j]['shader_block'][k]["buffer_count"])
                            shader_section += shader_name
                            for l in range(len(model_mesh_metadata['sections'][i]['data'][j]['shader_block'][k]['buffer'])):
                                x = model_mesh_metadata['sections'][i]['data'][j]['shader_block'][k]["buffer_type"]
                                if x == 1:
                                    shader_section += struct.pack(e+"f", model_mesh_metadata['sections'][i]['data'][j]['shader_block'][k]['buffer'][l])
                                elif x == 2:
                                    shader_section += struct.pack(e+"2f", *model_mesh_metadata['sections'][i]['data'][j]['shader_block'][k]['buffer'][l])
                                elif x ==  3:
                                    shader_section += struct.pack(e+"3f", *model_mesh_metadata['sections'][i]['data'][j]['shader_block'][k]['buffer'][l])
                                elif x ==  4:
                                    shader_section += struct.pack(e+"4f", *model_mesh_metadata['sections'][i]['data'][j]['shader_block'][k]['buffer'][l])
                                elif x ==  5:
                                    shader_section += struct.pack(e+"i", model_mesh_metadata['sections'][i]['data'][j]['shader_block'][k]['buffer'][l])
                    new_g1mg += struct.pack(e+"3I", model_mesh_metadata['sections'][i]['magic'], len(shader_section)+12,\
                        len(model_mesh_metadata['sections'][i]['data'])) + shader_section
                elif model_mesh_metadata['sections'][i]['type'] == 'VERTEX_BUFFERS':
                    vertex_stream = io.BytesIO()
                    for j in range(len(composite_vbs)):
                        vertex_stream.write(struct.pack(e+"3I", model_mesh_metadata['sections'][i]['data'][composite_vbs[j]['original_vb_num']]["unknown1"],\
                            int(composite_vbs[j]['fmt']['stride']), len(composite_vbs[j]['vb'][0]['Buffer'])))
                        if model_mesh_metadata["version"] > 0x30303430:
                            vertex_stream.write(struct.pack(e+"I", model_mesh_metadata['sections'][i]['data'][composite_vbs[j]['original_vb_num']]["unknown2"]))
                        write_vb_stream(composite_vbs[j]['vb'], vertex_stream, composite_vbs[j]['fmt'], e)
                    vertex_stream.seek(0,0)
                    vertex_section = vertex_stream.read()
                    vertex_stream.close()
                    new_g1mg += struct.pack(e+"3I", model_mesh_metadata['sections'][i]['magic'], len(vertex_section)+12,\
                        len(composite_vbs)) + vertex_section
                elif model_mesh_metadata['sections'][i]['type'] == 'VERTEX_ATTRIBUTES':
                    vbattr_section = bytes()
                    semantic_list = {'POSITION': 0, 'BLENDWEIGHT': 1, 'BLENDINDICES': 2, 'NORMAL': 3, 'PSIZE': 4, 'TEXCOORD': 5,\
                    'TANGENT': 6, 'BINORMAL': 7, 'TESSFACTOR': 8, 'POSITIONT': 9, 'COLOR': 10, 'FOG': 11, 'DEPTH': 12, 'SAMPLE': 13} #What is Sample??
                    dataType_list = {'R32_FLOAT': 0x00, 'R32G32_FLOAT': 0x01, 'R32G32B32_FLOAT': 0x02, 'R32G32B32A32_FLOAT': 0x03,\
                    'R8G8B8A8_UINT': 0x05, 'R16G16B16A16_UINT': 0x07, 'R32G32B32A32_UINT': 0x09, 'R16G16_FLOAT': 0x0A,\
                    'R16G16B16A16_FLOAT': 0x0B, 'R8G8B8A8_UNORM': 0x0D,  'UNKNOWN': 0xFF}
                    for j in range(len(composite_vbs)):
                        vbattr_section += struct.pack(e+"2I", 1, j)
                        vbattr_section += struct.pack(e+"I", len(composite_vbs[j]['fmt']['elements']))
                        for k in range(len(composite_vbs[j]['fmt']['elements'])):
                            vbattr_section += struct.pack(e+"2H4B", int(composite_vbs[j]['fmt']['elements'][k]['InputSlot']), # Not sure if correct\
                                int(composite_vbs[j]['fmt']['elements'][k]['AlignedByteOffset']),\
                                dataType_list[composite_vbs[j]['fmt']['elements'][k]['Format']],\
                                model_mesh_metadata['sections'][i]['data'][composite_vbs[j]['original_vb_num']]['attributes_list'][k]['dummy_var'],\
                                semantic_list[composite_vbs[j]['fmt']['elements'][k]['SemanticName']],\
                                int(composite_vbs[j]['fmt']['elements'][k]['SemanticIndex']))
                    new_g1mg += struct.pack(e+"3I", model_mesh_metadata['sections'][i]['magic'], len(vbattr_section)+12,\
                        len(composite_vbs)) + vbattr_section
                elif model_mesh_metadata['sections'][i]['type'] == 'JOINT_PALETTES':
                    joint_section = bytes()
                    for j in range(len(model_mesh_metadata['sections'][i]['data'])):
                        joint_section += struct.pack(e+"I", len(model_mesh_metadata['sections'][i]['data'][j]['joints']))
                        for k in range(len(model_mesh_metadata['sections'][i]['data'][j]['joints'])):
                            if (model_mesh_metadata['sections'][i]['data'][j]['joints'][k]['0x80000000_flag'] == 'True'):
                                joint_section += struct.pack(e+"3I", model_mesh_metadata['sections'][i]['data'][j]['joints'][k]['G1MMIndex'],\
                                    model_mesh_metadata['sections'][i]['data'][j]['joints'][k]['physicsIndex'] ^ 0x80000000,\
                                    model_mesh_metadata['sections'][i]['data'][j]['joints'][k]['jointIndex'] ^ 0x80000000)
                            else:
                                joint_section += struct.pack(e+"3I", model_mesh_metadata['sections'][i]['data'][j]['joints'][k]['G1MMIndex'],\
                                    model_mesh_metadata['sections'][i]['data'][j]['joints'][k]['physicsIndex'],\
                                    model_mesh_metadata['sections'][i]['data'][j]['joints'][k]['jointIndex'])
                    new_g1mg += struct.pack(e+"3I", model_mesh_metadata['sections'][i]['magic'], len(joint_section)+12,\
                        len(model_mesh_metadata['sections'][i]['data'])) + joint_section
                elif model_mesh_metadata['sections'][i]['type'] == 'INDEX_BUFFER':
                    index_stream = io.BytesIO()
                    for j in range(len(composite_vbs)):
                        # This assumes I am reversing my own code, no exotic formats!
                        index_stream.write(struct.pack(e+"2I", len([x for y in composite_vbs[j]['ib'] for x in y]), \
                            int(composite_vbs[j]['fmt']['format'].split('_FORMAT_R')[1].split('_UINT')[0])))
                        if model_mesh_metadata["version"] > 0x30303430:
                            index_stream.write(struct.pack(e+"I", model_mesh_metadata['sections'][i]['data'][composite_vbs[j]['original_vb_num']]["unknown1"]))
                        write_ib_stream([x for y in composite_vbs[j]['ib'] for x in y], index_stream, composite_vbs[j]['fmt'], e)
                        while (index_stream.tell() % 4) > 0:
                            index_stream.write(b'\x00')
                    index_stream.seek(0,0)
                    index_section = index_stream.read()
                    index_stream.close()
                    new_g1mg += struct.pack(e+"3I", model_mesh_metadata['sections'][i]['magic'], len(index_section)+12,\
                        len(composite_vbs)) + index_section
                elif model_mesh_metadata['sections'][i]['type'] == 'SUBMESH':
                    submesh_section = bytes()
                    submesh_count = 0
                    for j in range(len(composite_vbs)):
                        for k in list(composite_vbs[j]['vbsub_info'].keys()):
                                submesh_section += struct.pack(e+"14I",*list(composite_vbs[j]['vbsub_info'][k].values()))
                                submesh_count += 1
                    new_g1mg += struct.pack(e+"3I", model_mesh_metadata['sections'][i]['magic'], len(submesh_section)+12,\
                        submesh_count) + submesh_section
                elif model_mesh_metadata['sections'][i]['type'] == 'MESH_LOD':
                    subvbs = [x for x in model_mesh_metadata['sections'] if x['type'] == "SUBMESH"][0]
                    vbsubs = find_submeshes(model_mesh_metadata)
                    # Generate a map of original submesh index (old) to repacked submesh index (new), with LOD type
                    subvb_old_to_new = {}
                    new_index = 0
                    for j in range(len(composite_vbs)):
                        for k in range(len(composite_vbs[j]['vbsub_info'])):
                            subvb_old_to_new[list(composite_vbs[j]['vbsub_info'])[k]] = {'new_index': new_index,\
                                'submeshFlags': list(composite_vbs[j]['vbsub_info'].values())[k]['submeshFlags']}
                            new_index += 1
                    existing_subvb = list(subvb_old_to_new) # These are the submeshes that have not been deleted, by old number
                    lod_section = bytes()
                    for j in range(len(model_mesh_metadata['sections'][i]['data'])):
                        lod_block = struct.pack(e+"I", model_mesh_metadata['sections'][i]['data'][j]['LOD'])
                        if model_mesh_metadata["version"] > 0x30303330:
                            lod_block += struct.pack(e+"2I", model_mesh_metadata['sections'][i]['data'][j]['Group'],\
                                model_mesh_metadata['sections'][i]['data'][j]['GroupEntryIndex'])
                        lod_block += struct.pack(e+"2I", model_mesh_metadata['sections'][i]['data'][j]['submeshCount1'],\
                            model_mesh_metadata['sections'][i]['data'][j]['submeshCount2'])
                        if model_mesh_metadata["version"] > 0x30303340:
                            lod_block += struct.pack(e+"4I", model_mesh_metadata['sections'][i]['data'][j]['lodRangeStart'],\
                                model_mesh_metadata['sections'][i]['data'][j]['lodRangeLength'],\
                                model_mesh_metadata['sections'][i]['data'][j]['unknown1'],\
                                model_mesh_metadata['sections'][i]['data'][j]['unknown2'])
                        for k in range(len(model_mesh_metadata['sections'][i]['data'][j]['lod'])):
                            #First cull submeshes that have been deleted, then map to new indices
                            new_indices = [x for x in list(model_mesh_metadata['sections'][i]['data'][j]['lod'][k]['indices']) if x in existing_subvb]
                            new_indices = [subvb_old_to_new[x]['new_index'] for x in new_indices]
                            name = model_mesh_metadata['sections'][i]['data'][j]['lod'][k]['name'].encode()
                            while len(name) < 16:
                                name += b'\x00'
                            lod_block += name
                            lod_block += struct.pack(e+"2H2I",\
                                model_mesh_metadata['sections'][i]['data'][j]['lod'][k]['clothID'],\
                                model_mesh_metadata['sections'][i]['data'][j]['lod'][k]['unknown'],\
                                model_mesh_metadata['sections'][i]['data'][j]['lod'][k]['NUNID'],\
                                len(new_indices))
                            # In actual G1M, empty sections are allowed with padding, so this may need exploration
                            if len(new_indices) > 0:
                                #Map to new indices
                                lod_block += struct.pack(e+"{0}I".format(len(new_indices)), *new_indices)
                            else:
                                lod_block += struct.pack(e+"I", 0)
                        lod_section += lod_block
                    new_g1mg += struct.pack(e+"3I", model_mesh_metadata['sections'][i]['magic'], len(lod_section)+12,\
                        len(model_mesh_metadata['sections'][i]['data'])) + lod_section
                else:
                    f.seek(model_mesh_metadata['sections'][i]['offset'],0)
                    new_g1mg += f.read(model_mesh_metadata['sections'][i]['size'])
        except KeyError as e:
            print("KeyError: Missing value \"{0}\" detected in metadata section {1} subsection {2}!".format(e.args[0], \
                model_mesh_metadata['sections'][i]['type'], j))
            input("Press Enter to abort.")
            raise
    g1mg_header = model_mesh_metadata['magic'].encode()
    g1mg_header += struct.pack(e+"2I", model_mesh_metadata['version'], len(new_g1mg)+48)
    g1mg_header += model_mesh_metadata['platform'].encode()
    g1mg_header += struct.pack(e+"I6fI", model_mesh_metadata['reserved'], *list(bounding_box.values()),\
        len(model_mesh_metadata['sections']))
    return(g1mg_header + new_g1mg)

def build_g1m(g1m_name):
    with open(g1m_name + '.g1m', "rb") as f:
        g1m = G1Mmodel()
        g1m.g1m_data = f.read()
        return build_g1m_from_binary(g1m)
    
def get_skel_data_from_g1m(g1m):
    # if os.path.exists(g1m_name) and (os.path.isdir(g1m_name)):
    f = io.BytesIO(g1m.g1m_data)
        # with open(g1m_name + '.g1m', "rb") as f:
    print("Processing {0}...".format(g1m.g1m_hash))
    file = {}
    file["file_magic"], = struct.unpack(">I", f.read(4))
    if file["file_magic"] == 0x5F4D3147:
        e = '<' # Little Endian
    elif file["file_magic"] == 0x47314D5F:
        e = '>' # Big Endian
    # else:
    #     print("not G1M!") # Figure this out later
    #     sys.exit()
    # Pack G1MG and G1MF here, to insert into G1M. (Endianness is needed)
    file["file_version"] = f.read(4).hex()
    file["file_size"], = struct.unpack(e+"I", f.read(4))
    chunks = {}
    chunks["starting_offset"], chunks["reserved"], chunks["count"] = struct.unpack(e+"III", f.read(12))
    # Grab the skeleton for the vgmap sanity check
    f.seek(chunks["starting_offset"])
    have_skeleton = False
    model_skel_data = {}
    for i in range(chunks["count"]):
        chunk = {}
        chunk["start_offset"] = f.tell()
        chunk["magic"] = f.read(4).decode("utf-8")
        chunk["version"] = f.read(4).hex()
        chunk["size"], = struct.unpack(e+"I", f.read(4))
        if chunk["magic"] in ['G1MS', 'SM1G'] and have_skeleton == False:
            f.seek(chunk["start_offset"],0)
            model_skel_data = parseG1MS(f.read(chunk["size"]),e)
            if model_skel_data['jointCount'] > 1 and not model_skel_data['boneList'][0]['parentID'] < -200000000:
                #Internal Skeleton
                model_skel_data = calc_abs_skeleton(model_skel_data)
            have_skeleton == True # I guess some games duplicate this section?
        else:
            f.seek(chunk["start_offset"] + chunk["size"],0) # Move to next section    
    return model_skel_data
            
def build_g1m_from_binary(g1m):
    # if os.path.exists(g1m_name) and (os.path.isdir(g1m_name)):
    f = io.BytesIO(g1m.g1m_data)
        # with open(g1m_name + '.g1m', "rb") as f:
    print("Processing {0}...".format(g1m.g1m_hash))
    file = {}
    file["file_magic"], = struct.unpack(">I", f.read(4))
    if file["file_magic"] == 0x5F4D3147:
        e = '<' # Little Endian
    elif file["file_magic"] == 0x47314D5F:
        e = '>' # Big Endian
    # else:
    #     print("not G1M!") # Figure this out later
    #     sys.exit()
    # Pack G1MG and G1MF here, to insert into G1M. (Endianness is needed)
    file["file_version"] = f.read(4).hex()
    file["file_size"], = struct.unpack(e+"I", f.read(4))
    chunks = {}
    chunks["starting_offset"], chunks["reserved"], chunks["count"] = struct.unpack(e+"III", f.read(12))
    # Grab the skeleton for the vgmap sanity check
    f.seek(chunks["starting_offset"])
    have_skeleton = False
    for i in range(chunks["count"]):
        chunk = {}
        chunk["start_offset"] = f.tell()
        chunk["magic"] = f.read(4).decode("utf-8")
        chunk["version"] = f.read(4).hex()
        chunk["size"], = struct.unpack(e+"I", f.read(4))
        if chunk["magic"] in ['G1MS', 'SM1G'] and have_skeleton == False:
            f.seek(chunk["start_offset"],0)
            model_skel_data = parseG1MS(f.read(chunk["size"]),e)
            # json_path = Path(g1m_name) / '/skeleton.json'
            # if os.path.exists(g1m_name+'Oid.bin'):
            #     model_skel_oid = binary_oid_to_dict(g1m_name+'Oid.bin')
            #     model_skel_data = name_bones(model_skel_data, model_skel_oid)
            if model_skel_data['jointCount'] > 1 and not model_skel_data['boneList'][0]['parentID'] < -200000000:
                #Internal Skeleton
                model_skel_data = calc_abs_skeleton(model_skel_data)
            # else:
            #     ext_skel = get_ext_skeleton(g1m_name)
            #     if not ext_skel == False:
            #         model_skel_data = combine_skeleton(ext_skel, model_skel_data)
            have_skeleton == True # I guess some games duplicate this section?
        else:
            f.seek(chunk["start_offset"] + chunk["size"],0) # Move to next section
    new_g1mg_data = build_g1mg(g1m, model_skel_data, e)
    new_g1mf_data = build_g1mf(new_g1mg_data,g1m, e)
    # Move back to beginning to start rebuild
    f.seek(chunks["starting_offset"])
    new_g1m_data = bytes()
    for i in range(chunks["count"]):
        chunk = {}
        chunk["start_offset"] = f.tell()
        chunk["magic"] = f.read(4).decode("utf-8")
        chunk["version"] = f.read(4).hex()
        chunk["size"], = struct.unpack(e+"I", f.read(4))
        if chunk["magic"] in ['G1MF', 'FM1G']:
            new_g1m_data += new_g1mf_data # Replace section
            f.seek(chunk["start_offset"]+chunk["size"],0)
        elif chunk["magic"] in ['G1MG', 'GM1G']:
            new_g1m_data += new_g1mg_data # Replace section
            f.seek(chunk["start_offset"]+chunk["size"],0)
        else:
            f.seek(chunk["start_offset"],0) # Move to beginning
            new_g1m_data += f.read(chunk["size"]) # Read section
    f.seek(0)
    new_g1m_header = f.read(8)
    new_g1m_header += struct.pack(e+"I", len(new_g1m_data) + 24)
    f.seek(4,1)
    new_g1m_header += f.read(12)
    return(new_g1m_header + new_g1m_data)
    # else:
    #     return(False)

def process_g1m(g1m_name):
    new_g1m_data = build_g1m(g1m_name)
    if not new_g1m_data == False:
        # Instead of overwriting backups, it will just tag a number onto the end
        backup_suffix = ''
        if os.path.exists(g1m_name + '.g1m.bak' + backup_suffix):
            backup_suffix = '1'
            if os.path.exists(g1m_name + '.g1m.bak' + backup_suffix):
                while os.path.exists(g1m_name + '.g1m.bak' + backup_suffix):
                    backup_suffix = str(int(backup_suffix) + 1)
            shutil.copy2(g1m_name + '.g1m', g1m_name + '.g1m.bak' + backup_suffix)
        else:
            shutil.copy2(g1m_name + '.g1m', g1m_name + '.g1m.bak')
        with open(g1m_name + '.g1m','wb') as f:
            f.write(new_g1m_data)

if __name__ == "__main__":
    # Set current directory
    if getattr(sys, 'frozen', False):
        os.chdir(os.path.dirname(sys.executable))
    else:
        os.chdir(os.path.abspath(os.path.dirname(__file__)))

    # If argument given, attempt to import into file in argument
    if len(sys.argv) > 1:
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument('g1m_filename', help="Name of g1m file to import into (required).")
        args = parser.parse_args()
        if os.path.exists(args.g1m_filename) and args.g1m_filename[-4:].lower() == '.g1m' and os.path.isdir(args.g1m_filename[:-4]):
            process_g1m(args.g1m_filename[:-4])
    else:
        g1m_files = glob.glob('*.g1m')
        g1m_files = [x for x in g1m_files if os.path.isdir(x[:-4])]
        for i in range(len(g1m_files)):
            process_g1m(g1m_files[i][:-4])
