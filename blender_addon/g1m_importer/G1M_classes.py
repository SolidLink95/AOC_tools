from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
import shutil
import sys
from  g1m_importer.G1mImporter import G1Mmodel
import io
import re
from array import array
import struct
import numpy
import itertools
import collections
import os
from glob import glob
import json
import copy
import textwrap

import bpy
from bpy.props import StringProperty, EnumProperty, BoolProperty
from bpy.types import Panel, Operator, PropertyGroup
from bpy_extras.io_utils import unpack_list, ImportHelper, ExportHelper, axis_conversion
from bpy.props import BoolProperty, StringProperty, CollectionProperty
from bpy_extras.image_utils import load_image
from g1m_importer.g1m_exporter.g1m_export_meshes import parseG1M, parseG1MFile
from g1m_importer.g1m_exporter.g1m_to_basic_gltf import G1M2glTFBinary, gltfData
from g1m_importer.g1m_exporter.g1m_import_meshes import build_g1m_from_binary, get_skel_data_from_g1m
from g1m_importer.KtidsKidsobs import ktid_dict_to_binary_file 
# from g1m_importer.G1M_Exporter_plugin import exporter_classes_register,exporter_classes_unregister
from mathutils import Matrix, Vector
from g1m_importer.util import *
try:
    from bl_ui.generic_ui_list import draw_ui_list
except ImportError:
    # Blender older than 3.5. Just disable the semantic remap feature
    draw_ui_list = None

