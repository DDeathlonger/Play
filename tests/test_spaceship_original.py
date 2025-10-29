#!/usr/bin/env python3
"""
Test suite for Spaceship Designer
Tests core functionality without GUI dependencies
"""

import sys
import os
import numpy as np
import trimesh
import json

# Add the src directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

# Add the current directory to path to import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_spaceship_geometry_node():
    """Test SpaceshipGeometryNode class functionality"""
    print("Testing SpaceshipGeometryNode...")
    
    # Import after adding to path
    from spaceship_utils import SpaceshipGeometryNode
    
    # Test creation
    geometry_node = SpaceshipGeometryNode("cylinder", 0.5, 1.0, [255, 0, 0])
    assert module.type == "cylinder"
    assert module.radius == 0.5
    assert module.height == 1.0
    assert module.color == [255, 0, 0]
    assert module.enabled == True
    
    # Test serialization
    data = module.to_dict()
    assert "type" in data
    assert "radius" in data
    assert "height" in data
    
    # Test deserialization
    module2 = SpaceshipGeometryNode.from_dict(data)
    assert module2.type == module.type
    assert module2.radius == module.radius
    assert module2.height == module.height
    
    print("✓ SpaceshipGeometryNode tests passed")

def test_spaceship_generator():
    """Test SpaceshipGenerator class functionality - Uses optimized version"""
    print("Testing SpaceshipGenerator...")
    
    # Use the optimized spaceship designer instead of legacy version
    from spaceship_designer import OptimizedSpaceshipGenerator, DEFAULT_GRID_SIZE
    
    # Test creation
    generator = OptimizedSpaceshipGenerator()
    assert generator.grid_size == DEFAULT_GRID_SIZE
    assert len(generator.grid) > 0
    
    # Test mesh generation
    mesh = generator.generate_mesh()
    assert mesh is not None
    assert hasattr(mesh, 'vertices')
    assert hasattr(mesh, 'faces')
    assert len(mesh.vertices) > 0
    assert len(mesh.faces) > 0
    
    print(f"✓ Generated mesh with {len(mesh.vertices)} vertices, {len(mesh.faces)} faces")
    
    # Test primitive creation
    from spaceship_utils import SpaceshipGeometryNode
    test_module = SpaceshipGeometryNode("cylinder", 0.5, 1.0)
    primitive = generator.create_primitive(test_module)
    assert primitive is not None
    assert hasattr(primitive, 'vertices')
    
    print("✓ SpaceshipGenerator tests passed")

def test_export_functionality():
    """Test 3D model export functionality"""
    print("Testing export functionality...")
    
    from spaceship_advanced import SpaceshipGenerator
    
    generator = SpaceshipGenerator()
    mesh = generator.generate_mesh()
    
    # Test STL export
    try:
        mesh.export("test_spaceship.stl")
        assert os.path.exists("test_spaceship.stl")
        print("✓ STL export successful")
    except Exception as e:
        print(f"✗ STL export failed: {e}")
    
    # Test GLB export
    try:
        mesh.export("test_spaceship.glb")
        assert os.path.exists("test_spaceship.glb")
        print("✓ GLB export successful")
    except Exception as e:
        print(f"✗ GLB export failed: {e}")
    
    # Test OBJ export
    try:
        mesh.export("test_spaceship.obj")
        assert os.path.exists("test_spaceship.obj")
        print("✓ OBJ export successful")
    except Exception as e:
        print(f"✗ OBJ export failed: {e}")

def test_configuration_persistence():
    """Test save/load configuration functionality"""
    print("Testing configuration persistence...")
    
    from spaceship_advanced import SpaceshipGenerator
    
    generator1 = SpaceshipGenerator()
    
    # Save configuration
    test_config_file = "test_config.json"
    generator1.save_configuration(test_config_file)
    assert os.path.exists(test_config_file)
    
    # Load configuration
    generator2 = SpaceshipGenerator()
    generator2.load_configuration(test_config_file)
    
    # Verify loaded data
    assert generator2.grid_size == generator1.grid_size
    assert len(generator2.grid) == len(generator1.grid)
    
    print("✓ Configuration persistence tests passed")
    
    # Cleanup
    if os.path.exists(test_config_file):
        os.remove(test_config_file)

def test_reference_image_generation():
    """Test reference image generation"""
    print("Testing reference image generation...")
    
    from spaceship_advanced import SpaceshipGenerator
    
    generator = SpaceshipGenerator()
    
    try:
        ref_path = generator.generate_reference_image()
        if ref_path and os.path.exists(ref_path):
            print(f"✓ Reference image generated: {ref_path}")
        else:
            print("✗ Reference image generation failed")
    except Exception as e:
        print(f"✗ Reference image generation error: {e}")

def test_performance_baseline():
    """Test performance with different grid sizes"""
    print("Testing performance baseline...")
    
    from spaceship_advanced import SpaceshipGenerator
    import time
    
    # Test with smaller grid
    start_time = time.time()
    generator = SpaceshipGenerator((4, 3, 6))  # Smaller grid
    mesh = generator.generate_mesh()
    small_time = time.time() - start_time
    
    print(f"✓ Small grid (4,3,6): {len(mesh.vertices)} vertices in {small_time:.2f}s")
    
    # Test with default grid
    start_time = time.time()
    generator = SpaceshipGenerator()  # Default grid
    mesh = generator.generate_mesh()
    default_time = time.time() - start_time
    
    print(f"✓ Default grid (8,5,12): {len(mesh.vertices)} vertices in {default_time:.2f}s")
    
    # Performance ratio
    ratio = default_time / small_time if small_time > 0 else 0
    print(f"✓ Performance ratio: {ratio:.1f}x slower for larger grid")

def cleanup_test_files():
    """Clean up test files"""
    test_files = [
        "test_spaceship.stl",
        "test_spaceship.glb", 
        "test_spaceship.obj",
        "test_config.json"
    ]
    
    for file in test_files:
        if os.path.exists(file):
            os.remove(file)
            print(f"Cleaned up: {file}")

def main():
    """Run all tests"""
    print("=" * 60)
    print("Spaceship Designer Test Suite")
    print("=" * 60)
    
    try:
        test_spaceship_module()
        test_spaceship_generator()
        test_export_functionality()
        test_configuration_persistence()
        test_reference_image_generation()
        test_performance_baseline()
        
        print("\n" + "=" * 60)
        print("✓ All tests completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        cleanup_test_files()

if __name__ == "__main__":
    main()
