# Project File Structure - Organized Layout

## Current Organization (Updated October 28, 2025)

```
spaceship-designer/
├── 📁 .github/                    # GitHub and AI configuration
│   ├── copilot-instructions.md   # 🚨 PRIMARY AI INSTRUCTIONS
│   └── 📁 copilot/               # 🤖 CONSOLIDATED AI DOCUMENTATION
│       ├── 📁 context/           # AI Context & Current State
│       ├── 📁 guides/            # Development & Integration Guides
│       ├── 📁 protocols/         # AI Workflows & Validation Protocols
│       ├── 📁 reference/         # Technical Documentation & Flowcharts
│       ├── 📁 tools/             # Utilities and Generation Tools
│       ├── MASTER_DOCUMENTATION_INDEX.md    # Complete navigation index
│       ├── CONSOLIDATED_PROJECT_DOCUMENTATION.md  # Project overview
│       └── AI_DEVELOPMENT_GUIDE.md    # AI automation and visual testing
├── 📁 .venv/                     # Python virtual environment
├── 📁 .vscode/                   # VS Code workspace configuration
│   ├── launch.json              # Debug configurations (F5)
│   ├── settings.json            # Workspace settings
│   └── tasks.json               # Build and run tasks (Ctrl+Shift+P)
├── 📁 src/                       # Core application source code
│   ├── __init__.py              # Package initialization
│   ├── spaceship_designer.py    # 🚀 Main optimized application
│   ├── spaceship_advanced.py    # Legacy full-featured version
│   ├── spaceship_generator.py   # Alternative implementation
│   ├── spaceship_utils.py       # Shared utilities and components
│   └── ship.py                  # Experimental tabbed version
├── 📁 tests/                    # Test files and benchmarks
│   ├── test_spaceship.py       # Comprehensive test suite
│   └── performance_test.py      # Performance benchmarking
├── 📁 examples/                 # Example scripts and demos
│   ├── demo_spaceships.py       # Multiple ship generation examples
│   └── export_demo.py           # Command-line export demonstration
├── 📁 exports/                  # Generated 3D models and configurations
│   ├── *.stl                   # 3D printable models
│   ├── *.glb                   # Web/game engine format
│   ├── *.obj                   # General 3D software format
│   ├── *_config.json           # Spaceship configurations
│   └── *_reference.png         # Visual reference images

├── main.py                     # 🎯 Main entry point for organized structure
├── generate_flowcharts.py      # Flowchart generation utility
├── requirements.txt            # Python dependencies
├── README.md                   # User-facing documentation
├── universal_ai_controller.py  # Secure real-time AI control with intelligent visual validation
├── true_intelligent_demo.py    # Proven working AI system (Session 130512 validated)
├── max_security_ai_mcp.py     # Maximum Security MCP Server
└── generate_flowcharts.py      # Flowchart generation utility
```

## Entry Points and Usage

### Primary Entry Points
1. **`main.py`** - Organized entry point (recommended)
   - Properly handles import paths
   - Works with organized file structure
   - Run: `python main.py` or use VS Code F5

2. **`src/spaceship_designer.py`** - Direct optimized app
   - High-performance version
   - Run: `cd src && python spaceship_designer.py`

3. **`src/spaceship_advanced.py`** - Legacy full-featured app  
   - Complete original functionality
   - Run: `cd src && python spaceship_advanced.py`

### VS Code Integration
- **F5 (Debug)**: Launch "Spaceship Designer (Optimized)" configuration
- **Ctrl+Shift+P → Tasks**: Run "Run Optimized Spaceship Designer"
- **Terminal**: Automatic virtual environment activation

## File Responsibilities

### Core Application Files (`src/`)

#### `spaceship_designer.py` (648 lines) - **PRIMARY APP**
```python
# Main classes and responsibilities:
- OptimizedSpaceshipApp         # Main window and application
- HighPerformanceViewer         # OpenGL 3D rendering with GPU optimization  
- SimplifiedControlPanel        # Streamlined UI controls
- OptimizedSpaceshipGenerator   # Fast mesh generation with caching
```

#### `spaceship_utils.py` (380+ lines) - **SHARED UTILITIES**
```python
# Utility classes and functions:
- SpaceshipGeometryNode        # Data class for spaceship components
- MeshUtils                    # 3D primitive creation and transformation
- ConfigUtils                  # JSON save/load and default ship generation
- PerformanceUtils             # Optimization and GPU detection
```

#### `spaceship_advanced.py` (1130 lines) - **LEGACY VERSION**
```python
# Complete original implementation:
- SpaceshipViewer              # Full-featured OpenGL viewer
- ControlWidget                # Complete UI with all controls
- SpaceshipGenerator           # Original mesh generation logic
- InfoWidget                   # Detailed statistics and information
```

### Configuration and Setup

#### `.vscode/launch.json` - **DEBUG CONFIGURATIONS**
- Spaceship Designer (Optimized) - Main app debugging
- Legacy Spaceship App - Original version debugging  
- Export Demo - Command-line demo
- Run Tests - Test suite execution

#### `.vscode/tasks.json` - **BUILD TASKS**
- Run Optimized Spaceship Designer (default build task)
- Run Legacy Spaceship App
- Run Tests
- Export Demo
- Generate Flowcharts
- Install Dependencies

#### `.vscode/settings.json` - **WORKSPACE SETTINGS**
- Python interpreter configuration
- Virtual environment auto-activation
- Code formatting and linting
- IntelliSense configuration

## Performance Characteristics

### File Sizes and Complexity
```
spaceship_designer.py:    648 lines  │ Optimized, streamlined
spaceship_advanced.py:   1130 lines  │ Full-featured, comprehensive
spaceship_utils.py:      380+ lines  │ Shared utilities
spaceship_generator.py:   792 lines  │ Alternative implementation
ship.py:                  994 lines  │ Experimental version
```

### Runtime Performance
```
Optimized Version:
- Startup: ~0.5 seconds
- Memory: ~40MB
- Mesh: 424 vertices, 736 faces
- FPS: 30+ smooth rendering

Legacy Version:
- Startup: ~2-3 seconds  
- Memory: ~80MB
- Mesh: 33k+ vertices, 61k+ faces
- FPS: 20 with occasional lag
```

## Import Structure

### Organized Import Paths
```python
# From root directory (main.py):
sys.path.insert(0, 'src')
import spaceship_designer

# Within src/ package:
from .spaceship_utils import SpaceshipGeometryNode  # Relative import
from spaceship_utils import MeshUtils                # Absolute import (fallback)

# From examples/ or tests/:
sys.path.insert(0, '../src')  # Add src to path
from spaceship_designer import OptimizedSpaceshipGenerator
```

### VS Code Python Path Configuration
```json
"python.analysis.extraPaths": ["."],
"terminal.integrated.env.windows": {
    "PYTHONPATH": "${workspaceFolder};${workspaceFolder}\\src"
}
```

## Development Workflow

### Recommended Development Process
1. **Start VS Code**: `code .` from project root
2. **Run Application**: F5 or Ctrl+Shift+P → "Run Optimized Spaceship Designer"
3. **Make Changes**: Edit files in `src/` directory
4. **Test Changes**: Use VS Code tasks or F5 debugging
5. **Update Documentation**: Refresh `.github/copilot/context/` if needed

### File Modification Guidelines
- **UI Changes**: Edit `src/spaceship_designer.py`
- **Mesh Logic**: Edit `src/spaceship_utils.py` 
- **New Features**: Add to appropriate utility classes
- **Tests**: Add to `tests/` directory
- **Examples**: Add to `examples/` directory

### AI Context Integration

### AI Workflow Integration Points
1. **Context Check**: Always read `.github/copilot-instructions.md` first
2. **Pattern Reference**: Check `.github/copilot/context/development_patterns.md`  
3. **Visual Process**: Review `.github/copilot/reference/flowcharts/ai_iteration_process.png`
4. **Update Documentation**: Refresh copilot context after changes

### Reference Material Locations
- **Primary AI Instructions**: `.github/copilot-instructions.md`
- **AI Context**: `.github/copilot/context/`
- **Process Diagrams**: `.github/copilot/reference/flowcharts/`
- **Development Guides**: `.github/copilot/guides/`
- **AI Protocols**: `.github/copilot/protocols/`

This organized structure ensures maintainable, performant, and well-documented code that's ready for continued development and AI-assisted iteration!