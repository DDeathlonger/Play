#!/usr/bin/env python3
"""
MODULAR SPACESHIP DESIGNER - MAIN ENTRY POINT
Launches the refactored modular architecture with all systems integrated
"""

import sys
from pathlib import Path

# Add src to path for imports
current_dir = Path(__file__).parent
src_path = current_dir / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

def check_dependencies():
    """Check for required dependencies"""
    print("🔍 Checking dependencies...")
    
    required_modules = [
        ("PyQt6", "PyQt6 GUI framework"),
        ("OpenGL", "OpenGL 3D graphics"),
        ("trimesh", "3D mesh processing"),
        ("numpy", "Numerical computing"),
        ("requests", "HTTP client")
    ]
    
    missing = []
    available = []
    
    for module, description in required_modules:
        try:
            __import__(module)
            available.append(f"✅ {module} - {description}")
        except ImportError:
            missing.append(f"❌ {module} - {description}")
    
    # Print results
    for msg in available:
        print(msg)
    
    if missing:
        print("\n⚠️  Missing dependencies:")
        for msg in missing:
            print(msg)
        print("\nInstall with:")
        print("pip install PyQt6 PyQt6-tools PyOpenGL PyOpenGL_accelerate trimesh numpy requests")
        return False
    
    print("✅ All dependencies available")
    return True

def show_system_info():
    """Show modular system information"""
    print("\n🏗️  MODULAR ARCHITECTURE:")
    print("├── MCP Tools Module (mcp_tools.py)")
    print("│   ├── Session management with persistence")
    print("│   ├── Conflict resolution and port management") 
    print("│   └── Command routing and performance tracking")
    print("├── Ship Generation Module (ship_generation.py)")
    print("│   ├── High-performance mesh caching")
    print("│   ├── Template-based ship architectures")
    print("│   └── Multi-format export capabilities")
    print("├── UI System Module (ui_system.py)")
    print("│   ├── PyQt6 interface components")
    print("│   ├── Event management and theming")
    print("│   └── Modular layout management")
    print("├── 3D Display Module (display_3d.py)")
    print("│   ├── OpenGL rendering optimization")
    print("│   ├── Camera controls and interaction")
    print("│   └── Display list caching for performance")
    print("└── System Integration (system_integration.py)")
    print("    ├── Event bus for inter-module communication")
    print("    ├── Module registry and lifecycle management")
    print("    └── Unified API for all subsystems")

def main():
    """Main entry point for modular spaceship designer"""
    print("🎉 MODULAR SPACESHIP DESIGNER")
    print("=" * 60)
    print("Non-destructive refactored architecture")
    print("All original functionality preserved with enhanced performance")
    print("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        return 1
    
    # Show system architecture
    show_system_info()
    
    print(f"\n🚀 LAUNCHING MODULAR APPLICATION...")
    print("=" * 60)
    
    try:
        # Import modular application
        from modular_spaceship_designer import main as modular_main
        
        print("✅ Modular systems loaded successfully")
        print("✅ Starting integrated application...")
        
        # Run the modular application
        return modular_main()
        
    except ImportError as e:
        print(f"❌ Module import error: {e}")
        print("\nFallback options:")
        print("1. Original optimized version: python src/spaceship_designer.py") 
        print("2. Advanced version: python src/spaceship_advanced.py")
        print("3. Test individual modules in src/ directory")
        return 1
    except Exception as e:
        print(f"❌ Application startup error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())