"""
UI Panels for KWE-Blender KalOnline Terrain Tools
"""

import bpy
from bpy.props import StringProperty, BoolProperty, EnumProperty, IntProperty
from . import texture_manager
from . import operators

class KWE_PT_TerrainPanel(bpy.types.Panel):
    """Main terrain tools panel"""
    bl_label = "KalOnline Terrain"
    bl_idname = "KWE_PT_terrain"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "KWE"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        # Import/Export section
        box = layout.box()
        box.label(text="Import/Export", icon='IMPORT')
        
        row = box.row()
        row.operator("import_scene.kcm", text="Import KCM", icon='MESH_GRID')
        row.operator("export_scene.kcm", text="Export KCM", icon='EXPORT')
        
        # Texture path settings
        box.prop(scene, "kwe_texture_path", text="Texture Path")
        box.prop(scene, "kwe_env_file_path", text="N.ENV File")
        
        # Load texture list button
        box.operator("kwe.load_texture_list", text="Load Texture List", icon='FILE_REFRESH')

class KWE_PT_TexturePanel(bpy.types.Panel):
    """Texture management panel"""
    bl_label = "Texture Manager"
    bl_idname = "KWE_PT_texture"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "KWE"
    bl_parent_id = "KWE_PT_terrain"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        # Texture browser
        box = layout.box()
        box.label(text="Available Textures", icon='TEXTURE')
        
        # Texture list
        if hasattr(scene, 'kwe_texture_list'):
            box.template_list("KWE_UL_TextureList", "", scene, "kwe_texture_list", 
                            scene, "kwe_texture_index", rows=5)
        
        # Texture operations
        row = box.row()
        row.operator("kwe.refresh_textures", text="Refresh", icon='FILE_REFRESH')
        row.operator("kwe.preview_texture", text="Preview", icon='HIDE_OFF')
        
        # Replace texture section
        box = layout.box()
        box.label(text="Replace Texture", icon='FILE_BLEND')
        
        box.prop(scene, "kwe_source_texture", text="Source")
        box.prop(scene, "kwe_target_texture", text="Target")
        box.operator("kwe.replace_texture", text="Replace Texture", icon='ARROW_LEFTRIGHT')

class KWE_PT_TerrainEditPanel(bpy.types.Panel):
    """Terrain editing panel"""
    bl_label = "Terrain Editor"
    bl_idname = "KWE_PT_terrain_edit"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "KWE"
    bl_parent_id = "KWE_PT_terrain"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        obj = context.active_object
        
        if obj and obj.type == 'MESH':
            # Terrain info
            box = layout.box()
            box.label(text="Terrain Info", icon='INFO')
            
            mesh = obj.data
            box.label(text=f"Vertices: {len(mesh.vertices)}")
            box.label(text=f"Faces: {len(mesh.polygons)}")
            box.label(text=f"Materials: {len(mesh.materials)}")
            
            # Terrain tools
            box = layout.box()
            box.label(text="Terrain Tools", icon='TOOL_SETTINGS')
            
            box.operator("kwe.apply_texture_to_selection", text="Apply Texture to Selection", icon='BRUSH_DATA')
            box.operator("kwe.generate_heightmap", text="Export Heightmap", icon='IMAGE_DATA')
            
            # Height editing
            box = layout.box()
            box.label(text="Height Editing", icon='MESH_GRID')
            
            box.prop(scene, "kwe_height_strength", text="Strength")
            box.prop(scene, "kwe_height_radius", text="Radius")
            
            row = box.row()
            row.operator("kwe.raise_terrain", text="Raise", icon='TRIA_UP')
            row.operator("kwe.lower_terrain", text="Lower", icon='TRIA_DOWN')
            
        else:
            layout.label(text="Select a mesh object", icon='ERROR')

class KWE_UL_TextureList(bpy.types.UIList):
    """UI list for textures"""
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=item.name, icon='TEXTURE')
            layout.label(text=f"{item.width}x{item.height}")
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon='TEXTURE')

class KWE_TextureListItem(bpy.types.PropertyGroup):
    """Property group for texture list items"""
    name: StringProperty(name="Texture Name")
    filepath: StringProperty(name="File Path")
    width: IntProperty(name="Width")
    height: IntProperty(name="Height")
    format: StringProperty(name="Format")

# Property definitions
def register_properties():
    """Register custom properties"""
    
    # Texture path
    bpy.types.Scene.kwe_texture_path = StringProperty(
        name="Texture Path",
        description="Path to game texture files",
        default="",
        subtype='DIR_PATH'
    )
    
    # N.ENV file path
    bpy.types.Scene.kwe_env_file_path = StringProperty(
        name="N.ENV File",
        description="Path to game texture list file",
        default="",
        subtype='FILE_PATH'
    )
    
    # Source texture for replacement
    bpy.types.Scene.kwe_source_texture = StringProperty(
        name="Source Texture",
        description="Texture to replace",
        default=""
    )
    
    # Target texture for replacement
    bpy.types.Scene.kwe_target_texture = StringProperty(
        name="Target Texture",
        description="New texture file",
        default="",
        subtype='FILE_PATH'
    )
    
    # Height editing properties
    bpy.types.Scene.kwe_height_strength = bpy.props.FloatProperty(
        name="Height Strength",
        description="Strength of height modification",
        default=1.0,
        min=0.1,
        max=10.0
    )
    
    bpy.types.Scene.kwe_height_radius = bpy.props.FloatProperty(
        name="Height Radius",
        description="Radius of height modification",
        default=2.0,
        min=0.5,
        max=20.0
    )
    
    # Texture list
    bpy.types.Scene.kwe_texture_list = bpy.props.CollectionProperty(
        type=KWE_TextureListItem
    )
    
    bpy.types.Scene.kwe_texture_index = bpy.props.IntProperty(
        name="Texture Index",
        default=0
    )

def unregister_properties():
    """Unregister custom properties"""
    
    del bpy.types.Scene.kwe_texture_path
    del bpy.types.Scene.kwe_env_file_path
    del bpy.types.Scene.kwe_source_texture
    del bpy.types.Scene.kwe_target_texture
    del bpy.types.Scene.kwe_height_strength
    del bpy.types.Scene.kwe_height_radius
    del bpy.types.Scene.kwe_texture_list
    del bpy.types.Scene.kwe_texture_index

# Registration
classes = [
    KWE_TextureListItem,
    KWE_UL_TextureList,
    KWE_PT_TerrainPanel,
    KWE_PT_TexturePanel,
    KWE_PT_TerrainEditPanel,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    register_properties()

def unregister():
    unregister_properties()
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
