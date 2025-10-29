#!/usr/bin/env python3
"""
Test script to isolate trimesh import issue
"""

def test_basic_python_imports():
    """Test basic Python imports that should always work"""
    print("Testing basic imports...")
    
    try:
        import sys
        print("✅ sys imported successfully")
    except Exception as e:
        print(f"❌ sys failed: {e}")
        return False
    
    try:
        import os
        print("✅ os imported successfully")
    except Exception as e:
        print(f"❌ os failed: {e}")
        return False
    
    try:
        import numpy
        print(f"✅ numpy imported successfully (version: {numpy.__version__})")
    except Exception as e:
        print(f"❌ numpy failed: {e}")
        return False
    
    return True

def test_trimesh_step_by_step():
    """Test trimesh import step by step to find where it fails"""
    print("\nTesting trimesh imports step by step...")
    
    # Step 1: Try basic trimesh import
    try:
        import trimesh
        print("✅ Basic trimesh import succeeded")
    except Exception as e:
        print(f"❌ Basic trimesh import failed: {e}")
        return False
    
    # Step 2: Check trimesh version and location
    try:
        print(f"✅ trimesh version: {trimesh.__version__}")
        print(f"✅ trimesh location: {trimesh.__file__}")
    except Exception as e:
        print(f"❌ trimesh version/location check failed: {e}")
    
    # Step 3: Test trimesh.util specifically
    try:
        import trimesh.util
        print("✅ trimesh.util imported successfully")
        print(f"✅ trimesh.util attributes: {dir(trimesh.util)}")
    except Exception as e:
        print(f"❌ trimesh.util import failed: {e}")
        return False
    
    # Step 4: Check for has_module function specifically
    try:
        if hasattr(trimesh.util, 'has_module'):
            print("✅ trimesh.util.has_module exists")
        else:
            print("⚠️  trimesh.util.has_module does NOT exist")
            print("Available functions:")
            for attr in dir(trimesh.util):
                if not attr.startswith('_'):
                    print(f"  - {attr}")
    except Exception as e:
        print(f"❌ Error checking has_module: {e}")
    
    # Step 5: Try creating a simple primitive
    try:
        mesh = trimesh.primitives.Box(extents=[1, 1, 1])
        print(f"✅ Created simple box mesh: {mesh}")
    except Exception as e:
        print(f"❌ Failed to create simple mesh: {e}")
        return False
    
    return True

def test_alternative_import_methods():
    """Test alternative ways to import trimesh functionality"""
    print("\nTesting alternative import methods...")
    
    # Method 1: Import specific modules
    try:
        from trimesh import primitives
        print("✅ trimesh.primitives imported successfully")
        
        box = primitives.Box(extents=[1, 1, 1])
        print(f"✅ Created box with primitives: {box}")
    except Exception as e:
        print(f"❌ trimesh.primitives import failed: {e}")
    
    # Method 2: Import Trimesh class directly
    try:
        from trimesh.base import Trimesh
        print("✅ Trimesh class imported successfully")
        
        # Create empty mesh
        empty_mesh = Trimesh()
        print(f"✅ Created empty mesh: {empty_mesh}")
    except Exception as e:
        print(f"❌ Direct Trimesh class import failed: {e}")
    
    # Method 3: Check what's actually broken in the chain
    try:
        import trimesh.exchange
        print("✅ trimesh.exchange imported")
    except Exception as e:
        print(f"❌ trimesh.exchange failed: {e}")
    
    try:
        import trimesh.creation
        print("✅ trimesh.creation imported")
    except Exception as e:
        print(f"❌ trimesh.creation failed: {e}")

def main():
    """Run all tests to identify the exact issue"""
    print("🔍 TRIMESH IMPORT DIAGNOSTIC")
    print("=" * 40)
    
    # Test 1: Basic imports
    if not test_basic_python_imports():
        print("❌ Basic imports failed - environment issue")
        return 1
    
    # Test 2: Trimesh step by step
    if not test_trimesh_step_by_step():
        print("❌ Trimesh import failed - investigating alternatives")
        test_alternative_import_methods()
        return 1
    
    # Test 3: If we get here, trimesh works
    print("\n✅ All trimesh tests passed!")
    print("The issue might be in how the main application imports or uses trimesh")
    return 0

if __name__ == "__main__":
    exit_code = main()
    print(f"\nTest completed with exit code: {exit_code}")
    exit(exit_code)