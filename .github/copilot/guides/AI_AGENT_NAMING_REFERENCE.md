# 🤖 AI AGENT NAMING CONVENTION REFERENCE
## Quick Reference Guide for All AI Agents

*Updated October 28, 2025 - Post Naming Convention Consolidation*

---

## 🎯 **ESSENTIAL NAMING PATTERNS FOR AI AGENTS**

### **1. SECURE MCP CLIENT INTEGRATION**

#### **Initialization (Standard Pattern):**
```python
from secure_mcp_client import SecureMCPClient

# ✅ CORRECT - Use snake_case variables
workspace_root = "c:/Users/dante/OneDrive/Desktop/Play"
secure_mcp_client = SecureMCPClient(workspace_root=workspace_root)
```

#### **Core MCP Methods (All snake_case):**
```python
# Workspace operations
workspace_info = secure_mcp_client.get_workspace_info()
user_files = secure_mcp_client.get_user_files()
python_env = secure_mcp_client.get_python_environment_info()

# Code validation
syntax_errors = secure_mcp_client.check_syntax_errors(file_path)
code_result = secure_mcp_client.run_safe_code_snippet(code_snippet, context)

# Security
security_summary = secure_mcp_client.get_security_summary()
```

### **2. UNIVERSAL AI CONTROLLER INTEGRATION**

#### **Initialization (Standard Pattern):**
```python  
from universal_ai_controller import UniversalAIController

# ✅ CORRECT - Use snake_case variables
ai_controller = UniversalAIController()
session_id = ai_controller.session_id
```

#### **Visual Analysis Methods:**
```python
# Take screenshots with descriptive context
screenshot_path = ai_controller.see("ui_state_analysis")
screenshot_path = ai_controller.see("before_button_click") 
screenshot_path = ai_controller.see("after_mesh_generation")
```

#### **Navigation Methods:**
```python
# Mouse control with coordinate variables
mouse_x, mouse_y = 400, 300
ai_controller.click(mouse_x, mouse_y, reason="generate_new_spaceship")
ai_controller.drag(start_x, start_y, end_x, end_y, reason="rotate_viewport")

# Keyboard control
ai_controller.press_key('w', reason="toggle_wireframe")
ai_controller.type_text("test_ship", reason="enter_filename")

# Window management
app_focused = ai_controller.focus_app()
```

### **3. MAXIMUM SECURITY AI MCP SYSTEM**

#### **Initialization (Standard Pattern):**
```python
from max_security_ai_mcp import MaxSecurityAIMCP

# ✅ CORRECT - Use snake_case variables
max_security_ai = MaxSecurityAIMCP()
system_status = max_security_ai.start_secure_system()
```

#### **Secure Operations:**
```python
# Automated spaceship generation
generation_result = max_security_ai.autonomous_spaceship_generation()

# UI testing with security
test_results = max_security_ai.comprehensive_ui_testing()

# MCP workspace analysis
workspace_analysis = max_security_ai.analyze_workspace_with_mcp()

# Security stress testing
stress_results = max_security_ai.stress_test_security_system()
```

### **4. CORE APPLICATION INTEGRATION**

#### **Spaceship Designer Classes (CamelCase):**
```python
# ✅ CORRECT - Core application classes
from spaceship_designer import OptimizedSpaceshipGenerator, DEFAULT_GRID_SIZE
from spaceship_utils import SpaceshipGeometryNode, MeshUtils, ConfigUtils

# Initialization with snake_case variables
grid_size = DEFAULT_GRID_SIZE
spaceship_generator = OptimizedSpaceshipGenerator(grid_size)
```

#### **Mesh Operations (snake_case methods):**
```python
# Generate and manipulate meshes
generated_mesh = spaceship_generator.generate_mesh()
export_result = spaceship_generator.export_mesh("spaceship_model.stl")

# Configuration management
config_saved = spaceship_generator.save_configuration("ship_config.json")
config_loaded = spaceship_generator.load_configuration("ship_config.json")
```

#### **Utility Functions (snake_case):**
```python  
# Mesh utilities
primitive_mesh = MeshUtils.create_simple_primitive("cylinder", radius=0.5, height=1.0)
transformed_mesh = MeshUtils.apply_module_transform(mesh, module, world_position)

# Configuration utilities  
default_grid = ConfigUtils.create_default_grid(grid_size)
random_ship = ConfigUtils.generate_random_ship(grid_size)
```

---

## 🔒 **SECURITY INTEGRATION PATTERNS**

### **Secure File Operations:**
```python
# ✅ Always use secure patterns for file operations
file_path = "src/spaceship_designer.py"
syntax_check = secure_mcp_client.check_syntax_errors(file_path)

# Code execution with containment
code_snippet = "print('Hello from secure environment')"
execution_context = "secure_test_environment"
code_result = secure_mcp_client.run_safe_code_snippet(code_snippet, execution_context)
```

### **UI Automation with Security:**
```python
# ✅ Always validate window focus before UI operations
if ai_controller.focus_app():
    # Take screenshot to see current state
    current_state = ai_controller.see("pre_interaction_state")
    
    # Perform secure UI interaction
    ai_controller.secure_click(button_x, button_y, reason="test_functionality")
    
    # Verify result with another screenshot  
    post_state = ai_controller.see("post_interaction_state")
else:
    print("❌ Security violation: Target application not focused")
```

---

## 📝 **VARIABLE NAMING PATTERNS**

### **Coordinates and Positions:**
```python
# ✅ CORRECT - Descriptive coordinate names
button_x, button_y = 156, 347
start_x, start_y = 100, 100  
end_x, end_y = 200, 200
mouse_x, mouse_y = 400, 300

# ✅ CORRECT - Position tuples
grid_position = (x_index, y_index, z_index)
world_position = (world_x, world_y, world_z)
```

### **File and Path Variables:**
```python
# ✅ CORRECT - Descriptive file names  
workspace_root = "c:/Users/dante/OneDrive/Desktop/Play"
config_file_path = "spaceship_config.json"
screenshot_path = "ai_sessions/screenshot_123456.png"
export_file_name = "generated_spaceship.stl"
```

### **Session and State Variables:**
```python
# ✅ CORRECT - Session management
session_id = "114819"
action_count = 0
security_violations = 0
is_running = True
whitelist_verified = False
```

---

## ⚡ **QUICK INTEGRATION EXAMPLES**

### **Complete AI Workflow Pattern:**
```python
# Initialize all systems with standard naming
from universal_ai_controller import UniversalAIController
from secure_mcp_client import SecureMCPClient
from max_security_ai_mcp import MaxSecurityAIMCP

# Setup with snake_case variables
workspace_root = "c:/Users/dante/OneDrive/Desktop/Play"
ai_controller = UniversalAIController()
mcp_client = SecureMCPClient(workspace_root)
security_system = MaxSecurityAIMCP()

# Typical workflow
if ai_controller.focus_app():
    # Visual analysis
    current_state = ai_controller.see("workflow_start")
    
    # MCP workspace analysis  
    workspace_files = mcp_client.get_user_files()
    
    # Secure automated actions
    test_results = security_system.comprehensive_ui_testing()
    
    # Final verification
    final_state = ai_controller.see("workflow_complete")
```

### **Error Handling Pattern:**
```python
# ✅ CORRECT - Standardized error handling
try:
    # Attempt secure operation with standard naming
    generation_result = max_security_ai.autonomous_spaceship_generation()
    
except SecurityError as security_err:
    print(f"🔒 Security error: {security_err}")
    
except Exception as general_err:
    print(f"❌ General error: {general_err}")
    
finally:
    # Always save session with standard method name
    ai_controller.save_session()
```

---

## 🎯 **CRITICAL REMINDERS FOR ALL AI AGENTS**

### **✅ ALWAYS USE:**
1. **snake_case** for all variables, functions, and method names
2. **CamelCase** for all class names  
3. **SCREAMING_SNAKE_CASE** for all constants
4. **Descriptive names** that clearly indicate purpose
5. **Standard patterns** shown in this guide

### **❌ NEVER USE:**
1. **camelCase** for variables or functions (wrong for Python)
2. **snake_case** for class names (wrong for Python conventions) 
3. **Abbreviated names** that are unclear (e.g., `btn`, `img`, `cfg`)
4. **Mixed conventions** within the same codebase
5. **Non-standard patterns** not documented in this guide

### **🔒 SECURITY REQUIREMENTS:**
1. **Always** use `SecureMCPClient` for MCP operations
2. **Always** validate window focus before UI automation
3. **Always** use descriptive `reason` parameters for actions
4. **Always** take screenshots for visual confirmation
5. **Always** save session logs with standard method names

---

## 📚 **COMPLETE DOCUMENTATION REFERENCES**

- **Full Naming Standards**: `.github/copilot/context/UNIFIED_NAMING_CONVENTIONS.md`
- **Project Instructions**: `.github/copilot-instructions.md`
- **File Structure**: `.github/copilot/reference/file_structure.md`
- **Development Patterns**: `.github/copilot/context/development_patterns.md`

*This guide ensures all AI agents use consistent, secure, and maintainable naming patterns throughout the Spaceship Designer project.*