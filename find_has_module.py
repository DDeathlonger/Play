#!/usr/bin/env python3
"""
Find where has_module is being called in trimesh code
"""

import os
import re

def find_has_module_usage():
    """Search for has_module usage in trimesh files"""
    print("🔍 SEARCHING FOR has_module USAGE")
    print("=" * 40)
    
    venv_path = r"C:\Users\dante\OneDrive\Desktop\Play\.venv\Lib\site-packages"
    trimesh_path = os.path.join(venv_path, "trimesh")
    
    has_module_files = []
    
    # Search through all Python files
    for root, dirs, files in os.walk(trimesh_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        
                    if 'has_module' in content:
                        # Find line numbers
                        lines = content.split('\n')
                        matches = []
                        for i, line in enumerate(lines):
                            if 'has_module' in line:
                                matches.append((i+1, line.strip()))
                        
                        if matches:
                            rel_path = os.path.relpath(file_path, trimesh_path)
                            has_module_files.append((rel_path, matches))
                            
                except Exception as e:
                    pass  # Skip files we can't read
    
    if has_module_files:
        print(f"Found {len(has_module_files)} files using has_module:")
        for file_path, matches in has_module_files:
            print(f"\n📄 {file_path}:")
            for line_num, line in matches:
                print(f"  Line {line_num}: {line}")
    else:
        print("❌ No files found using has_module")
    
    return has_module_files

def analyze_dae_file():
    """Specifically look at the dae.py file that's causing the error"""
    print("\n🔍 ANALYZING DAE.PY ERROR")
    print("=" * 30)
    
    venv_path = r"C:\Users\dante\OneDrive\Desktop\Play\.venv\Lib\site-packages"
    dae_path = os.path.join(venv_path, "trimesh", "exchange", "dae.py")
    
    if os.path.exists(dae_path):
        try:
            with open(dae_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Find the problematic line (around line 447)
            for i, line in enumerate(lines[440:450], 441):  # Check around line 447
                if 'has_module' in line:
                    print(f"🎯 FOUND ERROR LINE {i}: {line.strip()}")
                    
                    # Show context
                    print("\nContext (lines around the error):")
                    start = max(0, i-5)
                    end = min(len(lines), i+3)
                    for j in range(start, end):
                        marker = ">>> " if j == i-1 else "    "
                        print(f"{marker}{j+1:3}: {lines[j].rstrip()}")
                    break
                    
        except Exception as e:
            print(f"❌ Error reading dae.py: {e}")
    else:
        print("❌ dae.py file not found")

def suggest_fix():
    """Suggest potential fixes"""
    print("\n💡 POTENTIAL FIXES")
    print("=" * 20)
    
    print("1. The has_module function appears to have been removed from trimesh.util")
    print("2. We need to either:")
    print("   a) Find what replaced has_module")
    print("   b) Implement a workaround")
    print("   c) Downgrade trimesh to a working version")
    print("   d) Use importlib.util.find_spec() as replacement")

if __name__ == "__main__":
    has_module_files = find_has_module_usage()
    analyze_dae_file()
    suggest_fix()