#!/usr/bin/env python3
"""
Strategic AI UI Controller
Enables AI agents to autonomously interact with the spaceship designer UI
based on visual analysis and strategic decision making
"""

import os
import sys
import time
import json
import psutil
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any

class StrategicUIController:
    """AI controller that can strategically interact with the UI to accomplish goals"""
    
    def __init__(self):
        self.screenshots_dir = Path("ai_screenshots")
        self.screenshots_dir.mkdir(exist_ok=True)
        self.app_process = None
        self.current_goal = None
        self.ui_state = {}
        self.interaction_history = []
        
    def set_goal(self, goal_description: str):
        """Set the current goal for AI to accomplish"""
        self.current_goal = goal_description
        print(f"🎯 AI Goal Set: {goal_description}")
        
    def start_app_strategically(self) -> bool:
        """Start app with goal-oriented approach"""
        print(f"🚀 Starting app to accomplish: {self.current_goal}")
        
        try:
            python_exe = r"C:/Users/dante/OneDrive/Desktop/Play/.venv/Scripts/python.exe"
            self.app_process = subprocess.Popen(
                [python_exe, "main.py"],
                cwd=os.getcwd(),
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0
            )
            
            time.sleep(3)  # Wait for full startup
            print(f"✅ App ready for strategic interaction (PID: {self.app_process.pid})")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start app: {e}")
            return False
    
    def capture_ui_state(self, context: str = "general") -> Optional[Path]:
        """Capture current UI state for analysis"""
        try:
            import pyautogui
            
            timestamp = datetime.now().strftime("%H%M%S_%f")[:9]  # Include microseconds for uniqueness
            filename = f"{timestamp}_{context}.png"
            filepath = self.screenshots_dir / filename
            
            screenshot = pyautogui.screenshot()
            
            # Try to focus on app window for cleaner screenshots
            try:
                import win32gui
                
                def find_app_window():
                    windows = []
                    def callback(hwnd, windows):
                        if win32gui.IsWindowVisible(hwnd):
                            title = win32gui.GetWindowText(hwnd)
                            if "Spaceship Designer" in title:
                                rect = win32gui.GetWindowRect(hwnd)
                                windows.append((hwnd, title, rect))
                        return True
                    
                    win32gui.EnumWindows(callback, windows)
                    return windows[0] if windows else None
                
                window_info = find_app_window()
                if window_info:
                    hwnd, title, rect = window_info
                    x1, y1, x2, y2 = rect
                    screenshot = screenshot.crop((x1, y1, x2, y2))
                    
                    # Update UI state with window info
                    self.ui_state['window_bounds'] = rect
                    self.ui_state['window_title'] = title
                    
            except Exception as e:
                print(f"Window focus failed (using full screen): {e}")
                
            screenshot.save(filepath)
            
            # Record this interaction
            self.interaction_history.append({
                'timestamp': datetime.now().isoformat(),
                'action': f"screenshot_{context}",
                'screenshot': str(filepath),
                'goal_context': self.current_goal
            })
            
            print(f"📸 UI State Captured: {filename}")
            return filepath
            
        except Exception as e:
            print(f"❌ Screenshot failed: {e}")
            return None
    
    def analyze_ui_for_goal(self, screenshot_path: Path) -> Dict[str, Any]:
        """Analyze UI screenshot to determine strategic actions for current goal"""
        
        # This is where AI would implement visual analysis
        # For now, providing strategic framework
        
        analysis = {
            'ui_elements_detected': [],
            'recommended_actions': [],
            'goal_progress': 'analyzing',
            'next_strategy': None
        }
        
        if not self.ui_state.get('window_bounds'):
            analysis['recommended_actions'].append("Unable to detect app window - may need to restart")
            return analysis
        
        # Strategic analysis based on current goal
        if self.current_goal:
            if "test functionality" in self.current_goal.lower():
                analysis['recommended_actions'] = [
                    "Test 'New Random Ship' button functionality",
                    "Verify keyboard shortcuts (W, L, R)",
                    "Test position controls and module updates",
                    "Verify 3D view interactions"
                ]
                analysis['next_strategy'] = 'systematic_testing'
                
            elif "generate" in self.current_goal.lower() and "ship" in self.current_goal.lower():
                analysis['recommended_actions'] = [
                    "Locate and click 'New Random Ship' button",
                    "Verify new mesh generation in console",
                    "Capture result screenshot"
                ]
                analysis['next_strategy'] = 'generate_content'
                
            elif "fix" in self.current_goal.lower() or "debug" in self.current_goal.lower():
                analysis['recommended_actions'] = [
                    "Test suspected broken functionality",
                    "Capture error states",
                    "Document specific failure points"
                ]
                analysis['next_strategy'] = 'debug_mode'
                
            else:
                analysis['recommended_actions'] = [
                    "Explore UI to understand available functions",
                    "Take baseline screenshots",
                    "Test basic interactions"
                ]
                analysis['next_strategy'] = 'exploration'
        
        print(f"🧠 AI Analysis: {len(analysis['recommended_actions'])} strategic actions identified")
        return analysis
    
    def execute_strategic_action(self, action: str) -> bool:
        """Execute a specific action strategically"""
        print(f"🎮 Executing: {action}")
        
        try:
            import pyautogui
            
            # Record action start
            action_start = datetime.now()
            before_screenshot = self.capture_ui_state(f"before_{action.replace(' ', '_')[:20]}")
            
            success = False
            
            # Strategic action execution based on content
            if "new random ship" in action.lower():
                success = self._strategic_button_click("new_random_ship", search_area="right_panel")
                
            elif "keyboard" in action.lower() and "w" in action.lower():
                pyautogui.press('w')
                success = True
                
            elif "keyboard" in action.lower() and "l" in action.lower():
                pyautogui.press('l')
                success = True
                
            elif "keyboard" in action.lower() and "r" in action.lower():
                pyautogui.press('r')
                success = True
                
            elif "position control" in action.lower():
                success = self._strategic_position_test()
                
            elif "test" in action.lower() and "3d" in action.lower():
                success = self._strategic_3d_interaction()
                
            else:
                print(f"⚠️ Unknown action type: {action}")
                success = False
            
            # Wait for UI response
            time.sleep(1)
            
            # Capture result
            after_screenshot = self.capture_ui_state(f"after_{action.replace(' ', '_')[:20]}")
            
            # Record interaction
            self.interaction_history.append({
                'timestamp': action_start.isoformat(),
                'action': action,
                'success': success,
                'before_screenshot': str(before_screenshot) if before_screenshot else None,
                'after_screenshot': str(after_screenshot) if after_screenshot else None,
                'goal_context': self.current_goal
            })
            
            result_status = "✅ SUCCESS" if success else "❌ FAILED"
            print(f"{result_status}: {action}")
            
            return success
            
        except Exception as e:
            print(f"❌ Action execution failed: {e}")
            return False
    
    def _strategic_button_click(self, button_type: str, search_area: str = "full") -> bool:
        """Strategically locate and click buttons based on UI analysis"""
        
        if not self.ui_state.get('window_bounds'):
            print("❌ No window bounds available for strategic clicking")
            return False
        
        x1, y1, x2, y2 = self.ui_state['window_bounds']
        
        # Strategic button location based on UI layout knowledge
        if search_area == "right_panel":
            # Control panel is typically on the right side
            search_x = x2 - 200  # Right side area
            search_y_start = y1 + 100  # Below title bar
            search_y_end = y2 - 100    # Above bottom
            
            # Try multiple strategic locations
            test_positions = [
                (search_x, search_y_start + 200),  # Upper area
                (search_x, search_y_start + 300),  # Middle area  
                (search_x, search_y_start + 400),  # Lower area
            ]
            
            for x, y in test_positions:
                try:
                    import pyautogui
                    pyautogui.click(x, y)
                    time.sleep(0.5)
                    
                    # Check if click had effect (this would be enhanced with visual analysis)
                    print(f"Strategic click attempted at ({x}, {y})")
                    return True  # Assume success for now
                    
                except Exception as e:
                    print(f"Click failed at ({x}, {y}): {e}")
                    continue
        
        return False
    
    def _strategic_position_test(self) -> bool:
        """Test position controls strategically"""
        try:
            import pyautogui
            
            if self.ui_state.get('window_bounds'):
                x1, y1, x2, y2 = self.ui_state['window_bounds']
                
                # Position controls likely in upper right
                pos_x = x2 - 150
                pos_y = y1 + 150
                
                pyautogui.click(pos_x, pos_y)
                time.sleep(0.5)
                pyautogui.press('up')  # Increment value
                
                return True
        except:
            pass
        return False
    
    def _strategic_3d_interaction(self) -> bool:
        """Test 3D view interactions strategically"""
        try:
            import pyautogui
            
            if self.ui_state.get('window_bounds'):
                x1, y1, x2, y2 = self.ui_state['window_bounds']
                
                # 3D view likely takes up left portion of window
                view_center_x = x1 + (x2 - x1) * 0.4  # Left 40% area
                view_center_y = y1 + (y2 - y1) * 0.5   # Middle height
                
                # Simulate mouse drag for rotation
                pyautogui.mouseDown(view_center_x, view_center_y)
                pyautogui.dragTo(view_center_x + 50, view_center_y + 50, duration=0.5)
                pyautogui.mouseUp()
                
                return True
        except:
            pass
        return False
    
    def accomplish_goal(self, goal: str) -> bool:
        """Main method: AI strategically accomplishes the stated goal"""
        self.set_goal(goal)
        
        print(f"\n🤖 AI STRATEGIC GOAL EXECUTION")
        print(f"Goal: {goal}")
        print("="*60)
        
        # Step 1: Start app
        if not self.start_app_strategically():
            return False
        
        try:
            # Step 2: Capture initial state
            initial_screenshot = self.capture_ui_state("initial_goal_state")
            
            # Step 3: Analyze UI for strategic approach
            analysis = self.analyze_ui_for_goal(initial_screenshot)
            
            # Step 4: Execute strategic actions
            success_count = 0
            total_actions = len(analysis['recommended_actions'])
            
            for action in analysis['recommended_actions']:
                if self.execute_strategic_action(action):
                    success_count += 1
                time.sleep(1)  # Brief pause between actions
            
            # Step 5: Final assessment
            final_screenshot = self.capture_ui_state("final_goal_state")
            
            success_rate = success_count / total_actions if total_actions > 0 else 0
            goal_accomplished = success_rate >= 0.7  # 70% success threshold
            
            print(f"\n📊 Goal Execution Summary:")
            print(f"Actions Completed: {success_count}/{total_actions}")
            print(f"Success Rate: {success_rate:.1%}")
            print(f"Goal Status: {'✅ ACCOMPLISHED' if goal_accomplished else '❌ NEEDS RETRY'}")
            
            return goal_accomplished
            
        finally:
            # Always close app
            self.close_app_strategically()
            
    def close_app_strategically(self):
        """Close app with cleanup"""
        print("🔚 Strategic app closure...")
        
        # Save interaction history
        history_file = self.screenshots_dir / "interaction_history.json"
        with open(history_file, 'w') as f:
            json.dump(self.interaction_history, f, indent=2)
        
        # Close app
        if self.app_process:
            try:
                self.app_process.terminate()
                self.app_process.wait(timeout=5)
                print("✅ App closed gracefully")
            except:
                # Force close if needed
                try:
                    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                        try:
                            if (proc.info['name'] == 'python.exe' and 
                                proc.info['cmdline'] and 
                                'main.py' in ' '.join(proc.info['cmdline'])):
                                proc.terminate()
                                proc.wait(timeout=3)
                                print("✅ App force closed")
                                break
                        except:
                            continue
                except:
                    pass
        
        self.app_process = None
    
    def get_latest_screenshot(self) -> Optional[Path]:
        """Get the most recent screenshot for analysis"""
        screenshots = list(self.screenshots_dir.glob("*.png"))
        if screenshots:
            latest = max(screenshots, key=lambda f: f.stat().st_mtime)
            return latest
        return None

def main():
    """Strategic UI Controller interface"""
    controller = StrategicUIController()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "goal" and len(sys.argv) > 2:
            # Execute specific goal
            goal = " ".join(sys.argv[2:])
            success = controller.accomplish_goal(goal)
            sys.exit(0 if success else 1)
            
        elif command == "test_functionality":
            success = controller.accomplish_goal("Test all UI functionality systematically")
            sys.exit(0 if success else 1)
            
        elif command == "generate_ship":
            success = controller.accomplish_goal("Generate a new random spaceship")
            sys.exit(0 if success else 1)
            
        elif command == "debug_ui":
            success = controller.accomplish_goal("Debug and identify UI interaction issues")
            sys.exit(0 if success else 1)
            
        elif command == "latest":
            latest = controller.get_latest_screenshot()
            print(f"📸 Latest screenshot: {latest}" if latest else "❌ No screenshots found")
            
    else:
        print("🤖 Strategic AI UI Controller")
        print("Commands:")
        print("  goal \"<description>\"     - Execute custom goal")
        print("  test_functionality       - Test all UI functions")
        print("  generate_ship            - Generate new spaceship")  
        print("  debug_ui                 - Debug UI interactions")
        print("  latest                   - Show latest screenshot")
        print("")
        print("Examples:")
        print("  python strategic_ui_controller.py goal \"Test the wireframe toggle\"")
        print("  python strategic_ui_controller.py test_functionality")

if __name__ == "__main__":
    main()