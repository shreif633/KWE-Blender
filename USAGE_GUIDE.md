# KWE-Blender Usage Guide

Complete guide for using the KalOnline Terrain Tools addon in Blender.

## 📦 Installation

### Method 1: Automatic Installation
```bash
python setup.py
```
Follow the interactive menu to install the addon.

### Method 2: Manual Installation
1. Download/clone the repository
2. In Blender: `Edit > Preferences > Add-ons`
3. Click `Install...` and select the addon folder
4. Enable "Import-Export: KWE-Blender - KalOnline Terrain Tools"

### Method 3: Zip Installation
```bash
python setup.py
# Choose option 2 to create addon zip
```
Then install the zip file in Blender preferences.

## 🚀 Quick Start

### 1. First Time Setup

1. **Open Blender** and ensure the addon is enabled
2. **Open 3D Viewport** and press `N` to show sidebar
3. **Find KWE Panel** in the sidebar (should appear as "KalOnline Terrain")

### 2. Configure Paths

In the KWE panel:
- **Texture Path**: Set to your KalOnline texture folder (e.g., `C:\KalOnline\Textures\`)
- **N.ENV File**: Set to your texture list file (e.g., `textures.env`)

### 3. Load Texture List

1. Click **"Load Texture List"** to load your N.ENV file
2. Click **"Refresh"** to scan for available textures
3. You should see textures listed in the texture browser

## 🌍 Importing Terrain

### Basic Import
1. Go to `File > Import > KalOnline Terrain (.kcm)`
2. Navigate to your KCM file
3. **Enable "Load Textures"** if you want to see real textures
4. Set **"Texture Path"** to your game texture folder
5. Click **"Import KCM"**

### Import Options
- **Load Textures**: Apply real game textures to terrain
- **Texture Path**: Path to texture files directory

### What Happens During Import
- KCM file is read and decrypted (if encrypted)
- Terrain mesh is generated from tile data
- Materials are created for each texture
- Textures are loaded and applied to faces
- Object is added to current scene

## 🎨 Texture Management

### Browsing Textures
1. In KWE panel, go to **"Texture Manager"** section
2. Use the texture list to browse available textures
3. Select a texture and click **"Preview"** to see it

### Replacing Textures
1. Set **"Source Texture"** to the texture you want to replace
2. Set **"Target Texture"** to the new texture file path
3. Click **"Replace Texture"**

### Applying Textures to Faces
1. Select your terrain object
2. Enter **Edit Mode** (`Tab`)
3. Select the faces you want to retexture
4. In KWE panel, select a texture from the list
5. Click **"Apply Texture to Selection"**

## ⚡ Terrain Editing

### Height Editing
1. Select terrain object and enter **Edit Mode**
2. Select vertices you want to modify
3. In **"Terrain Editor"** section:
   - Set **"Strength"** (how much to raise/lower)
   - Set **"Radius"** (area of effect)
4. Click **"Raise"** or **"Lower"** to modify height

### Face-Based Texturing
1. Enter **Edit Mode** and select faces
2. Choose texture from texture list
3. Click **"Apply Texture to Selection"**
4. The material will be created and applied automatically

## 📤 Exporting Terrain

### Basic Export
1. Select your terrain object
2. Go to `File > Export > KalOnline Terrain (.kcm)`
3. Choose save location
4. Configure export options:
   - **Export Texture References**: Include texture information
   - **Encrypt File**: Use KalOnline encryption (recommended)
5. Click **"Export KCM"**

### Export Requirements
- Object must be a mesh
- Mesh should be grid-like structure
- Materials should have texture nodes for texture export

### Validation
The exporter will check:
- Mesh has faces
- Mesh is roughly grid-like
- Materials exist (for texture export)

## 🛠️ Advanced Features

### Heightmap Export
1. Select terrain object
2. In **"Terrain Editor"** section
3. Click **"Export Heightmap"**
4. Choose save location for PNG heightmap

### Creating Terrain from Heightmap
```python
# In Blender's scripting workspace
import bpy
from kwe_blender.terrain_importer import create_terrain_from_heightmap

terrain = create_terrain_from_heightmap(
    width=64, 
    height=64, 
    heightmap_path="path/to/heightmap.png",
    texture_path="path/to/texture.dds"
)
```

### Batch Processing
```python
import bpy
import os
from kwe_blender import terrain_importer, terrain_exporter

# Import multiple KCM files
kcm_folder = "C:/KalOnline/Maps/"
for file in os.listdir(kcm_folder):
    if file.endswith(".kcm"):
        terrain_importer.import_kcm(
            bpy.context, 
            os.path.join(kcm_folder, file),
            load_textures=True,
            texture_path="C:/KalOnline/Textures/"
        )
```

## 🔧 Troubleshooting

### Common Issues

**"No texture selected" error:**
- Make sure you've loaded the texture list
- Click "Refresh" to scan for textures
- Check that texture path is correct

**"Invalid KCM file signature" error:**
- File may be corrupted
- File may not be a valid KCM file
- Try with a different KCM file

**Textures appear black:**
- Check texture path is correct
- Ensure texture files exist
- Try converting textures to PNG format
- Check Blender's texture display settings

**Import fails:**
- Check file permissions
- Ensure KCM file is not corrupted
- Try importing without textures first

**Export fails:**
- Select a mesh object
- Check mesh has faces
- Ensure materials exist for texture export

### Performance Tips

**For Large Terrains:**
- Disable texture loading during import for faster processing
- Use smaller texture sizes
- Limit viewport shading to solid mode

**For Many Textures:**
- Use texture atlases when possible
- Limit number of materials per object
- Clear texture cache periodically

### Debug Mode

Enable debug output in Blender console:
1. Go to `Window > Toggle System Console`
2. Import/export operations will show detailed logs
3. Check for error messages and warnings

## 📋 File Format Support

### Supported Formats

**Terrain Files:**
- `.kcm` - KalOnline terrain files (encrypted and unencrypted)

**Texture Files:**
- `.dds` - DirectDraw Surface (recommended)
- `.tga` - Targa
- `.bmp` - Bitmap
- `.png` - Portable Network Graphics
- `.jpg` - JPEG

**Texture Lists:**
- `.env` - N.ENV texture mapping files

### File Structure Requirements

**KCM Files:**
- Must have valid KCM signature
- Can be encrypted or unencrypted
- Should contain valid tile and texture data

**Texture Files:**
- Should be power-of-2 dimensions (256x256, 512x512, etc.)
- DDS format preferred for game compatibility

**N.ENV Files:**
```
# Format: ID=filename
0=grass01.dds
1=dirt01.dds
2=stone01.dds
```

## 🎮 Game Integration

### Workflow for Modding

1. **Extract** KCM files from game
2. **Import** into Blender using addon
3. **Edit** terrain and textures
4. **Export** back to KCM format
5. **Test** in game

### Best Practices

- **Backup** original files before modding
- **Test** exported files in game before distributing
- **Use** same texture dimensions as original
- **Maintain** tile grid structure for proper collision
- **Document** your changes for other modders

### Compatibility

- Works with original KalOnline terrain format
- Supports both encrypted and unencrypted files
- Maintains backward compatibility
- Preserves original file structure

## 📞 Support

### Getting Help

1. **Check** this usage guide first
2. **Run** the test suite: `python test_addon.py`
3. **Check** Blender console for error messages
4. **Report** issues with sample files and error logs

### Contributing

1. Fork the repository
2. Create feature branch
3. Test with real KCM files
4. Submit pull request with documentation

---

**Happy Terrain Editing!** 🌍✨
