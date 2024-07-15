import json
import os
from pathlib import Path
import struct
import io
import hashlib, re
import sys

def fileToMd5(file):
    return bytesToMd5(Path(file).read_bytes())

def bytesToMd5(data):
    return hashlib.md5(data).hexdigest().upper()

def u32_to_hex(u32):
    return hex(u32)[2:].zfill(8)

def hex_to_u32(hex_str):
    if isinstance(hex_str, int):
        return hex_str
    return int(hex_str, 16)

def get_entry_size_diff(val):
    if val == 0:
        return 0
    if val < 0xff:
        return 3
    elif val < 0xffff:
        return 2
    elif val < 0xfffff:
        return 1
    return 0

class KidsOb:
    def __init__(self) -> None:
        self.hdr = KODHeader()
        self.objects = []
        self.KOD_SIGNATURE = 0x4B4F445F
        self.KODI_SIGNATURE = 0x4B4F4449
        self.KODR_SIGNATURE = 0x4B4F4452
        self.KIDS_ODB_INT8 = 0
        self.KIDS_ODB_UINT8 = 1
        self.KIDS_ODB_INT16 = 2
        self.KIDS_ODB_UINT16 = 3
        self.KIDS_ODB_INT32 = 4
        self.KIDS_ODB_UINT32 = 5
        self.KIDS_ODB_FLOAT = 8
        self.KIDS_ODB_VECTOR4 = 10
        self.KIDS_ODB_VECTOR2 = 12
        self.KIDS_ODB_VECTOR3 = 13
    
    def from_binary(self, data: bytes):
        reader = io.BytesIO(data)
        def readU32():
            return struct.unpack('<I', reader.read(4))[0]
        def readI32():
            return struct.unpack('<i', reader.read(4))[0]
        def skipU32(n):
            for _ in range(n):
                readU32()
        self.hdr.signature = readU32()
        self.hdr.version = readU32()
        self.hdr.header_size = readU32()
        self.hdr.platform = readU32()
        self.hdr.num_entries = readU32()
        self.hdr.name_file = readU32()
        self.hdr.file_size = readU32() #//irrelevant
        for _ in range(self.hdr.num_entries):
            obj = KidsODBObject()
            entry = KODIHeader()
            entry.signature = readU32()
            entry.version = readU32()
            entry.entry_size = readU32()
            entry.name = readU32()
            entry.type = readU32()
            entry.num_columns = readU32()
            # if entry.signature == self.KODI_SIGNATURE:
            obj.name = u32_to_hex(entry.name)
            obj.type = entry.type
            obj.version = entry.version
            obj.is_r = False
            for _ in range(entry.num_columns):
                col = KidsODBColumn()
                col.type = readU32()
                col.row_num = readU32()
                col.name = u32_to_hex(readU32())
                obj.columns.append(col)
            for i in range(entry.num_columns):
                col = obj.columns[i]
                val = None
                for _ in range(col.row_num):
                    val = None
                    if col.type in [4,5,8]:
                        val = readU32()
                    else:
                        val = readU32()
                    if val is not None:
                        col.vals.append(u32_to_hex(val))
            self.objects.append(obj)
    
    def from_json_file(self, path):
        with open(path, 'r') as f:
            data = json.load(f)
        self.hdr = KODHeader()
        self.hdr.from_dict(data["header"])
        self.objects = []
        for obj_data in data["objects"]:
            obj = KidsODBObject()
            obj.from_dict(obj_data)
            self.objects.append(obj)

    def to_dict(self):
        return {obj.name: {col.name: col.vals for col in obj.columns} for obj in self.objects}
    
    def to_json(self):
        return {
            "header": self.hdr.to_dict(),
            "objects": [obj.to_dict() for obj in self.objects]
        }
    
    def to_json_file(self, path):
        with open(path, 'w') as f:
            json.dump(self.to_json(), f, indent=4)
    
    def to_binary(self):
        writer = io.BytesIO()
        
        def writeU32(val):
            writer.write(struct.pack('<I', val))
        
        writeU32(self.hdr.signature)
        writeU32(self.hdr.version)
        writeU32(self.hdr.header_size)
        writeU32(self.hdr.platform)
        writeU32(self.hdr.num_entries)
        writeU32(self.hdr.name_file)
        writeU32(0)  # Placeholder for file_size

        for obj in self.objects:
            entry_start = writer.tell()
            
            writeU32(self.KODI_SIGNATURE)  # entry.signature
            writeU32(hex_to_u32(obj.version))  # entry.version
            entry_size_placeholder_pos = writer.tell()
            writeU32(0)  # Placeholder for entry_size
            writeU32(hex_to_u32(obj.name))  # entry.name
            writeU32(obj.type)  # entry.type
            writeU32(len(obj.columns))  # entry.num_columns
            
            for col in obj.columns:
                writeU32(col.type)
                writeU32(col.row_num)
                writeU32(hex_to_u32(col.name))
            tmp = None
            for col in obj.columns:
                for val in col.vals:
                    tmp = hex_to_u32(val)
                    writeU32(tmp)
            corr_val = 0
            if tmp is not None:
                corr_val = get_entry_size_diff(tmp)
            
            entry_end = writer.tell()
            entry_size = entry_end - entry_start - corr_val
            writer.seek(entry_size_placeholder_pos)
            # writeU32(entry_size)
            writeU32(entry_size)
            writer.seek(entry_end)

        file_size = writer.tell()
        writer.seek(24)  # Move to file_size position
        writeU32(file_size)
        writer.seek(0)  # Reset to start
        return writer.getvalue()
   
   
    def to_binary_file(self, path):
        with open(path, 'wb') as f:
            f.write(self.to_binary())
    

class KidsODBColumn:
    def __init__(self) -> None:
        self.name = ""
        self.type = 0
        self.vals = []
        self.row_num = 0
    
    def to_dict(self):
        return {
            "name": self.name,
            "type": u32_to_hex(self.type),
            "vals": self.vals,
            "row_num": self.row_num
        }
    
    def from_dict(self, data):
        self.name = data["name"]
        self.type = hex_to_u32(data["type"])
        self.vals = data["vals"]
        self.row_num = data["row_num"]

class KODHeader():
    def __init__(self) -> None:
        self.signature = 0
        self.version = 0
        self.header_size = 0
        self.platform = 0
        self.num_entries = 0
        self.name_file = 0
        self.file_size = 0
    
    def to_dict(self):
        return {
            "signature": u32_to_hex(self.signature),
            "version": u32_to_hex(self.version),
            "header_size": u32_to_hex(self.header_size),
            "platform": u32_to_hex(self.platform),
            "num_entries": u32_to_hex(self.num_entries),
            "name_file": u32_to_hex(self.name_file),
            "file_size": u32_to_hex(self.file_size)
        }
    
    def from_dict(self, data):
        self.signature = hex_to_u32(data["signature"])
        self.version = hex_to_u32(data["version"])
        self.header_size = hex_to_u32(data["header_size"])
        self.platform = hex_to_u32(data["platform"])
        self.num_entries = hex_to_u32(data["num_entries"])
        self.name_file = hex_to_u32(data["name_file"])
        self.file_size = hex_to_u32(data["file_size"])

class KODIHeader():
    def __init__(self) -> None:
        self.signature = 0
        self.version = 0
        self.entry_size = 0
        self.name = 0
        self.type = 0
        self.num_columns = 0
        
    def to_dict(self):
        return {
            "signature": u32_to_hex(self.signature),
            "version": u32_to_hex(self.version),
            "entry_size": u32_to_hex(self.entry_size),
            "name": u32_to_hex(self.name),
            "type": u32_to_hex(self.type),
            "num_columns": u32_to_hex(self.num_columns)
        }
        
class KODRHeader():
    def __init__(self) -> None:
        self.signature = 0
        self.version = 0
        self.entry_size = 0
        self.name = 0
        self.parent_object_file = 0
        self.parent_object = 0
        self.num_columns = 0

class KidsODBObject():
    def __init__(self) -> None:
        self.name = ""
        self.type = 0
        self.version = 0
        self.parent_object_file = 0
        self.parent_object = 0
        self.is_r = False
        self.columns = []
        
    def to_dict(self):
        return {
            "name": self.name,
            "type": u32_to_hex(self.type),
            "version": u32_to_hex(self.version),
            "parent_object_file": u32_to_hex(self.parent_object_file),
            "parent_object": u32_to_hex(self.parent_object),
            "is_r": self.is_r,
            "columns": [col.to_dict() for col in self.columns]
        }
    
    def from_dict(self, data):
        self.name = data["name"]
        self.type = hex_to_u32(data["type"])
        self.version = hex_to_u32(data["version"])
        self.parent_object_file = hex_to_u32(data["parent_object_file"])
        self.parent_object = hex_to_u32(data["parent_object"])
        self.is_r = data["is_r"]
        self.columns = []
        for col_data in data["columns"]:
            col = KidsODBColumn()
            col.from_dict(col_data)
            self.columns.append(col)

def trim_json_str(s):
    return s.replace("[\n", "[").replace("\n        ]", "]").replace("[            ", "[")

def reformat_json_string(json_string):
    # Parse the string into a dictionary
    parsed_data = json.loads(json_string)
    
    # Reformat the dictionary into a compact JSON string
    compact_json = json.dumps(parsed_data, separators=(',', ': '), indent=4)
    
    return compact_json

def test_parsing():
    mainpath = Path(os.path.dirname(os.path.abspath(__file__)))
    
    path = mainpath / "CharacterEditor.kidssingletondb"
    with open(path, 'rb') as f:
        data = f.read()
    kidsob = KidsOb()
    kidsob.from_binary(data)
    kidsob.to_json_file(mainpath / "CharacterEditor.json")
    
    json_path = mainpath / "CharacterEditor.json"
    kidsob = KidsOb()
    kidsob.from_json_file(json_path)
    binary_path = mainpath / "CharacterEditor_converted.kidssingletondb"
    kidsob.to_binary_file(binary_path)
    
    def_path = mainpath / "CharacterEditor.kidssingletondb"
    
    print("Converted MD5:", fileToMd5(binary_path))
    print("Original MD5:", fileToMd5(def_path))
    
    data1 = def_path.read_bytes()
    data2 = binary_path.read_bytes()
    print(len(data1), len(data2), len(data1) == len(data2))
    x = 0
    for i, b in enumerate(data1):
        if b != data2[i]:
            print(hex(i), hex(b), hex(data2[i]))
            x += 1
    print(x)
            # break

if __name__ == "__main__":
    file = Path(sys.argv[1])
    if file.suffix == ".json":
        print("Converting JSON to binary kidssingletondb")
        kidsob = KidsOb()
        kidsob.from_json_file(file)
        kidsob.to_binary_file(file.with_suffix(".kidssingletondb"))
    else:
        print("Converting binary kidssingletondb to JSON")
        kidsob = KidsOb()
        with open(file, 'rb') as f:
            data = f.read()
        kidsob.from_binary(data)
        kidsob.to_json_file(file.with_suffix(".json"))
        
    
