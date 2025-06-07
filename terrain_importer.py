"""
KalOnline Terrain Importer for Blender
Imports KCM terrain files and applies real textures
"""

import bpy
import bmesh
import mathutils
from typing import List, Tuple, Optional
from . import kcm_file
from . import texture_manager

def import_kcm(context, filepath: str, load_textures: bool = True, texture_path: str = "") -> set:
    """Import KCM terrain file into Blender"""
    
    # Load KCM file
    kcm = kcm_file.KCMFile()
    if not kcm.read(filepath):
        return {'CANCELLED'}
    
    # Setup texture manager
    if load_textures and texture_path:
        texture_manager.texture_manager.set_texture_paths([texture_path])
    
    # Create terrain mesh
    terrain_obj = create_terrain_mesh(kcm, load_textures)
    if not terrain_obj:
        return {'CANCELLED'}
    
    # Add to scene
    context.collection.objects.link(terrain_obj)
    
    # Select and make active
    bpy.context.view_layer.objects.active = terrain_obj
    terrain_obj.select_set(True)
    
    print(f"Imported terrain: {kcm.header.width}x{kcm.header.height} tiles")
    print(f"Textures: {len(kcm.textures)}")
    
    return {'FINISHED'}

def create_terrain_mesh(kcm: kcm_file.KCMFile, load_textures: bool = True) -> Optional[bpy.types.Object]:
    """Create Blender mesh from KCM terrain data"""
    
    # Create new mesh
    mesh = bpy.data.meshes.new("KCM_Terrain")
    
    # Generate vertices, faces, and UVs
    vertices, faces, uvs, face_materials = generate_terrain_geometry(kcm)
    
    # Create mesh from data
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    
    # Add UV coordinates
    if uvs:
        add_uv_coordinates(mesh, uvs)
    
    # Create object
    terrain_obj = bpy.data.objects.new("KCM_Terrain", mesh)
    
    # Apply textures if requested
    if load_textures:
        apply_terrain_textures(terrain_obj, kcm, face_materials)
    
    return terrain_obj

def generate_terrain_geometry(kcm: kcm_file.KCMFile) -> Tuple[List, List, List, List]:
    """Generate vertices, faces, UVs and material assignments from terrain data"""
    
    vertices = []
    faces = []
    uvs = []
    face_materials = []
    
    width = kcm.header.width
    height = kcm.header.height
    tile_size = kcm.header.tile_size
    
    # Generate vertices (grid points)
    for y in range(height + 1):
        for x in range(width + 1):
            # Get height from surrounding tiles
            tile_height = get_vertex_height(kcm, x, y)
            
            # Create vertex
            vertex = (
                x * tile_size,
                y * tile_size,
                tile_height
            )
            vertices.append(vertex)
    
    # Generate faces (quads for each tile)
    for y in range(height):
        for x in range(width):
            # Get tile data
            tile = kcm.tiles[y][x]
            
            # Calculate vertex indices for this tile
            v1 = y * (width + 1) + x           # Bottom-left
            v2 = y * (width + 1) + (x + 1)     # Bottom-right
            v3 = (y + 1) * (width + 1) + (x + 1)  # Top-right
            v4 = (y + 1) * (width + 1) + x     # Top-left
            
            # Create face (quad)
            face = [v1, v2, v3, v4]
            faces.append(face)
            
            # Store material assignment
            face_materials.append(tile.texture_id)
            
            # Generate UV coordinates for this face
            face_uvs = [
                (tile.uv_u, tile.uv_v),                    # v1
                (tile.uv_u + 1.0, tile.uv_v),             # v2
                (tile.uv_u + 1.0, tile.uv_v + 1.0),       # v3
                (tile.uv_u, tile.uv_v + 1.0)              # v4
            ]
            uvs.extend(face_uvs)
    
    return vertices, faces, uvs, face_materials

def get_vertex_height(kcm: kcm_file.KCMFile, x: int, y: int) -> float:
    """Get height for vertex by averaging surrounding tile heights"""
    
    total_height = 0.0
    count = 0
    
    # Check all adjacent tiles
    for dy in [-1, 0]:
        for dx in [-1, 0]:
            tile_x = x + dx
            tile_y = y + dy
            
            # Check bounds
            if (tile_x >= 0 and tile_x < kcm.header.width and 
                tile_y >= 0 and tile_y < kcm.header.height):
                
                total_height += kcm.tiles[tile_y][tile_x].height
                count += 1
    
    return total_height / count if count > 0 else 0.0

def add_uv_coordinates(mesh: bpy.types.Mesh, uvs: List[Tuple[float, float]]):
    """Add UV coordinates to mesh"""
    
    # Create UV layer
    uv_layer = mesh.uv_layers.new(name="UVMap")
    
    # Assign UV coordinates
    for i, loop in enumerate(mesh.loops):
        if i < len(uvs):
            uv_layer.data[i].uv = uvs[i]

def apply_terrain_textures(terrain_obj: bpy.types.Object, kcm: kcm_file.KCMFile, face_materials: List[int]):
    """Apply textures to terrain faces"""
    
    # Create materials for each texture
    materials = {}
    
    for i, texture in enumerate(kcm.textures):
        material = texture_manager.texture_manager.create_material(
            texture.filename, 
            f"Terrain_Tex_{i:03d}"
        )
        
        if material:
            materials[i] = material
            terrain_obj.data.materials.append(material)
    
    # Assign materials to faces
    if materials and face_materials:
        # Enter edit mode
        bpy.context.view_layer.objects.active = terrain_obj
        bpy.ops.object.mode_set(mode='EDIT')
        
        # Get bmesh representation
        bm = bmesh.from_mesh(terrain_obj.data)
        bm.faces.ensure_lookup_table()
        
        # Assign materials to faces
        for face_idx, texture_id in enumerate(face_materials):
            if face_idx < len(bm.faces) and texture_id in materials:
                # Get material index
                mat_index = list(terrain_obj.data.materials).index(materials[texture_id])
                bm.faces[face_idx].material_index = mat_index
        
        # Update mesh
        bmesh.update_edit_mesh(terrain_obj.data)
        
        # Return to object mode
        bpy.ops.object.mode_set(mode='OBJECT')

def create_terrain_from_heightmap(width: int, height: int, heightmap_path: str, texture_path: str = "") -> Optional[bpy.types.Object]:
    """Create terrain from heightmap image (utility function)"""
    
    try:
        # Load heightmap
        heightmap = bpy.data.images.load(heightmap_path)
        
        # Create KCM structure
        kcm = kcm_file.KCMFile()
        kcm.create_empty_terrain(width, height)
        
        # Sample heightmap for tile heights
        pixels = list(heightmap.pixels)
        img_width = heightmap.size[0]
        img_height = heightmap.size[1]
        
        for y in range(height):
            for x in range(width):
                # Sample heightmap
                u = x / (width - 1)
                v = y / (height - 1)
                
                px = int(u * (img_width - 1))
                py = int(v * (img_height - 1))
                
                # Get height from red channel
                pixel_idx = (py * img_width + px) * 4
                height_value = pixels[pixel_idx] * 100.0  # Scale height
                
                # Set tile height
                kcm.tiles[y][x].height = height_value
        
        # Add default texture if provided
        if texture_path:
            kcm.add_texture(texture_path)
            for y in range(height):
                for x in range(width):
                    kcm.tiles[y][x].texture_id = 0
        
        # Create mesh
        return create_terrain_mesh(kcm, bool(texture_path))
        
    except Exception as e:
        print(f"Error creating terrain from heightmap: {e}")
        return None
