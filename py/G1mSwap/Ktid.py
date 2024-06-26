import os
import sys
import io
import struct


def ktid_dict_to_binary_file(path, data):
    with open(path, "wb") as f:
        f.write(ktid_dict_to_binary(data))
    
    
def ktid_dict_to_binary(data):
    res = b""
    for key, value in data.items():
        res += struct.pack("<I", int(key))
        res += struct.pack("<I", int(value, 16))
    return res


def ktid_binary_to_dict(data):
    if len(data) % 8 != 0:
        print("Warning, ktid length should be multiple of 8")
    res = {}
    with io.BytesIO(data) as f:
        while True:
            try:
                key = struct.unpack("<I", f.read(4))[0]
                value = struct.unpack("<I", f.read(4))[0]
                res[str(key)] = hex(value)[2:]
            except:
                break
    return res

def ktid_file_to_dict(file_path):
    with open(file_path, "rb") as f:
        return ktid_binary_to_dict(f.read())