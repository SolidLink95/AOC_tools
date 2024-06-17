from setuptools import setup, Extension
import pybind11
import os

# Set the environment variables to use g++ for compiling
os.environ['CC'] = 'g++'
os.environ['CXX'] = 'g++'



ext_modules = [
    Extension(
        "kidsob_module",
        [
            "bindings.cpp",
             "W:/coding/AOC_tools/jsoncpp/src/lib_json/json_value.cpp",
             "W:/coding/AOC_tools/jsoncpp/src/lib_json/json_reader.cpp",
             "W:/coding/AOC_tools/jsoncpp/src/lib_json/json_writer.cpp",
            "KidsObjDBFile.cpp",
            "W:/coding/AOC_tools/py/G1tPy/cpp/Utils.cpp",
            "W:/coding/AOC_tools/eternity_common/MemoryStream.cpp",
            "W:/coding/AOC_tools/eternity_common/Stream.cpp",
            
        ],
        include_dirs=[
            pybind11.get_include(),
            # "W:/coding/AOC_tools/eternity_common",
            "W:/coding/AOC_tools/zlib-win-build-1.3.1-p1",
            "W:/coding/AOC_tools/py/G1tPy/cpp",
            "W:/coding/AOC_tools/rapidjson/include",
            "W:/coding/AOC_tools/jsoncpp/include",
            "W:/coding/AOC_tools/jsoncpp/src/lib_json",
        ],
        language="c++",
        extra_compile_args=["/std:c++17"]
        # extra_compile_args=['-std=c++14'],  # Use C++14 standard
    ),
]

setup(
    name="kidsob_module",
    version="0.1",
    description="A module for reading KidsObjDB files.",
    ext_modules=ext_modules,
    install_requires=['pybind11'],
)