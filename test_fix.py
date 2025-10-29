#!/usr/bin/env python3
"""Test if trimesh import works after fix"""

def test_trimesh_import():
    try:
        import trimesh
        print("✅ trimesh imports successfully")
        
        # Test basic functionality
        box = trimesh.primitives.Box(extents=[1, 1, 1])
        print(f"✅ Created test box: {box}")
        
        # Test the specific function that was broken
        if hasattr(trimesh.util, 'has_module'):
            print("✅ has_module function exists")
        else:
            print("❌ has_module still missing")
            
        return True
        
    except Exception as e:
        print(f"❌ trimesh import still broken: {e}")
        return False

if __name__ == "__main__":
    test_trimesh_import()