#!/usr/bin/env python3
"""
SPACESHIP DESIGNER - UNIFIED ENTRY POINT
Redirects to the designated spaceship.py entry point as per copilot instructions
"""

import sys
import os
from pathlib import Path

def main():
    """Redirect to the designated spaceship.py entry point"""
    print("� SPACESHIP DESIGNER - UNIFIED ENTRY POINT")
    print("=" * 50)
    print("Redirecting to designated entry point: spaceship.py")
    print("=" * 50)
    
    # Import and run spaceship.py main function
    try:
        current_dir = Path(__file__).parent
        spaceship_path = current_dir / "spaceship.py"
        
        if not spaceship_path.exists():
            print("❌ spaceship.py not found!")
            return 1
        
        # Import spaceship geometry node and run its main
        sys.path.insert(0, str(current_dir))
        import spaceship
        return spaceship.main()
        
    except Exception as e:
        print(f"❌ Failed to launch spaceship.py: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())