import json
import os
from pathlib import Path
import sys
import struct
import io

def u32_to_hex(u32):
    return hex(u32)[2:].zfill( 8)

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
        # self.objects = [KidsODBObject() for _ in range(self.hdr.num_entries)]
        for _ in range(self.hdr.num_entries):
            obj = KidsODBObject()
            entry = KODIHeader()
            entry.signature = readU32()
            entry.version = readU32()
            entry.entry_size = readU32()
            entry.name = readU32()
            entry.type = readU32()
            entry.num_columns = readU32()
            if entry.signature == self.KODI_SIGNATURE:
                obj.name = u32_to_hex(entry.name)
                obj.type = entry.type
                obj.version = entry.version
                obj.is_r = False
            # else:
            #     continue #skip other headers
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
                    # skipU32(3)
                    val = None
                    if col.type in [4,5,8]:
                        val = readU32()
                    else:
                        val = readU32()
                    if val is not None:
                        col.vals.append(u32_to_hex(val))
            
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
        
def trim_json_str(s):
    return s.replace("[\n", "[").replace("\n        ]", "]").replace("[            ", "[")

def reformat_json_string(json_string):
    # Parse the string into a dictionary
    parsed_data = json.loads(json_string)
    
    # Reformat the dictionary into a compact JSON string
    compact_json = json.dumps(parsed_data, separators=(',', ': '), indent=4)
    
    return compact_json

if __name__=="__main__":
    mainpath = Path(os.path.dirname(os.path.abspath(__file__)))
    path = mainpath / "CharacterEditor.kidssingletondb"
    with open(path, 'rb') as f:
        data = f.read()
    kidsob = KidsOb()
    kidsob.from_binary(data)
    kidsob.to_json_file(mainpath / "CharacterEditor.json")