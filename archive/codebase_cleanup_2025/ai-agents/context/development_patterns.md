# AI Context - Development Patterns and Best Practices

## Code Organization Patterns

### File Structure Conventions
```
spaceship-designer/
├── src/                    # Core application code
│   ├── __init__.py        # Package initialization
│   ├── spaceship_designer.py   # Main optimized app
│   ├── spaceship_advanced.py   # Legacy full-featured app
│   └── spaceship_utils.py      # Shared utilities
├── tests/                  # Test files
├── examples/              # Example scripts and demos
├── exports/               # Generated 3D models and configs
├── .github/ai-agents/     # Documentation and AI context
│   ├── ai-context/       # AI-specific documentation
│   └── flowcharts/       # Process diagrams
├── .vscode/              # VS Code configuration
├── .github/              # GitHub and AI instructions
└── main.py               # Entry point
```

### Import Pattern Rules
1. **Relative imports within src/ package**: `from .module import Class`
2. **Absolute imports for external libraries**: `import numpy as np`
3. **Add src/ to Python path in entry points**: `sys.path.insert(0, 'src')`

### Naming Conventions
- **Files**: lowercase_with_underscores.py
- **Classes**: CamelCase (SpaceshipGenerator)
- **Functions**: lowercase_with_underscores()
- **Constants**: UPPER_CASE_WITH_UNDERSCORES
- **Variables**: lowercase_with_underscores

## Performance Optimization Patterns

### Mesh Generation Best Practices
```python
# ✅ Good - Low polygon primitives for real-time editing
mesh = trimesh.primitives.Cylinder(radius=r, height=h, sections=8)

# ❌ Avoid - High polygon count for interactive use
mesh = trimesh.primitives.Cylinder(radius=r, height=h, sections=32)
```

### Caching Pattern
```python
class OptimizedSpaceshipGenerator:
    def __init__(self):
        self.cached_mesh = None
        self.mesh_dirty = True
    
    def generate_mesh(self, use_cache=True):
        if use_cache and not self.mesh_dirty and self.cached_mesh:
            return self.cached_mesh
        # ... generate mesh
        self.cached_mesh = result
        self.mesh_dirty = False
        return result
```

### GPU Optimization Pattern
```python
# Check for hardware acceleration
def is_gpu_available():
    try:
        from OpenGL.GL import glGetString, GL_RENDERER
        renderer = glGetString(GL_RENDERER)
        return b'software' not in renderer.lower()
    except:
        return False

# Use vertex arrays for performance
glEnableClientState(GL_VERTEX_ARRAY)
glVertexPointer(3, GL_FLOAT, 0, vertices)
glDrawElements(GL_TRIANGLES, len(faces) * 3, GL_UNSIGNED_INT, faces)
```

## Error Handling Patterns

### Graceful Fallbacks
```python
def create_primitive(prim_type, radius, height):
    try:
        if prim_type == "cylinder":
            return trimesh.primitives.Cylinder(radius=radius, height=height, sections=8)
        elif prim_type == "cone":
            # Manual cone creation if primitive not available
            cylinder = trimesh.primitives.Cylinder(radius=radius, height=height, sections=8)
            vertices = cylinder.vertices.copy()
            # Taper top vertices
            for i, vertex in enumerate(vertices):
                if vertex[2] > 0:
                    vertices[i][0] *= 0.1
                    vertices[i][1] *= 0.1
            return trimesh.Trimesh(vertices=vertices, faces=cylinder.faces)
    except Exception as e:
        print(f"Error creating primitive {prim_type}: {e}")
        # Always return a valid mesh
        return trimesh.primitives.Box(extents=[radius*2, radius*2, height])
```

### Qt Import Pattern
```python
# Try PyQt6 first, fallback to PyQt5
try:
    from PyQt6.QtWidgets import *
    from PyQt6.QtGui import *
    from PyQt6.QtCore import *
    from PyQt6.QtOpenGLWidgets import QOpenGLWidget
    QT_VERSION = 6
except ImportError:
    try:
        from PyQt5.QtWidgets import *
        from PyQt5.QtGui import *
        from PyQt5.QtCore import *
        from PyQt5.QtOpenGL import QOpenGLWidget
        QT_VERSION = 5
    except ImportError:
        print("Error: Neither PyQt6 nor PyQt5 found!")
        sys.exit(1)
```

## UI Design Patterns

### Simplified Control Panel Pattern
```python
class SimplifiedControlPanel(QWidget):
    def __init__(self, generator, viewer):
        super().__init__()
        self.generator = generator
        self.viewer = viewer
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Group related controls
        pos_group = QGroupBox("Position")
        props_group = QGroupBox("Properties") 
        actions_group = QGroupBox("Actions")
        
        # Keep controls minimal and focused
        layout.addWidget(pos_group)
        layout.addWidget(props_group)
        layout.addWidget(actions_group)
```

### Real-time Update Pattern
```python
def update_module(self):
    """Update module and refresh display"""
    module = SpaceshipModule(
        type=self.type_combo.currentText(),
        enabled=self.enabled_check.isChecked(),
        radius=self.radius_spin.value()
    )
    self.generator.update_module(self.current_position, module)
    self.refresh_mesh()  # Immediate visual feedback

def refresh_mesh(self):
    """Refresh 3D display"""
    mesh = self.generator.generate_mesh()
    self.viewer.update_mesh(mesh)
```

## VS Code Integration Patterns

### Launch Configuration Pattern
```json
{
    "name": "App Name",
    "type": "debugpy",
    "request": "launch",
    "program": "${workspaceFolder}/path/to/script.py",
    "console": "integratedTerminal",
    "cwd": "${workspaceFolder}",
    "env": {
        "PYTHONPATH": "${workspaceFolder}"
    },
    "python": "${workspaceFolder}/.venv/Scripts/python.exe"
}
```

### Task Definition Pattern
```json
{
    "label": "Task Name",
    "type": "shell",
    "command": "${workspaceFolder}/.venv/Scripts/python.exe",
    "args": ["script.py"],
    "group": {
        "kind": "build",
        "isDefault": true
    },
    "presentation": {
        "echo": true,
        "reveal": "always",
        "panel": "shared"
    }
}
```

## Data Management Patterns

### Configuration Pattern
```python
@staticmethod
def save_grid_config(grid, filename):
    """Save grid configuration with error handling"""
    try:
        config_data = {}
        for position, module in grid.items():
            if module.enabled:
                key = f"{position[0]},{position[1]},{position[2]}"
                config_data[key] = module.to_dict()
        
        with open(filename, 'w') as f:
            json.dump(config_data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving configuration: {e}")
        return False
```

### Default Ship Generation Pattern
```python
def create_default_grid(grid_size):
    """Create recognizable spaceship shape"""
    nx, ny, nz = grid_size
    grid = {}
    center_x, center_y = nx // 2, ny // 2
    
    # Initialize all as disabled
    for x in range(nx):
        for y in range(ny):
            for z in range(nz):
                grid[(x, y, z)] = SpaceshipModule(enabled=False)
    
    # Main fuselage - creates recognizable ship shape
    for z in range(1, nz - 1):
        size_factor = 1.0 - abs(z - nz//2) / (nz//2) * 0.3
        grid[(center_x, center_y, z)] = SpaceshipModule(
            type="cylinder", radius=0.5 * size_factor, 
            color=[120, 140, 180], enabled=True
        )
    
    # Engines at rear
    grid[(center_x, center_y, 0)] = SpaceshipModule(
        type="cylinder", radius=0.7, height=0.6,
        color=[255, 100, 50], enabled=True
    )
    
    # Nose/cockpit at front
    grid[(center_x, center_y, nz-1)] = SpaceshipModule(
        type="cone", radius=0.4, height=0.8,
        color=[100, 150, 200], enabled=True
    )
```

## Testing Patterns

### Performance Test Pattern
```python
def test_performance():
    """Benchmark key operations"""
    import time
    
    # Test mesh generation speed
    start_time = time.time()
    for i in range(100):
        mesh = MeshUtils.create_simple_primitive("cylinder", 0.5, 1.0)
    end_time = time.time()
    
    print(f"Generated 100 primitives in {end_time - start_time:.3f}s")
    print(f"Speed: {100/(end_time - start_time):.1f} primitives/sec")
```

### Integration Test Pattern
```python
def test_full_workflow():
    """Test complete application workflow"""
    # 1. Create generator
    generator = OptimizedSpaceshipGenerator()
    
    # 2. Generate mesh
    mesh = generator.generate_mesh()
    assert len(mesh.vertices) > 0
    
    # 3. Test export
    mesh.export("test_output.stl")
    assert os.path.exists("test_output.stl")
    
    # 4. Test configuration
    assert generator.save_configuration("test_config.json")
    assert generator.load_configuration("test_config.json")
```

## Common Anti-Patterns to Avoid

### ❌ Performance Anti-Patterns
- High polygon primitives for real-time editing
- No caching of expensive mesh operations  
- Synchronous mesh generation blocking UI
- Memory leaks from unreleased OpenGL resources

### ❌ Code Organization Anti-Patterns
- Circular imports between modules
- Hard-coded file paths
- Mixing UI logic with mesh generation
- No error handling for external library failures

### ❌ VS Code Integration Anti-Patterns
- Hard-coded Python interpreter paths
- Missing PYTHONPATH configuration
- No task definitions for common operations
- Absolute imports when relative imports are appropriate

## AI Assistant Guidelines

### Before Making Changes
1. **Check Current State**: Read references/ai-context/current_project_state.md
2. **Verify Structure**: Confirm files are in expected locations (src/, tests/, etc.)
3. **Review Patterns**: Follow established patterns for consistency
4. **Consider Performance**: Evaluate impact on application responsiveness

### When Making Changes
1. **Use Established Patterns**: Follow existing code organization and naming
2. **Maintain Performance**: Keep mesh operations optimized
3. **Test Thoroughly**: Use VS Code tasks to validate changes
4. **Update Documentation**: Refresh AI context after significant changes

### After Making Changes
1. **Validate Functionality**: Run tests and check application still works
2. **Update Context**: Refresh references/ai-context/ if needed
3. **Document Decisions**: Explain significant architectural choices
4. **Performance Check**: Ensure changes don't degrade performance

This ensures consistent, maintainable, and performant code across all iterations!