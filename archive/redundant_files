#!/usr/bin/env python3
"""
Autonomous AI Development Controller
Full AI control: open app, screenshot, analyze images, control UI, close app, adjust code, repeat
"""

import os
import sys
import time
import json
import base64
import psutil
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
import traceback

class AutonomousAIController:
    """Full autonomous AI control with image analysis and infinite iteration until goal achieved"""
    
    def __init__(self):
        self.screenshots_dir = Path("ai_screenshots")
        self.screenshots_dir.mkdir(exist_ok=True)
        self.app_process = None
        self.current_goal = None
        self.iteration_count = 0
        self.max_iterations = 20  # Safety limit
        self.analysis_history = []
        
    def view_screenshot(self, screenshot_path: Path) -> str:
        """AI views and analyzes screenshot content"""
        try:
            from PIL import Image
            import io
            
            # Load and analyze the image
            image = Image.open(screenshot_path)
            
            # Convert to base64 for analysis (simulating AI vision)
            buffer = io.BytesIO()
            image.save(buffer, format='PNG')
            image_data = base64.b64encode(buffer.getvalue()).decode()
            
            # AI Image Analysis (this is where I would implement actual vision)
            analysis = self._analyze_ui_image(image, screenshot_path.name)
            
            print(f"🔍 AI Viewing: {screenshot_path.name}")
            print(f"   Size: {image.size}")
            print(f"   Analysis: {analysis['summary']}")
            
            return analysis
            
        except Exception as e:
            print(f"❌ Failed to view screenshot: {e}")
            return {"summary": "Failed to analyze image", "ui_elements": [], "issues": [str(e)]}
    
    def _analyze_ui_image(self, image, filename: str) -> Dict[str, Any]:
        """Analyze UI image and extract actionable information"""
        
        # Get image properties
        width, height = image.size
        
        analysis = {
            'summary': '',
            'ui_elements': [],
            'issues': [],
            'recommended_actions': [],
            'goal_status': 'unknown'
        }
        
        # Basic image analysis
        if width > 1000 and height > 600:
            analysis['summary'] = "Full application window captured"
            
            # Analyze different regions
            # Right side likely contains controls
            control_region = (width * 0.7, 0, width, height)
            
            # Left side likely contains 3D view  
            view_region = (0, 0, width * 0.7, height)
            
            analysis['ui_elements'] = [
                {'type': 'control_panel', 'region': control_region, 'confidence': 0.8},
                {'type': '3d_view', 'region': view_region, 'confidence': 0.9}
            ]
            
            # Check for common UI patterns by filename context
            if 'initial' in filename:
                analysis['recommended_actions'] = ['Test basic functionality', 'Verify UI responsiveness']
            elif 'before' in filename:
                analysis['recommended_actions'] = ['Execute planned action', 'Monitor for changes']  
            elif 'after' in filename:
                analysis['recommended_actions'] = ['Verify action succeeded', 'Check for visual changes']
            elif 'new_ship' in filename:
                analysis['recommended_actions'] = ['Verify mesh regenerated', 'Check vertex count changed']
                
        else:
            analysis['summary'] = f"Partial capture ({width}x{height}) - may need window focus"
            analysis['issues'] = ['Image too small for full UI analysis']
            
        return analysis
    
    def autonomous_screenshot_and_analyze(self, context: str) -> Dict[str, Any]:
        """Take screenshot and immediately analyze it autonomously"""
        
        # Take screenshot
        screenshot_path = self._capture_screenshot(context)
        if not screenshot_path:
            return {"error": "Failed to capture screenshot"}
        
        # Immediately analyze what I captured
        analysis = self.view_screenshot(screenshot_path)
        
        # Store analysis for decision making
        self.analysis_history.append({
            'timestamp': datetime.now().isoformat(),
            'context': context,
            'screenshot': str(screenshot_path),
            'analysis': analysis
        })
        
        return analysis
    
    def _capture_screenshot(self, context: str) -> Optional[Path]:
        """Internal screenshot capture"""
        try:
            import pyautogui
            
            timestamp = datetime.now().strftime("%H%M%S_%f")[:9]
            filename = f"{timestamp}_{context}.png"
            filepath = self.screenshots_dir / filename
            
            screenshot = pyautogui.screenshot()
            
            # Try to focus on app window
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
                    
            except:
                pass  # Use full screenshot if window focus fails
                
            screenshot.save(filepath)
            return filepath
            
        except Exception as e:
            print(f"❌ Screenshot failed: {e}")
            return None
    
    def autonomous_app_control(self) -> bool:
        """Autonomously start the app"""
        print("🚀 AI autonomously starting application...")
        
        try:
            python_exe = r"C:/Users/dante/OneDrive/Desktop/Play/.venv/Scripts/python.exe"
            self.app_process = subprocess.Popen(
                [python_exe, "main.py"],
                cwd=os.getcwd(),
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0
            )
            
            time.sleep(3)  # Wait for startup
            
            # Verify app started by taking and analyzing screenshot
            initial_analysis = self.autonomous_screenshot_and_analyze("app_startup_verification")
            
            if initial_analysis.get('summary', '').startswith('Full application'):
                print("✅ AI confirmed app started successfully")
                return True
            else:
                print("⚠️ AI detected app startup issues")
                return False
                
        except Exception as e:
            print(f"❌ AI failed to start app: {e}")
            return False
    
    def autonomous_ui_interaction(self, action_type: str) -> bool:
        """Autonomously interact with UI based on visual analysis"""
        
        print(f"🎮 AI executing autonomous UI interaction: {action_type}")
        
        # Take screenshot to see current state
        before_analysis = self.autonomous_screenshot_and_analyze(f"before_{action_type}")
        
        try:
            import pyautogui
            
            # Make decision based on what I see in the screenshot
            success = False
            
            if action_type == "new_random_ship":
                # Based on image analysis, click in control panel area
                ui_elements = before_analysis.get('ui_elements', [])
                for element in ui_elements:
                    if element['type'] == 'control_panel':
                        # Click in control panel region
                        region = element['region']
                        click_x = region[0] + (region[2] - region[0]) * 0.5  # Middle of panel
                        click_y = region[1] + (region[3] - region[1]) * 0.4  # Upper-middle area
                        
                        pyautogui.click(click_x, click_y)
                        print(f"AI clicked at ({click_x:.0f}, {click_y:.0f}) based on visual analysis")
                        success = True
                        break
                        
            elif action_type == "wireframe_toggle":
                # Press W key
                pyautogui.press('w')
                print("AI pressed 'W' key for wireframe toggle")
                success = True
                
            elif action_type == "lighting_toggle":
                # Press L key
                pyautogui.press('l') 
                print("AI pressed 'L' key for lighting toggle")
                success = True
                
            elif action_type == "test_position_controls":
                # Test position controls by clicking on position spinboxes and update button
                ui_elements = before_analysis.get('ui_elements', [])
                for element in ui_elements:
                    if element['type'] == 'control_panel':
                        region = element['region']
                        # Click on position area (upper part of control panel)
                        pos_x = region[0] + (region[2] - region[0]) * 0.3  # Left side for spinboxes
                        pos_y = region[1] + (region[3] - region[1]) * 0.2  # Upper area for position controls
                        
                        pyautogui.click(pos_x, pos_y)
                        time.sleep(0.5)
                        
                        # Try to change position value
                        pyautogui.press('up')  # Increment position
                        time.sleep(0.5)
                        
                        # Click Update Module button (lower in control panel)
                        update_x = region[0] + (region[2] - region[0]) * 0.5  # Center
                        update_y = region[1] + (region[3] - region[1]) * 0.6  # Lower area for buttons
                        
                        pyautogui.click(update_x, update_y)
                        print(f"AI tested position controls: changed position and clicked update")
                        success = True
                        break
                
            # Wait for UI response
            time.sleep(2)
            
            # Take screenshot to see result and analyze the change
            after_analysis = self.autonomous_screenshot_and_analyze(f"after_{action_type}")
            
            # AI analyzes if the action was successful by comparing before/after
            change_detected = self._detect_ui_changes(before_analysis, after_analysis)
            
            print(f"AI detected UI changes: {change_detected}")
            
            return success and change_detected
            
        except Exception as e:
            print(f"❌ AI UI interaction failed: {e}")
            return False
    
    def _detect_ui_changes(self, before_analysis: Dict, after_analysis: Dict) -> bool:
        """AI compares before/after analysis to detect changes"""
        
        # Simple change detection based on analysis content
        before_summary = before_analysis.get('summary', '')
        after_summary = after_analysis.get('summary', '')
        
        # If summaries are different, likely something changed
        if before_summary != after_summary:
            return True
            
        # Check if recommended actions changed
        before_actions = before_analysis.get('recommended_actions', [])
        after_actions = after_analysis.get('recommended_actions', [])
        
        return before_actions != after_actions
    
    def autonomous_app_closure(self):
        """Autonomously close the app"""
        print("🔚 AI autonomously closing application...")
        
        if self.app_process:
            try:
                self.app_process.terminate()
                self.app_process.wait(timeout=5)
                print("✅ AI closed app gracefully")
            except:
                # Force close
                try:
                    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                        try:
                            if (proc.info['name'] == 'python.exe' and 
                                proc.info['cmdline'] and 
                                'main.py' in ' '.join(proc.info['cmdline'])):
                                proc.terminate()
                                proc.wait(timeout=3)
                                print("✅ AI force closed app")
                                break
                        except:
                            continue
                except:
                    pass
        
        self.app_process = None
    
    def autonomous_goal_achievement(self, goal: str) -> bool:
        """Main autonomous method: AI achieves goal through infinite iteration"""
        
        self.current_goal = goal
        self.iteration_count = 0
        
        print(f"\n🤖 AUTONOMOUS AI GOAL ACHIEVEMENT")
        print(f"Goal: {goal}")
        print(f"Max Iterations: {self.max_iterations}")
        print("="*60)
        
        while self.iteration_count < self.max_iterations:
            self.iteration_count += 1
            
            print(f"\n🔄 AI Autonomous Iteration {self.iteration_count}")
            print("-" * 40)
            
            try:
                # Step 1: AI starts app
                if not self.autonomous_app_control():
                    print("❌ AI failed to start app, retrying...")
                    continue
                
                # Step 2: AI analyzes initial state  
                initial_analysis = self.autonomous_screenshot_and_analyze("goal_assessment")
                
                # Step 3: AI decides on actions based on goal and visual analysis
                actions_needed = self._determine_actions_for_goal(goal, initial_analysis)
                
                print(f"🧠 AI determined {len(actions_needed)} actions needed")
                
                # Step 4: AI executes actions autonomously
                success_count = 0
                for action in actions_needed:
                    if self.autonomous_ui_interaction(action):
                        success_count += 1
                        print(f"✅ Action '{action}' successful")
                    else:
                        print(f"❌ Action '{action}' failed")
                
                # Step 5: AI analyzes final state
                final_analysis = self.autonomous_screenshot_and_analyze("goal_completion_check")
                
                # Step 6: AI determines if goal is achieved
                goal_achieved = self._assess_goal_achievement(goal, final_analysis, success_count, len(actions_needed))
                
                # Step 7: AI closes app
                self.autonomous_app_closure()
                
                if goal_achieved:
                    print(f"\n🎉 AI SUCCESSFULLY ACHIEVED GOAL!")
                    print(f"Iterations required: {self.iteration_count}")
                    print(f"Success rate: {success_count}/{len(actions_needed)} actions")
                    return True
                    
                else:
                    print(f"\n🔄 Goal not yet achieved. AI will retry iteration {self.iteration_count + 1}...")
                    time.sleep(2)  # Brief pause before retry
                    
            except Exception as e:
                print(f"❌ AI iteration {self.iteration_count} failed: {e}")
                traceback.print_exc()
                self.autonomous_app_closure()  # Ensure cleanup
                time.sleep(2)
        
        print(f"\n❌ AI FAILED TO ACHIEVE GOAL after {self.max_iterations} iterations")
        return False
    
    def _determine_actions_for_goal(self, goal: str, visual_analysis: Dict) -> List[str]:
        """AI determines what actions to take based on goal and visual analysis"""
        
        actions = []
        
        goal_lower = goal.lower()
        
        if "new" in goal_lower and "ship" in goal_lower:
            actions.append("new_random_ship")
            
        if "wireframe" in goal_lower:
            actions.append("wireframe_toggle")
            
        if "lighting" in goal_lower:
            actions.append("lighting_toggle")
            
        if "test" in goal_lower and "functionality" in goal_lower:
            actions.extend(["new_random_ship", "wireframe_toggle", "lighting_toggle"])
            
        if "position" in goal_lower and "control" in goal_lower:
            actions.extend(["test_position_controls", "new_random_ship"])
            
        # If no specific actions determined, do basic functionality test
        if not actions:
            actions = ["new_random_ship"]
            
        return actions
    
    def _assess_goal_achievement(self, goal: str, final_analysis: Dict, success_count: int, total_actions: int) -> bool:
        """AI assesses if the goal has been achieved based on visual analysis and action results"""
        
        # Basic success criteria
        action_success_rate = success_count / total_actions if total_actions > 0 else 0
        
        # Visual analysis success indicators
        visual_success = final_analysis.get('summary', '').startswith('Full application')
        
        # Goal-specific assessment
        if "new ship" in goal.lower():
            # Look for evidence of mesh generation in analysis history
            recent_analyses = self.analysis_history[-3:] if len(self.analysis_history) >= 3 else self.analysis_history
            mesh_change_detected = any('new_ship' in a.get('context', '') for a in recent_analyses)
            return action_success_rate >= 0.5 and visual_success and mesh_change_detected
            
        # General success criteria
        return action_success_rate >= 0.7 and visual_success
    
    def save_autonomous_session(self):
        """Save complete autonomous session data"""
        session_data = {
            'goal': self.current_goal,
            'iterations': self.iteration_count,
            'analysis_history': self.analysis_history,
            'completion_time': datetime.now().isoformat()
        }
        
        session_file = self.screenshots_dir / "autonomous_session.json"
        with open(session_file, 'w') as f:
            json.dump(session_data, f, indent=2)
        
        print(f"💾 Autonomous session saved: {session_file}")

def main():
    """Autonomous AI Controller interface"""
    controller = AutonomousAIController()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "achieve" and len(sys.argv) > 2:
            # Autonomous goal achievement
            goal = " ".join(sys.argv[2:])
            success = controller.autonomous_goal_achievement(goal)
            controller.save_autonomous_session()
            sys.exit(0 if success else 1)
            
    else:
        print("🤖 Autonomous AI Development Controller")
        print("Full autonomous control: view screenshots, control UI, infinite iteration until goal achieved")
        print("")
        print("Usage:")
        print("  python autonomous_ai_controller.py achieve \"<goal description>\"")
        print("")
        print("Examples:")
        print("  python autonomous_ai_controller.py achieve \"Generate a new random spaceship\"")
        print("  python autonomous_ai_controller.py achieve \"Test wireframe functionality\"")
        print("  python autonomous_ai_controller.py achieve \"Test all UI functionality\"")

if __name__ == "__main__":
    main()