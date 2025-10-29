#!/usr/bin/env python3
"""
Simple pytest verification test
"""
import pytest
import sys
import os

def test_pytest_basic_functionality():
    """Test that pytest can run basic assertions"""
    assert True
    assert 1 + 1 == 2
    assert "hello" == "hello"

def test_python_version():
    """Test Python version compatibility"""
    assert sys.version_info.major == 3
    assert sys.version_info.minor >= 8  # Require Python 3.8+

def test_imports_work():
    """Test that basic imports work in pytest context"""
    import numpy as np
    import trimesh
    
    # Test numpy
    arr = np.array([1, 2, 3])
    assert len(arr) == 3
    
    # Test trimesh
    box = trimesh.primitives.Box(extents=[1, 1, 1])
    assert box is not None

@pytest.mark.unit
def test_with_marker():
    """🎯 Test that pytest markers work"""
    assert True

@pytest.mark.integration  
def test_spaceship_integration():
    """🔗 Test basic spaceship integration"""
    # Test that our core modules can be imported together
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))
    
    from spaceship_utils import SpaceshipGeometryNode
    node = SpaceshipGeometryNode("cylinder", 0.5, 1.0, [255, 0, 0])
    assert node.type == "cylinder"
    
@pytest.mark.slow
def test_slow_operation():
    """🐌 Test a slow operation (simulated)"""
    import time
    time.sleep(0.1)  # Simulate slow operation
    assert True

if __name__ == "__main__":
    # Allow running this test file directly
    pytest.main([__file__, "-v"])