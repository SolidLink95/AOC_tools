import bpy
from bpy.props import StringProperty, EnumProperty, BoolProperty
from bpy.types import Panel, Operator, PropertyGroup
from pathlib import Path
from g1m_importer.blender_g1m import export_3dmigoto
from g1m_importer.g1m_exporter.g1m_import_meshes import build_g1m_from_binary
from g1m_importer.util import *
import os, sys

class OBJECT_OT_SelectDirectory(Operator):
    bl_idname = "object.select_directory"
    bl_label = "Select Directory"
    directory: StringProperty(subtype='DIR_PATH')
    
    def execute(self, context):
        context.scene.Aoc_G1m_Exporter.directory_path = self.directory
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

def get_armatures(self, context):
    items = [(obj.name, obj.name, "") for obj in bpy.data.objects if obj.type == 'ARMATURE']
    if not items:
        items = [("None", "No G1MS Found", "")]
    return items

class OBJECT_OT_Export(Operator):
    bl_idname = "object.export_g1m"
    bl_label = "Export G1M"
    
    flip_winding: BoolProperty(
            name="Flip Winding Order",
            description="Flip winding order during export (automatically set to match the import option)",
            default=False,
            )

    flip_normal: BoolProperty(
            name="Flip Normal",
            description="Flip Normals during export (automatically set to match the import option)",
            default=False,
            )

    flip_tangent: BoolProperty(
            name="Flip Tangent",
            description="Flip Tangents during export (automatically set to match the flip normals option)",
            default=False,
            )
    
    def execute(self, context):
        AocG1mExporter = context.scene.Aoc_G1m_Exporter
        dest_dir = Path(Aoc_G1m_Exporter.destination_path)
        context = bpy.context
        arm = bpy.data.objects.get(AocG1mExporter.g1ms_list)
        if arm is None:
            arm = next((o for o in bpy.data.objects if o.type=="ARMATURE" and "g1m_backup" in o), None)
        if arm is None:
            return {'CANCELLED'}
        meshes = [o for o in bpy.data.objects if o.type=="MESH" and o.parent == arm]
        
        if AocG1mExporter.only_selected_objects:
            meshes = [o for o in bpy.data.objects if o in context.selected_objects]
        g1m = G1Mmodel()
        g1m.g1m_hash = arm.name
        g1m.g1m_data = arm["g1m_backup"]
        temp_path = Path(os.path.expandvars("%temp%")) / g1m.g1m_hash
        g1m.temp_path = temp_path
        remove_dir_if_exists(temp_path)
        temp_path.mkdir()
        for m in meshes:
            name = m.name.split(".")[0] if "." in m.name else m.name
            vb_path = str(temp_path / f"{name}.vb")
            ib_path = str(temp_path / f"{name}.ib")
            fmt_path = str(temp_path / f"{name}.fmt")
            ini_path = str(temp_path / f"{name}_generated.ini")
            export_3dmigoto(self,  m, context, vb_path, ib_path, fmt_path, ini_path)
        new_g1m_data = build_g1m_from_binary(g1m)
        remove_dir_if_exists(temp_path)
        dest_path = dest_dir / f"{g1m.g1m_hash}.g1m"
        dest_path.write_bytes(new_g1m_data)
        

        # Placeholder for actual export logic
        # self.report({'INFO'}, f"Exporting {len(armatures)} armature(s)...")

        return {'FINISHED'}

class OBJECT_PT_CustomPanel(Panel):
    bl_label = "Age of Calamity G1M Export Tool"
    bl_idname = "OBJECT_PT_custom_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tool'
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        AocG1mExporter = scene.Aoc_G1m_Exporter
        
        layout.label(text="AOC G1M Export")
        
        layout.prop(AocG1mExporter, "directory_path")
        layout.prop(AocG1mExporter, "destination_path")
        layout.operator("object.select_directory")
        
        layout.prop(AocG1mExporter, "g1ms_list", text="Armatures")
        
        layout.prop(AocG1mExporter, "only_selected_objects", text="Only Selected Objects")

        # Check if there is at least one armature
        if bpy.data.objects and any(obj.type == 'ARMATURE' for obj in bpy.data.objects):
            layout.operator("object.export_g1m", text="Export")

class AocPath(PropertyGroup):
    directory_path: StringProperty(
        name="Dump Path",
        description="Path to a directory with Age of Calamity raw files extracted",
        default="",
        maxlen=1024,
        subtype='DIR_PATH'
    )
    destination_path: StringProperty(
        name="export path",
        description="Path to a directory where g1m file will be exported",
        default="",
        maxlen=1024,
        subtype='DIR_PATH'
    )
    g1ms_list: EnumProperty(
        name="G1M List",
        description="Select G1M file to export",
        items=get_armatures
    )
    only_selected_objects: BoolProperty(
        name="Only Selected Objects",
        description="Export only selected armature objects",
        default=False
    )
    

exporter_classes = [
    AocPath,
    OBJECT_OT_SelectDirectory,
    OBJECT_OT_Export,
    OBJECT_PT_CustomPanel
]

def exporter_classes_register():
    for cls in exporter_classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.Aoc_G1m_Exporter = bpy.props.PointerProperty(type=AocPath)

def exporter_classes_unregister():
    for cls in exporter_classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.Aoc_G1m_Exporter

# if __name__ == "__main__":
#     register()
