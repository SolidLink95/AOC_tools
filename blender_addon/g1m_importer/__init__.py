from g1m_importer.blender_g1m import *
# from g1m_importer.G1M_Exporter_plugin import exporter_classes_register
import bpy
import os
os.system("cls" )

bl_info = {
    "name": "G1M importer/exporter",
    "blender": (2, 93, 0),
    "author": "Ian Munsie (darkstarsword@gmail.com)",
    "location": "File > Import-Export",
    "description": "Imports meshes from G1M files",
    "category": "Import-Export",
    "tracker_url": "https://github.com/DarkStarSword/3d-fixes/issues",
}

if __name__ == "__main__":
    register()