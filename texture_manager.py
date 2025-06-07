"""
Texture Manager for KalOnline game textures
Handles loading, caching, and management of terrain textures
"""

import bpy
import bmesh
import os
from typing import Dict, List, Optional, Tuple
from . import kcm_file

class TextureManager:
    """Manages texture loading and caching for KalOnline terrain"""
    
    def __init__(self):
        self.texture_cache: Dict[str, bpy.types.Image] = {}
        self.material_cache: Dict[str, bpy.types.Material] = {}
        self.texture_paths: List[str] = []
        self.game_texture_list: Dict[str, str] = {}  # For n.env texture mapping
    
    def set_texture_paths(self, paths: List[str]):
        """Set search paths for textures"""
        self.texture_paths = paths
    
    def load_game_texture_list(self, env_file_path: str) -> bool:
        """Load n.env texture list file"""
        try:
            with open(env_file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Parse texture entry (assuming format: ID=filename)
                        if '=' in line:
                            tex_id, filename = line.split('=', 1)
                            self.game_texture_list[tex_id.strip()] = filename.strip()
            return True
        except Exception as e:
            print(f"Error loading texture list: {e}")
            return False
    
    def find_texture_file(self, filename: str) -> Optional[str]:
        """Find texture file in search paths"""
        # Try direct path first
        if os.path.exists(filename):
            return filename
        
        # Search in texture paths
        for path in self.texture_paths:
            full_path = os.path.join(path, filename)
            if os.path.exists(full_path):
                return full_path
            
            # Try different extensions
            base_name = os.path.splitext(filename)[0]
            for ext in ['.dds', '.tga', '.bmp', '.png', '.jpg']:
                test_path = os.path.join(path, base_name + ext)
                if os.path.exists(test_path):
                    return test_path
        
        return None
    
    def load_texture(self, filename: str) -> Optional[bpy.types.Image]:
        """Load texture into Blender"""
        # Check cache first
        if filename in self.texture_cache:
            return self.texture_cache[filename]
        
        # Find texture file
        texture_path = self.find_texture_file(filename)
        if not texture_path:
            print(f"Texture not found: {filename}")
            return None
        
        try:
            # Load image
            image = bpy.data.images.load(texture_path)
            image.name = os.path.basename(filename)
            
            # Cache the image
            self.texture_cache[filename] = image
            
            return image
        except Exception as e:
            print(f"Error loading texture {filename}: {e}")
            return None
    
    def create_material(self, texture_filename: str, material_name: str = None) -> Optional[bpy.types.Material]:
        """Create material with texture"""
        if not material_name:
            material_name = f"Mat_{os.path.splitext(texture_filename)[0]}"
        
        # Check cache
        if material_name in self.material_cache:
            return self.material_cache[material_name]
        
        # Load texture
        image = self.load_texture(texture_filename)
        if not image:
            return None
        
        # Create material
        material = bpy.data.materials.new(name=material_name)
        material.use_nodes = True
        
        # Clear default nodes
        material.node_tree.nodes.clear()
        
        # Create nodes
        output_node = material.node_tree.nodes.new(type='ShaderNodeOutputMaterial')
        principled_node = material.node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')
        texture_node = material.node_tree.nodes.new(type='ShaderNodeTexImage')
        
        # Set texture
        texture_node.image = image
        
        # Connect nodes
        material.node_tree.links.new(texture_node.outputs['Color'], principled_node.inputs['Base Color'])
        material.node_tree.links.new(principled_node.outputs['BSDF'], output_node.inputs['Surface'])
        
        # Position nodes
        output_node.location = (400, 0)
        principled_node.location = (200, 0)
        texture_node.location = (0, 0)
        
        # Cache material
        self.material_cache[material_name] = material
        
        return material
    
    def apply_texture_to_face(self, mesh_obj: bpy.types.Object, face_index: int, texture_filename: str):
        """Apply texture to specific face of mesh"""
        if not mesh_obj or mesh_obj.type != 'MESH':
            return
        
        # Create material if needed
        material = self.create_material(texture_filename)
        if not material:
            return
        
        # Add material to object if not present
        if material.name not in mesh_obj.data.materials:
            mesh_obj.data.materials.append(material)
        
        # Get material index
        mat_index = list(mesh_obj.data.materials).index(material)
        
        # Enter edit mode
        bpy.context.view_layer.objects.active = mesh_obj
        bpy.ops.object.mode_set(mode='EDIT')
        
        # Select face and assign material
        bm = bmesh.from_mesh(mesh_obj.data)
        bm.faces.ensure_lookup_table()
        
        if face_index < len(bm.faces):
            # Deselect all
            for face in bm.faces:
                face.select = False
            
            # Select target face
            bm.faces[face_index].select = True
            
            # Assign material
            bm.faces[face_index].material_index = mat_index
            
            # Update mesh
            bmesh.update_edit_mesh(mesh_obj.data)
        
        # Return to object mode
        bpy.ops.object.mode_set(mode='OBJECT')
    
    def get_available_textures(self) -> List[str]:
        """Get list of available textures from search paths"""
        textures = []
        
        for path in self.texture_paths:
            if os.path.exists(path):
                for file in os.listdir(path):
                    if file.lower().endswith(('.dds', '.tga', '.bmp', '.png', '.jpg')):
                        textures.append(file)
        
        return sorted(list(set(textures)))
    
    def replace_texture(self, old_filename: str, new_filename: str) -> bool:
        """Replace texture in cache and update materials"""
        try:
            # Load new texture
            new_image = self.load_texture(new_filename)
            if not new_image:
                return False
            
            # Find materials using old texture
            old_image = self.texture_cache.get(old_filename)
            if old_image:
                # Update all materials using this texture
                for material in bpy.data.materials:
                    if material.use_nodes:
                        for node in material.node_tree.nodes:
                            if node.type == 'TEX_IMAGE' and node.image == old_image:
                                node.image = new_image
                
                # Remove old image from cache
                del self.texture_cache[old_filename]
                
                # Remove old image from Blender
                bpy.data.images.remove(old_image)
            
            # Update cache
            self.texture_cache[new_filename] = new_image
            
            return True
        except Exception as e:
            print(f"Error replacing texture: {e}")
            return False
    
    def clear_cache(self):
        """Clear texture and material caches"""
        self.texture_cache.clear()
        self.material_cache.clear()
    
    def get_texture_info(self, filename: str) -> Optional[Dict]:
        """Get texture information"""
        texture_path = self.find_texture_file(filename)
        if not texture_path:
            return None
        
        try:
            # Load image temporarily to get info
            temp_image = bpy.data.images.load(texture_path)
            info = {
                'filename': filename,
                'path': texture_path,
                'width': temp_image.size[0],
                'height': temp_image.size[1],
                'format': os.path.splitext(filename)[1].upper()[1:],
                'size_mb': os.path.getsize(texture_path) / (1024 * 1024)
            }
            
            # Remove temporary image
            bpy.data.images.remove(temp_image)
            
            return info
        except Exception as e:
            print(f"Error getting texture info: {e}")
            return None

# Global texture manager instance
texture_manager = TextureManager()
