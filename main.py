#!/usr/bin/env python3
"""
Spaceship Designer - Main Entry Point
Organized project structure with proper imports
"""

import sys
import os

# Add src directory to Python path for imports
src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

def main():
    """Main application entry point"""
    try:
        # Change to src directory for relative imports to work
        os.chdir(src_dir)
        
        # Import and run the optimized spaceship designer
        import spaceship_designer
        return spaceship_designer.main()
    except ImportError as e:
        print(f"Import error: {e}")
        print("Make sure all dependencies are installed: pip install -r requirements.txt")
        print("Current Python path:")
        for path in sys.path:
            print(f"  {path}")
        return 1
    except Exception as e:
        print(f"Application error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())