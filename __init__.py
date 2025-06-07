bl_info = {
    "name": "KWE-Blender - KalOnline Terrain Tools",
    "author": "KWE Team",
    "version": (1, 0, 0),
    "blender": (3, 0, 0),
    "location": "File > Import-Export, 3D Viewport > Sidebar > KWE",
    "description": "Import/Export KalOnline terrain files (.kcm) with texture support",
    "category": "Import-Export",
}

import bpy
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy_extras.io_utils import ImportHelper, ExportHelper

# Import our modules
from . import kcm_file
from . import terrain_importer
from . import terrain_exporter
from . import texture_manager
from . import ui_panels
from . import operators

# Operator classes
class ImportKCM(bpy.types.Operator, ImportHelper):
    """Import KalOnline terrain file (.kcm)"""
    bl_idname = "import_scene.kcm"
    bl_label = "Import KCM"
    bl_options = {'REGISTER', 'UNDO'}
    
    filename_ext = ".kcm"
    filter_glob: StringProperty(
        default="*.kcm",
        options={'HIDDEN'},
        maxlen=255,
    )
    
    load_textures: BoolProperty(
        name="Load Textures",
        description="Load and apply terrain textures",
        default=True,
    )
    
    texture_path: StringProperty(
        name="Texture Path",
        description="Path to game texture files",
        default="",
        subtype='DIR_PATH'
    )
    
    def execute(self, context):
        return terrain_importer.import_kcm(context, self.filepath, self.load_textures, self.texture_path)

class ExportKCM(bpy.types.Operator, ExportHelper):
    """Export KalOnline terrain file (.kcm)"""
    bl_idname = "export_scene.kcm"
    bl_label = "Export KCM"
    bl_options = {'REGISTER', 'UNDO'}
    
    filename_ext = ".kcm"
    filter_glob: StringProperty(
        default="*.kcm",
        options={'HIDDEN'},
        maxlen=255,
    )
    
    export_textures: BoolProperty(
        name="Export Texture References",
        description="Export texture file references",
        default=True,
    )
    
    def execute(self, context):
        return terrain_exporter.export_kcm(context, self.filepath, self.export_textures)

# Menu functions
def menu_func_import(self, context):
    self.layout.operator(ImportKCM.bl_idname, text="KalOnline Terrain (.kcm)")

def menu_func_export(self, context):
    self.layout.operator(ExportKCM.bl_idname, text="KalOnline Terrain (.kcm)")

# Registration
classes = [
    ImportKCM,
    ExportKCM,
]

def register():
    # Register classes
    for cls in classes:
        bpy.utils.register_class(cls)
    
    # Register other modules
    ui_panels.register()
    operators.register()
    
    # Add to menus
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)

def unregister():
    # Unregister classes
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    # Unregister other modules
    ui_panels.unregister()
    operators.unregister()
    
    # Remove from menus
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)

if __name__ == "__main__":
    register()
