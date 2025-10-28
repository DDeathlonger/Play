#!/usr/bin/env python3
"""
Spaceship Designer Demo
Generates several example spaceships and exports them as 3D models
"""

import sys
import os
from spaceship_advanced import SpaceshipGenerator, SpaceshipModule

def create_simple_fighter():
    """Create a simple fighter-style spaceship"""
    print("Creating simple fighter spaceship...")
    
    generator = SpaceshipGenerator((6, 3, 8))  # Smaller, focused design
    
    # Customize some modules for a fighter look
    for (x, y, z), module in generator.grid.items():
        if z < 2:  # Engine area - make engines more prominent
            module.type = "cylinder"
            module.radius *= 1.2
            module.color = [255, 100, 50]  # Orange engines
        elif z > 6:  # Nose - make it sharp
            module.type = "cone"
            module.radius *= 0.8
            module.color = [100, 100, 150]  # Blue nose
        elif abs(x - 3) < 1 and y == 1:  # Central fuselage
            module.type = "box"
            module.radius *= 1.3
            module.color = [150, 150, 160]  # Gray hull
    
    return generator

def create_bulky_cruiser():
    """Create a bulky cruiser-style spaceship"""
    print("Creating bulky cruiser spaceship...")
    
    generator = SpaceshipGenerator((8, 5, 10))  # Larger, bulkier design
    
    # Customize for cruiser look
    for (x, y, z), module in generator.grid.items():
        if 2 < z < 8:  # Main body - make it bulky
            module.type = "box"
            module.radius *= 1.4
            module.height *= 1.2
            module.color = [80, 120, 160]  # Dark blue hull
        elif z < 2:  # Engines - multiple large engines
            module.type = "cylinder"
            module.radius *= 1.5
            module.color = [200, 80, 80]  # Red engines
    
    return generator

def create_sleek_racer():
    """Create a sleek racing spaceship"""
    print("Creating sleek racer spaceship...")
    
    generator = SpaceshipGenerator((4, 3, 12))  # Long and narrow
    
    # Customize for racing look
    for (x, y, z), module in generator.grid.items():
        # Make it streamlined
        module.type = "wedge" if z > 8 else "cylinder"
        module.radius *= 0.8  # Make it slimmer
        module.height *= 0.9
        
        if z < 3:  # Racing engines
            module.color = [100, 255, 100]  # Green engines
        else:
            module.color = [200, 200, 220]  # Silver body

    return generator

def generate_and_export_ships():
    """Generate example spaceships and export them"""
    print("=" * 60)
    print("Spaceship Designer Demo - Generating Example Ships")
    print("=" * 60)
    
    ships = [
        ("fighter", create_simple_fighter),
        ("cruiser", create_bulky_cruiser), 
        ("racer", create_sleek_racer)
    ]
    
    for ship_name, create_func in ships:
        print(f"\n--- {ship_name.upper()} SPACESHIP ---")
        
        try:
            # Generate the ship
            generator = create_func()
            mesh = generator.generate_mesh()
            
            print(f"✓ Generated {ship_name}: {len(mesh.vertices)} vertices, {len(mesh.faces)} faces")
            
            # Export in multiple formats
            formats = ["stl", "glb", "obj"]
            for fmt in formats:
                filename = f"{ship_name}_spaceship.{fmt}"
                try:
                    mesh.export(filename)
                    file_size = os.path.getsize(filename) / 1024  # KB
                    print(f"✓ Exported {filename} ({file_size:.1f} KB)")
                except Exception as e:
                    print(f"✗ Failed to export {filename}: {e}")
            
            # Generate reference image
            try:
                ref_path = generator.generate_reference_image()
                if ref_path:
                    # Rename to be specific to this ship
                    new_ref_path = f"{ship_name}_reference.png"
                    if os.path.exists(ref_path):
                        os.rename(ref_path, new_ref_path)
                        print(f"✓ Generated reference image: {new_ref_path}")
            except Exception as e:
                print(f"✗ Reference image failed: {e}")
            
            # Save configuration
            config_path = f"{ship_name}_config.json"
            generator.save_configuration(config_path)
            print(f"✓ Saved configuration: {config_path}")
            
        except Exception as e:
            print(f"✗ Failed to generate {ship_name}: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("Demo completed! Generated files:")
    print("=" * 60)
    
    # List all generated files
    demo_files = []
    for file in os.listdir("."):
        if any(ship in file for ship, _ in ships):
            size = os.path.getsize(file) / 1024  # KB
            demo_files.append((file, size))
    
    for filename, size in sorted(demo_files):
        print(f"  {filename:<25} ({size:.1f} KB)")
    
    print(f"\nTotal files generated: {len(demo_files)}")

def show_usage_examples():
    """Show examples of how to use the spaceship designer programmatically"""
    print("\n" + "=" * 60)
    print("USAGE EXAMPLES")
    print("=" * 60)
    
    print("""
# Basic Usage:
from spaceship_advanced import SpaceshipGenerator

# Create a generator with default settings
generator = SpaceshipGenerator()

# Generate the 3D mesh
mesh = generator.generate_mesh()

# Export to different formats
mesh.export("my_spaceship.stl")      # For 3D printing
mesh.export("my_spaceship.glb")      # For web/games
mesh.export("my_spaceship.obj")      # For general use

# Save/load configurations
generator.save_configuration("my_design.json")
generator.load_configuration("my_design.json")

# Generate reference images
generator.generate_reference_image()

# Customize individual modules
for position, module in generator.grid.items():
    x, y, z = position
    if z < 2:  # Engine area
        module.type = "cylinder"
        module.color = [255, 0, 0]  # Red engines
        module.radius *= 1.5

# Custom grid sizes
small_ship = SpaceshipGenerator((4, 3, 6))
large_ship = SpaceshipGenerator((12, 7, 16))
""")

if __name__ == "__main__":
    generate_and_export_ships()
    show_usage_examples()
    
    print("\n" + "=" * 60)
    print("Ready for development!")
    print("Run: python spaceship_advanced.py")
    print("=" * 60)
