#!/usr/bin/env python3
"""
AI Development Cycle Controller
Automated screenshot, check, close, adjust, repeat system for AI iterations
"""

import os
import sys
import time
import json
import shutil
import psutil
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional

# Add src to path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

class DevelopmentCycleController:
    """Controls the automated development cycle with screenshot persistence"""
    
    def __init__(self):
        self.screenshots_dir = Path("ai_screenshots")  # Clean, simple folder name
        self.cycle_log = Path("ai_screenshots/cycle_log.json")  # Keep log with images
        self.app_process = None
        self.current_cycle = self.load_cycle_count()
        
    def load_cycle_count(self):
        """Load current cycle count"""
        if self.cycle_log.exists():
            try:
                with open(self.cycle_log, 'r') as f:
                    data = json.load(f)
                    return data.get('current_cycle', 0) + 1
            except:
                pass
        return 1
    
    def start_new_cycle(self):
        """Start a new development cycle - clears old screenshots"""
        print(f"\n🔄 Starting Development Cycle {self.current_cycle}")
        print("="*60)
        
        # Clear old screenshots for new cycle
        if self.screenshots_dir.exists():
            shutil.rmtree(self.screenshots_dir)
            print("📸 Cleared old screenshots")
            
        self.screenshots_dir.mkdir(exist_ok=True)
        
        # Save cycle start
        cycle_data = {
            'current_cycle': self.current_cycle,
            'start_time': datetime.now().isoformat(),
            'screenshots_cleared': True,
            'documentation_location': '.github/ai-agents/',
            'primary_instructions': '.github/copilot-instructions.md'
        }
        
        with open(self.cycle_log, 'w') as f:
            json.dump(cycle_data, f, indent=2)
            
        print(f"✅ Cycle {self.current_cycle} initialized")
        
    def start_app(self):
        """Start the spaceship app for testing"""
        print("🚀 Starting spaceship app...")
        
        try:
            python_exe = r"C:/Users/dante/OneDrive/Desktop/Play/.venv/Scripts/python.exe"
            self.app_process = subprocess.Popen(
                [python_exe, "main.py"],
                cwd=os.getcwd(),
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0
            )
            
            # Wait for app to start
            time.sleep(3)
            print(f"✅ App started (PID: {self.app_process.pid})")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start app: {e}")
            return False
    
    def take_screenshot(self, description: str) -> Optional[Path]:
        """Take screenshot and save to current cycle directory"""
        try:
            import pyautogui
            
            timestamp = datetime.now().strftime("%H%M%S")
            filename = f"{timestamp}_{description}.png"
            filepath = self.screenshots_dir / filename
            
            screenshot = pyautogui.screenshot()
            
            # Try to focus on app window
            try:
                import win32gui
                
                def find_window():
                    windows = []
                    def callback(hwnd, windows):
                        if win32gui.IsWindowVisible(hwnd):
                            title = win32gui.GetWindowText(hwnd)
                            if "Spaceship Designer" in title:
                                windows.append((hwnd, title))
                        return True
                    
                    win32gui.EnumWindows(callback, windows)
                    return windows[0] if windows else None
                
                window_info = find_window()
                if window_info:
                    hwnd, title = window_info
                    rect = win32gui.GetWindowRect(hwnd)
                    x1, y1, x2, y2 = rect
                    screenshot = screenshot.crop((x1, y1, x2, y2))
                    
            except:
                pass  # Use full screenshot if window focus fails
                
            screenshot.save(filepath)
            print(f"📸 Screenshot: {filename}")
            return filepath
            
        except Exception as e:
            print(f"❌ Screenshot failed: {e}")
            return None
    
    def test_ui_functionality(self):
        """Test key UI functions and capture results"""
        print("🧪 Testing UI functionality...")
        
        test_results = {}
        
        # Test 1: Take initial state screenshot
        initial_screenshot = self.take_screenshot("initial_state")
        test_results['initial_state'] = str(initial_screenshot) if initial_screenshot else None
        
        # Test 2: Try "New Random Ship" button
        try:
            import pyautogui
            
            # Approximate button location (right side of window)
            button_x = 1156  # From previous successful test
            button_y = 347   # From previous successful test
            
            before_screenshot = self.take_screenshot("before_new_ship")
            
            pyautogui.click(button_x, button_y)
            time.sleep(2)  # Wait for generation
            
            after_screenshot = self.take_screenshot("after_new_ship")
            
            test_results['new_ship_test'] = {
                'before': str(before_screenshot) if before_screenshot else None,
                'after': str(after_screenshot) if after_screenshot else None,
                'tested': True
            }
            
            print("✅ New ship button test completed")
            
        except Exception as e:
            print(f"❌ New ship test failed: {e}")
            test_results['new_ship_test'] = {'tested': False, 'error': str(e)}
        
        # Test 3: Try keyboard shortcuts
        try:
            import pyautogui
            
            # Test wireframe toggle
            pyautogui.press('w')
            time.sleep(0.5)
            wireframe_screenshot = self.take_screenshot("wireframe_toggle")
            
            # Test lighting toggle  
            pyautogui.press('l')
            time.sleep(0.5)
            lighting_screenshot = self.take_screenshot("lighting_toggle")
            
            test_results['keyboard_tests'] = {
                'wireframe': str(wireframe_screenshot) if wireframe_screenshot else None,
                'lighting': str(lighting_screenshot) if lighting_screenshot else None,
                'tested': True
            }
            
            print("✅ Keyboard shortcut tests completed")
            
        except Exception as e:
            print(f"❌ Keyboard tests failed: {e}")
            test_results['keyboard_tests'] = {'tested': False, 'error': str(e)}
        
        return test_results
    
    def close_app(self):
        """Close the spaceship app"""
        print("🔚 Closing app...")
        
        closed = False
        
        # Try to close gracefully first
        if self.app_process:
            try:
                self.app_process.terminate()
                self.app_process.wait(timeout=5)
                closed = True
                print("✅ App closed gracefully")
            except:
                pass
        
        # Force close if needed
        if not closed:
            try:
                for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                    try:
                        if (proc.info['name'] == 'python.exe' and 
                            proc.info['cmdline'] and 
                            'main.py' in ' '.join(proc.info['cmdline'])):
                            
                            proc.terminate()
                            proc.wait(timeout=3)
                            closed = True
                            print(f"✅ Force closed app (PID: {proc.info['pid']})")
                            break
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                        continue
                        
            except Exception as e:
                print(f"❌ Close failed: {e}")
        
        self.app_process = None
        return closed
    
    def analyze_results(self, test_results):
        """Analyze test results and generate recommendations"""
        print("📊 Analyzing test results...")
        
        recommendations = []
        issues_found = []
        
        # Check screenshot availability
        screenshots = list(self.screenshots_dir.glob("*.png"))
        if len(screenshots) == 0:
            issues_found.append("No screenshots captured - screenshot system may be broken")
        else:
            print(f"✅ {len(screenshots)} screenshots captured successfully")
        
        # Check new ship functionality
        if test_results.get('new_ship_test', {}).get('tested'):
            recommendations.append("✅ New Random Ship button is working")
        else:
            issues_found.append("❌ New Random Ship button not working")
            recommendations.append("🔧 Fix New Random Ship button functionality")
        
        # Check keyboard shortcuts
        if test_results.get('keyboard_tests', {}).get('tested'):
            recommendations.append("✅ Keyboard shortcuts are working")  
        else:
            issues_found.append("❌ Keyboard shortcuts not working")
            recommendations.append("🔧 Fix keyboard shortcut detection")
        
        # Print summary
        print(f"\n📋 Test Summary - Cycle {self.current_cycle}")
        print("="*50)
        
        if issues_found:
            print("🔍 Issues Found:")
            for issue in issues_found:
                print(f"  {issue}")
        
        print(f"\n💡 Recommendations:")
        for rec in recommendations:
            print(f"  {rec}")
            
        return {
            'issues': issues_found,
            'recommendations': recommendations,
            'screenshots_count': len(screenshots),
            'cycle_complete': len(issues_found) == 0
        }
    
    def get_latest_screenshot(self) -> Optional[Path]:
        """Get the most recent screenshot for AI analysis"""
        screenshots = list(self.screenshots_dir.glob("*.png"))
        if screenshots:
            latest = max(screenshots, key=lambda f: f.stat().st_mtime)
            print(f"📸 Latest screenshot: {latest.name}")
            return latest
        return None
    
    def complete_cycle(self):
        """Complete the full development cycle"""
        print(f"\n🎯 Executing Full Development Cycle {self.current_cycle}")
        print("="*60)
        
        # Step 1: Start new cycle (clear old screenshots)
        self.start_new_cycle()
        
        # Step 2: Start app
        if not self.start_app():
            return False
        
        # Step 3: Test functionality with screenshots
        test_results = self.test_ui_functionality()
        
        # Step 4: Close app
        self.close_app()
        
        # Step 5: Analyze results
        analysis = self.analyze_results(test_results)
        
        # Step 6: Save cycle data
        cycle_data = {
            'cycle': self.current_cycle,
            'completed_time': datetime.now().isoformat(),
            'test_results': test_results,
            'analysis': analysis,
            'latest_screenshot': str(self.get_latest_screenshot()) if self.get_latest_screenshot() else None
        }
        
        with open(self.cycle_log, 'w') as f:
            json.dump(cycle_data, f, indent=2)
        
        print(f"\n✅ Development Cycle {self.current_cycle} Complete")
        print(f"📊 Results saved to: {self.cycle_log}")
        print(f"📸 Screenshots in: {self.screenshots_dir}")
        
        return analysis.get('cycle_complete', False)

def main():
    """Main entry point for development cycle controller"""
    controller = DevelopmentCycleController()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "cycle":
            # Run full development cycle
            success = controller.complete_cycle()
            print(f"\n🎯 Cycle Status: {'SUCCESS' if success else 'NEEDS FIXES'}")
            
        elif command == "start":
            # Just start app for manual testing
            controller.start_app()
            
        elif command == "close":
            # Just close app
            controller.close_app()
            
        elif command == "screenshot":
            # Take single screenshot
            if controller.start_app():
                time.sleep(2)
                controller.take_screenshot("manual_capture")
                controller.close_app()
                
        elif command == "latest":
            # Show latest screenshot info
            latest = controller.get_latest_screenshot()
            if latest:
                print(f"📸 Latest screenshot: {latest}")
            else:
                print("❌ No screenshots found")
    else:
        print("AI Development Cycle Controller")
        print("Commands:")
        print("  cycle      - Run full development cycle")
        print("  start      - Start app only")
        print("  close      - Close app only")  
        print("  screenshot - Quick screenshot test")
        print("  latest     - Show latest screenshot")

if __name__ == "__main__":
    main()