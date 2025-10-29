# Universal AI Controller - Complete Guide

## Overview

The `UniversalAIController` is a secure, real-time AI control system that enables AI agents to interact with the spaceship designer application through visual feedback and precise input control.

## Key Features

### 🔒 Security-First Design
- **Whitelist Protection**: Only allows interaction with "Spaceship Designer" and "Optimized Spaceship" applications
- **Security Audit Trail**: Complete logging of all actions and security violations
- **Violation Tracking**: Monitors and blocks unauthorized window access attempts

### 👁️ Visual Feedback System
- **Real-time Screenshots**: Capture application interface for AI analysis
- **Timestamped Images**: All screenshots saved with session ID and sequence numbers
- **Before/After Comparison**: Enable visual verification of UI changes

### 🎯 Precise Control
- **Pixel-Perfect Clicking**: Accurate mouse positioning and clicking
- **Smooth Mouse Movement**: Natural cursor movement patterns
- **Keyboard Input**: Key presses and text typing capabilities
- **Drag Operations**: Click-and-drag functionality for UI manipulation

## Class Interface

### Initialization
```python
from universal_ai_controller import UniversalAIController
controller = UniversalAIController()
# Automatically creates session directory and initializes security system
```

### Core Methods

#### Visual Observation
```python
# Take screenshot with context
screenshot_info = controller.see("analyzing_ui_layout")

# Returns dictionary with:
# - action_id: Sequential action number
# - timestamp: Precise timing
# - context: Your description
# - screenshot_path: Full path to saved image
# - mouse_position: Current cursor location
# - screen_size: Display dimensions
# - action_type: "observe" or "observe_blocked"
# - security_cleared: Boolean security status
# - active_window: Current focused window title
```

#### Mouse Control
```python
# Left click
controller.click(400, 300, reason="test_viewport_click")

# Right click
controller.click(400, 300, button="right", reason="context_menu")

# Move cursor without clicking
controller.move_to(500, 400, reason="hover_over_button")

# Drag operation
controller.drag(100, 100, 200, 200, reason="drag_slider")
```

#### Keyboard Control
```python
# Single key press
controller.press_key('w', reason="toggle_wireframe")
controller.press_key('escape', reason="close_dialog")

# Type text string
controller.type_text("Hello World", reason="enter_filename")
```

#### Window Management
```python
# Focus spaceship application
success = controller.focus_app()  # Returns True if found and focused

# Wait with reason tracking
controller.wait(2.0, reason="wait_for_ui_update")
```

#### Session Management
```python
# Save complete session log
controller.save_session()

# Get security summary
summary = controller.get_security_summary()

# Get current whitelist
whitelist = controller.get_whitelist()
```

## Security System

### Whitelist Configuration
The controller only allows interaction with windows containing:
- "Spaceship Designer"
- "Optimized Spaceship"

### Security Checks
Every action performs automatic security validation:
1. Gets active window title
2. Checks against whitelist
3. Blocks or allows action
4. Logs result with violation tracking

### Violation Handling
```python
# Security violations are automatically:
# 1. Logged to session file
# 2. Counted and tracked
# 3. Reported in security summary
# 4. Block the requested action
```

## File Structure

### Session Directory: `ai_sessions/`
```
ai_sessions/
├── s{session_id}_{action_num}_{context}.png    # Screenshots
├── whitelist_{session_id}.json                 # Session whitelist log
├── session_{session_id}.json                   # Complete session audit
└── security_summary_{session_id}.json          # Security analysis
```

### Screenshot Naming Convention
- `s094922_001_before_interactions.png`
  - `s094922`: Session ID (timestamp-based)
  - `001`: Action sequence number
  - `before_interactions`: Context description

## Usage Patterns

### 1. Basic UI Testing
```python
controller = UniversalAIController()

# Focus app and see interface
controller.focus_app()
initial = controller.see("initial_state")

# Test button click
controller.click(400, 300, reason="test_generate_button")
after_click = controller.see("after_generate_click")

# Verify with keyboard shortcut
controller.press_key('w', reason="test_wireframe_toggle")
final = controller.see("wireframe_toggled")
```

### 2. Systematic Feature Testing
```python
def test_ui_elements():
    controller = UniversalAIController()
    controller.focus_app()
    
    # Test coordinates for different UI elements
    test_points = [
        (400, 300, "viewport_center"),
        (150, 100, "generate_button"),
        (150, 130, "random_button"),
        (150, 160, "clear_button")
    ]
    
    for x, y, element_name in test_points:
        controller.see(f"before_{element_name}")
        controller.click(x, y, reason=f"test_{element_name}")
        controller.see(f"after_{element_name}")
        controller.wait(1.0, reason="observe_response")
```

### 3. Debug Visual Issues
```python
def debug_mesh_generation():
    controller = UniversalAIController()
    controller.focus_app()
    
    # Capture before state
    before = controller.see("mesh_before_generation")
    
    # Generate new mesh
    controller.click(150, 100, reason="generate_new_mesh") 
    controller.wait(2.0, reason="wait_for_generation")
    
    # Capture after state
    after = controller.see("mesh_after_generation")
    
    # Toggle wireframe to see geometry
    controller.press_key('w', reason="show_wireframe_geometry")
    wireframe = controller.see("mesh_wireframe_view")
    
    print(f"Debug screenshots: {before}, {after}, {wireframe}")
```

### 4. Performance Analysis
```python
def analyze_ui_responsiveness():
    controller = UniversalAIController()
    controller.focus_app()
    
    start_time = time.time()
    
    # Rapid UI interactions
    for i in range(5):
        controller.press_key('w', reason=f"wireframe_toggle_{i}")
        controller.wait(0.5, reason="measure_response_time")
        controller.see(f"response_test_{i}")
    
    total_time = time.time() - start_time
    print(f"UI responsiveness test completed in {total_time:.2f}s")
```

## Integration with Development Workflow

### With AI Development Cycle
```python
# In ai_development_cycle.py integration:
controller = UniversalAIController()

def visual_test_cycle():
    controller.focus_app()
    
    # Test current functionality
    before = controller.see("cycle_start")
    
    # Execute test sequence
    test_all_ui_elements(controller)
    
    # Capture results
    after = controller.see("cycle_complete")
    
    return {"before": before, "after": after}
```

### Error Debugging
```python
def debug_ui_error():
    controller = UniversalAIController()
    
    try:
        controller.focus_app()
        controller.click(400, 300, reason="reproduce_error")
        controller.see("error_reproduction")
    except Exception as e:
        controller.see("error_state")
        print(f"Error captured with visual evidence: {e}")
```

## Best Practices

### 1. Always Provide Context
```python
# ✅ Good: Descriptive context
controller.see("testing_wireframe_after_mesh_generation")

# ❌ Avoid: Generic context  
controller.see("test")
```

### 2. Use Appropriate Wait Times
```python
# ✅ Good: Wait for UI response
controller.click(400, 300, reason="generate_mesh")
controller.wait(2.0, reason="wait_for_mesh_generation")
controller.see("mesh_generated")

# ❌ Avoid: No wait time for visual changes
controller.click(400, 300, reason="generate_mesh")
controller.see("immediate_check")  # May capture mid-transition
```

### 3. Systematic Testing
```python
# ✅ Good: Test one element at a time
for element in ui_elements:
    before = controller.see(f"before_{element.name}")
    element.test_click(controller)
    after = controller.see(f"after_{element.name}")
    element.verify_result(before, after)
```

### 4. Security Awareness
```python
# ✅ Good: Check focus success
if controller.focus_app():
    # Proceed with testing
    controller.see("app_focused")
else:
    print("Could not focus app - is it running?")

# ✅ Good: Handle security blocks gracefully
result = controller.see("test_state")
if result.get("action_type") == "observe_blocked":
    print("Security blocked - wrong window focused")
```

## Troubleshooting

### Common Issues

1. **"Could not find spaceship application window"**
   - Ensure spaceship app is running
   - Check window title matches whitelist
   - Try manually focusing the app first

2. **"SECURITY BLOCK" messages**
   - Wrong window is focused (VS Code, browser, etc.)
   - Use `controller.focus_app()` to switch to allowed window
   - Check whitelist with `controller.get_whitelist()`

3. **Empty screenshot results**
   - Security system blocked the screenshot
   - Window not in foreground
   - Application may have crashed

4. **Mouse clicks not working**
   - Coordinates may be outside window bounds
   - App window may not be focused
   - Security system may be blocking interaction

### Debug Commands
```python
# Check current session status
controller.save_session()
print(controller.get_security_summary())

# List all screenshots for session
import os
session_dir = Path("ai_sessions")
screenshots = list(session_dir.glob(f"s{controller.session_id}_*.png"))
print(f"Screenshots captured: {len(screenshots)}")
```

## Real-world Examples

The UniversalAIController has been successfully used to:

### ✅ Verified Capabilities (October 28, 2025):
1. **Focus Application**: Successfully found and focused "Spaceship Designer - Optimized"
2. **Visual Feedback**: Captured before/after screenshots of UI interactions  
3. **Mouse Control**: Clicked 3D viewport at precise coordinates (400, 350)
4. **Keyboard Control**: Toggled wireframe (W), lighting (L), and reset view (R)
5. **Security Protection**: Blocked VS Code interactions, allowed only spaceship app
6. **Session Management**: Complete audit trail saved to `ai_sessions/`

### Sample Session Output:
```
Universal AI Controller initialized - Session 094922
Focused window: Spaceship Designer - Optimized
SEE #1: before_interactions -> s094922_001_before_interactions.png  
CLICK #2: left at (400, 350) - interact_with_3d_viewport
KEY #3: 'w' - toggle_wireframe_display
KEY #4: 'l' - toggle_lighting_mode  
KEY #5: 'r' - reset_camera_view
SEE #6: after_all_interactions -> s094922_006_after_all_interactions.png
```

This tool enables AI agents to debug, test, and interact with the spaceship designer application through real-time visual feedback and precise control, making it essential for AI-driven development and testing workflows.