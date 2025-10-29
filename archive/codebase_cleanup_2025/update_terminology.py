#!/usr/bin/env python3
"""
Terminology Update Script
Updates all references from SpaceshipGeometryNode to SpaceshipGeometryNode across the project
"""

import os
import re
from pathlib import Path

def update_file_content(file_path):
    """Update SpaceshipGeometryNode references to SpaceshipGeometryNode in a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Update class references
        content = content.replace('SpaceshipGeometryNode', 'SpaceshipGeometryNode')
        
        # Update variable names that should refer to geometry nodes
        content = re.sub(r'\bmodule\b(?=\s*=\s*SpaceshipGeometryNode)', 'geometry_node', content)
        content = re.sub(r'\bmodule\b(?=\s*:\s*SpaceshipGeometryNode)', 'geometry_node', content)
        content = re.sub(r'def\s+(\w*module\w*)\s*\(', lambda m: f"def {m.group(1).replace('module', 'geometry_node')}(", content)
        
        # Update comments and documentation
        content = content.replace('spaceship geometry node', 'spaceship geometry node')
        content = content.replace('Spaceship geometry node', 'Spaceship geometry node')
        content = content.replace('geometry node type', 'geometry node type')
        content = content.replace('geometry node at', 'geometry node at')
        content = content.replace('each geometry node', 'each geometry node')
        content = content.replace('all geometry nodes', 'all geometry nodes')
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Updated: {file_path}")
            return True
        else:
            return False
            
    except Exception as e:
        print(f"❌ Error updating {file_path}: {e}")
        return False

def main():
    """Update terminology across all Python files"""
    project_root = Path(".")
    updated_files = []
    
    # Find all Python files
    python_files = list(project_root.rglob("*.py"))
    
    print(f"Found {len(python_files)} Python files to check...")
    
    for file_path in python_files:
        # Skip archived files and __pycache__
        if 'archive' in str(file_path) or '__pycache__' in str(file_path):
            continue
            
        if update_file_content(file_path):
            updated_files.append(file_path)
    
    print(f"\n✅ Updated {len(updated_files)} files:")
    for file_path in updated_files:
        print(f"   - {file_path}")
    
    print("\n🎯 Terminology update complete!")

if __name__ == "__main__":
    main()