#!/usr/bin/env python3
"""
UI Coordinate Grid Generator and Screenshot Cropper
Generates coordinate grids for different resolutions and handles window-specific screenshots
"""

import json
import pyautogui
import win32gui
import win32con
from PIL import Image, ImageGrab
from pathlib import Path

class UIGridGenerator:
    """Generate coordinate grids based on screen resolution and window detection"""
    
    def __init__(self):
        self.screen_size = pyautogui.size()
        self.resolution_key = f"{self.screen_size.width}x{self.screen_size.height}"
        
    def generate_systematic_grid(self, bounds, step_size=50):
        """Generate systematic coordinate grid within bounds"""
        coordinates = []
        
        for y in range(bounds['y_min'], bounds['y_max'], step_size):
            for x in range(bounds['x_min'], bounds['x_max'], step_size):
                coordinates.append({
                    "x": x, 
                    "y": y, 
                    "zone": f"grid_{x}_{y}"
                })
        
        return coordinates
    
    def generate_adaptive_left_panel(self):
        """Generate left panel coordinates based on current screen size"""
        start_x = int(self.screen_size.width * 0.05)  # 5% from left edge
        start_y = int(self.screen_size.height * 0.1)   # 10% from top
        step_x = 60
        step_y = 40
        columns = 3
        rows = 6 if self.screen_size.height < 800 else 8
        
        coordinates = []
        for row in range(rows):
            for col in range(columns):
                coordinates.append({
                    "x": start_x + (col * step_x),
                    "y": start_y + (row * step_y),
                    "zone": f"left_panel_r{row}_c{col}"
                })
        
        return coordinates
    
    def generate_adaptive_viewport(self):
        """Generate viewport coordinates based on screen size"""
        center_x = int(self.screen_size.width * 0.4)
        center_y = int(self.screen_size.height * 0.4)
        radius = int(min(self.screen_size.width, self.screen_size.height) * 0.1)
        
        coordinates = [
            {"x": center_x, "y": center_y, "zone": "viewport_center"},
            {"x": center_x - radius, "y": center_y - radius, "zone": "viewport_upper_left"},
            {"x": center_x + radius, "y": center_y - radius, "zone": "viewport_upper_right"},
            {"x": center_x - radius, "y": center_y + radius, "zone": "viewport_lower_left"},
            {"x": center_x + radius, "y": center_y + radius, "zone": "viewport_lower_right"},
            {"x": center_x - radius//2, "y": center_y, "zone": "viewport_mid_left"},
            {"x": center_x + radius//2, "y": center_y, "zone": "viewport_mid_right"},
            {"x": center_x, "y": center_y - radius//2, "zone": "viewport_mid_top"},
            {"x": center_x, "y": center_y + radius//2, "zone": "viewport_mid_bottom"}
        ]
        
        return coordinates
    
    def generate_adaptive_bottom_toolbar(self):
        """Generate bottom toolbar coordinates"""
        start_x = int(self.screen_size.width * 0.05)
        y_position = int(self.screen_size.height * 0.8)
        button_width = 80
        button_count = 8 if self.screen_size.width > 1920 else 6
        
        coordinates = []
        for i in range(button_count):
            coordinates.append({
                "x": start_x + (i * button_width),
                "y": y_position,
                "zone": f"bottom_btn_{i+1}"
            })
        
        return coordinates
    
    def get_current_resolution_grid(self):
        """Generate complete coordinate grid for current screen resolution"""
        return {
            "resolution": self.resolution_key,
            "screen_size": {"width": self.screen_size.width, "height": self.screen_size.height},
            "generated_timestamp": pyautogui.position(),  # Use as timestamp placeholder
            "ui_zones": {
                "left_panel": {
                    "description": "Adaptive left panel controls",
                    "coordinates": self.generate_adaptive_left_panel()
                },
                "viewport_center": {
                    "description": "Adaptive 3D viewport area",
                    "coordinates": self.generate_adaptive_viewport()
                },
                "bottom_toolbar": {
                    "description": "Adaptive bottom toolbar",
                    "coordinates": self.generate_adaptive_bottom_toolbar()
                }
            }
        }

class WindowScreenshotCropper:
    """Crop screenshots to specific application window bounds"""
    
    def __init__(self, window_titles=["Spaceship Designer", "Optimized Spaceship"]):
        self.window_titles = window_titles
        
    def find_target_window(self):
        """Find and return coordinates of target application window"""
        def enum_window_callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                window_text = win32gui.GetWindowText(hwnd)
                if window_text:
                    windows.append((hwnd, window_text))
            return True
        
        windows = []
        win32gui.EnumWindows(enum_window_callback, windows)
        
        # Look for target windows
        for hwnd, title in windows:
            if any(target.lower() in title.lower() for target in self.window_titles):
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
    
    def capture_window_screenshot(self, save_path=None):
        """Capture screenshot cropped to application window only"""
        window_info = self.find_target_window()
        
        if not window_info:
            # Fall back to full screen if window not found
            screenshot = pyautogui.screenshot()
            if save_path:
                screenshot.save(save_path)
            return screenshot, None
        
        # Capture full screen then crop to window
        full_screenshot = pyautogui.screenshot()
        
        # Crop to window bounds
        cropped = full_screenshot.crop((
            window_info["left"],
            window_info["top"], 
            window_info["right"],
            window_info["bottom"]
        ))
        
        if save_path:
            cropped.save(save_path)
            
        return cropped, window_info
    
    def adjust_coordinates_for_window(self, global_coordinates, window_info):
        """Convert global screen coordinates to window-relative coordinates"""
        if not window_info:
            return global_coordinates
            
        adjusted = []
        for coord in global_coordinates:
            adjusted.append({
                "x": coord["x"] - window_info["left"],
                "y": coord["y"] - window_info["top"],
                "zone": coord["zone"],
                "global_x": coord["x"],
                "global_y": coord["y"]
            })
        
        return adjusted

def generate_current_system_grid():
    """Generate coordinate grid for current system resolution"""
    generator = UIGridGenerator()
    grid = generator.get_current_resolution_grid()
    
    # Save to reference file
    reference_file = Path("reference") / "current_system_grid.json"
    reference_file.parent.mkdir(exist_ok=True)
    
    with open(reference_file, 'w') as f:
        json.dump(grid, f, indent=2)
    
    print(f"Generated coordinate grid for {generator.resolution_key}")
    print(f"Saved to: {reference_file}")
    print(f"Left panel coordinates: {len(grid['ui_zones']['left_panel']['coordinates'])}")
    print(f"Viewport coordinates: {len(grid['ui_zones']['viewport_center']['coordinates'])}")
    print(f"Bottom toolbar coordinates: {len(grid['ui_zones']['bottom_toolbar']['coordinates'])}")
    
    return grid

def test_window_cropping():
    """Test window-specific screenshot cropping"""
    cropper = WindowScreenshotCropper()
    
    # Test cropped screenshot
    cropped_screenshot, window_info = cropper.capture_window_screenshot("test_cropped.png")
    
    if window_info:
        print(f"Found window: {window_info['title']}")
        print(f"Window bounds: {window_info['left']}, {window_info['top']}, {window_info['width']}x{window_info['height']}")
        print(f"Cropped screenshot saved: test_cropped.png")
    else:
        print("Target window not found, captured full screen")
    
    return cropped_screenshot, window_info

if __name__ == "__main__":
    # Generate grid for current system
    current_grid = generate_current_system_grid()
    
    # Test window cropping
    cropped_img, window_info = test_window_cropping()
    
    print("\nCoordinate grid generation and window cropping utilities ready!")
    print("Use generate_current_system_grid() to create resolution-specific coordinates")
    print("Use WindowScreenshotCropper() to capture app-specific screenshots")