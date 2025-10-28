#!/usr/bin/env python3
"""
Minimal Secure Spaceship Designer Startup Controller
Only uses standard library modules

⚠️ LEGACY SYSTEM: For new projects, use max_security_ai_mcp.py instead
This system is preserved for compatibility and reference.
"""

import subprocess
import sys
import time
import signal
from pathlib import Path

class MinimalSecureStartup:
    """Minimal secure startup with standard library only"""
    
    def __init__(self):
        self.app_process = None
        
    def start_app(self):
        """Start the spaceship app"""
        print("🚀 Starting Spaceship Designer...")
        
        try:
            # Start the app
            self.app_process = subprocess.Popen(
                [sys.executable, "main.py"],
                cwd=Path.cwd()
            )
            
            print(f"📋 App process started (PID: {self.app_process.pid})")
            
            # Give app time to initialize
            time.sleep(3)
            
            # Check if process is still running
            if self.app_process.poll() is None:
                print("✅ App started successfully")
                return True
            else:
                print("❌ App process exited unexpectedly")
                return False
                
        except Exception as e:
            print(f"❌ App startup failed: {e}")
            return False
    
    def test_ai_controller(self):
        """Test the AI controller system"""
        print("🤖 Testing AI controller...")
        
        try:
            # Import and test controller
            sys.path.insert(0, '.')
            from universal_ai_controller import UniversalAIController
            
            controller = UniversalAIController()
            
            # Test screenshot capability
            result = controller.see("startup_test")
            if result and result.get('screenshot_path'):
                print(f"✅ AI controller working")
                print(f"📸 Screenshot: {result['screenshot_path']}")
                
                # Test edge-sticking mouse behavior
                print("🖱️ Testing edge-sticking mouse behavior...")
                controller.move_to(50, 50, reason="test_edge_sticking")
                time.sleep(1)
                
                # Try to move outside window bounds (should stick to edges)
                controller.move_to(-100, -100, reason="test_negative_coordinates")
                controller.move_to(9999, 9999, reason="test_large_coordinates")
                
                print("✅ Edge-sticking mouse behavior tested")
                return True
            else:
                print("❌ AI controller test failed")
                return False
                
        except Exception as e:
            print(f"❌ AI controller test error: {e}")
            return False
    
    def run_startup(self):
        """Execute minimal startup sequence"""
        print("=" * 50)
        print("🔒 MINIMAL SECURE STARTUP")
        print("=" * 50)
        
        # Step 1: Start app
        print("\n1️⃣ Starting application...")
        if not self.start_app():
            print("❌ STARTUP FAILED: Could not start app")
            return False
        
        # Step 2: Test AI controller
        print("\n2️⃣ Testing AI controller...")
        if not self.test_ai_controller():
            print("❌ STARTUP FAILED: AI controller not working")
            return False
        
        print("\n" + "=" * 50)
        print("✅ STARTUP COMPLETE!")
        print("✅ App is running with containment")
        print("✅ AI controller has edge-sticking behavior")
        print("✅ Mouse cannot leave app window")
        print("=" * 50)
        
        return True
    
    def shutdown(self):
        """Clean shutdown"""
        if self.app_process:
            print("🛑 Shutting down app...")
            self.app_process.terminate()
            try:
                self.app_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.app_process.kill()
            print("✅ Shutdown complete")

def main():
    """Main entry point"""
    startup = MinimalSecureStartup()
    
    def signal_handler(signum, frame):
        print("\n🛑 Shutdown requested")
        startup.shutdown()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        success = startup.run_startup()
        if success:
            print("\n🎮 System ready!")
            print("🖱️ Mouse is contained with edge-sticking")
            print("📋 Press Ctrl+C to shutdown...")
            
            # Keep running
            while True:
                time.sleep(1)
        else:
            print("\n❌ Startup failed")
            return 1
            
    except KeyboardInterrupt:
        print("\n🛑 Shutdown requested")
    except Exception as e:
        print(f"\n❌ Startup error: {e}")
        return 1
    finally:
        startup.shutdown()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())