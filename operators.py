"""
Operators for KWE-Blender KalOnline Terrain Tools
"""

import bpy
import bmesh
import os
from bpy.props import StringProperty
from . import texture_manager
from . import terrain_importer

class KWE_OT_LoadTextureList(bpy.types.Operator):
    """Load texture list from N.ENV file"""
    bl_idname = "kwe.load_texture_list"
    bl_label = "Load Texture List"
    bl_description = "Load game texture list from N.ENV file"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        scene = context.scene
        env_path = scene.kwe_env_file_path
        
        if not env_path or not os.path.exists(env_path):
            self.report({'ERROR'}, "N.ENV file not found")
            return {'CANCELLED'}
        
        # Load texture list
        if texture_manager.texture_manager.load_game_texture_list(env_path):
            self.report({'INFO'}, f"Loaded texture list from {env_path}")
            
            # Refresh texture list in UI
            bpy.ops.kwe.refresh_textures()
            
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "Failed to load texture list")
            return {'CANCELLED'}

class KWE_OT_RefreshTextures(bpy.types.Operator):
    """Refresh available texture list"""
    bl_idname = "kwe.refresh_textures"
    bl_label = "Refresh Textures"
    bl_description = "Refresh list of available textures"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        scene = context.scene
        texture_path = scene.kwe_texture_path
        
        if texture_path:
            texture_manager.texture_manager.set_texture_paths([texture_path])
        
        # Get available textures
        textures = texture_manager.texture_manager.get_available_textures()
        
        # Clear existing list
        scene.kwe_texture_list.clear()
        
        # Add textures to list
        for texture_name in textures:
            item = scene.kwe_texture_list.add()
            item.name = texture_name
            
            # Get texture info
            info = texture_manager.texture_manager.get_texture_info(texture_name)
            if info:
                item.filepath = info['path']
                item.width = info['width']
                item.height = info['height']
                item.format = info['format']
        
        self.report({'INFO'}, f"Found {len(textures)} textures")
        return {'FINISHED'}

class KWE_OT_PreviewTexture(bpy.types.Operator):
    """Preview selected texture"""
    bl_idname = "kwe.preview_texture"
    bl_label = "Preview Texture"
    bl_description = "Preview selected texture in image editor"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        scene = context.scene
        
        if not scene.kwe_texture_list or scene.kwe_texture_index >= len(scene.kwe_texture_list):
            self.report({'ERROR'}, "No texture selected")
            return {'CANCELLED'}
        
        # Get selected texture
        texture_item = scene.kwe_texture_list[scene.kwe_texture_index]
        
        # Load texture
        image = texture_manager.texture_manager.load_texture(texture_item.name)
        if not image:
            self.report({'ERROR'}, f"Failed to load texture: {texture_item.name}")
            return {'CANCELLED'}
        
        # Show in image editor
        for area in context.screen.areas:
            if area.type == 'IMAGE_EDITOR':
                area.spaces[0].image = image
                break
        else:
            # No image editor found, create one
            bpy.ops.screen.area_split(direction='VERTICAL', factor=0.5)
            context.area.type = 'IMAGE_EDITOR'
            context.area.spaces[0].image = image
        
        self.report({'INFO'}, f"Previewing: {texture_item.name}")
        return {'FINISHED'}

class KWE_OT_ReplaceTexture(bpy.types.Operator):
    """Replace texture in terrain"""
    bl_idname = "kwe.replace_texture"
    bl_label = "Replace Texture"
    bl_description = "Replace texture in selected terrain"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        scene = context.scene
        source = scene.kwe_source_texture
        target = scene.kwe_target_texture
        
        if not source or not target:
            self.report({'ERROR'}, "Source and target textures must be specified")
            return {'CANCELLED'}
        
        # Replace texture
        if texture_manager.texture_manager.replace_texture(source, target):
            self.report({'INFO'}, f"Replaced {source} with {target}")
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "Failed to replace texture")
            return {'CANCELLED'}

class KWE_OT_ApplyTextureToSelection(bpy.types.Operator):
    """Apply texture to selected faces"""
    bl_idname = "kwe.apply_texture_to_selection"
    bl_label = "Apply Texture to Selection"
    bl_description = "Apply selected texture to selected faces"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        scene = context.scene
        obj = context.active_object
        
        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "No mesh object selected")
            return {'CANCELLED'}
        
        if not scene.kwe_texture_list or scene.kwe_texture_index >= len(scene.kwe_texture_list):
            self.report({'ERROR'}, "No texture selected")
            return {'CANCELLED'}
        
        # Get selected texture
        texture_item = scene.kwe_texture_list[scene.kwe_texture_index]
        
        # Apply texture to selected faces
        if context.mode == 'EDIT_MESH':
            # Get selected faces
            bm = bmesh.from_edit_mesh(obj.data)
            selected_faces = [f for f in bm.faces if f.select]
            
            if not selected_faces:
                self.report({'ERROR'}, "No faces selected")
                return {'CANCELLED'}
            
            # Create/get material
            material = texture_manager.texture_manager.create_material(texture_item.name)
            if not material:
                self.report({'ERROR'}, f"Failed to create material for {texture_item.name}")
                return {'CANCELLED'}
            
            # Add material to object
            if material.name not in obj.data.materials:
                obj.data.materials.append(material)
            
            # Get material index
            mat_index = list(obj.data.materials).index(material)
            
            # Assign material to selected faces
            for face in selected_faces:
                face.material_index = mat_index
            
            # Update mesh
            bmesh.update_edit_mesh(obj.data)
            
            self.report({'INFO'}, f"Applied {texture_item.name} to {len(selected_faces)} faces")
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "Must be in Edit mode")
            return {'CANCELLED'}

class KWE_OT_GenerateHeightmap(bpy.types.Operator):
    """Generate heightmap from terrain"""
    bl_idname = "kwe.generate_heightmap"
    bl_label = "Generate Heightmap"
    bl_description = "Export terrain as heightmap image"
    bl_options = {'REGISTER'}
    
    filepath: StringProperty(
        name="File Path",
        description="Output heightmap file path",
        default="heightmap.png",
        subtype='FILE_PATH'
    )
    
    def execute(self, context):
        obj = context.active_object
        
        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "No mesh object selected")
            return {'CANCELLED'}
        
        # Import the exporter function
        from . import terrain_exporter
        
        # Export heightmap
        if terrain_exporter.export_heightmap(obj, self.filepath):
            self.report({'INFO'}, f"Heightmap exported to {self.filepath}")
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "Failed to export heightmap")
            return {'CANCELLED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class KWE_OT_RaiseTerrain(bpy.types.Operator):
    """Raise terrain at cursor position"""
    bl_idname = "kwe.raise_terrain"
    bl_label = "Raise Terrain"
    bl_description = "Raise terrain vertices near cursor"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        return self.modify_terrain(context, 1.0)
    
    def modify_terrain(self, context, direction):
        scene = context.scene
        obj = context.active_object
        
        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "No mesh object selected")
            return {'CANCELLED'}
        
        if context.mode != 'EDIT_MESH':
            self.report({'ERROR'}, "Must be in Edit mode")
            return {'CANCELLED'}
        
        strength = scene.kwe_height_strength * direction
        radius = scene.kwe_height_radius
        
        # Get bmesh
        bm = bmesh.from_edit_mesh(obj.data)
        
        # Get selected vertices or use cursor position
        selected_verts = [v for v in bm.vertices if v.select]
        
        if not selected_verts:
            self.report({'ERROR'}, "No vertices selected")
            return {'CANCELLED'}
        
        # Modify heights
        for vert in selected_verts:
            # Apply height modification
            vert.co.z += strength
        
        # Update mesh
        bmesh.update_edit_mesh(obj.data)
        
        action = "Raised" if direction > 0 else "Lowered"
        self.report({'INFO'}, f"{action} {len(selected_verts)} vertices")
        return {'FINISHED'}

class KWE_OT_LowerTerrain(bpy.types.Operator):
    """Lower terrain at cursor position"""
    bl_idname = "kwe.lower_terrain"
    bl_label = "Lower Terrain"
    bl_description = "Lower terrain vertices near cursor"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        return KWE_OT_RaiseTerrain.modify_terrain(self, context, -1.0)

# Registration
classes = [
    KWE_OT_LoadTextureList,
    KWE_OT_RefreshTextures,
    KWE_OT_PreviewTexture,
    KWE_OT_ReplaceTexture,
    KWE_OT_ApplyTextureToSelection,
    KWE_OT_GenerateHeightmap,
    KWE_OT_RaiseTerrain,
    KWE_OT_LowerTerrain,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
