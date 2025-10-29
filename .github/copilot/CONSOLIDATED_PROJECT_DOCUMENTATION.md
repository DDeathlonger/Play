# SPACESHIP DESIGNER PROJECT - CONSOLIDATED DOCUMENTATION

## 📖 OVERVIEW

This is a **3D spaceship modeling application** with **autonomous AI control capabilities** built with PyQt6, OpenGL, and advanced AI automation systems. The project includes both the core application and sophisticated AI testing/control systems.

## 🎯 QUICK START

### Single Entry Point
**ALWAYS use this exact command - NO VARIATIONS:**

```bash
C:/Users/dante/OneDrive/Desktop/Play/.venv/Scripts/python.exe spaceship.py
```

### What You Get
- **High-performance 3D GUI** with GPU acceleration detection
- **Real-time mesh generation** (~400 vertices, 700 faces - 60% faster than legacy)
- **MCP Server Integration** with AI automation capabilities
- **Multiple export formats**: STL, GLB, OBJ, PLY
- **Interactive controls**: rotate, pan, zoom, wireframe modes
- **Configuration persistence**: JSON save/load
- **VS Code integration**: Launch configs, tasks, debugging

## 🏗️ ARCHITECTURE

### Core Architecture
- **`spaceship.py`** - Single designated entry point
- **`src/spaceship_designer.py`** - Main application with MCP integration
- **`src/spaceship_utils.py`** - Shared utilities and mesh generation
- **`tests/`** - Consolidated test suite  
- **`.github/copilot/`** - AI documentation and instructions
- **`app_components/`** - Application features (UI system, ship generation, display)

### AI Automation Components
- **Maximum Security MCP Server** - Port 8765 with whitelist protection  
- **Universal AI Controller** - Screenshot-based intelligent interaction
- **Autonomous Testing** - Self-validating UI interaction cycles

### Performance Specifications
- **Startup**: ~0.5 seconds
- **Memory**: ~40MB
- **Mesh**: 424 vertices, 736 faces
- **FPS**: 30+ smooth rendering
- **Export**: STL, GLB, OBJ, PLY formats

## 🎮 CONTROLS

### Mouse Controls
- **Left Mouse + Drag**: Rotate view
- **Right Mouse + Drag**: Pan view
- **Mouse Wheel**: Zoom in/out

### Keyboard Shortcuts
- **W**: Toggle wireframe mode
- **L**: Toggle lighting
- **R**: Reset view to default

### UI Controls
- **Generate**: Create new random spaceship
- **Clear**: Remove all modules
- **Export**: Save as 3D file format
- **Save/Load**: Configuration persistence

## 🔧 DEVELOPMENT

### Dependencies
- PyQt6 (GUI framework)
- OpenGL (3D graphics)
- trimesh (3D mesh processing)
- numpy (numerical computing)
- requests (HTTP client for MCP)

### VS Code Integration
- **F5**: Debug launch "Spaceship Designer (Optimized)"
- **Ctrl+Shift+P**: Tasks → "Run Optimized Spaceship Designer"
- **Virtual Environment**: `.venv/Scripts/python.exe` (auto-activated)

### Testing
```bash
# Run consolidated tests
python tests/test_spaceship.py

# AI automation test
python demos_and_tests/ui_tests/true_intelligent_demo.py
```

## 🤖 AI AUTOMATION

### Intelligent Visual System
The project includes a sophisticated AI system that can:
- Take screenshots and analyze UI state
- Make intelligent decisions based on visual analysis
- Interact with the application through mouse/keyboard
- Maintain complete audit trails with security logging

### MCP Integration
- **Server**: Automatically starts on port 8765
- **Endpoints**: `/health`, `/commands`, `/status`
- **Commands**: `see`, `click`, `move_to`, `press_key`, `focus_app`
- **Security**: Whitelist protection, boundary constraints

## 📋 PROJECT STATUS

### ✅ Fully Working
- 3D spaceship generation with grid-based procedural system
- Real-time mesh editing with immediate visual feedback
- Export system (STL for 3D printing, GLB for games, OBJ for CAD)
- Configuration persistence (JSON save/load)
- Interactive 3D controls (mouse/keyboard navigation)
- Performance optimization (60% faster than legacy, GPU detection)
- MCP server integration with AI automation
- Secure AI control system with screenshot analysis

### 📈 Performance Metrics
- **Optimized Version**: 424 vertices, 736 faces, ~40MB memory
- **Legacy Version**: 33k+ vertices, 61k+ faces, ~80MB memory
- **AI System**: <1s screenshot capture, strategic targeting
- **Export**: Multiple formats with fast generation

## 🛡️ SECURITY

### AI System Security
- **Whitelist Protection**: Only "Spaceship Designer" apps accessible
- **Boundary Constraints**: Mouse locked to app window bounds
- **Speed Limits**: Human-like movement (500-600px/s)
- **Violation Logging**: All unauthorized attempts tracked
- **Session Auditing**: Complete action history with timestamps

### MCP Server Security
- **Port Management**: Automatic conflict resolution
- **Thread Safety**: Proper Qt event loop integration
- **Error Handling**: Graceful degradation and recovery
- **Connection Limits**: Controlled client access

## 🎯 NAMING CONVENTIONS

### Files
- **snake_case.py** for Python files
- **kebab-case.md** for documentation
- **PascalCase** for classes
- **camelCase** for methods (where appropriate)

### Variables & Functions
- **snake_case** for variables and functions
- **SCREAMING_SNAKE_CASE** for constants
- **CamelCase** for classes

## 📚 ADDITIONAL RESOURCES

### Documentation Structure
- **`.github/copilot/`** - AI instructions and reference
- **`tests/`** - Test documentation and examples
- **`demos_and_tests/`** - Working demonstrations
- **`archive/`** - Legacy code and references

### Key Files
- **`copilot-instructions.md`** - Comprehensive AI agent instructions
- **`test_spaceship.py`** - Main test suite
- **`true_intelligent_demo.py`** - AI automation demonstration

This documentation consolidates all essential information while maintaining clarity and structure for both human developers and AI agents.