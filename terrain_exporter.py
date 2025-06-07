"""
KalOnline Terrain Exporter for Blender
Exports Blender terrain to KCM format
"""

import bpy
import bmesh
import mathutils
import os
from typing import List, Tuple, Optional, Dict
from . import kcm_file

def export_kcm(context, filepath: str, export_textures: bool = True, encrypt: bool = True) -> set:
    """Export selected terrain object to KCM file"""
    
    # Get active object
    obj = context.active_object
    if not obj or obj.type != 'MESH':
        print("No mesh object selected")
        return {'CANCELLED'}
    
    # Convert mesh to KCM format
    kcm = mesh_to_kcm(obj, export_textures)
    if not kcm:
        return {'CANCELLED'}
    
    # Write KCM file
    if not kcm.write(filepath, encrypt=encrypt):
        print("Failed to write KCM file")
        return {'CANCELLED'}
    
    print(f"Exported terrain to: {filepath}")
    print(f"Dimensions: {kcm.header.width}x{kcm.header.height}")
    print(f"Textures: {len(kcm.textures)}")
    
    return {'FINISHED'}

def mesh_to_kcm(obj: bpy.types.Object, export_textures: bool = True) -> Optional[kcm_file.KCMFile]:
    """Convert Blender mesh to KCM terrain data"""
    
    # Get mesh data
    mesh = obj.data
    
    # Analyze mesh to determine terrain dimensions
    dimensions = analyze_terrain_mesh(mesh)
    if not dimensions:
        print("Could not determine terrain dimensions")
        return None
    
    width, height, tile_size = dimensions
    
    # Create KCM structure
    kcm = kcm_file.KCMFile()
    kcm.create_empty_terrain(width, height, tile_size)
    
    # Extract texture information
    if export_textures:
        extract_textures(kcm, obj)
    
    # Extract tile data
    extract_tile_data(kcm, obj, width, height, tile_size)
    
    return kcm

def analyze_terrain_mesh(mesh: bpy.types.Mesh) -> Optional[Tuple[int, int, int]]:
    """Analyze mesh to determine terrain grid dimensions"""
    
    # Get all vertex positions
    vertices = [v.co for v in mesh.vertices]
    
    if len(vertices) < 4:
        return None
    
    # Find bounds
    min_x = min(v.x for v in vertices)
    max_x = max(v.x for v in vertices)
    min_y = min(v.y for v in vertices)
    max_y = max(v.y for v in vertices)
    
    # Find unique X and Y coordinates to determine grid
    x_coords = sorted(list(set(v.x for v in vertices)))
    y_coords = sorted(list(set(v.y for v in vertices)))
    
    if len(x_coords) < 2 or len(y_coords) < 2:
        return None
    
    # Calculate tile size (assuming regular grid)
    tile_size_x = x_coords[1] - x_coords[0]
    tile_size_y = y_coords[1] - y_coords[0]
    
    # Use average tile size
    tile_size = int((tile_size_x + tile_size_y) / 2)
    
    # Calculate grid dimensions
    width = len(x_coords) - 1
    height = len(y_coords) - 1
    
    return width, height, tile_size

def extract_textures(kcm: kcm_file.KCMFile, obj: bpy.types.Object):
    """Extract texture information from object materials"""
    
    texture_map = {}  # Map material index to texture ID
    
    for mat_idx, material in enumerate(obj.data.materials):
        if material and material.use_nodes:
            # Find texture nodes
            for node in material.node_tree.nodes:
                if node.type == 'TEX_IMAGE' and node.image:
                    image = node.image
                    
                    # Get texture filename
                    if image.filepath:
                        filename = os.path.basename(image.filepath)
                    else:
                        filename = image.name
                    
                    # Add texture to KCM
                    texture_id = kcm.add_texture(
                        filename,
                        image.size[0],
                        image.size[1],
                        get_image_format(image)
                    )
                    
                    texture_map[mat_idx] = texture_id
                    break
    
    return texture_map

def get_image_format(image: bpy.types.Image) -> str:
    """Determine image format from Blender image"""
    
    if image.filepath:
        ext = os.path.splitext(image.filepath)[1].lower()
        format_map = {
            '.dds': 'DDS',
            '.tga': 'TGA',
            '.bmp': 'BMP',
            '.png': 'PNG',
            '.jpg': 'JPG',
            '.jpeg': 'JPG'
        }
        return format_map.get(ext, 'DDS')
    
    return 'DDS'

def extract_tile_data(kcm: kcm_file.KCMFile, obj: bpy.types.Object, width: int, height: int, tile_size: int):
    """Extract tile data from mesh faces"""
    
    # Get mesh in world coordinates
    mesh = obj.data
    world_matrix = obj.matrix_world
    
    # Create bmesh for easier face access
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.faces.ensure_lookup_table()
    
    # Get texture map
    texture_map = extract_textures(kcm, obj)
    
    # Get UV layer
    uv_layer = bm.loops.layers.uv.active
    
    # Process each face as a terrain tile
    for face in bm.faces:
        # Get face center in world coordinates
        face_center = world_matrix @ face.calc_center_median()
        
        # Calculate tile coordinates
        tile_x = int(face_center.x / tile_size)
        tile_y = int(face_center.y / tile_size)
        
        # Check bounds
        if tile_x >= 0 and tile_x < width and tile_y >= 0 and tile_y < height:
            tile = kcm.tiles[tile_y][tile_x]
            
            # Set height (Z coordinate)
            tile.height = face_center.z
            
            # Set texture ID
            if face.material_index in texture_map:
                tile.texture_id = texture_map[face.material_index]
            
            # Calculate normal
            normal = world_matrix.to_3x3() @ face.normal
            tile.normal_x = normal.x
            tile.normal_y = normal.y
            tile.normal_z = normal.z
            
            # Get UV coordinates (use first vertex UV)
            if uv_layer and len(face.loops) > 0:
                uv = face.loops[0][uv_layer].uv
                tile.uv_u = uv.x
                tile.uv_v = uv.y
    
    bm.free()

def export_heightmap(obj: bpy.types.Object, filepath: str, width: int = 512, height: int = 512) -> bool:
    """Export terrain as heightmap image"""
    
    try:
        # Create new image
        image = bpy.data.images.new("Heightmap", width, height)
        
        # Get mesh data
        mesh = obj.data
        world_matrix = obj.matrix_world
        
        # Find height bounds
        vertices = [world_matrix @ v.co for v in mesh.vertices]
        min_z = min(v.z for v in vertices)
        max_z = max(v.z for v in vertices)
        height_range = max_z - min_z if max_z > min_z else 1.0
        
        # Create heightmap pixels
        pixels = [0.0] * (width * height * 4)  # RGBA
        
        for y in range(height):
            for x in range(width):
                # Convert pixel coordinates to world coordinates
                world_x = (x / (width - 1)) * (max(v.x for v in vertices) - min(v.x for v in vertices))
                world_y = (y / (height - 1)) * (max(v.y for v in vertices) - min(v.y for v in vertices))
                
                # Sample height at this position
                height_value = sample_height_at_position(mesh, world_matrix, world_x, world_y)
                
                # Normalize height to 0-1 range
                normalized_height = (height_value - min_z) / height_range
                
                # Set pixel (grayscale)
                pixel_idx = (y * width + x) * 4
                pixels[pixel_idx] = normalized_height      # R
                pixels[pixel_idx + 1] = normalized_height  # G
                pixels[pixel_idx + 2] = normalized_height  # B
                pixels[pixel_idx + 3] = 1.0               # A
        
        # Set pixels and save
        image.pixels = pixels
        image.filepath_raw = filepath
        image.file_format = 'PNG'
        image.save()
        
        # Remove temporary image
        bpy.data.images.remove(image)
        
        return True
        
    except Exception as e:
        print(f"Error exporting heightmap: {e}")
        return False

def sample_height_at_position(mesh: bpy.types.Mesh, world_matrix: mathutils.Matrix, x: float, y: float) -> float:
    """Sample height at specific X,Y position using nearest vertex"""
    
    min_distance = float('inf')
    closest_height = 0.0
    
    for vertex in mesh.vertices:
        world_pos = world_matrix @ vertex.co
        distance = ((world_pos.x - x) ** 2 + (world_pos.y - y) ** 2) ** 0.5
        
        if distance < min_distance:
            min_distance = distance
            closest_height = world_pos.z
    
    return closest_height

def validate_terrain_mesh(obj: bpy.types.Object) -> List[str]:
    """Validate mesh for terrain export"""
    
    issues = []
    
    if not obj or obj.type != 'MESH':
        issues.append("Object is not a mesh")
        return issues
    
    mesh = obj.data
    
    # Check if mesh has faces
    if len(mesh.polygons) == 0:
        issues.append("Mesh has no faces")
    
    # Check if mesh is roughly grid-like
    vertices = [v.co for v in mesh.vertices]
    if len(vertices) < 4:
        issues.append("Mesh has too few vertices")
    
    # Check for materials if textures are needed
    if len(mesh.materials) == 0:
        issues.append("Mesh has no materials (textures won't be exported)")
    
    return issues
