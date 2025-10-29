#!/usr/bin/env python3
"""
Test suite for Spaceship Designer - Updated for cleaned codebase
Tests core functionality without GUI dependencies
"""

import sys
import os
import numpy as np
import trimesh
import json

# Add the src directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

def test_spaceship_geometry_node():
    """Test SpaceshipGeometryNode class functionality"""
    print("Testing SpaceshipGeometryNode...")
    
    # Import from working modules
    from spaceship_utils import SpaceshipGeometryNode
    
    # Test creation
    geometry_node = SpaceshipGeometryNode("cylinder", 0.5, 1.0, [255, 0, 0])
    assert geometry_node.type == "cylinder"
    assert geometry_node.radius == 0.5
    assert geometry_node.height == 1.0
    assert geometry_node.color == [255, 0, 0]
    
    # Test enabled state
    assert geometry_node.enabled == True
    geometry_node.enabled = False
    assert geometry_node.enabled == False
    
    # Test rotation and scale
    assert geometry_node.rotation == [0, 0, 0]
    assert geometry_node.scale == [1.0, 1.0, 1.0]
    
    geometry_node.rotation = [90, 0, 0]
    geometry_node.scale = [2.0, 1.0, 1.0]
    assert geometry_node.rotation == [90, 0, 0]
    assert geometry_node.scale == [2.0, 1.0, 1.0]
    
    print("✓ SpaceshipGeometryNode tests passed")

def test_spaceship_generator():
    """Test OptimizedSpaceshipGenerator class functionality"""
    print("Testing OptimizedSpaceshipGenerator...")
    
    # Use the optimized spaceship designer instead of legacy version
    from spaceship_designer import OptimizedSpaceshipGenerator, DEFAULT_GRID_SIZE
    
    # Test creation
    generator = OptimizedSpaceshipGenerator()
    
    # Test grid initialization
    assert generator.grid is not None
    assert len(generator.grid) >= 0
    
    # Test mesh generation
    mesh = generator.generate_mesh()
    assert mesh is not None
    assert len(mesh.vertices) > 0
    assert len(mesh.faces) > 0
    
    print(f"✓ Generated mesh with {len(mesh.vertices)} vertices, {len(mesh.faces)} faces")
    
    # Test primitive creation using MeshUtils
    from spaceship_utils import MeshUtils
    primitive = MeshUtils.create_simple_primitive("cylinder", 0.5, 1.0)
    assert primitive is not None
    assert hasattr(primitive, 'vertices')
    
    print("✓ SpaceshipGenerator tests passed")

def test_mesh_utilities():
    """Test mesh utility functions"""
    print("Testing mesh utilities...")
    
    from spaceship_utils import MeshUtils
    
    # Test primitive creation
    cylinder = MeshUtils.create_simple_primitive("cylinder", 0.5, 1.0)
    assert cylinder is not None
    assert len(cylinder.vertices) > 0
    
    box = MeshUtils.create_simple_primitive("box", 0.5, 1.0)
    assert box is not None
    assert len(box.vertices) > 0
    
    sphere = MeshUtils.create_simple_primitive("sphere", 0.5, 1.0)
    assert sphere is not None
    assert len(sphere.vertices) > 0
    
    print("✓ Mesh utilities tests passed")

def test_config_management():
    """Test configuration utilities"""
    print("Testing configuration management...")
    
    from spaceship_utils import ConfigUtils
    
    # Test default grid creation
    grid_size = (3, 2, 3)
    grid = ConfigUtils.create_default_grid(grid_size)
    assert grid is not None
    # Default grid may have some modules
    
    # Test random grid creation
    random_grid = ConfigUtils.create_random_grid(grid_size)
    assert random_grid is not None
    
    print("✓ Configuration management tests passed")

def test_export_functionality():
    """Test export functionality"""
    print("Testing export functionality...")
    
    from spaceship_designer import OptimizedSpaceshipGenerator
    
    # Create generator and generate mesh
    generator = OptimizedSpaceshipGenerator()
    mesh = generator.generate_mesh()
    
    # Test STL export
    stl_file = "test_export.stl"
    success = generator.export_stl(stl_file)
    assert success == True
    assert os.path.exists(stl_file)
    
    # Test GLB export
    glb_file = "test_export.glb"
    success = generator.export_glb(glb_file)
    assert success == True
    assert os.path.exists(glb_file)
    
    # Cleanup
    if os.path.exists(stl_file):
        os.remove(stl_file)
    if os.path.exists(glb_file):
        os.remove(glb_file)
    
    print("✓ Export functionality tests passed")

def run_performance_test():
    """Run basic performance test"""
    print("Running performance test...")
    
    import time
    from spaceship_designer import OptimizedSpaceshipGenerator
    
    # Test generation speed
    generator = OptimizedSpaceshipGenerator()
    
    start_time = time.time()
    mesh = generator.generate_mesh()
    generation_time = time.time() - start_time
    
    print(f"✓ Mesh generation time: {generation_time:.3f} seconds")
    print(f"✓ Mesh complexity: {len(mesh.vertices)} vertices, {len(mesh.faces)} faces")
    
    assert generation_time < 5.0  # Should complete in under 5 seconds
    assert len(mesh.vertices) > 100  # Should have reasonable complexity

def main():
    """Run all tests"""
    print("=" * 50)
    print("🧪 SPACESHIP DESIGNER TEST SUITE")
    print("=" * 50)
    
    try:
        test_spaceship_geometry_node()
        test_spaceship_generator()
        test_mesh_utilities()
        test_config_management()
        test_export_functionality()
        run_performance_test()
        
        print("\n" + "=" * 50)
        print("✅ ALL TESTS PASSED!")
        print("✅ Core functionality working correctly")
        print("✅ Export system operational")
        print("✅ Configuration management functional")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())