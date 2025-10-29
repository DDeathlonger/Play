#!/usr/bin/env python3
"""
SPACESHIP DESIGNER - SIMPLE LAUNCHER
Launches the working spaceship designer application
"""

import sys
import os
from pathlib import Path

def main():
    """Launch the spaceship designer"""
    
    print("🚀 SPACESHIP DESIGNER")
    print("=" * 40)
    print("3D Spaceship Modeling Application")
    print("=" * 40)
    
    # Add src to path
    current_dir = Path(__file__).parent
    src_path = current_dir / "src"
    sys.path.insert(0, str(src_path))
    
    # Check dependencies
    try:
        import PyQt6
        import OpenGL
        import trimesh
        import numpy
        print("✅ All dependencies available")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Install with: pip install PyQt6 PyOpenGL trimesh numpy")
        return 1
    
    print("\n🎯 Launching application...")
    
    try:
        # Try advanced version (known working)
        print("Loading advanced spaceship designer...")
        from spaceship_advanced import main as advanced_main
        print("✅ Advanced version loaded")
        return advanced_main()
        
    except ImportError as e:
        print(f"❌ Failed to load spaceship designer: {e}")
        print("Make sure you're running from the correct directory")
        return 1
    
    except Exception as e:
        print(f"❌ Application error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())