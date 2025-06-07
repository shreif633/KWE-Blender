"""
KCM File Format Handler for KalOnline Terrain Files
Converted from Delphi 7 original implementation
"""

import struct
import os
from typing import List, Tuple, Optional, Dict, Any

class KCMHeader:
    """KCM file header structure"""
    def __init__(self):
        self.signature = b"KCM"  # File signature
        self.version = 1         # File format version
        self.width = 0           # Terrain width in tiles
        self.height = 0          # Terrain height in tiles
        self.tile_size = 32      # Size of each terrain tile
        self.texture_count = 0   # Number of textures used
        self.reserved = [0] * 8  # Reserved bytes for future use

class KCMTile:
    """Individual terrain tile data"""
    def __init__(self):
        self.height = 0.0        # Tile height/elevation
        self.texture_id = 0      # Index to texture array
        self.flags = 0           # Tile flags (walkable, etc.)
        self.normal_x = 0.0      # Normal vector X
        self.normal_y = 1.0      # Normal vector Y  
        self.normal_z = 0.0      # Normal vector Z
        self.uv_u = 0.0          # Texture U coordinate
        self.uv_v = 0.0          # Texture V coordinate

class KCMTexture:
    """Texture information"""
    def __init__(self):
        self.filename = ""       # Texture filename
        self.width = 256         # Texture width
        self.height = 256        # Texture height
        self.format = "DDS"      # Texture format (DDS, TGA, BMP)

class KCMFile:
    """Main KCM file class for reading/writing terrain data"""
    
    def __init__(self):
        self.header = KCMHeader()
        self.textures: List[KCMTexture] = []
        self.tiles: List[List[KCMTile]] = []  # 2D array of tiles
        self.filepath = ""
    
    def read(self, filepath: str) -> bool:
        """Read KCM file from disk"""
        try:
            self.filepath = filepath
            with open(filepath, 'rb') as f:
                # Read header
                if not self._read_header(f):
                    return False
                
                # Read textures
                if not self._read_textures(f):
                    return False
                
                # Read tile data
                if not self._read_tiles(f):
                    return False
                
            return True
        except Exception as e:
            print(f"Error reading KCM file: {e}")
            return False
    
    def write(self, filepath: str) -> bool:
        """Write KCM file to disk"""
        try:
            with open(filepath, 'wb') as f:
                # Write header
                self._write_header(f)
                
                # Write textures
                self._write_textures(f)
                
                # Write tile data
                self._write_tiles(f)
                
            return True
        except Exception as e:
            print(f"Error writing KCM file: {e}")
            return False
    
    def _read_header(self, f) -> bool:
        """Read file header"""
        # Read signature (4 bytes)
        sig = f.read(4)
        if sig[:3] != b"KCM":
            print("Invalid KCM file signature")
            return False
        
        # Read header data
        data = struct.unpack('<IIIII', f.read(20))
        self.header.version = data[0]
        self.header.width = data[1]
        self.header.height = data[2]
        self.header.tile_size = data[3]
        self.header.texture_count = data[4]
        
        # Read reserved bytes
        f.read(32)  # Skip reserved area
        
        return True
    
    def _read_textures(self, f) -> bool:
        """Read texture information"""
        self.textures = []
        
        for i in range(self.header.texture_count):
            texture = KCMTexture()
            
            # Read filename length and filename
            filename_len = struct.unpack('<I', f.read(4))[0]
            texture.filename = f.read(filename_len).decode('utf-8')
            
            # Read texture properties
            data = struct.unpack('<III', f.read(12))
            texture.width = data[0]
            texture.height = data[1]
            format_id = data[2]
            
            # Convert format ID to string
            format_map = {0: "DDS", 1: "TGA", 2: "BMP", 3: "PNG"}
            texture.format = format_map.get(format_id, "DDS")
            
            self.textures.append(texture)
        
        return True
    
    def _read_tiles(self, f) -> bool:
        """Read terrain tile data"""
        self.tiles = []
        
        for y in range(self.header.height):
            row = []
            for x in range(self.header.width):
                tile = KCMTile()
                
                # Read tile data (32 bytes per tile)
                data = struct.unpack('<fIfffffff', f.read(32))
                tile.height = data[0]
                tile.texture_id = data[1]
                tile.flags = int(data[2])
                tile.normal_x = data[3]
                tile.normal_y = data[4]
                tile.normal_z = data[5]
                tile.uv_u = data[6]
                tile.uv_v = data[7]
                
                row.append(tile)
            self.tiles.append(row)
        
        return True
    
    def _write_header(self, f):
        """Write file header"""
        # Write signature
        f.write(b"KCM\x00")
        
        # Write header data
        f.write(struct.pack('<IIIII', 
            self.header.version,
            self.header.width,
            self.header.height,
            self.header.tile_size,
            self.header.texture_count
        ))
        
        # Write reserved bytes
        f.write(b'\x00' * 32)
    
    def _write_textures(self, f):
        """Write texture information"""
        for texture in self.textures:
            # Write filename
            filename_bytes = texture.filename.encode('utf-8')
            f.write(struct.pack('<I', len(filename_bytes)))
            f.write(filename_bytes)
            
            # Write texture properties
            format_map = {"DDS": 0, "TGA": 1, "BMP": 2, "PNG": 3}
            format_id = format_map.get(texture.format, 0)
            
            f.write(struct.pack('<III', 
                texture.width,
                texture.height,
                format_id
            ))
    
    def _write_tiles(self, f):
        """Write terrain tile data"""
        for row in self.tiles:
            for tile in row:
                f.write(struct.pack('<fIfffffff',
                    tile.height,
                    tile.texture_id,
                    float(tile.flags),
                    tile.normal_x,
                    tile.normal_y,
                    tile.normal_z,
                    tile.uv_u,
                    tile.uv_v
                ))
    
    def get_texture_path(self, texture_id: int, base_path: str = "") -> str:
        """Get full path to texture file"""
        if texture_id < 0 or texture_id >= len(self.textures):
            return ""
        
        texture = self.textures[texture_id]
        if base_path:
            return os.path.join(base_path, texture.filename)
        return texture.filename
    
    def add_texture(self, filename: str, width: int = 256, height: int = 256, format: str = "DDS") -> int:
        """Add a new texture and return its ID"""
        texture = KCMTexture()
        texture.filename = filename
        texture.width = width
        texture.height = height
        texture.format = format
        
        self.textures.append(texture)
        self.header.texture_count = len(self.textures)
        
        return len(self.textures) - 1
    
    def create_empty_terrain(self, width: int, height: int, tile_size: int = 32):
        """Create empty terrain with specified dimensions"""
        self.header.width = width
        self.header.height = height
        self.header.tile_size = tile_size
        self.header.texture_count = 0
        
        # Initialize empty tiles
        self.tiles = []
        for y in range(height):
            row = []
            for x in range(width):
                tile = KCMTile()
                row.append(tile)
            self.tiles.append(row)
