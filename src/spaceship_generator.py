#!/usr/bin/env python3
"""
Advanced Spaceship 3D Model Generator
Creates sophisticated, connected spaceship meshes with real-time preview and editing.
"""

import sys
import json
import numpy as np
import trimesh
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# Import shared utilities
try:
    from .spaceship_utils import SpaceshipGeometryNode, MeshUtils
except ImportError:
    # Fallback for standalone execution
    from spaceship_utils import SpaceshipGeometryNode, MeshUtils

try:
    from PyQt6.QtWidgets import *
    from PyQt6.QtGui import *
    from PyQt6.QtCore import *
    from PyQt6.QtOpenGLWidgets import QOpenGLWidget
except ImportError:
    print("PyQt6 not found, trying PyQt5...")
    try:
        from PyQt5.QtWidgets import *
        from PyQt5.QtGui import *
        from PyQt5.QtCore import *
        from PyQt5.QtOpenGL import QOpenGLWidget
    except ImportError:
        print("Neither PyQt6 nor PyQt5 found. Please install PyQt6.")
        sys.exit(1)

try:
    from OpenGL.GL import *
    from OpenGL.GLU import *
except ImportError:
    print("PyOpenGL not found. Please install PyOpenGL.")
    sys.exit(1)

# Configuration
GRID_SIZE = (8, 5, 12)  # X, Y, Z dimensions
GRID_FILE = "spaceship_config.json"

# SpaceshipGeometryNode is now imported from spaceship_utils.py

class SpaceshipGenerator:
    """Main class for generating spaceship geometry"""
    
    def __init__(self, grid_size=GRID_SIZE):
        self.grid_size = grid_size
        self.grid = self.create_default_spaceship()
    
    def create_default_spaceship(self):
        """Create a default spaceship configuration"""
        nx, ny, nz = self.grid_size
        grid = {}
        
        for x in range(nx):
            for y in range(ny):
                for z in range(nz):
                    # Calculate position factors
                    center_x = abs(x - nx//2) / (nx//2) if nx > 1 else 0
                    center_y = abs(y - ny//2) / (ny//2) if ny > 1 else 0
                    front_factor = z / (nz - 1) if nz > 1 else 0
                    
                    # Determine geometry node type and properties based on position
                    if z < nz * 0.2:  # Rear engines
                        mod_type = "cylinder" if center_x < 0.7 else "cone"
                        radius = 0.4 + 0.3 * (1 - center_x) * (1 - center_y)
                        height = 1.2
                        color = [150, 50, 200]  # Purple engines
                    elif z < nz * 0.4:  # Main hull
                        mod_type = "box"
                        radius = 0.6 + 0.4 * (1 - center_x) * (1 - center_y)
                        height = 1.5
                        color = [80, 120, 180]  # Blue hull
                    elif z < nz * 0.7:  # Mid section
                        mod_type = np.random.choice(["cylinder", "box", "sphere"])
                        radius = 0.3 + 0.4 * (1 - center_x) * (1 - center_y)
                        height = 1.0
                        color = [120, 120, 140]  # Gray details
                    else:  # Front/cockpit
                        mod_type = "wedge" if z > nz * 0.8 else "cone"
                        radius = 0.2 + 0.5 * (1 - center_x) * (1 - center_y) * (1 - front_factor)
                        height = 0.8
                        color = [60, 80, 120]  # Dark cockpit
                    
                    # Add some variation
                    radius *= (0.8 + 0.4 * np.random.random())
                    height *= (0.8 + 0.4 * np.random.random())
                    
                    # Add color variation
                    color = [max(10, min(255, c + 30 * np.random.randn())) for c in color]
                    
                    grid[(x, y, z)] = SpaceshipGeometryNode(mod_type, radius, height, color)
        
        return grid
    
    def create_primitive(self, module):
        """Create a 3D primitive based on geometry node type using shared MeshUtils"""
        if not module.enabled:
            return None
        
        try:
            # Use centralized mesh creation utilities
            return MeshUtils.create_simple_primitive(
                module.type, 
                radius=module.radius, 
                height=module.height
            )
            
        except Exception as e:
            print(f"Error creating primitive {module.type}: {e}")
            return trimesh.creation.box(extents=[0.1, 0.1, 0.1])
    
    def generate_mesh(self):
        """Generate the complete spaceship mesh"""
        nx, ny, nz = self.grid_size
        meshes = []
        
        # Generate all module meshes
        for (x, y, z), module in self.grid.items():
            if not module.enabled:
                continue
                
            mesh = self.create_primitive(module)
            if mesh is None:
                continue
            
            # Apply scaling
            scale = module.scale
            mesh.apply_scale(scale)
            
            # Apply rotation
            for i, angle in enumerate(module.rotation):
                if abs(angle) > 0.001:
                    axis = [0, 0, 0]
                    axis[i] = 1
                    mesh.apply_transform(
                        trimesh.transformations.rotation_matrix(np.radians(angle), axis)
                    )
            
            # Position the mesh
            pos_x = (x - nx//2) * 1.5
            pos_y = (y - ny//2) * 1.5  
            pos_z = (z - nz//2) * 1.2
            mesh.apply_translation([pos_x, pos_y, pos_z])
            
            # Set colors
            color = module.color + [255]
            vertex_colors = np.tile(color, (len(mesh.vertices), 1))
            mesh.visual.vertex_colors = vertex_colors
            
            meshes.append(mesh)
        
        if not meshes:
            return trimesh.creation.box(extents=[1, 1, 1])
        
        # Combine all meshes
        try:
            combined = trimesh.util.concatenate(meshes)
            return combined.smoothed()
        except:
            return meshes[0]
    
    def save_configuration(self, filename=None):
        """Save the current spaceship configuration"""
        filename = filename or GRID_FILE
        
        config = {
            "grid_size": self.grid_size,
            "modules": {}
        }
        
        for pos, module in self.grid.items():
            config["modules"][str(pos)] = module.to_dict()
        
        with open(filename, 'w') as f:
            json.dump(config, f, indent=2)
    
    def load_configuration(self, filename=None):
        """Load a spaceship configuration"""
        filename = filename or GRID_FILE
        
        try:
            with open(filename, 'r') as f:
                config = json.load(f)
            
            self.grid_size = tuple(config.get("grid_size", GRID_SIZE))
            self.grid = {}
            
            for pos_str, module_data in config.get("modules", {}).items():
                pos = eval(pos_str)  # Convert string back to tuple
                self.grid[pos] = SpaceshipGeometryNode.from_dict(module_data)
                
        except FileNotFoundError:
            print(f"Configuration file {filename} not found, using default.")
            self.grid = self.create_default_spaceship()
        except Exception as e:
            print(f"Error loading configuration: {e}")
            self.grid = self.create_default_spaceship()

class SpaceshipViewer(QOpenGLWidget):
    """OpenGL widget for 3D spaceship preview"""
    
    def __init__(self, generator):
        super().__init__()
        self.generator = generator
        self.mesh = None
        self.rot_x = 20
        self.rot_y = 30
        self.zoom = -15
        self.last_pos = None
        self.wireframe = False
        self.lighting = True
        self.update_mesh()
        
        # Auto-update timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(50)  # 20 FPS
    
    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        
        # Lighting setup
        glLightfv(GL_LIGHT0, GL_POSITION, [5.0, 5.0, 10.0, 1.0])
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.3, 0.3, 0.3, 1.0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8, 0.8, 0.8, 1.0])
        
        glClearColor(0.02, 0.02, 0.05, 1.0)  # Space background
    
    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, w/h if h > 0 else 1, 0.1, 100)
        glMatrixMode(GL_MODELVIEW)
    
    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        # Camera
        glTranslatef(0, 0, self.zoom)
        glRotatef(self.rot_x, 1, 0, 0)
        glRotatef(self.rot_y, 0, 1, 0)
        
        # Rendering mode
        if self.wireframe:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        
        if self.lighting:
            glEnable(GL_LIGHTING)
        else:
            glDisable(GL_LIGHTING)
        
        self.render_mesh()
        self.render_axes()
    
    def render_mesh(self):
        if self.mesh is None:
            return
        
        vertices = self.mesh.vertices
        faces = self.mesh.faces
        
        try:
            normals = self.mesh.vertex_normals
        except:
            normals = np.zeros_like(vertices)
        
        glBegin(GL_TRIANGLES)
        for face in faces:
            for vertex_idx in face:
                if vertex_idx < len(vertices):
                    # Normal
                    if vertex_idx < len(normals):
                        glNormal3f(*normals[vertex_idx])
                    
                    # Color
                    if hasattr(self.mesh.visual, 'vertex_colors') and vertex_idx < len(self.mesh.visual.vertex_colors):
                        color = self.mesh.visual.vertex_colors[vertex_idx][:3] / 255.0
                        glColor3f(*color)
                    else:
                        glColor3f(0.7, 0.7, 0.9)
                    
                    # Vertex
                    glVertex3f(*vertices[vertex_idx])
        glEnd()
    
    def render_axes(self):
        """Render coordinate axes"""
        glDisable(GL_LIGHTING)
        glLineWidth(2.0)
        glBegin(GL_LINES)
        
        # X axis - Red
        glColor3f(1.0, 0.0, 0.0)
        glVertex3f(0, 0, 0)
        glVertex3f(3, 0, 0)
        
        # Y axis - Green  
        glColor3f(0.0, 1.0, 0.0)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 3, 0)
        
        # Z axis - Blue
        glColor3f(0.0, 0.0, 1.0)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 0, 3)
        
        glEnd()
        glLineWidth(1.0)
        
        if self.lighting:
            glEnable(GL_LIGHTING)
    
    def update_mesh(self):
        """Regenerate mesh from current configuration"""
        self.mesh = self.generator.generate_mesh()
    
    def mousePressEvent(self, event):
        self.last_pos = event.position().toPoint() if hasattr(event.position(), 'toPoint') else event.pos()
    
    def mouseMoveEvent(self, event):
        if self.last_pos is None:
            return
        
        pos = event.position().toPoint() if hasattr(event.position(), 'toPoint') else event.pos()
        dx = pos.x() - self.last_pos.x()
        dy = pos.y() - self.last_pos.y()
        
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.rot_x += dy * 0.5
            self.rot_y += dx * 0.5
        
        self.last_pos = pos
    
    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        self.zoom += delta * 0.01
        self.zoom = max(-50, min(-2, self.zoom))

class ControlWidget(QWidget):
    """Control panel for editing spaceship geometry nodes"""
    
    def __init__(self, generator, viewer):
        super().__init__()
        self.generator = generator
        self.viewer = viewer
        self.current_pos = (0, 0, 0)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Position selection
        pos_group = QGroupBox("Module Position")
        pos_layout = QGridLayout()
        
        self.spin_x = QSpinBox()
        self.spin_x.setRange(0, self.generator.grid_size[0] - 1)
        self.spin_y = QSpinBox()
        self.spin_y.setRange(0, self.generator.grid_size[1] - 1)
        self.spin_z = QSpinBox()
        self.spin_z.setRange(0, self.generator.grid_size[2] - 1)
        
        pos_layout.addWidget(QLabel("X:"), 0, 0)
        pos_layout.addWidget(self.spin_x, 0, 1)
        pos_layout.addWidget(QLabel("Y:"), 1, 0)
        pos_layout.addWidget(self.spin_y, 1, 1)
        pos_layout.addWidget(QLabel("Z:"), 2, 0)
        pos_layout.addWidget(self.spin_z, 2, 1)
        
        pos_group.setLayout(pos_layout)
        layout.addWidget(pos_group)
        
        # Module properties
        props_group = QGroupBox("Module Properties")
        props_layout = QGridLayout()
        
        self.enabled_check = QCheckBox("Enabled")
        props_layout.addWidget(self.enabled_check, 0, 0, 1, 2)
        
        self.type_combo = QComboBox()
        self.type_combo.addItems(["cylinder", "cone", "box", "sphere", "torus", "wedge"])
        props_layout.addWidget(QLabel("Type:"), 1, 0)
        props_layout.addWidget(self.type_combo, 1, 1)
        
        self.radius_spin = QDoubleSpinBox()
        self.radius_spin.setRange(0.01, 5.0)
        self.radius_spin.setSingleStep(0.05)
        self.radius_spin.setDecimals(3)
        props_layout.addWidget(QLabel("Radius:"), 2, 0)
        props_layout.addWidget(self.radius_spin, 2, 1)
        
        self.height_spin = QDoubleSpinBox()
        self.height_spin.setRange(0.01, 5.0)
        self.height_spin.setSingleStep(0.05)
        self.height_spin.setDecimals(3)
        props_layout.addWidget(QLabel("Height:"), 3, 0)
        props_layout.addWidget(self.height_spin, 3, 1)
        
        self.color_btn = QPushButton("Choose Color")
        props_layout.addWidget(self.color_btn, 4, 0, 1, 2)
        
        props_group.setLayout(props_layout)
        layout.addWidget(props_group)
        
        # Action buttons
        action_group = QGroupBox("Actions")
        action_layout = QVBoxLayout()
        
        self.update_btn = QPushButton("Update Module")
        self.randomize_btn = QPushButton("Generate New Ship")
        self.save_btn = QPushButton("Save Configuration")
        self.load_btn = QPushButton("Load Configuration")
        self.export_btn = QPushButton("Export 3D Model")
        self.reference_btn = QPushButton("Generate Reference Image")
        
        action_layout.addWidget(self.update_btn)
        action_layout.addWidget(self.randomize_btn)
        action_layout.addWidget(self.save_btn)
        action_layout.addWidget(self.load_btn)
        action_layout.addWidget(self.export_btn)
        action_layout.addWidget(self.reference_btn)
        
        action_group.setLayout(action_layout)
        layout.addWidget(action_group)
        
        # View controls
        view_group = QGroupBox("View Controls")
        view_layout = QVBoxLayout()
        
        self.wireframe_btn = QPushButton("Toggle Wireframe")
        self.lighting_btn = QPushButton("Toggle Lighting")
        
        view_layout.addWidget(self.wireframe_btn)
        view_layout.addWidget(self.lighting_btn)
        
        view_group.setLayout(view_layout)
        layout.addWidget(view_group)
        
        layout.addStretch()
        self.setLayout(layout)
        
        # Connect signals
        self.spin_x.valueChanged.connect(self.update_position)
        self.spin_y.valueChanged.connect(self.update_position)
        self.spin_z.valueChanged.connect(self.update_position)
        self.update_btn.clicked.connect(self.update_module)
        self.randomize_btn.clicked.connect(self.randomize_ship)
        self.save_btn.clicked.connect(self.save_config)
        self.load_btn.clicked.connect(self.load_config)
        self.export_btn.clicked.connect(self.export_model)
        self.reference_btn.clicked.connect(self.generate_reference)
        self.color_btn.clicked.connect(self.choose_color)
        self.wireframe_btn.clicked.connect(self.toggle_wireframe)
        self.lighting_btn.clicked.connect(self.toggle_lighting)
        
        self.update_ui()
    
    def update_position(self):
        """Update current position and refresh UI"""
        self.current_pos = (self.spin_x.value(), self.spin_y.value(), self.spin_z.value())
        self.update_ui()
    
    def update_ui(self):
        """Update UI elements to reflect current module"""
        if self.current_pos in self.generator.grid:
            module = self.generator.grid[self.current_pos]
            self.enabled_check.setChecked(module.enabled)
            self.type_combo.setCurrentText(module.type)
            self.radius_spin.setValue(module.radius)
            self.height_spin.setValue(module.height)
    
    def update_geometry_node(self):
        """Update the current module with UI values"""
        if self.current_pos not in self.generator.grid:
            self.generator.grid[self.current_pos] = SpaceshipGeometryNode()
        
        module = self.generator.grid[self.current_pos]
        module.enabled = self.enabled_check.isChecked()
        module.type = self.type_combo.currentText()
        module.radius = self.radius_spin.value()
        module.height = self.height_spin.value()
        
        self.viewer.update_mesh()
    
    def choose_color(self):
        """Open color picker dialog"""
        if self.current_pos in self.generator.grid:
            module = self.generator.grid[self.current_pos]
            current_color = QColor(*module.color[:3])
            color = QColorDialog.getColor(current_color, self)
            
            if color.isValid():
                module.color = [color.red(), color.green(), color.blue()]
                self.viewer.update_mesh()
    
    def randomize_ship(self):
        """Generate a new random spaceship"""
        self.generator.grid = self.generator.create_default_spaceship()
        self.update_ui()
        self.viewer.update_mesh()
    
    def save_config(self):
        """Save current configuration"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Configuration", "spaceship_config.json", 
            "JSON Files (*.json)"
        )
        if filename:
            self.generator.save_configuration(filename)
            QMessageBox.information(self, "Saved", f"Configuration saved to {filename}")
    
    def load_config(self):
        """Load configuration from file"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Load Configuration", "", "JSON Files (*.json)"
        )
        if filename:
            self.generator.load_configuration(filename)
            self.update_ui()
            self.viewer.update_mesh()
            QMessageBox.information(self, "Loaded", f"Configuration loaded from {filename}")
    
    def export_model(self):
        """Export the 3D model"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export 3D Model", "spaceship", 
            "STL Files (*.stl);;GLB Files (*.glb);;OBJ Files (*.obj);;PLY Files (*.ply)"
        )
        if filename:
            try:
                mesh = self.generator.generate_mesh()
                mesh.export(filename)
                QMessageBox.information(self, "Exported", f"Model exported to {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export: {e}")
    
    def generate_reference(self):
        """Generate reference image"""
        try:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
            
            nx, ny, nz = self.generator.grid_size
            
            # Top view
            top_view = np.zeros((nx, nz, 3))
            for x in range(nx):
                for z in range(nz):
                    colors = []
                    for y in range(ny):
                        pos = (x, y, z)
                        if pos in self.generator.grid and self.generator.grid[pos].enabled:
                            color = np.array(self.generator.grid[pos].color) / 255.0
                            colors.append(color)
                    if colors:
                        top_view[x, z] = np.mean(colors, axis=0)
            
            ax1.imshow(top_view, origin='lower', aspect='auto')
            ax1.set_title("Spaceship Top View")
            ax1.set_xlabel("Z (Front-Back)")
            ax1.set_ylabel("X (Left-Right)")
            
            # Side view
            side_view = np.zeros((ny, nz, 3))
            for y in range(ny):
                for z in range(nz):
                    colors = []
                    for x in range(nx):
                        pos = (x, y, z)
                        if pos in self.generator.grid and self.generator.grid[pos].enabled:
                            color = np.array(self.generator.grid[pos].color) / 255.0
                            colors.append(color)
                    if colors:
                        side_view[y, z] = np.mean(colors, axis=0)
            
            ax2.imshow(side_view, origin='lower', aspect='auto')
            ax2.set_title("Spaceship Side View")
            ax2.set_xlabel("Z (Front-Back)")
            ax2.set_ylabel("Y (Up-Down)")
            
            plt.tight_layout()
            plt.savefig("spaceship_reference.png", dpi=150, bbox_inches='tight')
            plt.show()
            
            QMessageBox.information(self, "Reference Generated", 
                                  "Reference image saved as spaceship_reference.png")
            
        except Exception as e:
            QMessageBox.critical(self, "Reference Error", f"Failed to generate reference: {e}")
    
    def toggle_wireframe(self):
        """Toggle wireframe mode"""
        self.viewer.wireframe = not self.viewer.wireframe
    
    def toggle_lighting(self):
        """Toggle lighting"""
        self.viewer.lighting = not self.viewer.lighting

class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Advanced Spaceship Designer v3.0")
        self.setMinimumSize(1200, 800)
        
        # Create generator and components
        self.generator = SpaceshipGenerator()
        self.viewer = SpaceshipViewer(self.generator)
        self.controls = ControlWidget(self.generator, self.viewer)
        
        # Setup UI
        central_widget = QWidget()
        layout = QHBoxLayout()
        
        layout.addWidget(self.viewer, 3)  # 3/4 of space for viewer
        layout.addWidget(self.controls, 1)  # 1/4 for controls
        
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        
        # Setup menu bar
        self.create_menu_bar()
        
        # Status bar
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready - Use mouse to rotate view, scroll to zoom")
    
    def create_menu_bar(self):
        """Create application menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        new_action = QAction('New Spaceship', self)
        new_action.triggered.connect(self.controls.randomize_ship)
        file_menu.addAction(new_action)
        
        file_menu.addSeparator()
        
        save_action = QAction('Save Configuration', self)
        save_action.triggered.connect(self.controls.save_config)
        file_menu.addAction(save_action)
        
        load_action = QAction('Load Configuration', self)
        load_action.triggered.connect(self.controls.load_config)
        file_menu.addAction(load_action)
        
        file_menu.addSeparator()
        
        export_action = QAction('Export 3D Model', self)
        export_action.triggered.connect(self.controls.export_model)
        file_menu.addAction(export_action)
        
        # View menu
        view_menu = menubar.addMenu('View')
        
        wireframe_action = QAction('Toggle Wireframe', self)
        wireframe_action.triggered.connect(self.controls.toggle_wireframe)
        view_menu.addAction(wireframe_action)
        
        lighting_action = QAction('Toggle Lighting', self)
        lighting_action.triggered.connect(self.controls.toggle_lighting)
        view_menu.addAction(lighting_action)
        
        # Tools menu
        tools_menu = menubar.addMenu('Tools')
        
        reference_action = QAction('Generate Reference Image', self)
        reference_action.triggered.connect(self.controls.generate_reference)
        tools_menu.addAction(reference_action)

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("Spaceship Designer")
    app.setApplicationVersion("3.0")
    
    # Apply dark theme
    app.setStyle('Fusion')
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(0, 0, 0))
    app.setPalette(palette)
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Load or create initial configuration
    try:
        window.generator.load_configuration()
        window.viewer.update_mesh()
        print("Loaded existing configuration")
    except:
        print("Using default spaceship configuration")
    
    return app.exec()

if __name__ == "__main__":
    print("Starting Advanced Spaceship Designer...")
    print(f"Grid size: {GRID_SIZE}")
    print("Controls:")
    print("- Mouse: Rotate view")
    print("- Scroll: Zoom")
    print("- Edit modules in control panel")
    print("- Export to STL, GLB, OBJ, PLY formats")
    print("-" * 50)
    
    sys.exit(main())
