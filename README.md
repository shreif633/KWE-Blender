# KWE-Blender - KalOnline Terrain Tools

A powerful Blender addon for importing, editing, and exporting KalOnline MMORPG terrain files (.kcm) with full texture support. Converted from the original Delphi 7 implementation.

## Features

### 🌍 Terrain Import/Export
- **Import KCM files** - Load KalOnline terrain files into Blender
- **Export KCM files** - Save Blender terrain back to KalOnline format
- **Real texture display** - View actual game textures in Blender viewport
- **Heightmap support** - Export terrain as heightmap images
- **Encryption support** - Handle encrypted KCM files with CRC validation

### 🎨 Texture Management
- **Texture browser** - Browse and preview available game textures
- **Texture replacement** - Replace textures in terrain with new ones
- **N.ENV support** - Load game texture lists from N.ENV files
- **Multiple formats** - Support for DDS, TGA, BMP, PNG texture formats

### ⚡ Terrain Editing
- **Face-based texturing** - Apply textures to selected faces
- **Height editing** - Raise/lower terrain vertices
- **Material management** - Automatic material creation and assignment
- **UV mapping** - Proper UV coordinate handling

## Installation

1. Download or clone this repository
2. In Blender, go to `Edit > Preferences > Add-ons`
3. Click `Install...` and select the addon folder
4. Enable "Import-Export: KWE-Blender - KalOnline Terrain Tools"

## Quick Start

### Importing Terrain

1. Go to `File > Import > KalOnline Terrain (.kcm)`
2. Select your KCM file
3. Set the texture path to your game's texture folder
4. Enable "Load Textures" to see real textures
5. Click "Import KCM"

### Setting Up Textures

1. Open the KWE panel in the 3D Viewport sidebar (press `N`)
2. Set "Texture Path" to your game's texture folder
3. Set "N.ENV File" to your texture list file (see `sample_textures.env`)
4. Click "Load Texture List"
5. Click "Refresh" to scan for available textures

### Editing Terrain

1. Select the imported terrain object
2. Enter Edit mode (`Tab`)
3. Select faces you want to retexture
4. In the KWE panel, select a texture from the list
5. Click "Apply Texture to Selection"

### Exporting Terrain

1. Select your terrain object
2. Go to `File > Export > KalOnline Terrain (.kcm)`
3. Choose export location and settings
4. Click "Export KCM"

## File Structure

```
KWE-Blender/
├── __init__.py              # Main addon entry point
├── kcm_file.py             # KCM file format handler
├── util.py                 # Encryption/decryption and CRC utilities
├── terrain_importer.py     # Terrain import functionality
├── terrain_exporter.py     # Terrain export functionality
├── texture_manager.py      # Texture loading and management
├── ui_panels.py            # Blender UI panels
├── operators.py            # Blender operators
├── sample_textures.env     # Sample texture list file
└── README.md               # This documentation
```

## KCM File Format

The KCM (KalOnline Map) format stores terrain data including:

- **Header**: File signature, version, dimensions, tile size
- **Textures**: List of texture files with properties
- **Tiles**: 2D grid of terrain tiles with height, texture, normals, UV data

### File Structure
```
KCM Header (56 bytes)
├── Signature: "KCM\0" (4 bytes)
├── Version: uint32 (4 bytes)
├── Width: uint32 (4 bytes) - terrain width in tiles
├── Height: uint32 (4 bytes) - terrain height in tiles
├── Tile Size: uint32 (4 bytes) - size of each tile
├── Texture Count: uint32 (4 bytes)
└── Reserved: 32 bytes

Texture List (variable size)
├── For each texture:
│   ├── Filename Length: uint32 (4 bytes)
│   ├── Filename: string (variable)
│   ├── Width: uint32 (4 bytes)
│   ├── Height: uint32 (4 bytes)
│   └── Format: uint32 (4 bytes) - 0=DDS, 1=TGA, 2=BMP, 3=PNG

Tile Data (32 bytes per tile)
├── For each tile (row by row):
│   ├── Height: float (4 bytes)
│   ├── Texture ID: uint32 (4 bytes)
│   ├── Flags: float (4 bytes) - converted from uint32
│   ├── Normal X: float (4 bytes)
│   ├── Normal Y: float (4 bytes)
│   ├── Normal Z: float (4 bytes)
│   ├── UV U: float (4 bytes)
│   └── UV V: float (4 bytes)
```

## Encryption System

KalOnline uses a proprietary encryption system for protecting game files. The addon includes full support for this encryption:

### Encryption Features
- **Automatic Detection** - Detects if KCM files are encrypted
- **CRC32 Validation** - Verifies file integrity with checksums
- **Transparent Handling** - Automatically encrypts/decrypts during import/export
- **Original Algorithm** - Uses the exact encryption from the original game

### Encryption Process
1. **CRC Calculation** - Calculate CRC32 of original data
2. **CRC Prepending** - Add CRC to beginning of data
3. **XOR Encryption** - Apply XOR cipher with rolling key
4. **File Writing** - Save encrypted data to disk

### Security Notes
- The encryption is for game file protection, not security
- Original algorithm preserved exactly as in Delphi 7 source
- CRC validation ensures file integrity
- Encryption key: 0x5A (default for KCM files)

## N.ENV Texture List Format

The N.ENV file format maps texture IDs to filenames:

```
# Comments start with #
TextureID=filename.dds
0=grass01.dds
1=dirt01.dds
2=stone01.dds
```

## Usage Examples

### Basic Import
```python
import bpy
from kwe_blender import terrain_importer

# Import terrain with textures
terrain_importer.import_kcm(
    bpy.context,
    "path/to/terrain.kcm",
    load_textures=True,
    texture_path="path/to/textures/"
)
```

### Texture Management
```python
from kwe_blender import texture_manager

# Setup texture paths
texture_manager.texture_manager.set_texture_paths([
    "C:/Game/Textures/",
    "C:/Game/Terrain/"
])

# Load texture list
texture_manager.texture_manager.load_game_texture_list("textures.env")

# Replace texture
texture_manager.texture_manager.replace_texture("old.dds", "new.dds")
```

## Troubleshooting

### Common Issues

**"Texture not found" errors:**
- Check that texture path is correct
- Ensure texture files exist in the specified folder
- Try different file extensions (.dds, .tga, .bmp, .png)

**"Invalid KCM file signature" error:**
- File may be corrupted or not a valid KCM file
- Check file size and format

**Textures appear black/missing:**
- Blender may not support the texture format
- Try converting textures to PNG or TGA format
- Check material nodes are properly connected

**Export fails:**
- Ensure mesh is properly structured as a grid
- Check that materials have texture nodes
- Validate terrain dimensions

### Performance Tips

- Use smaller texture sizes for better viewport performance
- Limit the number of different materials per terrain
- Use texture atlases when possible
- Enable GPU acceleration in Blender preferences

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with sample KCM files
5. Submit a pull request

## License

This project is open source. Please respect the original KalOnline game assets and use only for educational/modding purposes.

## Credits

- Original KCM format implementation from Delphi 7
- Blender Python API documentation
- KalOnline community for format specifications