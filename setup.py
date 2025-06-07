"""
Setup script for KWE-Blender addon
Helps with installation and configuration
"""

import os
import sys
import shutil
import zipfile
from pathlib import Path

def get_blender_addon_path():
    """Get Blender addon installation path"""
    
    # Common Blender addon paths
    if sys.platform == "win32":
        # Windows
        paths = [
            os.path.expanduser("~/AppData/Roaming/Blender Foundation/Blender/*/scripts/addons/"),
            "C:/Program Files/Blender Foundation/Blender/*/scripts/addons/",
        ]
    elif sys.platform == "darwin":
        # macOS
        paths = [
            os.path.expanduser("~/Library/Application Support/Blender/*/scripts/addons/"),
            "/Applications/Blender.app/Contents/Resources/*/scripts/addons/",
        ]
    else:
        # Linux
        paths = [
            os.path.expanduser("~/.config/blender/*/scripts/addons/"),
            "/usr/share/blender/*/scripts/addons/",
        ]
    
    # Find existing Blender installation
    for path_pattern in paths:
        import glob
        matches = glob.glob(path_pattern)
        if matches:
            return matches[0]
    
    return None

def create_addon_zip():
    """Create addon zip file for manual installation"""
    
    addon_files = [
        "__init__.py",
        "kcm_file.py",
        "terrain_importer.py", 
        "terrain_exporter.py",
        "texture_manager.py",
        "ui_panels.py",
        "operators.py",
        "README.md",
        "sample_textures.env"
    ]
    
    zip_path = "KWE-Blender.zip"
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in addon_files:
            if os.path.exists(file):
                zipf.write(file, f"KWE-Blender/{file}")
    
    print(f"✓ Created addon zip: {zip_path}")
    return zip_path

def install_addon():
    """Install addon to Blender"""
    
    addon_path = get_blender_addon_path()
    
    if not addon_path:
        print("✗ Could not find Blender addon directory")
        print("Please install manually:")
        print("1. Create addon zip using create_addon_zip()")
        print("2. In Blender: Edit > Preferences > Add-ons > Install...")
        print("3. Select the zip file and enable the addon")
        return False
    
    target_dir = os.path.join(addon_path, "KWE-Blender")
    
    # Create target directory
    os.makedirs(target_dir, exist_ok=True)
    
    # Copy addon files
    addon_files = [
        "__init__.py",
        "kcm_file.py", 
        "terrain_importer.py",
        "terrain_exporter.py",
        "texture_manager.py",
        "ui_panels.py",
        "operators.py"
    ]
    
    for file in addon_files:
        if os.path.exists(file):
            shutil.copy2(file, target_dir)
            print(f"✓ Copied {file}")
        else:
            print(f"✗ Missing file: {file}")
    
    print(f"✓ Addon installed to: {target_dir}")
    print("Please restart Blender and enable the addon in Preferences > Add-ons")
    return True

def setup_sample_data():
    """Setup sample data for testing"""
    
    # Create sample directory structure
    sample_dir = "sample_data"
    os.makedirs(sample_dir, exist_ok=True)
    os.makedirs(os.path.join(sample_dir, "textures"), exist_ok=True)
    os.makedirs(os.path.join(sample_dir, "terrain"), exist_ok=True)
    
    # Copy sample texture list
    if os.path.exists("sample_textures.env"):
        shutil.copy2("sample_textures.env", os.path.join(sample_dir, "textures.env"))
    
    # Create sample readme
    readme_content = """# Sample Data for KWE-Blender

This directory contains sample data for testing the KWE-Blender addon.

## Directory Structure:
- textures/     - Place your game texture files here (.dds, .tga, .bmp, .png)
- terrain/      - Place your KCM terrain files here
- textures.env  - Sample texture list file

## Usage:
1. Copy your game textures to the textures/ folder
2. Copy your KCM terrain files to the terrain/ folder  
3. Edit textures.env to match your texture files
4. In Blender, set the texture path to this textures/ folder
5. Load the textures.env file in the KWE panel

## Creating Test Textures:
If you don't have game textures, you can create simple test textures:
- Create 256x256 images in any image editor
- Save as PNG or TGA format
- Name them according to the textures.env file
"""
    
    with open(os.path.join(sample_dir, "README.txt"), "w") as f:
        f.write(readme_content)
    
    print(f"✓ Sample data directory created: {sample_dir}")

def main():
    """Main setup function"""
    
    print("KWE-Blender Setup")
    print("=" * 30)
    
    while True:
        print("\nOptions:")
        print("1. Install addon to Blender")
        print("2. Create addon zip for manual installation")
        print("3. Setup sample data directory")
        print("4. Exit")
        
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == "1":
            install_addon()
        elif choice == "2":
            create_addon_zip()
        elif choice == "3":
            setup_sample_data()
        elif choice == "4":
            break
        else:
            print("Invalid choice. Please enter 1-4.")
    
    print("\nSetup completed!")

if __name__ == "__main__":
    main()
