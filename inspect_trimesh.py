#!/usr/bin/env python3
"""
Direct inspection of trimesh.util to see what's available
"""

import sys
import os

def inspect_trimesh_util_directly():
    """Bypass the broken import and look at the util module directly"""
    print("🔍 DIRECT TRIMESH.UTIL INSPECTION")
    print("=" * 40)
    
    # Find trimesh installation path
    venv_path = r"C:\Users\dante\OneDrive\Desktop\Play\.venv\Lib\site-packages"
    trimesh_path = os.path.join(venv_path, "trimesh")
    util_path = os.path.join(trimesh_path, "util.py")
    
    print(f"Checking: {util_path}")
    
    if os.path.exists(util_path):
        print("✅ util.py file exists")
        
        # Read the file to see what's actually in it
        try:
            with open(util_path, 'r') as f:
                content = f.read()
            
            print(f"✅ File size: {len(content)} characters")
            
            # Look for has_module function
            if 'def has_module' in content:
                print("✅ has_module function found in file")
            else:
                print("❌ has_module function NOT found in file")
                
            # Show all function definitions
            lines = content.split('\n')
            functions = [line.strip() for line in lines if line.strip().startswith('def ')]
            
            print(f"\n📋 Functions found in util.py ({len(functions)}):")
            for func in functions[:10]:  # Show first 10
                print(f"  {func}")
            
            if len(functions) > 10:
                print(f"  ... and {len(functions) - 10} more")
                
        except Exception as e:
            print(f"❌ Error reading util.py: {e}")
    else:
        print("❌ util.py file does not exist")
        
        # Check if it's a directory instead
        if os.path.exists(os.path.join(trimesh_path, "util")):
            print("📁 Found util/ directory instead of util.py")
            util_dir = os.path.join(trimesh_path, "util")
            files = os.listdir(util_dir)
            print(f"Contents: {files}")
            
            # Check __init__.py in util directory
            init_file = os.path.join(util_dir, "__init__.py")
            if os.path.exists(init_file):
                print("Checking util/__init__.py:")
                try:
                    with open(init_file, 'r') as f:
                        content = f.read()
                    
                    if 'has_module' in content:
                        print("✅ has_module found in util/__init__.py")
                    else:
                        print("❌ has_module NOT found in util/__init__.py")
                        print("First 500 chars of file:")
                        print(content[:500])
                        
                except Exception as e:
                    print(f"❌ Error reading util/__init__.py: {e}")

def check_trimesh_files():
    """Check the overall trimesh installation structure"""
    print("\n🔍 TRIMESH INSTALLATION STRUCTURE")
    print("=" * 40)
    
    venv_path = r"C:\Users\dante\OneDrive\Desktop\Play\.venv\Lib\site-packages"
    trimesh_path = os.path.join(venv_path, "trimesh")
    
    if os.path.exists(trimesh_path):
        files = os.listdir(trimesh_path)
        print(f"Trimesh directory contents ({len(files)} items):")
        for item in sorted(files):
            item_path = os.path.join(trimesh_path, item)
            if os.path.isdir(item_path):
                print(f"  📁 {item}/")
            else:
                print(f"  📄 {item}")

if __name__ == "__main__":
    inspect_trimesh_util_directly()
    check_trimesh_files()