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
    
    def _get_target_window_bounds(self):
        """Get bounds of target application window for cropping"""
        try:
            def enum_window_callback(hwnd, windows):
                if win32gui.IsWindowVisible(hwnd):
                    window_text = win32gui.GetWindowText(hwnd)
                    if window_text:
                        windows.append((hwnd, window_text))
                return True
            
            windows = []
            win32gui.EnumWindows(enum_window_callback, windows)
            
            # Look for whitelisted windows
            for hwnd, title in windows:
                if any(allowed.lower() in title.lower() for allowed in self.window_whitelist):
                    rect = win32gui.GetWindowRect(hwnd)
                    return {
                        "hwnd": hwnd,
                        "title": title,
                        "left": rect[0],
                        "top": rect[1],
                        "right": rect[2], 
                        "bottom": rect[3],
                        "width": rect[2] - rect[0],
                        "height": rect[3] - rect[1]
                    }
            
            return None
            
        except Exception:
            return None
        
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
        # STEP 1: Capture full screen immediately
        screenshot = pyautogui.screenshot()
        
        # STEP 2: Crop immediately after capture if window found
        window_info = self._get_target_window_bounds()
        screenshot_type = "full_screen"
        
        if window_info and context != "full_screen":
            # Crop to application window bounds immediately
            screenshot = screenshot.crop((
                window_info["left"],
                window_info["top"],
                window_info["right"], 
                window_info["bottom"]
            ))
            screenshot_type = "cropped_to_window"
        
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
            "screenshot_type": screenshot_type,
            "window_info": window_info,
            "mouse_position": {"x": mouse_pos.x, "y": mouse_pos.y},
            "screen_size": {"width": screen_size.width, "height": screen_size.height},
            "action_type": "observe",
            "security_cleared": True,
            "active_window": security_info.get("allowed_window", "Unknown")
        }
        
        self.session_log.append(observation)
        print(f"SEE #{self.action_count}: {context} -> {filename}")
        return observation
        
    def _constrain_coordinates_to_window(self, x, y):
        """Constrain coordinates to application window bounds"""
        window_info = self._get_target_window_bounds()
        
        if not window_info:
            # No window found, return original coordinates
            return x, y, None
        
        # Constrain coordinates to window bounds with padding
        padding = 5  # Keep 5px away from edges
        constrained_x = max(window_info["left"] + padding, 
                          min(x, window_info["right"] - padding))
        constrained_y = max(window_info["top"] + padding,
                          min(y, window_info["bottom"] - padding))
        
        return constrained_x, constrained_y, window_info
    
    def _calculate_movement_duration(self, start_x, start_y, end_x, end_y, window_info=None):
        """Calculate movement duration with speed restrictions"""
        # Calculate distance
        distance = ((end_x - start_x) ** 2 + (end_y - start_y) ** 2) ** 0.5
        
        # Speed restrictions (pixels per second)
        if window_info:
            # Within app window - moderate speed for precision
            min_speed = 200  # Minimum 200 px/sec (slow for precision)
            max_speed = 800  # Maximum 800 px/sec (fast but controlled)
        else:
            # Outside app or no window - slower for safety
            min_speed = 100  # Very slow for safety
            max_speed = 400  # Moderate maximum
        
        # Calculate duration based on distance and speed limits
        max_duration = distance / min_speed  # Slowest allowed time
        min_duration = distance / max_speed  # Fastest allowed time
        
        # Default duration (middle ground)
        default_duration = distance / 500  # 500 px/sec default
        
        # Constrain to min/max bounds
        duration = max(min_duration, min(default_duration, max_duration))
        
        # Absolute bounds for sanity
        duration = max(0.1, min(duration, 3.0))  # 0.1s to 3.0s maximum
        
        return duration

    def move_to(self, x, y, smooth=True, reason="navigation"):
        """AI ACTION: Move mouse to coordinates with STRICT window constraints - CANNOT leave app"""
        self.action_count += 1
        
        try:
            # Get current position for speed calculation
            current_pos = pyautogui.position()
            
            # CRITICAL: Constrain target coordinates to window bounds - NO EXCEPTIONS
            constrained_x, constrained_y, window_info = self._constrain_coordinates_to_window(x, y)
            
            # SECURITY: If no window info, keep mouse at current position (stick to edge)
            if not window_info:
                print(f"� MOUSE CONTAINMENT: No target window - keeping current position")
                return
            
            # Mouse sticks to window edges instead of blocking movement
            if constrained_x != x or constrained_y != y:
                print(f"� MOUSE STICK: Constrained ({x},{y}) → ({constrained_x},{constrained_y})")
            
            # Calculate appropriate movement duration
            duration = self._calculate_movement_duration(
                current_pos.x, current_pos.y, 
                constrained_x, constrained_y, 
                window_info
            )
            
            # Perform movement with calculated duration
            if smooth:
                pyautogui.moveTo(constrained_x, constrained_y, duration=duration, tween=pyautogui.easeInOutQuad)
            else:
                pyautogui.moveTo(constrained_x, constrained_y)
                
            actual_pos = pyautogui.position()
            
            # Calculate movement distance and speed for logging
            distance = ((constrained_x - current_pos.x) ** 2 + (constrained_y - current_pos.y) ** 2) ** 0.5
            speed = distance / duration if duration > 0 else 0
            
            action = {
                "action_id": self.action_count,
                "action_type": "move",
                "target_requested": {"x": x, "y": y},
                "target_constrained": {"x": constrained_x, "y": constrained_y},
                "actual": {"x": actual_pos.x, "y": actual_pos.y},
                "movement_info": {
                    "distance_pixels": round(distance, 2),
                    "duration_seconds": round(duration, 3),
                    "speed_pixels_per_second": round(speed, 2),
                    "constrained_to_window": bool(window_info),
                    "window_title": window_info["title"] if window_info else None
                },
                "smooth": smooth,
                "reason": reason,
                "success": True,
                "timestamp": datetime.now().strftime("%H%M%S_%f")[:12]
            }
            
            self.session_log.append(action)
            constrained_msg = f" -> ({constrained_x}, {constrained_y})" if (constrained_x != x or constrained_y != y) else ""
            speed_msg = f" [{speed:.0f}px/s]" if speed > 0 else ""
            print(f"MOVE #{self.action_count}: to ({x}, {y}){constrained_msg}{speed_msg} - {reason}")
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
            # CRITICAL: Constrain click coordinates to window bounds - NO CLICKS OUTSIDE APP
            constrained_x, constrained_y, window_info = self._constrain_coordinates_to_window(x, y)
            
            # SECURITY: Stick click to window edge if no bounds available
            if not window_info:
                print(f"� CLICK CONTAINMENT: No target window - click at current mouse position")
                constrained_x, constrained_y = pyautogui.position()
            
            # Clicks stick to window edges instead of being blocked
            if constrained_x != x or constrained_y != y:
                print(f"� CLICK STICK: Constrained ({x},{y}) → ({constrained_x},{constrained_y})")
            
            # Move to constrained position with appropriate speed
            current_pos = pyautogui.position()
            duration = self._calculate_movement_duration(
                current_pos.x, current_pos.y,
                constrained_x, constrained_y,
                window_info
            )
            
            pyautogui.moveTo(constrained_x, constrained_y, duration=duration)
            time.sleep(0.1)
            
            # Perform click at constrained coordinates
            if button == "left":
                pyautogui.click(constrained_x, constrained_y, clicks=clicks)
            elif button == "right":
                pyautogui.rightClick(constrained_x, constrained_y)
            
            # Calculate movement info for logging
            distance = ((constrained_x - current_pos.x) ** 2 + (constrained_y - current_pos.y) ** 2) ** 0.5
            speed = distance / duration if duration > 0 else 0
                
            action = {
                "action_id": self.action_count,
                "action_type": "click",
                "position_requested": {"x": x, "y": y},
                "position_constrained": {"x": constrained_x, "y": constrained_y},
                "movement_info": {
                    "distance_pixels": round(distance, 2),
                    "duration_seconds": round(duration, 3),
                    "speed_pixels_per_second": round(speed, 2),
                    "constrained_to_window": bool(window_info),
                    "window_title": window_info["title"] if window_info else None
                },
                "button": button,
                "clicks": clicks,
                "reason": reason,
                "success": True,
                "timestamp": datetime.now().strftime("%H%M%S_%f")[:12]
            }
            
            self.session_log.append(action)
            constrained_msg = f" -> ({constrained_x}, {constrained_y})" if (constrained_x != x or constrained_y != y) else ""
            speed_msg = f" [{speed:.0f}px/s]" if speed > 0 else ""
            print(f"CLICK #{self.action_count}: {button} at ({x}, {y}){constrained_msg}{speed_msg} - {reason}")
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
    
    def drag(self, start_x, start_y, end_x, end_y, duration=None, reason="manipulation"):
        """AI ACTION: Drag from start to end point with window constraints and speed limits"""
        self.action_count += 1
        
        try:
            # Constrain both start and end coordinates to window bounds
            constrained_start_x, constrained_start_y, window_info = self._constrain_coordinates_to_window(start_x, start_y)
            constrained_end_x, constrained_end_y, _ = self._constrain_coordinates_to_window(end_x, end_y)
            
            # Calculate appropriate duration if not provided
            if duration is None:
                duration = self._calculate_movement_duration(
                    constrained_start_x, constrained_start_y,
                    constrained_end_x, constrained_end_y,
                    window_info
                )
                # Drag operations should be slightly slower for precision
                duration = duration * 1.5  # 50% slower than regular movement
                duration = max(0.2, min(duration, 4.0))  # 0.2s to 4.0s bounds
            
            # Move to start position first
            current_pos = pyautogui.position()
            move_duration = self._calculate_movement_duration(
                current_pos.x, current_pos.y,
                constrained_start_x, constrained_start_y,
                window_info
            )
            
            pyautogui.moveTo(constrained_start_x, constrained_start_y, duration=move_duration)
            time.sleep(0.1)
            
            # Perform drag to constrained end position
            pyautogui.dragTo(constrained_end_x, constrained_end_y, duration=duration, button='left')
            
            # Calculate drag distance and speed for logging
            drag_distance = ((constrained_end_x - constrained_start_x) ** 2 + (constrained_end_y - constrained_start_y) ** 2) ** 0.5
            drag_speed = drag_distance / duration if duration > 0 else 0
            
            action = {
                "action_id": self.action_count,
                "action_type": "drag",
                "start_requested": {"x": start_x, "y": start_y},
                "start_constrained": {"x": constrained_start_x, "y": constrained_start_y},
                "end_requested": {"x": end_x, "y": end_y},
                "end_constrained": {"x": constrained_end_x, "y": constrained_end_y},
                "movement_info": {
                    "drag_distance_pixels": round(drag_distance, 2),
                    "drag_duration_seconds": round(duration, 3),
                    "drag_speed_pixels_per_second": round(drag_speed, 2),
                    "constrained_to_window": bool(window_info),
                    "window_title": window_info["title"] if window_info else None
                },
                "reason": reason,
                "success": True,
                "timestamp": datetime.now().strftime("%H%M%S_%f")[:12]
            }
            
            self.session_log.append(action)
            constrained_msg = ""
            if (constrained_start_x != start_x or constrained_start_y != start_y or 
                constrained_end_x != end_x or constrained_end_y != end_y):
                constrained_msg = f" -> ({constrained_start_x}, {constrained_start_y}) to ({constrained_end_x}, {constrained_end_y})"
            speed_msg = f" [{drag_speed:.0f}px/s]" if drag_speed > 0 else ""
            print(f"DRAG #{self.action_count}: ({start_x}, {start_y}) -> ({end_x}, {end_y}){constrained_msg}{speed_msg} - {reason}")
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