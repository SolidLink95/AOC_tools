import io
from pathlib import Path
import cpp.g1t_module as g1t_module
import hashlib
from Dds_rs import png_to_dds, dds_to_png

def fileToMd5(file):
    return bytesToMd5(Path(file).read_bytes())

def bytesToMd5(data):
    return hashlib.md5(data).hexdigest().upper()


class G1T():
    def __init__(self, input_data) -> None:
        self.data = None
        self.metadata = {}
        if self.process_data(input_data):
            return
        
        metadata, dds_data = g1t_module.G1tDecompile(self.data)
        if metadata.startswith("Error"):
            raise ValueError(metadata)
        self.dds = [bytes(e) for e in dds_data]
        self.parse_metadata(metadata)
        
        
    def process_data(self, input_data):
        self.data = None
        if isinstance(input_data, bytes):
            self.data = input_data
        elif isinstance(input_data, bytearray):
            self.data = bytes(input_data)
        elif isinstance(input_data, str) or isinstance(input_data, Path):
            p = Path(input_data)
            if p.exists():
                if p.is_dir():
                    self.from_dir(p)
                    return True
                elif p.is_file():
                    self.data = p.read_bytes()
                else:
                    raise ValueError("Invalid path")
        elif isinstance(input_data, G1T):
            self.data = input_data.data
        elif isinstance(input_data, io.BytesIO) or isinstance(input_data, io.BufferedReader):
            self.data = input_data.read()
        if self.data is None:
            raise ValueError("Invalid input data")
        if not self.data.startswith(b"GT1"):
            print(f"Magic data: expected GT1, got {self.data[:3]}")
            raise ValueError("Invalid magic data")
        return False
    
    
    def from_dir(self, directory):
        dds_files = [e for e in directory.glob("*") if str(e).lower().endswith(".dds")]
        csv = directory / "g1t.csv"
        if not csv.exists():
            raise FileNotFoundError(f"CSV file not found: {csv}")
        metadata = csv.read_text()
        self.dds = [e.read_bytes() for e in dds_files]
        self.parse_metadata(metadata)
        m_count = len(self.metadata.keys())
        d_count = len(self.dds)
        if m_count != d_count:
            print(f"Metadata count ({m_count}) and DDS count ({d_count}) mismatch")
            raise ValueError("Invalid data count")
        
    
    def parse_metadata(self, metadata):
        self.metadata = {}
        for line in metadata.split("\n"):
            if line.strip() == "":
                continue
            if line.count(";") != 6:
                raise Exception(f"Invalid metadata line: {line}")
            id, w, h, formatStr, formatInt, mip_count, _ = line.split(";")
            self.metadata[id] = {
                "width": int(w),
                "height": int(h),
                "format": formatStr,
                "formatInt": int(formatInt),
                "mip_count": int(mip_count),
                "MD5": bytesToMd5(self.dds[int(id)])
            }
    
    def metadata_to_csv(self):
        res = ""
        for key, value in self.metadata.items():
            res += f"{key};{value['width']};{value['height']};{value['format']};{value['formatInt']};{value['mip_count']};\n"
        return res
    
    def to_binary(self):
        # print(len(self.dds))
        # print(self.dds[0][:10])
        # print(bytesToMd5(self.dds[0]))
        dds = [bytes(e) for e in self.dds]
        rawdata = g1t_module.G1tCompile(dds)
        if len(rawdata) == 0:
            raise ValueError("Failed to compile G1T data")
        return bytes(rawdata)
    
    def extract_to_dir(self, dest_dir):
        dest_dir = Path(dest_dir)
        dest_dir.mkdir(parents=True, exist_ok=True)
        for key, value in self.metadata.items():
            dds_file = dest_dir / f"{key}.dds"
            dds_file.write_bytes(self.dds[int(key)])
        csv_file = dest_dir / "g1t.csv"
        csv_file.write_text(self.metadata_to_csv())
    
    def save_file(self, dest_file):
        file_path = Path(dest_file)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        rawdata = self.to_binary()
        file_path.write_bytes(rawdata)