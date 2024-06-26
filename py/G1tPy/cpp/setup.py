# setup.py
from setuptools import setup, Extension
import pybind11

########## python setup.py build_ext --inplace

ext_modules = [
    Extension(
        "g1t_module",
         [
             "bindings.cpp", 
             "G1tFile.cpp", 
             "DdsFile.cpp",
             "Utils.cpp",
            #  "json.cpp",
             "W:/coding/AOC_tools/jsoncpp/src/lib_json/json_value.cpp",
             "W:/coding/AOC_tools/jsoncpp/src/lib_json/json_reader.cpp",
             "W:/coding/AOC_tools/jsoncpp/src/lib_json/json_writer.cpp",
            #  "../../../eternity_common/BaseFile.cpp",
            #  "../../../eternity_common/Utils.cpp",
            ],
        include_dirs=[
            pybind11.get_include(),
            # "./../../../src/**",
            "W:/coding/AOC_tools/eternity_common",
            # "C:/Users/All Users/mingw64/mingw64/x86_64-w64-mingw32/include",
            "W:/coding/AOC_tools/zlib-win-build-1.3.1-p1",
            "W:/coding/AOC_tools/rapidjson/include",
            "W:/coding/AOC_tools/jsoncpp/include",
            "W:/coding/AOC_tools/jsoncpp/src/lib_json",
            # "C:/Users/Mati/AppData/Local/Programs/Python/Python312/Lib/site-packages/pybind11/include",
            # "C:/Users/Mati/AppData/Local/Programs/Python/Python312/include",
            # "C:/ProgramData/mingw64/mingw64/x86_64-w64-mingw32/include"
            
            ],
        # libraries=["zlib"],  # Ensure zlib is linked
        # library_dirs=["W:/coding/AOC_tools/zlib-win-build-1.3.1-p1"],
        language="c++",
        extra_compile_args=["/std:c++17"]  # Add C++17 support
    ),
]

setup(
    name="g1t_module",
    version="0.1",
    ext_modules=ext_modules,
)
