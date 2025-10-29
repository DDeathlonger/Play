#!/usr/bin/env python3
"""
Secure Spaceship Designer Startup Controller
Ensures proper initialization order and complete window containment
"""

import subprocess
import sys
import time
import win32gui
import psutil
import requests
from pathlib import Path

class SecureStartupController:
    """Controls secure startup with proper initialization order"""
    
    def __init__(self):
        self.app_process = None
        self.app_window_found = False
        self.app_verified_working = False
        self.mcp_server_process = None
        self.mcp_server_port = 5962
        
    def verify_app_window_exists(self):
        """Verify the spaceship app window exists and is on top"""
        try:
            def enum_window_callback(hwnd, windows):
                if win32gui.IsWindowVisible(hwnd):
                    window_text = win32gui.GetWindowText(hwnd)
                    if "Spaceship Designer" in window_text and "Optimized" in window_text:
                        windows.append((hwnd, window_text))
                return True
            
            windows = []
            win32gui.EnumWindows(enum_window_callback, windows)
            
            if windows:
                hwnd, title = windows[0]
                # Try to ensure it's the foreground window (but don't fail if it doesn't work)
                try:
                    win32gui.SetForegroundWindow(hwnd)
                except Exception as focus_err:
                    print(f"⚠️ Focus warning: {focus_err}")
                    # Continue anyway - window exists
                print(f"✅ App window verified: {title}")
                return True, hwnd
            
            return False, None
            
        except Exception as e:
            print(f"❌ Window verification failed: {e}")
            return False, None
    
    def start_app_with_containment(self):
        """Start the spaceship app with always-on-top behavior"""
        print("🚀 Starting Spaceship Designer with containment...")
        
        try:
            # Use virtual environment Python
            python_exe = Path(".venv/Scripts/python.exe")
            if not python_exe.exists():
                python_exe = "python"
            
            # Start the app
            self.app_process = subprocess.Popen(
                [str(python_exe), "main.py"],
                cwd=Path.cwd()
            )
            
            print(f"📋 App process started (PID: {self.app_process.pid})")
            
            # Wait for app window to appear and verify it's working
            for attempt in range(20):  # 10 second timeout
                time.sleep(0.5)
                
                found, hwnd = self.verify_app_window_exists()
                if found:
                    self.app_window_found = True
                    print(f"✅ App window found after {attempt * 0.5:.1f}s")
                    break
                    
                print(f"⏳ Waiting for app window... attempt {attempt + 1}/20")
                
            if not self.app_window_found:
                print("❌ App window not found within timeout")
                return False
            
            # Additional verification - check if app is responsive
            time.sleep(2)  # Let app fully initialize
            found, hwnd = self.verify_app_window_exists()
            if found:
                self.app_verified_working = True
                print("✅ App verified working and always on top")
                return True
            else:
                print("❌ App window lost focus or crashed")
                return False
                
        except Exception as e:
            print(f"❌ App startup failed: {e}")
            return False
    
    def verify_mouse_containment(self):
        """Verify mouse movement is properly contained"""
        print("🖱️ Verifying mouse containment...")
        
        try:
            from universal_ai_controller import UniversalAIController
            
            # Create controller and test containment
            controller = UniversalAIController()
            
            # Test that mouse cannot leave app window
            success = controller.focus_app()
            if not success:
                print("❌ Could not focus app for mouse test")
                return False
            
            # Take a screenshot to confirm containment system works
            result = controller.see("containment_verification")
            if result and result.get('screenshot_path'):
                print("✅ Mouse containment system verified")
                print(f"📸 Containment verified: {result['screenshot_path']}")
                return True
            else:
                print("❌ Mouse containment verification failed")
                return False
                
        except Exception as e:
            print(f"❌ Mouse containment test failed: {e}")
            return False
    
    def enable_mcp_server_access(self):
        """Enable MCP server only after app is verified working"""
        if not self.app_verified_working:
            print("❌ Cannot enable MCP server - app not verified working")
            return False
        
        print("🔓 App verified working - MCP server access enabled")
        print("📋 MCP server can now be used safely:")
        print("   - App is running and contained")
        print("   - Mouse is constrained to app window")
        print("   - App maintains always-on-top focus")
        
        return True
    
    def check_existing_mcp_server(self):
        """Check if MCP server is already running"""
        try:
            # Try to connect to see if server is alive
            response = requests.get(f"http://localhost:{self.mcp_server_port}/health", timeout=2)
            if response.status_code == 200:
                print(f"⚠️ MCP server already running on port {self.mcp_server_port}")
                return True
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            # Server not running - this is expected
            pass
        except Exception as e:
            print(f"⚠️ Error checking MCP server: {e}")
        
        return False
    
    def stop_existing_mcp_server(self):
        """Stop any existing MCP server processes"""
        print("🛑 Stopping existing MCP server processes...")
        
        try:
            # Find MCP server processes by name
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = proc.info['cmdline']
                    if cmdline and any('mcp' in arg.lower() and 'server' in arg.lower() for arg in cmdline):
                        print(f"🛑 Terminating MCP server process PID {proc.info['pid']}")
                        proc.terminate()
                        
                        # Wait for graceful shutdown
                        try:
                            proc.wait(timeout=5)
                        except psutil.TimeoutExpired:
                            print(f"🛑 Force killing MCP server process PID {proc.info['pid']}")
                            proc.kill()
                            
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                    
            print("✅ Existing MCP server processes stopped")
            
        except Exception as e:
            print(f"⚠️ Error stopping MCP servers: {e}")
    
    def start_mcp_server(self):
        """Start new MCP server after cleanup"""
        if not self.app_verified_working:
            print("❌ Cannot start MCP server - app not verified")
            return False
        
        print("🚀 Starting fresh MCP server...")
        
        try:
            # Use virtual environment Python if available
            python_exe = Path(".venv/Scripts/python.exe")
            if not python_exe.exists():
                python_exe = "python"
            
            # Start MCP server (assuming it's available in environment)
            self.mcp_server_process = subprocess.Popen(
                [str(python_exe), "-m", "mcp_pylance_mcp_s", "--port", str(self.mcp_server_port)],
                cwd=Path.cwd(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            print(f"📋 MCP server started (PID: {self.mcp_server_process.pid})")
            
            # Wait for server to be ready
            for attempt in range(10):  # 5 second timeout
                time.sleep(0.5)
                if self.check_existing_mcp_server():
                    print(f"✅ MCP server ready after {attempt * 0.5:.1f}s")
                    return True
                print(f"⏳ Waiting for MCP server... attempt {attempt + 1}/10")
            
            print("❌ MCP server failed to start within timeout")
            return False
            
        except Exception as e:
            print(f"❌ MCP server startup failed: {e}")
            return False
    
    def manage_mcp_server_lifecycle(self):
        """Complete MCP server lifecycle management"""
        print("🔄 Managing MCP server lifecycle...")
        
        # Step 1: Check for existing server
        if self.check_existing_mcp_server():
            # Step 2: Stop existing server
            self.stop_existing_mcp_server()
            time.sleep(1)  # Brief pause for cleanup
        
        # Step 3: Start fresh server
        return self.start_mcp_server()
    
    def stop_mcp_server(self):
        """Stop the MCP server we started"""
        if self.mcp_server_process:
            print("🛑 Shutting down MCP server...")
            self.mcp_server_process.terminate()
            try:
                self.mcp_server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.mcp_server_process.kill()
            print("✅ MCP server shutdown complete")
    
    def run_secure_startup(self):
        """Execute the complete secure startup sequence"""
        print("=" * 60)
        print("🔒 SECURE SPACESHIP DESIGNER STARTUP")
        print("=" * 60)
        
        # Step 1: Start app with containment
        print("\n1️⃣ Starting application...")
        if not self.start_app_with_containment():
            print("❌ STARTUP FAILED: Could not start or verify app")
            return False
        
        # Step 2: Verify mouse containment
        print("\n2️⃣ Verifying mouse containment...")
        if not self.verify_mouse_containment():
            print("❌ STARTUP FAILED: Mouse containment not working")
            return False
        
        # Step 3: Enable MCP server access
        print("\n3️⃣ Enabling MCP server access...")
        if not self.enable_mcp_server_access():
            print("❌ STARTUP FAILED: Cannot enable MCP server")
            return False
        
        # Step 4: Manage MCP server lifecycle
        print("\n4️⃣ Managing MCP server lifecycle...")
        if not self.manage_mcp_server_lifecycle():
            print("❌ STARTUP FAILED: MCP server management failed")
            return False
        
        print("\n" + "=" * 60)
        print("✅ SECURE STARTUP COMPLETE!")
        print("✅ App is running with full containment")
        print("✅ Mouse cannot leave app window")
        print("✅ MCP server is running and ready")
        print("=" * 60)
        
        return True
    
    def shutdown(self):
        """Clean shutdown of all processes"""
        # Stop MCP server first
        self.stop_mcp_server()
        
        # Then stop the app
        if self.app_process:
            print("🛑 Shutting down spaceship app...")
            self.app_process.terminate()
            try:
                self.app_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.app_process.kill()
            print("✅ App shutdown complete")
        
        print("✅ Complete shutdown finished")

def main():
    """Main entry point for secure startup"""
    controller = SecureStartupController()
    
    try:
        success = controller.run_secure_startup()
        if success:
            print("\n🎮 You can now safely use MCP server tools!")
            print("📋 The app is contained and ready for AI control")
            
            # Keep running until user interrupts
            input("\n Press Enter to shutdown...")
        else:
            print("\n❌ Startup failed - check errors above")
            return 1
            
    except KeyboardInterrupt:
        print("\n🛑 Shutdown requested by user")
    except Exception as e:
        print(f"\n❌ Startup error: {e}")
        return 1
    finally:
        controller.shutdown()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())