# TECHNICAL REFERENCE - SPACESHIP DESIGNER

## 🏗️ CODE ARCHITECTURE

### Entry Point Flow
```
spaceship.py → src/spaceship_designer.py → UI + MCP Server
```

### Core Classes

#### SpaceshipGeometryNode (Data Structure)
```python
{
    "type": "cylinder|cone|box|sphere|torus|wedge",
    "radius": float,          # 0.5 to 3.0
    "height": float,          # 0.5 to 4.0
    "color": [r, g, b],      # RGB values 0-1
    "enabled": bool,         # Geometry node active state
    "rotation": [x, y, z],   # Euler angles
    "scale": [x, y, z]       # Scale factors
}
```

#### OptimizedSpaceshipGenerator
```python
class OptimizedSpaceshipGenerator:
    def __init__(self):
        self.grid_size = (8, 5, 12)  # x, y, z dimensions
        self.modules = {}            # 3D grid storage
        self.mesh_cache = {}         # Performance optimization
    
    def generate_random_spaceship(self) -> None:
        """Creates procedural spaceship with 15-25 modules"""
        
    def create_mesh(self) -> trimesh.Trimesh:
        """Generates combined mesh from all modules"""
        
    def export_mesh(self, filepath: str, format: str) -> bool:
        """Exports to STL, GLB, OBJ, PLY formats"""
```

#### SpaceshipViewer (OpenGL Widget)
```python
class SpaceshipViewer(QOpenGLWidget):
    def __init__(self, generator):
        self.generator = generator
        self.rotation_x = -20.0
        self.rotation_y = 45.0
        self.zoom_level = 5.0
        self.wireframe_mode = False
    
    def paintGL(self):
        """Main OpenGL rendering loop"""
        
    def mousePressEvent(self, event):
        """Handle mouse interactions for 3D navigation"""
```

### MCP Integration

#### IntegratedMCPManager
```python
class IntegratedMCPManager:
    def __init__(self, parent_app):
        self.app = parent_app
        self.port = 8765
        self.server = None
        self.server_thread = None
    
    def start_server(self) -> bool:
        """Starts MCP server in background thread"""
        
    def stop_server(self) -> None:
        """Gracefully shuts down server"""
```

#### MCPHandler (HTTP Endpoints)
```python
class MCPHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests (/health, /status)"""
        
    def do_POST(self):
        """Handle POST requests (/commands)"""
        
    # Available commands:
    # - see: Take screenshot
    # - click: Mouse click with coordinates
    # - move_to: Mouse movement
    # - press_key: Keyboard input
    # - focus_app: Window focus
```

## 🎯 PERFORMANCE OPTIMIZATIONS

### Mesh Generation
```python
# Optimized primitive creation
def create_primitive(prim_type, radius, height):
    """Low-poly primitives for real-time performance"""
    if prim_type == "cylinder":
        return trimesh.primitives.Cylinder(
            radius=radius, 
            height=height, 
            sections=8  # Reduced from 32 for performance
        )
```

### Caching System
```python
def create_mesh(self):
    """Uses mesh_cache to avoid redundant calculations"""
    cache_key = self.get_cache_key()
    if cache_key in self.mesh_cache:
        return self.mesh_cache[cache_key]
```

### GPU Detection
```python
def detect_gpu_capabilities(self):
    """Automatically adjusts rendering quality based on hardware"""
    renderer = gl.glGetString(gl.GL_RENDERER).decode('utf-8')
    if any(gpu in renderer.lower() for gpu in ['nvidia', 'amd', 'intel']):
        self.high_quality_rendering = True
```

## 🔌 API ENDPOINTS

### MCP Server API
- **Base URL**: `http://localhost:8765`
- **Content-Type**: `application/json`

#### GET /health
```json
{
    "status": "healthy",
    "timestamp": "2025-01-11T10:30:00Z"
}
```

#### GET /status
```json
{
    "mcp_active": true,
    "app_focused": true,
    "modules_count": 18,
    "last_screenshot": "ai_screenshots/screenshot_20250111_103000.png"
}
```

#### POST /commands
```json
{
    "command": "see|click|move_to|press_key|focus_app",
    "params": {
        "x": 150,
        "y": 200,
        "reason": "test_generate_button"
    }
}
```

## 🧪 TESTING FRAMEWORK

### Unit Tests Structure
```python
class TestSpaceshipGeneration(unittest.TestCase):
    def setUp(self):
        self.generator = OptimizedSpaceshipGenerator()
    
    def test_module_creation(self):
        """Test individual module generation"""
        
    def test_mesh_export(self):
        """Test export functionality"""
        
    def test_performance_benchmarks(self):
        """Validate performance requirements"""
```

### AI Integration Tests
```python
class TestMCPIntegration(unittest.TestCase):
    def test_server_startup(self):
        """Validate MCP server starts successfully"""
        
    def test_command_execution(self):
        """Test AI command processing"""
        
    def test_screenshot_capture(self):
        """Validate visual feedback system"""
```

## 🎮 CONTROLS & SHORTCUTS

### Keyboard Mapping
```python
def keyPressEvent(self, event):
    key_map = {
        Qt.Key.Key_W: self.toggle_wireframe,
        Qt.Key.Key_L: self.toggle_lighting,
        Qt.Key.Key_R: self.reset_view,
        Qt.Key.Key_G: self.generate_spaceship,
        Qt.Key.Key_C: self.clear_spaceship,
        Qt.Key.Key_E: self.export_dialog,
        Qt.Key.Key_S: self.save_configuration,
        Qt.Key.Key_O: self.load_configuration
    }
```

### Mouse Controls
```python
def mousePressEvent(self, event):
    if event.button() == Qt.MouseButton.LeftButton:
        self.last_mouse_pos = event.position()
        self.mouse_mode = "rotate"
    elif event.button() == Qt.MouseButton.RightButton:
        self.last_mouse_pos = event.position()
        self.mouse_mode = "pan"

def wheelEvent(self, event):
    """Zoom control via mouse wheel"""
    delta = event.angleDelta().y() / 120.0
    self.zoom_level *= (1.1 ** delta)
```

## 📊 PERFORMANCE BENCHMARKS

### Startup Performance
- **Application Launch**: ~0.5 seconds
- **MCP Server Start**: ~0.2 seconds
- **OpenGL Context**: ~0.1 seconds
- **Total Ready State**: ~0.8 seconds

### Runtime Performance
- **Mesh Generation**: ~50ms for 20 modules
- **Export (STL)**: ~100ms for standard mesh
- **Screenshot Capture**: ~200ms including analysis
- **UI Responsiveness**: 30+ FPS rendering

### Memory Usage
- **Base Application**: ~25MB
- **With Mesh Data**: ~40MB
- **Peak (Export)**: ~60MB
- **MCP Server**: ~5MB additional

## 🔧 CONFIGURATION

### Default Settings
```python
DEFAULT_CONFIG = {
    "grid_size": (8, 5, 12),
    "mcp_port": 8765,
    "auto_save": True,
    "export_format": "stl",
    "wireframe_on_start": False,
    "ai_automation": True
}
```

### File Locations
- **Configuration**: `spaceship_config.json`
- **Screenshots**: `ai_screenshots/`
- **Exports**: `exports/`
- **Logs**: `mcp_server.log`

## 🛡️ ERROR HANDLING

### Common Error Patterns
```python
def safe_mesh_operation(func):
    """Decorator for mesh operations with fallback"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"Mesh operation failed: {e}")
            return create_fallback_mesh()
    return wrapper
```

### MCP Error Responses
```json
{
    "error": true,
    "message": "Command execution failed",
    "details": "Specific error description",
    "timestamp": "2025-01-11T10:30:00Z"
}
```

## 🔗 DEPENDENCIES

### Core Requirements
```
PyQt6>=6.4.0
trimesh>=3.15.0
numpy>=1.21.0
requests>=2.28.0
```

### Optional Dependencies
```
pyglet>=1.5.0      # Advanced OpenGL features
pillow>=9.0.0      # Screenshot processing
psutil>=5.8.0      # System monitoring
```

This technical reference consolidates all implementation details, API specifications, and performance data into a single authoritative source.