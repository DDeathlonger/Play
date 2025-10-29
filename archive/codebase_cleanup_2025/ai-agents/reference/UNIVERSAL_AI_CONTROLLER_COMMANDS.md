# 🎯 UNIVERSAL AI CONTROLLER - COMPLETE COMMAND REFERENCE

## **THE ONE DEFINITIVE AI CONTROL SYSTEM**

All AI agents must use **ONLY** the `UniversalAIController` for any UI interaction. This is the proven, secure system with whitelist protection, boundary enforcement, and complete visual validation.

---

## 🔒 **INITIALIZATION AND SECURITY**

```python
from universal_ai_controller import UniversalAIController

# Initialize the controller (automatic security setup)
controller = UniversalAIController()
# ✅ Creates session directory: ai_sessions/
# ✅ Initializes whitelist: ["Spaceship Designer", "Optimized Spaceship"]
# ✅ Sets up boundary constraints and speed limits
# ✅ Enables security logging and violation tracking
```

---

## 👁️ **VISUAL ANALYSIS - THE CORE COMMAND**

**The `see()` method is the foundation of all UI testing:**

```python
# MANDATORY: Use after EVERY interaction
screenshot_path = controller.see("description_of_what_you_expect_to_see")

# Returns: Full path to timestamped screenshot
# Example: "ai_sessions/s123456_001_description_of_what_you_expect_to_see.png"

# Visual validation examples:
baseline = controller.see("initial_app_state")
after_click = controller.see("button_pressed_result")  
final_state = controller.see("operation_completed")
```

**When to use `see()`:**
- ✅ **Before any interaction** - Capture baseline
- ✅ **After every click** - Confirm button response
- ✅ **After keyboard input** - Verify shortcut effects
- ✅ **During exploration** - Document current state
- ✅ **Before closing** - Capture final result

---

## 🖱️ **MOUSE CONTROL COMMANDS**

### **Click Operations:**
```python
# Left click (most common)
controller.click(x, y, reason="what_this_accomplishes")

# Right click (context menus)
controller.click(x, y, button="right", reason="open_context_menu")

# Double click
controller.click(x, y, clicks=2, reason="double_click_action")

# Example coordinates for spaceship app:
controller.click(150, 450, reason="generate_new_spaceship")  # Generate button
controller.click(150, 580, reason="export_stl_file")        # Export button
```

### **Mouse Movement:**
```python
# Move without clicking (hover effects, positioning)
controller.move_to(x, y, reason="hover_over_element")

# Smooth movement (default, human-like curves)
controller.move_to(x, y, smooth=True, reason="natural_movement")
```

### **Drag Operations:**
```python
# Drag from point A to point B
controller.drag(start_x, start_y, end_x, end_y, reason="drag_operation")

# Examples:
controller.drag(100, 200, 300, 400, reason="pan_3d_view")
controller.drag(50, 50, 150, 150, reason="select_region")
```

---

## ⌨️ **KEYBOARD CONTROL COMMANDS**

### **Single Key Presses:**
```python
# Spaceship app shortcuts:
controller.press_key('w', reason="toggle_wireframe_mode")
controller.press_key('l', reason="toggle_lighting")
controller.press_key('r', reason="reset_view_to_default")

# Navigation keys:
controller.press_key('tab', reason="navigate_to_next_field")
controller.press_key('enter', reason="confirm_action")
controller.press_key('escape', reason="close_dialog")
```

### **Key Combinations:**
```python
# Standard shortcuts:
controller.press_key('ctrl+s', reason="save_configuration")
controller.press_key('ctrl+o', reason="open_file_dialog")
controller.press_key('ctrl+z', reason="undo_last_action")
controller.press_key('alt+f4', reason="close_application")
```

### **Text Input:**
```python
# Type text strings:
controller.type_text("spaceship_config.json", reason="filename_input")
controller.type_text("Hello World", reason="text_entry")

# Clear field and type:
controller.press_key('ctrl+a', reason="select_all_text")
controller.type_text("new_value", reason="replace_text")
```

---

## 🎯 **WINDOW AND FOCUS MANAGEMENT**

### **Application Focus:**
```python
# Focus the spaceship designer (REQUIRED before any interaction)
focused = controller.focus_app()

if focused:
    print("✅ App focused - safe to proceed")
    # Continue with interactions...
else:
    print("❌ App focus failed - cannot proceed safely")
    return
```

### **Window Detection:**
```python
# Get security information:
whitelist = controller.get_whitelist()          # View allowed apps
security = controller.get_security_summary()    # Get violation report

print(f"Allowed apps: {whitelist}")
print(f"Security status: {security}")
```

---

## ⏱️ **TIMING AND FLOW CONTROL**

### **Controlled Delays:**
```python
# Wait for processing:
controller.wait(2.0, reason="allow_mesh_generation")
controller.wait(0.5, reason="ui_animation_complete")
controller.wait(1.0, reason="dialog_appear")

# Between rapid interactions:
controller.click(x, y, reason="first_action")
controller.wait(0.3, reason="prevent_double_click")
controller.click(x2, y2, reason="second_action")
```

---

## 📊 **SESSION MANAGEMENT**

### **Save Complete Session:**
```python
# Always save at the end of testing:
controller.save_session()

# This saves:
# - All screenshots with timestamps
# - Complete action log with reasons
# - Security summary and violations
# - Session metadata and statistics
```

### **Session Files Created:**
- `ai_sessions/session_HHMMSS.json` - Complete action log
- `ai_sessions/whitelist_HHMMSS.json` - Security whitelist
- `ai_sessions/sHHMMSS_NNN_description.png` - All screenshots

---

## 🚀 **COMPLETE UI TESTING WORKFLOW**

### **Standard Testing Pattern:**
```python
def test_ui_feature():
    # 1. Initialize and focus
    controller = UniversalAIController()
    if not controller.focus_app():
        return "FOCUS_FAILED"
    
    # 2. Capture baseline
    baseline = controller.see("feature_test_baseline")
    
    # 3. Perform interaction
    controller.click(150, 450, reason="test_feature_button")
    
    # 4. Capture result immediately
    result = controller.see("feature_activated")
    
    # 5. Test additional aspects
    controller.press_key('w', reason="test_wireframe_toggle")
    wireframe = controller.see("wireframe_mode_result")
    
    # 6. Save complete session
    controller.save_session()
    
    return "SUCCESS"
```

---

## 🔍 **EXPLORATION AND DISCOVERY**

### **Dynamic UI Exploration:**
```python
# Systematic exploration pattern:
controller = UniversalAIController()
controller.focus_app()

# Explore different UI areas:
areas_to_test = [
    (150, 400, "generation_controls"),
    (150, 550, "export_buttons"), 
    (300, 350, "module_settings"),
    (450, 200, "3d_viewport")
]

for x, y, description in areas_to_test:
    # Move to area
    controller.move_to(x, y, reason=f"explore_{description}")
    area_view = controller.see(f"{description}_area")
    
    # Test interaction
    controller.click(x, y, reason=f"test_{description}")
    interaction = controller.see(f"{description}_interaction")
    
    # Brief pause between areas
    controller.wait(1.0, reason="area_transition")

controller.save_session()
```

---

## 🛡️ **SECURITY AND BOUNDARIES**

### **Automatic Security Features:**
- **Boundary Enforcement**: Mouse constrained to app window bounds
- **Speed Limits**: Human-like movement (500-600px/s average)
- **Whitelist Protection**: Only spaceship apps accessible
- **Screenshot Validation**: Every image verified for security
- **Violation Logging**: Unauthorized attempts blocked and logged

### **Security Status Checking:**
```python
# Check security during session:
summary = controller.get_security_summary()
print(f"Security violations: {summary['security_violations']}")
print(f"Compliance rate: {summary['security_rate']}")

# Verify whitelist:
allowed_apps = controller.get_whitelist()
print(f"Whitelisted applications: {allowed_apps}")
```

---

## ✅ **SUCCESS CRITERIA**

A UI testing session is **successful** when:

1. ✅ **`controller.focus_app()` returns `True`**
2. ✅ **Screenshots captured after every interaction**
3. ✅ **Visual evidence confirms expected outcomes**
4. ✅ **`controller.save_session()` completes successfully**
5. ✅ **Zero security violations in session summary**

---

## 🎯 **READY-TO-USE EXAMPLES**

### **Generate New Spaceship:**
```python
controller = UniversalAIController()
controller.focus_app()
baseline = controller.see("before_generation")
controller.click(150, 450, reason="generate_new_spaceship")
result = controller.see("spaceship_generated")
controller.save_session()
```

### **Test All Keyboard Shortcuts:**
```python
controller = UniversalAIController()
controller.focus_app()

shortcuts = [('w', 'wireframe'), ('l', 'lighting'), ('r', 'reset')]
for key, feature in shortcuts:
    controller.press_key(key, reason=f"test_{feature}")
    controller.see(f"{feature}_toggle_result")

controller.save_session()
```

### **Export Functionality Test:**
```python
controller = UniversalAIController()
controller.focus_app()
controller.click(150, 580, reason="test_stl_export")
controller.see("export_dialog_opened")
controller.press_key('escape', reason="close_export_dialog")
controller.see("dialog_closed")
controller.save_session()
```

**This is the ONLY system AI agents should use for UI interaction - no exceptions!**