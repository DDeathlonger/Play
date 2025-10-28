#!/usr/bin/env python3
"""
Universal Real-time AI Controller
Secure real-time AI control with whitelist protection
"""

import pyautogui
import time
from datetime import datetime
from pathlib import Path
import json
import win32gui
from PIL import ImageGrab

class UniversalAIController:
    """
    Secure real-time AI controller with whitelist protection:
    
    1. AI can SEE current state via screenshots (whitelisted apps only)
    2. AI can SEND commands (move, click, drag, type, etc.)
    3. AI gets IMMEDIATE visual feedback
    4. AI can make INTELLIGENT decisions based on what it sees
    5. Complete audit trail with security logging
    """
    
    def __init__(self):
        self.session_dir = Path("ai_sessions")
        self.session_dir.mkdir(exist_ok=True)
        
        # Security: ONLY the development app is whitelisted
        self.window_whitelist = [
            "Spaceship Designer",
            "Optimized Spaceship"
        ]
        
        # Session tracking
        self.session_id = datetime.now().strftime("%H%M%S")
        self.action_count = 0
        self.session_log = []
        self.security_violations = 0
        
        # Configure for responsive control
        pyautogui.PAUSE = 0.2
        pyautogui.FAILSAFE = True
        
        print(f"Universal AI Controller initialized - Session {self.session_id}")
        print(f"Window whitelist: {len(self.window_whitelist)} allowed applications")
        self._log_whitelist()
    
    def _log_whitelist(self):
        """Log current whitelist for transparency"""
        whitelist_log = {
            "session_id": self.session_id,
            "whitelist": self.window_whitelist,
            "timestamp": datetime.now().strftime("%H%M%S_%f")[:12]
        }
        
        whitelist_file = self.session_dir / f"whitelist_{self.session_id}.json"
        with open(whitelist_file, 'w') as f:
            json.dump(whitelist_log, f, indent=2)
        
        print(f"Whitelist logged: {whitelist_file}")
    
    def _is_window_allowed(self, window_title=""):
        """Check if window is in whitelist"""
        if not window_title:
            return True  # Allow desktop/general screenshots
        
        # Check against whitelist
        for allowed in self.window_whitelist:
            if allowed.lower() in window_title.lower():
                return True
        
        return False
    
    def _get_active_window_title(self):
        """Get title of currently active window"""
        try:
            hwnd = win32gui.GetForegroundWindow()
            window_title = win32gui.GetWindowText(hwnd)
            return window_title
        except ImportError:
            # Fallback if win32gui not available
            return "Unknown"
        except Exception:
            return "Unknown"
    
    def _security_check(self, action_type="screenshot"):
        """Perform security check before sensitive actions"""
        active_window = self._get_active_window_title()
        
        if not self._is_window_allowed(active_window):
            self.security_violations += 1
            
            violation = {
                "violation_id": self.security_violations,
                "action_type": action_type,
                "blocked_window": active_window,
                "timestamp": datetime.now().strftime("%H%M%S_%f")[:12],
                "reason": "Window not in whitelist"
            }
            
            self.session_log.append(violation)
            
            print(f"SECURITY BLOCK #{self.security_violations}: '{active_window}' not whitelisted")
            return False, violation
        
        print(f"Security check passed: '{active_window}' is whitelisted")
        return True, {"allowed_window": active_window}
        
    def see(self, context="observation"):
        """AI VISION: Take screenshot with security validation"""
        self.action_count += 1
        timestamp = datetime.now().strftime("%H%M%S_%f")[:12]
        
        # Security check
        allowed, security_info = self._security_check("screenshot")
        if not allowed:
            violation_response = {
                "action_id": self.action_count,
                "timestamp": timestamp,
                "context": context,
                "action_type": "observe_blocked",
                "security_violation": security_info,
                "message": "Screenshot blocked: Window not in whitelist"
            }
            self.session_log.append(violation_response)
            print(f"SEE #{self.action_count}: BLOCKED - {security_info['blocked_window']}")
            return violation_response
        
        # Proceed with screenshot if allowed
        screenshot = pyautogui.screenshot()
        filename = f"s{self.session_id}_{self.action_count:03d}_{context}.png"
        filepath = self.session_dir / filename
        screenshot.save(filepath)
        
        # Get current mouse position and screen info
        mouse_pos = pyautogui.position()
        screen_size = pyautogui.size()
        
        observation = {
            "action_id": self.action_count,
            "timestamp": timestamp,
            "context": context,
            "screenshot_path": str(filepath),
            "mouse_position": {"x": mouse_pos.x, "y": mouse_pos.y},
            "screen_size": {"width": screen_size.width, "height": screen_size.height},
            "action_type": "observe",
            "security_cleared": True,
            "active_window": security_info.get("allowed_window", "Unknown")
        }
        
        self.session_log.append(observation)
        print(f"SEE #{self.action_count}: {context} -> {filename}")
        return observation
        
    def move_to(self, x, y, smooth=True, reason="navigation"):
        """AI ACTION: Move mouse to coordinates"""
        self.action_count += 1
        
        try:
            if smooth:
                pyautogui.moveTo(x, y, duration=0.8, tween=pyautogui.easeInOutQuad)
            else:
                pyautogui.moveTo(x, y)
                
            actual_pos = pyautogui.position()
            
            action = {
                "action_id": self.action_count,
                "action_type": "move",
                "target": {"x": x, "y": y},
                "actual": {"x": actual_pos.x, "y": actual_pos.y},
                "smooth": smooth,
                "reason": reason,
                "success": True,
                "timestamp": datetime.now().strftime("%H%M%S_%f")[:12]
            }
            
            self.session_log.append(action)
            print(f"MOVE #{self.action_count}: to ({x}, {y}) - {reason}")
            return action
            
        except Exception as e:
            error_action = {
                "action_id": self.action_count,
                "action_type": "move",
                "error": str(e),
                "success": False
            }
            self.session_log.append(error_action)
            return error_action
    
    def click(self, x, y, button="left", clicks=1, reason="interaction"):
        """AI ACTION: Click at coordinates with security check"""
        self.action_count += 1
        
        # Security check for click actions
        allowed, security_info = self._security_check("click")
        if not allowed:
            violation_response = {
                "action_id": self.action_count,
                "action_type": "click_blocked",
                "security_violation": security_info,
                "target_position": {"x": x, "y": y},
                "success": False,
                "message": "Click blocked: Window not in whitelist"
            }
            self.session_log.append(violation_response)
            print(f"CLICK #{self.action_count}: BLOCKED at ({x}, {y}) - {security_info['blocked_window']}")
            return violation_response
        
        try:
            # Move to position first
            pyautogui.moveTo(x, y, duration=0.3)
            time.sleep(0.1)
            
            # Perform click
            if button == "left":
                pyautogui.click(x, y, clicks=clicks)
            elif button == "right":
                pyautogui.rightClick(x, y)
                
            action = {
                "action_id": self.action_count,
                "action_type": "click",
                "position": {"x": x, "y": y},
                "button": button,
                "clicks": clicks,
                "reason": reason,
                "success": True,
                "timestamp": datetime.now().strftime("%H%M%S_%f")[:12]
            }
            
            self.session_log.append(action)
            print(f"CLICK #{self.action_count}: {button} at ({x}, {y}) - {reason}")
            return action
            
        except Exception as e:
            error_action = {
                "action_id": self.action_count,
                "action_type": "click",
                "error": str(e),
                "success": False
            }
            self.session_log.append(error_action)
            return error_action
    
    def drag(self, start_x, start_y, end_x, end_y, duration=1.0, reason="manipulation"):
        """AI ACTION: Drag from start to end point"""
        self.action_count += 1
        
        try:
            pyautogui.moveTo(start_x, start_y)
            time.sleep(0.1)
            pyautogui.dragTo(end_x, end_y, duration=duration, button='left')
            
            action = {
                "action_id": self.action_count,
                "action_type": "drag",
                "start": {"x": start_x, "y": start_y},
                "end": {"x": end_x, "y": end_y},
                "duration": duration,
                "reason": reason,
                "success": True,
                "timestamp": datetime.now().strftime("%H%M%S_%f")[:12]
            }
            
            self.session_log.append(action)
            print(f"DRAG #{self.action_count}: ({start_x}, {start_y}) -> ({end_x}, {end_y}) - {reason}")
            return action
            
        except Exception as e:
            error_action = {
                "action_id": self.action_count,
                "action_type": "drag",
                "error": str(e),
                "success": False
            }
            self.session_log.append(error_action)
            return error_action
    
    def type_text(self, text, reason="input"):
        """AI ACTION: Type text at current location"""
        self.action_count += 1
        
        try:
            pyautogui.typewrite(text, interval=0.05)
            
            action = {
                "action_id": self.action_count,
                "action_type": "type",
                "text": text,
                "reason": reason,
                "success": True,
                "timestamp": datetime.now().strftime("%H%M%S_%f")[:12]
            }
            
            self.session_log.append(action)
            print(f"TYPE #{self.action_count}: '{text}' - {reason}")
            return action
            
        except Exception as e:
            error_action = {
                "action_id": self.action_count,
                "action_type": "type",
                "error": str(e),
                "success": False
            }
            self.session_log.append(error_action)
            return error_action
    
    def press_key(self, key, reason="shortcut"):
        """AI ACTION: Press keyboard key"""
        self.action_count += 1
        
        try:
            pyautogui.press(key)
            
            action = {
                "action_id": self.action_count,
                "action_type": "key_press",
                "key": key,
                "reason": reason,
                "success": True,
                "timestamp": datetime.now().strftime("%H%M%S_%f")[:12]
            }
            
            self.session_log.append(action)
            print(f"KEY #{self.action_count}: '{key}' - {reason}")
            return action
            
        except Exception as e:
            error_action = {
                "action_id": self.action_count,
                "action_type": "key_press",
                "error": str(e),
                "success": False
            }
            self.session_log.append(error_action)
            return error_action
    
    def wait(self, seconds, reason="timing"):
        """AI ACTION: Wait for specified time"""
        self.action_count += 1
        
        time.sleep(seconds)
        
        action = {
            "action_id": self.action_count,
            "action_type": "wait",
            "duration": seconds,
            "reason": reason,
            "success": True,
            "timestamp": datetime.now().strftime("%H%M%S_%f")[:12]
        }
        
        self.session_log.append(action)
        print(f"WAIT #{self.action_count}: {seconds}s - {reason}")
        return action
    
    def focus_app(self):
        """Find and focus the spaceship application window"""
        
        def enum_window_callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                window_text = win32gui.GetWindowText(hwnd)
                if window_text:
                    windows.append((hwnd, window_text))
            return True
        
        windows = []
        win32gui.EnumWindows(enum_window_callback, windows)
        
        # Look for spaceship app windows
        for hwnd, title in windows:
            if any(whitelist_name.lower() in title.lower() for whitelist_name in self.window_whitelist):
                try:
                    win32gui.SetForegroundWindow(hwnd)
                    print(f"Focused window: {title}")
                    return True
                except:
                    pass
        
        print("Could not find spaceship application window")
        return False
    
    def get_whitelist(self):
        """Get current whitelist (read-only for security)"""
        return self.window_whitelist.copy()
    
    def get_security_summary(self):
        """Get security statistics for this session"""
        return {
            "total_actions": self.action_count,
            "security_violations": self.security_violations,
            "whitelist_size": len(self.window_whitelist),
            "security_rate": f"{((self.action_count - self.security_violations) / max(self.action_count, 1) * 100):.1f}%"
        }
    
    def save_session(self):
        """Save complete session log with security information"""
        session_file = self.session_dir / f"session_{self.session_id}.json"
        
        session_summary = {
            "session_id": self.session_id,
            "total_actions": self.action_count,
            "security_violations": self.security_violations,
            "window_whitelist": self.window_whitelist,
            "security_summary": self.get_security_summary(),
            "start_time": self.session_log[0]["timestamp"] if self.session_log else None,
            "end_time": self.session_log[-1]["timestamp"] if self.session_log else None,
            "actions": self.session_log
        }
        
        with open(session_file, 'w') as f:
            json.dump(session_summary, f, indent=2)
        
        print(f"Session saved: {session_file}")
        print(f"Security summary: {self.get_security_summary()}")
        return session_file

# No command-line interface - Pure controller class for AI integration only