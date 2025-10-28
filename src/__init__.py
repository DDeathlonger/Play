"""
Spaceship Designer - Source Package
Core application modules and utilities
"""

from .spaceship_designer import OptimizedSpaceshipApp, main
from .spaceship_utils import SpaceshipModule, MeshUtils, ConfigUtils, PerformanceUtils
from .spaceship_advanced import SpaceshipViewer as LegacyViewer

__version__ = "2.0.0"
__author__ = "Spaceship Designer Team"

__all__ = [
    'OptimizedSpaceshipApp',
    'main', 
    'SpaceshipModule',
    'MeshUtils',
    'ConfigUtils', 
    'PerformanceUtils',
    'LegacyViewer'
]