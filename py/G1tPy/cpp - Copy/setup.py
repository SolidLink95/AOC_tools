from setuptools import setup, Extension
import pybind11

ext_modules = [
    Extension(
        "g1t_module",
        ["bindings.cpp"],
        include_dirs = [pybind11.get_include()],
        language="c++"
    )
]

setup(
    name="g1t_module",
    version="0.0.1",
    ext_modules=ext_modules
)