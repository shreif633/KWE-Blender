"""
Test script for KWE-Blender addon
Run this in Blender's scripting workspace to test functionality
"""

import bpy
import os
import sys

# Add addon path to sys.path if running as script
addon_path = os.path.dirname(__file__)
if addon_path not in sys.path:
    sys.path.append(addon_path)

def test_kcm_file_format():
    """Test KCM file format reading/writing"""
    print("Testing KCM file format...")
    
    try:
        from kcm_file import KCMFile, KCMTexture, KCMTile
        
        # Create test terrain
        kcm = KCMFile()
        kcm.create_empty_terrain(4, 4, 32)
        
        # Add test texture
        texture_id = kcm.add_texture("test_grass.dds", 256, 256, "DDS")
        
        # Set some tile data
        for y in range(4):
            for x in range(4):
                tile = kcm.tiles[y][x]
                tile.height = (x + y) * 2.0  # Simple height pattern
                tile.texture_id = texture_id
                tile.uv_u = x / 4.0
                tile.uv_v = y / 4.0
        
        # Test write/read
        test_file = "/tmp/test_terrain.kcm"
        if kcm.write(test_file):
            print("✓ KCM write successful")
            
            # Test read
            kcm2 = KCMFile()
            if kcm2.read(test_file):
                print("✓ KCM read successful")
                print(f"  Dimensions: {kcm2.header.width}x{kcm2.header.height}")
                print(f"  Textures: {len(kcm2.textures)}")
                print(f"  First tile height: {kcm2.tiles[0][0].height}")
            else:
                print("✗ KCM read failed")
        else:
            print("✗ KCM write failed")
            
    except Exception as e:
        print(f"✗ KCM test failed: {e}")

def test_texture_manager():
    """Test texture manager functionality"""
    print("\nTesting texture manager...")
    
    try:
        from texture_manager import TextureManager
        
        tm = TextureManager()
        
        # Test texture path setting
        tm.set_texture_paths(["/tmp", "."])
        print("✓ Texture paths set")
        
        # Test texture list loading (create dummy file)
        env_content = """# Test texture list
0=grass.dds
1=dirt.dds
2=stone.dds"""
        
        with open("/tmp/test.env", "w") as f:
            f.write(env_content)
        
        if tm.load_game_texture_list("/tmp/test.env"):
            print("✓ Texture list loaded")
            print(f"  Loaded {len(tm.game_texture_list)} textures")
        else:
            print("✗ Texture list loading failed")
            
    except Exception as e:
        print(f"✗ Texture manager test failed: {e}")

def test_terrain_creation():
    """Test terrain mesh creation"""
    print("\nTesting terrain creation...")
    
    try:
        from terrain_importer import create_terrain_mesh
        from kcm_file import KCMFile
        
        # Create test terrain
        kcm = KCMFile()
        kcm.create_empty_terrain(3, 3, 16)
        
        # Add height variation
        for y in range(3):
            for x in range(3):
                kcm.tiles[y][x].height = (x + y) * 1.5
        
        # Create mesh
        terrain_obj = create_terrain_mesh(kcm, load_textures=False)
        
        if terrain_obj:
            print("✓ Terrain mesh created")
            print(f"  Vertices: {len(terrain_obj.data.vertices)}")
            print(f"  Faces: {len(terrain_obj.data.polygons)}")
            
            # Add to scene for visual verification
            bpy.context.collection.objects.link(terrain_obj)
            bpy.context.view_layer.objects.active = terrain_obj
            terrain_obj.select_set(True)
            
        else:
            print("✗ Terrain mesh creation failed")
            
    except Exception as e:
        print(f"✗ Terrain creation test failed: {e}")

def test_addon_registration():
    """Test addon registration"""
    print("\nTesting addon registration...")
    
    try:
        # Test if addon classes are registered
        if hasattr(bpy.types, 'KWE_PT_TerrainPanel'):
            print("✓ UI panels registered")
        else:
            print("✗ UI panels not registered")
        
        if hasattr(bpy.ops, 'kwe'):
            print("✓ Operators registered")
        else:
            print("✗ Operators not registered")
            
        if hasattr(bpy.ops, 'import_scene') and hasattr(bpy.ops.import_scene, 'kcm'):
            print("✓ Import operator registered")
        else:
            print("✗ Import operator not registered")
            
    except Exception as e:
        print(f"✗ Registration test failed: {e}")

def create_sample_terrain():
    """Create a sample terrain for testing"""
    print("\nCreating sample terrain...")
    
    try:
        # Clear existing mesh objects
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=False, confirm=False)
        
        # Create a simple grid terrain
        bpy.ops.mesh.primitive_grid_add(
            x_subdivisions=8,
            y_subdivisions=8,
            size=16,
            location=(0, 0, 0)
        )
        
        terrain_obj = bpy.context.active_object
        terrain_obj.name = "Sample_Terrain"
        
        # Add some height variation
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        
        # Add displacement modifier for height variation
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # Add material
        material = bpy.data.materials.new(name="Terrain_Material")
        material.use_nodes = True
        terrain_obj.data.materials.append(material)
        
        print("✓ Sample terrain created")
        print(f"  Name: {terrain_obj.name}")
        print(f"  Vertices: {len(terrain_obj.data.vertices)}")
        print(f"  Faces: {len(terrain_obj.data.polygons)}")
        
    except Exception as e:
        print(f"✗ Sample terrain creation failed: {e}")

def run_all_tests():
    """Run all tests"""
    print("=" * 50)
    print("KWE-Blender Addon Test Suite")
    print("=" * 50)
    
    test_kcm_file_format()
    test_texture_manager()
    test_terrain_creation()
    test_addon_registration()
    create_sample_terrain()
    
    print("\n" + "=" * 50)
    print("Test suite completed!")
    print("Check the console output for results.")
    print("=" * 50)

if __name__ == "__main__":
    run_all_tests()
