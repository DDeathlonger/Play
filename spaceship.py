#!/usr/bin/env python3
"""
SPACESHIP DESIGNER - CLEAN LAUNCH
Simple launcher for the working spaceship designer application
"""

import sys
import os
from pathlib import Path

def main():
    """Launch the working spaceship designer"""
    
    print("🚀 SPACESHIP DESIGNER")
    print("=" * 30)
    
    # Add src to path
    current_dir = Path(__file__).parent
    src_path = current_dir / "src"
    sys.path.insert(0, str(src_path))
    
    try:
        # Launch the MCP-integrated version first
        os.chdir(src_path)
        from spaceship_designer import main as spaceship_main
        
        print("✅ Loading MCP-integrated spaceship designer...")
        return spaceship_main()
        
    except Exception as e:
        print(f"MCP version failed: {e}")
        print("Falling back to basic version...")
        
        try:
            from spaceship_advanced import main as advanced_main
            return advanced_main()
        except Exception as e2:
            print(f"Error: {e2}")
            print("\nTry running directly:")
            print("cd src && python spaceship_designer.py")
            return 1

if __name__ == "__main__":
    sys.exit(main())