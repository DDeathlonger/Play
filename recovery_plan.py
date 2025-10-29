#!/usr/bin/env python3
"""
RECOVERY PLAN - Fix corrupted libraries from module→geometry_node replacement
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

def assess_damage():
    """Check what libraries were corrupted by the module→geometry_node replacement"""
    print("🔍 ASSESSING LIBRARY CORRUPTION")
    print("=" * 40)
    
    venv_path = Path(r"C:\Users\dante\OneDrive\Desktop\Play\.venv\Lib\site-packages")
    
    corrupted_files = []
    suspicious_patterns = [
        "has_geometry_node",  # Should be has_module
        "geometry_node_name",  # Should be module_name
        "import_geometry_node",  # Should be import_module
        "def geometry_node_",  # Should be def module_
        "geometry_node.py",  # Should be module.py
    ]
    
    print("Scanning for corruption patterns...")
    
    # Scan critical libraries
    critical_libs = ["trimesh", "numpy", "PyQt6", "requests"]
    
    for lib in critical_libs:
        lib_path = venv_path / lib
        if lib_path.exists():
            print(f"\nChecking {lib}...")
            
            for py_file in lib_path.rglob("*.py"):
                try:
                    with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    for pattern in suspicious_patterns:
                        if pattern in content:
                            corrupted_files.append((str(py_file), pattern))
                            print(f"  ❌ {py_file.name}: Found '{pattern}'")
                            break
                    
                except Exception:
                    pass  # Skip unreadable files
        else:
            print(f"  ⚠️  {lib} not found")
    
    print(f"\n📊 CORRUPTION SUMMARY")
    print(f"Found {len(corrupted_files)} corrupted files")
    
    return corrupted_files

def create_recovery_options():
    """Present recovery options from least to most destructive"""
    print("\n💡 RECOVERY OPTIONS (Least to Most Destructive)")
    print("=" * 50)
    
    print("OPTION 1: TARGETED LIBRARY REINSTALL (RECOMMENDED)")
    print("- Reinstall only affected libraries (trimesh, etc.)")
    print("- Preserves all other packages")
    print("- Quick and safe")
    
    print("\nOPTION 2: VIRTUAL ENVIRONMENT BACKUP & SELECTIVE RESTORE")
    print("- Backup current venv")
    print("- Create fresh venv")
    print("- Restore non-corrupted packages")
    print("- Reinstall corrupted ones fresh")
    
    print("\nOPTION 3: MANUAL FILE REPAIR")
    print("- Identify specific corrupted functions")
    print("- Manually fix the renamed functions")
    print("- Most targeted but time-intensive")
    
    print("\nOPTION 4: COMPLETE VENV RECREATION (NUCLEAR OPTION)")
    print("- Delete entire venv")
    print("- Recreate from scratch")
    print("- Guaranteed clean but loses all packages")

def option1_targeted_reinstall():
    """Execute Option 1: Reinstall affected libraries"""
    print("\n🔧 EXECUTING OPTION 1: TARGETED REINSTALL")
    print("=" * 40)
    
    # Libraries that are likely corrupted based on common usage
    likely_corrupted = [
        "trimesh",
        "numpy",  # If it had module-related code
        "matplotlib",  # If it was affected
        "pyglet",  # Common with trimesh
    ]
    
    venv_python = r"C:\Users\dante\OneDrive\Desktop\Play\.venv\Scripts\python.exe"
    venv_pip = r"C:\Users\dante\OneDrive\Desktop\Play\.venv\Scripts\pip.exe"
    
    print("Step 1: Check which packages are installed")
    for pkg in likely_corrupted:
        try:
            result = subprocess.run([venv_pip, "show", pkg], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                version = [line for line in result.stdout.split('\n') 
                          if line.startswith('Version:')]
                if version:
                    print(f"  ✅ {pkg}: {version[0]}")
                else:
                    print(f"  ✅ {pkg}: installed")
            else:
                print(f"  ⚠️  {pkg}: not installed")
        except Exception as e:
            print(f"  ❌ {pkg}: error checking ({e})")
    
    print("\nStep 2: Generate reinstall commands")
    print("Run these commands to fix the corruption:")
    print()
    
    for pkg in likely_corrupted:
        print(f"{venv_pip} uninstall {pkg} -y")
        print(f"{venv_pip} install {pkg}")
        print()

def option2_backup_and_restore():
    """Execute Option 2: Backup venv and selective restore"""
    print("\n🔧 OPTION 2: BACKUP AND SELECTIVE RESTORE")
    print("=" * 40)
    
    venv_path = Path(r"C:\Users\dante\OneDrive\Desktop\Play\.venv")
    backup_path = Path(r"C:\Users\dante\OneDrive\Desktop\Play\.venv_backup")
    
    print("Commands to execute this option:")
    print(f"1. Backup: copy {venv_path} {backup_path}")
    print("2. Delete current venv")
    print("3. Create new venv: python -m venv .venv")
    print("4. Reinstall packages from requirements or pip freeze")

def test_fix_effectiveness():
    """Test if the fix worked"""
    print("\n🧪 TEST SCRIPT FOR VERIFICATION")
    print("=" * 30)
    
    test_script = '''
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
'''
    
    print("Save this as test_fix.py and run after applying the fix:")
    print(test_script)

def main():
    """Main recovery workflow"""
    print("🚨 LIBRARY CORRUPTION RECOVERY TOOL")
    print("Fixing damage from module→geometry_node replacement")
    print("=" * 50)
    
    # Step 1: Assess the damage
    corrupted_files = assess_damage()
    
    # Step 2: Present options
    create_recovery_options()
    
    # Step 3: Recommended approach
    print("\n🎯 RECOMMENDED ACTION")
    print("Execute Option 1 (Targeted Reinstall) first:")
    option1_targeted_reinstall()
    
    # Step 4: Provide test
    test_fix_effectiveness()
    
    print("\n⚠️  IMPORTANT NOTES:")
    print("1. The corruption likely affected multiple libraries")
    print("2. After fixing, test the spaceship app thoroughly")
    print("3. If Option 1 doesn't work, try Option 2")
    print("4. Keep the backup until you're sure everything works")

if __name__ == "__main__":
    main()