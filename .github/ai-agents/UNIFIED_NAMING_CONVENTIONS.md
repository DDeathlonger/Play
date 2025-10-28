# 🎯 UNIFIED NAMING CONVENTIONS - SPACESHIP DESIGNER PROJECT
## MANDATORY STANDARD FOR ALL AI AGENTS AND DEVELOPERS

*Updated October 28, 2025 - Applied Across Entire Project*

---

## 📋 **COMPLETE NAMING STANDARD**

### **1. FILE NAMING CONVENTIONS**

#### **Python Files (.py)**
- **Format**: `snake_case.py` 
- **Pattern**: `module_name.py`, `feature_description.py`
- **Examples**:
  - ✅ `spaceship_designer.py`
  - ✅ `spaceship_advanced_legacy.py` 
  - ✅ `max_security_ai_mcp.py`
  - ✅ `universal_ai_controller.py`
  - ❌ `SpaceshipDesigner.py` (avoid CamelCase files)
  - ❌ `spaceship-designer.py` (avoid hyphens)

#### **Configuration Files**
- **JSON**: `snake_case_config.json`
- **Examples**: `spaceship_config.json`, `ai_session_config.json`

#### **Documentation Files (.md)**
- **Format**: `SCREAMING_SNAKE_CASE.md` for major docs, `snake_case.md` for regular
- **Examples**:
  - ✅ `README.md`, `UNIFIED_NAMING_CONVENTIONS.md`
  - ✅ `development_patterns.md`, `file_structure.md`

### **2. DIRECTORY NAMING CONVENTIONS**

#### **Directory Structure**
- **Format**: `snake_case/` for all directories
- **Examples**:
  - ✅ `src/` (core application)
  - ✅ `tests/` (test files)
  - ✅ `examples/` (example scripts)
  - ✅ `ai_sessions/` (AI automation logs)
  - ✅ `.github/ai-agents/` (special case: kebab-case for GitHub)

### **3. PYTHON CODE NAMING CONVENTIONS**

#### **Class Names**
- **Format**: `CamelCase` (PascalCase)
- **Pattern**: `FeatureNameClass`, `SystemComponentName`
- **Examples**:
  ```python
  ✅ class SpaceshipModule:
  ✅ class OptimizedSpaceshipGenerator:
  ✅ class HighPerformanceViewer:
  ✅ class MaxSecurityAIMCP:
  ✅ class UniversalAIController:
  ✅ class SecureMCPClient:
  
  ❌ class spaceship_module:     # Wrong - use CamelCase
  ❌ class SPACESHIP_MODULE:     # Wrong - not for classes
  ```

#### **Function Names**
- **Format**: `snake_case()`
- **Pattern**: `action_description()`, `get_something()`, `create_something()`
- **Examples**:
  ```python
  ✅ def generate_mesh():
  ✅ def create_primitive():
  ✅ def apply_module_transform():
  ✅ def secure_click():
  ✅ def analyze_workspace_with_mcp():
  ✅ def get_user_files():
  
  ❌ def GenerateMesh():          # Wrong - use snake_case
  ❌ def createPrimitive():       # Wrong - not camelCase
  ```

#### **Method Names** 
- **Format**: `snake_case()` (same as functions)
- **Private Methods**: `_snake_case()` (leading underscore)
- **Examples**:
  ```python
  ✅ def save_configuration(self):
  ✅ def load_configuration(self):
  ✅ def _internal_helper_method(self):
  ✅ def _security_check(self):
  ```

#### **Variable Names**
- **Format**: `snake_case`
- **Pattern**: `descriptive_name`, `feature_value`
- **Examples**:
  ```python
  ✅ grid_size = (8, 5, 12)
  ✅ mesh_vertices = []
  ✅ session_id = "123456"
  ✅ action_count = 0
  ✅ window_whitelist = []
  
  ❌ gridSize = (8, 5, 12)       # Wrong - use snake_case
  ❌ MeshVertices = []           # Wrong - not for variables
  ```

#### **Parameter Names**
- **Format**: `snake_case`
- **Pattern**: Match variable naming exactly
- **Examples**:
  ```python
  ✅ def create_mesh(grid_size, mesh_type, color_values):
  ✅ def secure_click(x_coord, y_coord, button_type="left"):
  ✅ def analyze_workspace(workspace_root, file_pattern):
  
  ❌ def create_mesh(gridSize, meshType):    # Wrong - use snake_case
  ```

#### **Constants**
- **Format**: `SCREAMING_SNAKE_CASE`
- **Pattern**: `FEATURE_CONSTANT`, `DEFAULT_VALUE`
- **Examples**:
  ```python
  ✅ DEFAULT_GRID_SIZE = (8, 5, 12)
  ✅ CONFIG_FILE = "spaceship_config.json"
  ✅ QT_VERSION = 6
  ✅ MAX_MESH_VERTICES = 10000
  ✅ AI_SESSION_DIR = "ai_sessions"
  
  ❌ default_grid_size = (8, 5, 12)  # Wrong - use SCREAMING_SNAKE_CASE
  ❌ DefaultGridSize = (8, 5, 12)    # Wrong - not for constants
  ```

#### **Module-Level Variables**
- **Format**: `snake_case` (if not constant)
- **Examples**:
  ```python
  ✅ current_session = None
  ✅ active_generator = None
  ```

### **4. AI SYSTEM SPECIFIC CONVENTIONS**

#### **AI Controller Classes**
- **Pattern**: `PurposeAIController` or `SystemTypeAI`
- **Examples**:
  ```python
  ✅ class UniversalAIController:
  ✅ class MaxSecurityAIMCP:
  ✅ class AutonomousAIController:
  ✅ class StrategicUIController:
  ```

#### **MCP Integration Names**
- **Pattern**: `mcp_operation_name()`, `secure_mcp_action()`
- **Examples**:
  ```python
  ✅ def get_workspace_info():
  ✅ def check_syntax_errors():
  ✅ def run_safe_code_snippet():
  ✅ def analyze_workspace_with_mcp():
  ```

#### **Security Method Names**
- **Pattern**: `secure_action()`, `_security_check()`
- **Examples**:
  ```python
  ✅ def secure_see():
  ✅ def secure_click():
  ✅ def _security_check():
  ✅ def _validate_whitelist():
  ```

### **5. UI COMPONENT NAMING**

#### **Qt Widget Classes**
- **Pattern**: `FeaturePurposeWidget`, `ComponentNameViewer`
- **Examples**:
  ```python
  ✅ class HighPerformanceViewer(QOpenGLWidget):
  ✅ class SimplifiedControlPanel(QWidget):
  ✅ class OptimizedSpaceshipApp(QMainWindow):
  ```

#### **UI Method Names**
- **Pattern**: `action_description()`, `on_event_triggered()`
- **Examples**:
  ```python
  ✅ def on_new_ship_clicked():
  ✅ def update_mesh_display():
  ✅ def toggle_wireframe_mode():
  ```

### **6. TEST FILE CONVENTIONS**

#### **Test File Names**
- **Pattern**: `test_feature_name.py`
- **Examples**:
  ```python
  ✅ test_spaceship.py
  ✅ test_performance.py
  ✅ test_ai_controller.py
  ✅ test_mcp_integration.py
  ```

#### **Test Function Names**
- **Pattern**: `test_specific_functionality()`
- **Examples**:
  ```python
  ✅ def test_spaceship_module():
  ✅ def test_mesh_generation():
  ✅ def test_config_management():
  ✅ def test_ai_security_validation():
  ```

### **7. EXPORT AND CONFIGURATION CONVENTIONS**

#### **Export File Names**
- **Pattern**: `descriptive_name_timestamp.extension`
- **Examples**:
  ```python
  ✅ "spaceship_config.json"
  ✅ "demo_spaceship_reference.png"
  ✅ "test_spaceship.stl"
  ```

#### **Configuration Keys (JSON)**
- **Format**: `snake_case` for consistency with Python
- **Examples**:
  ```json
  ✅ {
    "grid_size": [8, 5, 12],
    "mesh_type": "optimized",
    "export_format": "stl"
  }
  ```

---

## 🎯 **IMPLEMENTATION CHECKLIST**

### **✅ COMPLETED UPDATES:**
1. **Core Application Files (`src/`)**
   - All class names standardized to CamelCase
   - All function names standardized to snake_case
   - All constants standardized to SCREAMING_SNAKE_CASE
   - All variables standardized to snake_case

2. **AI System Files**
   - Security method names standardized
   - MCP integration names standardized
   - Controller class names standardized

3. **Test and Example Files**
   - Test function names standardized
   - Example script names standardized

4. **Documentation Files**
   - All references updated to new naming conventions
   - File structure documentation updated

---

## 🤖 **AI AGENT COMPLIANCE**

### **MANDATORY FOR ALL AI AGENTS:**

#### **When Creating New Files:**
```python
# ✅ CORRECT - Follow naming conventions
def create_new_feature():
    file_name = "feature_description.py"
    class_name = "FeatureController" 
    function_name = "process_feature_data"
    constant_name = "MAX_FEATURE_SIZE"
```

#### **When Reading Existing Code:**
- **ALWAYS** use the standardized names when referencing classes/functions
- **ALWAYS** follow snake_case for new variables and functions
- **ALWAYS** use CamelCase for new classes

#### **When Updating Documentation:**
- **ALWAYS** update references to match new naming conventions
- **ALWAYS** ensure consistency across all documentation files

#### **When Testing AI Systems:**
- **ALWAYS** use standardized method names for MCP integration
- **ALWAYS** follow security naming patterns for AI controllers

---

## 🔒 **SECURITY INTEGRATION NAMES**

### **MCP Server Connection:**
```python
✅ secure_mcp_client = SecureMCPClient()
✅ workspace_info = secure_mcp_client.get_workspace_info()
✅ syntax_errors = secure_mcp_client.check_syntax_errors(file_path)
```

### **AI Navigation:**
```python
✅ ai_controller = UniversalAIController()
✅ screenshot_path = ai_controller.see("ui_state")
✅ ai_controller.secure_click(x_coord, y_coord)
```

---

## ✨ **FINAL NOTES**

This naming convention standard ensures:
- **Consistency** across all project files
- **Readability** for both humans and AI agents
- **Maintainability** for future development
- **Security clarity** for AI automation systems
- **MCP integration compatibility** for all agents

**ALL AI AGENTS MUST FOLLOW THESE CONVENTIONS WHEN:**
- Creating new files or classes
- Modifying existing code
- Writing documentation
- Testing systems
- Implementing new features

*This standard is now applied project-wide and must be maintained going forward.*