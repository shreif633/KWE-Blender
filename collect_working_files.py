#!/usr/bin/env python3
"""
Script to help collect and organize working KCM addon files
Run this script in the directory containing your working KCM addon
"""

import os
import shutil
import zipfile
from pathlib import Path

def find_addon_files(search_path="."):
    """Find potential addon files"""
    addon_files = []
    
    # Common addon file patterns
    patterns = [
        "*.py",
        "*.md", 
        "*.txt",
        "*.kcm",
        "*.env",
        "*.dds",
        "*.tga"
    ]
    
    for root, dirs, files in os.walk(search_path):
        for file in files:
            file_path = os.path.join(root, file)
            
            # Check if it's likely an addon file
            if (file.endswith('.py') or 
                'kcm' in file.lower() or
                'opl' in file.lower() or
                'kal' in file.lower() or
                file.endswith('.env')):
                
                addon_files.append(file_path)
    
    return addon_files

def analyze_python_files(files):
    """Analyze Python files for KCM-related content"""
    kcm_files = []
    
    for file_path in files:
        if file_path.endswith('.py'):
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read().lower()
                    
                    # Check for KCM-related keywords
                    if any(keyword in content for keyword in [
                        'kcm', 'kalonline', 'terrain', 'import_kcm', 
                        'export_kcm', 'bl_info', 'bpy.types'
                    ]):
                        kcm_files.append(file_path)
                        
            except Exception as e:
                print(f"Could not read {file_path}: {e}")
    
    return kcm_files

def create_working_files_package():
    """Create a package of working files"""
    
    print("🔍 Searching for KCM addon files...")
    
    # Find all potential files
    all_files = find_addon_files()
    print(f"Found {len(all_files)} potential files")
    
    # Analyze Python files
    kcm_files = analyze_python_files(all_files)
    print(f"Found {len(kcm_files)} KCM-related Python files")
    
    if not kcm_files:
        print("❌ No KCM addon files found!")
        print("Please run this script in the directory containing your working KCM addon")
        return False
    
    # Create package directory
    package_dir = "working_kcm_addon"
    if os.path.exists(package_dir):
        shutil.rmtree(package_dir)
    os.makedirs(package_dir)
    
    # Copy files
    print(f"\n📦 Creating package in {package_dir}/")
    
    for file_path in all_files:
        try:
            # Determine destination
            rel_path = os.path.relpath(file_path)
            dest_path = os.path.join(package_dir, rel_path)
            
            # Create destination directory
            dest_dir = os.path.dirname(dest_path)
            if dest_dir:
                os.makedirs(dest_dir, exist_ok=True)
            
            # Copy file
            shutil.copy2(file_path, dest_path)
            print(f"  ✓ {rel_path}")
            
        except Exception as e:
            print(f"  ❌ Failed to copy {file_path}: {e}")
    
    # Create info file
    info_content = f"""# Working KCM Addon Files

This package contains the working KCM addon files found in your system.

## Files Included:
"""
    
    for file_path in sorted(all_files):
        rel_path = os.path.relpath(file_path)
        file_size = os.path.getsize(file_path)
        info_content += f"- {rel_path} ({file_size} bytes)\n"
    
    info_content += f"""
## KCM-Related Python Files:
"""
    
    for file_path in sorted(kcm_files):
        rel_path = os.path.relpath(file_path)
        info_content += f"- {rel_path}\n"
    
    info_content += """
## Next Steps:
1. Review the files in this package
2. Share this package with the KWE-Blender developer
3. The working implementation will be integrated with enhanced features

## Integration:
The developer will:
- Analyze your working KCM format handler
- Preserve the proven import/export logic
- Integrate with enhanced UI and features
- Create comprehensive documentation
"""
    
    with open(os.path.join(package_dir, "PACKAGE_INFO.md"), 'w') as f:
        f.write(info_content)
    
    # Create zip file
    zip_path = "working_kcm_addon.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(package_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arc_path = os.path.relpath(file_path, package_dir)
                zipf.write(file_path, arc_path)
    
    print(f"\n✅ Package created successfully!")
    print(f"📁 Directory: {package_dir}/")
    print(f"📦 Zip file: {zip_path}")
    print(f"\nYou can share either the directory or zip file.")
    
    return True

def main():
    """Main function"""
    print("=" * 60)
    print("🔧 Working KCM Addon File Collector")
    print("=" * 60)
    print()
    print("This script will help collect your working KCM addon files")
    print("for integration with the enhanced KWE-Blender features.")
    print()
    
    # Check current directory
    current_dir = os.getcwd()
    print(f"📂 Current directory: {current_dir}")
    print()
    
    # Ask for confirmation
    response = input("Search for KCM addon files in current directory? (y/n): ")
    if response.lower() != 'y':
        print("Please navigate to your KCM addon directory and run this script again.")
        return
    
    # Create package
    if create_working_files_package():
        print("\n🎉 Success! Your working KCM addon files have been packaged.")
        print("\nNext steps:")
        print("1. Share the 'working_kcm_addon.zip' file")
        print("2. The working implementation will be integrated")
        print("3. You'll get enhanced features with proven KCM support")
    else:
        print("\n❌ No KCM addon files found.")
        print("\nTroubleshooting:")
        print("- Make sure you're in the correct directory")
        print("- Check that the addon files have .py extension")
        print("- Look for files containing 'kcm', 'import', or 'export'")

if __name__ == "__main__":
    main()
