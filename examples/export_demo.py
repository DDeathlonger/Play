#!/usr/bin/env python3
"""
Simple Spaceship Export Demo
Creates a spaceship and exports it to various formats without GUI
"""

import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

def main():
    try:
        # Import our spaceship generator
        from spaceship_designer import OptimizedSpaceshipGenerator
        
        print("=" * 50)
        print("Simple Spaceship Export Demo")
        print("=" * 50)
        
        # Create a spaceship generator
        print("Creating spaceship generator...")
        generator = OptimizedSpaceshipGenerator()
        
        # Generate the mesh
        print("Generating 3D mesh...")
        mesh = generator.generate_mesh()
        
        print(f"Generated spaceship: {len(mesh.vertices)} vertices, {len(mesh.faces)} faces")
        
        # Export to different formats
        exports = [
            ("demo_spaceship.stl", "STL format (3D printing)"),
            ("demo_spaceship.glb", "GLB format (web/games)"), 
            ("demo_spaceship.obj", "OBJ format (general use)")
        ]
        
        print("\nExporting spaceship...")
        for filename, description in exports:
            try:
                mesh.export(filename)
                file_size = os.path.getsize(filename) / 1024  # KB
                print(f"✓ {filename:<20} - {description} ({file_size:.1f} KB)")
            except Exception as e:
                print(f"✗ Failed to export {filename}: {e}")
        
        # Generate reference image
        print("\nGenerating reference image...")
        try:
            ref_path = generator.generate_reference_image()
            if ref_path and os.path.exists(ref_path):
                # Rename to demo-specific name
                os.rename(ref_path, "demo_spaceship_reference.png")
                print("✓ Reference image: demo_spaceship_reference.png")
        except Exception as e:
            print(f"✗ Reference image failed: {e}")
        
        # Save configuration
        print("\nSaving configuration...")
        try:
            generator.save_configuration("demo_spaceship_config.json")
            print("✓ Configuration saved: demo_spaceship_config.json")
        except Exception as e:
            print(f"✗ Configuration save failed: {e}")
        
        print("\n" + "=" * 50)
        print("Demo completed successfully!")
        print("Files generated:")
        
        # List generated files
        demo_files = [f for f in os.listdir(".") if f.startswith("demo_spaceship")]
        for filename in sorted(demo_files):
            if os.path.isfile(filename):
                size = os.path.getsize(filename) / 1024
                print(f"  {filename:<30} ({size:.1f} KB)")
        
        print("\nYou can now:")
        print("- Open STL files in 3D printing software")
        print("- Load GLB files in web browsers or game engines")  
        print("- Import OBJ files into 3D modeling software")
        print("- View the reference PNG image")
        print("- Load the JSON config in the main application")
        
        return True
        
    except ImportError as e:
        print(f"Import error: {e}")
        print("Make sure all dependencies are installed:")
        print("pip install numpy trimesh PyQt6 PyOpenGL matplotlib")
        return False
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🚀 Ready for development!")
        print("Run 'python spaceship_advanced.py' for the full GUI application")
    else:
        print("\n❌ Demo failed - check error messages above")
    
    sys.exit(0 if success else 1)
