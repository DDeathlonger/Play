import sys
import json
import numpy as np
import trimesh
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QComboBox, QDoubleSpinBox, QLabel, QColorDialog, 
                             QFileDialog, QSpinBox, QTabWidget, QTextEdit, QSlider, 
                             QGroupBox, QGridLayout, QCheckBox, QProgressBar)
from PyQt6.QtGui import QColor, QPixmap
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from OpenGL.GL import *
from OpenGL.GLU import *
import os
from scipy import ndimage


# ----------------------------
# 1. Enhanced spaceship parameters
# ----------------------------
GRID_NX, GRID_NY, GRID_NZ = 8, 5, 12  # Larger grid for more detail
GRID_FILE = "spaceship_grid.json"

def init_grid():
    """Initialize a sophisticated spaceship grid with varied geometry"""
    grid = np.empty((GRID_NX, GRID_NY, GRID_NZ), dtype=object)
    
    # Define spaceship sections
    for x in range(GRID_NX):
        for y in range(GRID_NY):
            for z in range(GRID_NZ):
                # Position factors
                center_x = abs(x - GRID_NX//2) / (GRID_NX//2)
                center_y = abs(y - GRID_NY//2) / (GRID_NY//2) if GRID_NY > 1 else 0
                front_z = z / GRID_NZ  # 0 = back, 1 = front
                
                # Determine component type based on position
                if z < 2:  # Engine section
                    component_type = "cylinder" if center_x < 0.6 else "cone"
                    radius = 0.4 + 0.2 * (1 - center_x) * (1 - center_y)
                    height = 0.8 + 0.3 * np.random.rand()
                    color = [80, 40, 120]  # Purple engines
                elif z < 4:  # Main body
                    component_type = "box"
                    radius = 0.6 + 0.2 * (1 - center_x) * (1 - center_y)
                    height = 1.0 + 0.2 * np.random.rand()
                    color = [60, 80, 120]  # Blue hull
                elif z < 8:  # Mid section with details
                    component_type = np.random.choice(["cylinder", "box", "cone"])
                    radius = 0.3 + 0.3 * (1 - center_x) * (1 - center_y)
                    height = 0.6 + 0.4 * np.random.rand()
                    color = [70, 70, 90]  # Gray details
                else:  # Front/cockpit
                    component_type = "cone" if z > 9 else "cylinder"
                    radius = 0.2 + 0.4 * (1 - center_x) * (1 - center_y) * (1 - front_z)
                    height = 0.5 + 0.3 * np.random.rand()
                    color = [40, 60, 80]  # Dark blue cockpit
                
                # Add some randomness for organic look
                radius += 0.05 * np.random.randn()
                height += 0.1 * np.random.randn()
                
                grid[x, y, z] = {
                    "type": component_type,
                    "radius": max(0.1, radius),
                    "height": max(0.2, height),
                    "color": [max(10, min(255, c + 20*np.random.randn())) for c in color],
                    "rotation": [0, 0, 0],  # Euler angles
                    "scale": [1.0, 1.0, 1.0],
                    "enabled": True,
                    "material": "metal"
                }
    return grid

def save_grid(grid):
    """Save grid to JSON with proper serialization"""
    serializable_grid = []
    for x in range(grid.shape[0]):
        x_row = []
        for y in range(grid.shape[1]):
            y_row = []
            for z in range(grid.shape[2]):
                y_row.append(grid[x, y, z])
            x_row.append(y_row)
        serializable_grid.append(x_row)
    
    with open(GRID_FILE, "w") as f:
        json.dump(serializable_grid, f, indent=2)

def load_grid():
    """Load grid from JSON or create new if not exists"""
    try:
        with open(GRID_FILE, "r") as f:
            data = json.load(f)
            grid = np.empty((len(data), len(data[0]), len(data[0][0])), dtype=object)
            for x in range(len(data)):
                for y in range(len(data[x])):
                    for z in range(len(data[x][y])):
                        grid[x, y, z] = data[x][y][z]
            return grid
    except:
        return init_grid()

def generate_reference_image(grid):
    """Generate a 2D reference image of the spaceship"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
    
    # Top view
    top_view = np.zeros((Nx, Nz, 3))
    for x in range(Nx):
        for z in range(Nz):
            # Get average properties across Y axis
            avg_color = [0, 0, 0]
            for y in range(Ny):
                if grid[x, y, z]["enabled"]:
                    color = grid[x, y, z]["color"]
                    avg_color = [avg_color[i] + color[i]/255.0 for i in range(3)]
            top_view[x, z] = [c/Ny for c in avg_color]
    
    ax1.imshow(top_view, origin='lower')
    ax1.set_title("Spaceship Top View")
    ax1.set_xlabel("Z (Front-Back)")
    ax1.set_ylabel("X (Left-Right)")
    
    # Side view
    side_view = np.zeros((Ny, Nz, 3))
    for y in range(Ny):
        for z in range(Nz):
            # Get average properties across X axis
            avg_color = [0, 0, 0]
            for x in range(Nx):
                if grid[x, y, z]["enabled"]:
                    color = grid[x, y, z]["color"]
                    avg_color = [avg_color[i] + color[i]/255.0 for i in range(3)]
            side_view[y, z] = [c/Nx for c in avg_color]
    
    ax2.imshow(side_view, origin='lower')
    ax2.set_title("Spaceship Side View")
    ax2.set_xlabel("Z (Front-Back)")
    ax2.set_ylabel("Y (Up-Down)")
    
    plt.tight_layout()
    plt.savefig("spaceship_reference.png", dpi=150, bbox_inches='tight')
    plt.close()
    return "spaceship_reference.png"

grid = load_grid()


# ----------------------------
# 2. Enhanced mesh generation with connectivity
# ----------------------------
def create_primitive(module_type, radius, height, sections=16):
    """Create primitive mesh based on type"""
    if module_type == "cylinder":
        return trimesh.creation.cylinder(radius=radius, height=height, sections=sections)
    elif module_type == "cone":
        return trimesh.creation.cone(radius=radius, height=height, sections=sections)
    elif module_type == "sphere":
        return trimesh.creation.icosphere(subdivisions=2, radius=radius)
    elif module_type == "torus":
        return trimesh.creation.torus(major_radius=radius, minor_radius=radius*0.3, major_sections=sections, minor_sections=8)
    elif module_type == "wedge":
        # Create a wedge shape for aerodynamic parts
        mesh = trimesh.creation.box(extents=[radius*2, height, radius*2])
        # Slice it to create wedge
        vertices = mesh.vertices.copy()
        # Modify vertices to create wedge shape
        for i, vertex in enumerate(vertices):
            if vertex[2] > 0:  # Front part
                scale = 1 - (vertex[2] / radius)
                vertices[i][0] *= scale
                vertices[i][1] *= scale
        mesh.vertices = vertices
        return mesh
    else:  # box
        return trimesh.creation.box(extents=[radius*2, height, radius*2])

def connect_modules(mesh1, mesh2, pos1, pos2):
    """Create connecting geometry between two modules"""
    direction = np.array(pos2) - np.array(pos1)
    distance = np.linalg.norm(direction)
    
    if distance < 0.1:
        return None
        
    # Create a connecting cylinder
    connector_radius = min(0.1, distance * 0.1)
    connector = trimesh.creation.cylinder(
        radius=connector_radius, 
        height=distance, 
        sections=8
    )
    
    # Orient the connector
    if distance > 0:
        direction_normalized = direction / distance
        # Calculate rotation to align with direction
        z_axis = np.array([0, 0, 1])
        if not np.allclose(direction_normalized, z_axis):
            rotation_axis = np.cross(z_axis, direction_normalized)
            rotation_angle = np.arccos(np.clip(np.dot(z_axis, direction_normalized), -1, 1))
            rotation_matrix = trimesh.transformations.rotation_matrix(rotation_angle, rotation_axis)
            connector.apply_transform(rotation_matrix)
    
    # Position the connector
    center_pos = (np.array(pos1) + np.array(pos2)) / 2
    connector.apply_translation(center_pos)
    
    return connector

def generate_mesh(grid):
    """Generate complete spaceship mesh with connections"""
    Nx, Ny, Nz = grid.shape
    meshes = []
    positions = {}
    
    # First pass: create all modules and store positions
    for x in range(Nx):
        for y in range(Ny):
            for z in range(Nz):
                module = grid[x, y, z]
                if not module.get("enabled", True):
                    continue
                    
                pos_x = (x - Nx/2) * 1.2
                pos_y = (y - Ny/2) * 1.2
                pos_z = (z - Nz/2) * 1.0
                
                position = [pos_x, pos_y, pos_z]
                positions[(x, y, z)] = position
                
                # Create the mesh
                try:
                    m = create_primitive(
                        module["type"], 
                        module["radius"], 
                        module["height"]
                    )
                    
                    # Apply scaling
                    scale = module.get("scale", [1.0, 1.0, 1.0])
                    m.apply_scale(scale)
                    
                    # Apply rotation
                    rotation = module.get("rotation", [0, 0, 0])
                    for i, angle in enumerate(rotation):
                        if abs(angle) > 0.01:
                            axis = [0, 0, 0]
                            axis[i] = 1
                            m.apply_transform(trimesh.transformations.rotation_matrix(
                                np.radians(angle), axis
                            ))
                    
                    # Apply translation
                    m.apply_translation(position)
                    
                    # Set color
                    color = module.get("color", [128, 128, 128])
                    vertex_colors = np.tile(color + [255], (len(m.vertices), 1))
                    m.visual.vertex_colors = vertex_colors
                    
                    meshes.append(m)
                except Exception as e:
                    print(f"Error creating mesh at ({x},{y},{z}): {e}")
                    continue
    
    # Second pass: create connections between adjacent modules
    for x in range(Nx):
        for y in range(Ny):
            for z in range(Nz):
                if not grid[x, y, z].get("enabled", True):
                    continue
                    
                current_pos = positions.get((x, y, z))
                if current_pos is None:
                    continue
                
                # Check adjacent positions for connections
                for dx, dy, dz in [(1,0,0), (0,1,0), (0,0,1)]:
                    nx, ny, nz = x+dx, y+dy, z+dz
                    if (0 <= nx < Nx and 0 <= ny < Ny and 0 <= nz < Nz and
                        grid[nx, ny, nz].get("enabled", True)):
                        
                        next_pos = positions.get((nx, ny, nz))
                        if next_pos is not None:
                            connector = connect_modules(None, None, current_pos, next_pos)
                            if connector is not None:
                                # Color the connector gray
                                connector_color = [100, 100, 100, 255]
                                vertex_colors = np.tile(connector_color, (len(connector.vertices), 1))
                                connector.visual.vertex_colors = vertex_colors
                                meshes.append(connector)
    
    if not meshes:
        # Return a simple box if no valid meshes
        return trimesh.creation.box(extents=[1, 1, 1])
    
    # Combine all meshes
    try:
        combined_mesh = trimesh.util.concatenate(meshes)
        # Smooth the mesh for better appearance
        combined_mesh = combined_mesh.smoothed()
        return combined_mesh
    except Exception as e:
        print(f"Error combining meshes: {e}")
        return meshes[0] if meshes else trimesh.creation.box(extents=[1, 1, 1])


# ----------------------------
# 3. Enhanced OpenGL Widget for 3D preview
# ----------------------------
class MeshGLWidget(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.mesh = generate_mesh(grid)
        self.rot_x = 20
        self.rot_y = 30
        self.zoom = -15
        self.last_pos = None
        self.lighting = True
        self.wireframe = False
        self.auto_rotate = False
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_rotation)
        self.update_timer.start(50)  # 20 FPS

    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        
        # Set up lighting
        light_pos = [5.0, 5.0, 10.0, 1.0]
        light_ambient = [0.2, 0.2, 0.2, 1.0]
        light_diffuse = [0.8, 0.8, 0.8, 1.0]
        light_specular = [1.0, 1.0, 1.0, 1.0]
        
        glLightfv(GL_LIGHT0, GL_POSITION, light_pos)
        glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
        glLightfv(GL_LIGHT0, GL_SPECULAR, light_specular)
        
        glClearColor(0.05, 0.05, 0.1, 1.0)  # Dark space background

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, w/h if h != 0 else 1, 0.1, 100)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        # Camera transform
        glTranslatef(0, 0, self.zoom)
        glRotatef(self.rot_x, 1, 0, 0)
        glRotatef(self.rot_y, 0, 1, 0)
        
        # Toggle wireframe
        if self.wireframe:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        
        # Toggle lighting
        if self.lighting:
            glEnable(GL_LIGHTING)
        else:
            glDisable(GL_LIGHTING)
        
        self.draw_mesh()

    def draw_mesh(self):
        if self.mesh is None:
            return
            
        vertices = np.array(self.mesh.vertices)
        faces = np.array(self.mesh.faces)
        
        # Calculate normals for better lighting
        try:
            vertex_normals = self.mesh.vertex_normals
        except:
            vertex_normals = np.zeros_like(vertices)
        
        glBegin(GL_TRIANGLES)
        for face in faces:
            for idx in face:
                # Set normal
                if len(vertex_normals) > idx:
                    glNormal3f(*vertex_normals[idx])
                
                # Set color
                if (hasattr(self.mesh.visual, "vertex_colors") and 
                    len(self.mesh.visual.vertex_colors) > idx):
                    c = self.mesh.visual.vertex_colors[idx][:3] / 255.0
                    glColor3f(*c)
                else:
                    glColor3f(0.6, 0.6, 0.8)
                
                # Set vertex
                glVertex3f(*vertices[idx])
        glEnd()
        
        # Draw coordinate system
        self.draw_coordinate_system()

    def draw_coordinate_system(self):
        """Draw XYZ coordinate system for reference"""
        glDisable(GL_LIGHTING)
        glLineWidth(2.0)
        glBegin(GL_LINES)
        
        # X axis - Red
        glColor3f(1.0, 0.0, 0.0)
        glVertex3f(0, 0, 0)
        glVertex3f(2, 0, 0)
        
        # Y axis - Green
        glColor3f(0.0, 1.0, 0.0)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 2, 0)
        
        # Z axis - Blue
        glColor3f(0.0, 0.0, 1.0)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 0, 2)
        
        glEnd()
        glLineWidth(1.0)
        if self.lighting:
            glEnable(GL_LIGHTING)

    def update_rotation(self):
        if self.auto_rotate:
            self.rot_y += 1
            self.update()

    def update_mesh(self):
        """Update the mesh from current grid"""
        self.mesh = generate_mesh(grid)
        self.update()

    def mousePressEvent(self, event):
        self.last_pos = (event.position().x(), event.position().y())

    def mouseMoveEvent(self, event):
        if self.last_pos is None:
            return
            
        dx = event.position().x() - self.last_pos[0]
        dy = event.position().y() - self.last_pos[1]
        
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.rot_x += dy * 0.5
            self.rot_y += dx * 0.5
        elif event.buttons() == Qt.MouseButton.RightButton:
            self.zoom += dy * 0.1
            
        self.last_pos = (event.position().x(), event.position().y())
        self.update()

    def wheelEvent(self, event):
        self.zoom += event.angleDelta().y() * 0.01
        self.zoom = max(-50, min(-1, self.zoom))
        self.update()

    def toggle_wireframe(self):
        self.wireframe = not self.wireframe
        self.update()

    def toggle_lighting(self):
        self.lighting = not self.lighting
        self.update()

    def toggle_auto_rotate(self):
        self.auto_rotate = not self.auto_rotate


# ----------------------------
# 4. Enhanced GUI Control Panel
# ----------------------------
class ControlPanel(QWidget):
    def __init__(self, mesh_widget):
        super().__init__()
        self.mesh_widget = mesh_widget
        self.current_x = 0
        self.current_y = 0
        self.current_z = 0
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Position selection group
        pos_group = QGroupBox("Module Position")
        pos_layout = QGridLayout()
        
        pos_layout.addWidget(QLabel("X:"), 0, 0)
        self.spin_x = QSpinBox()
        self.spin_x.setRange(0, Nx-1)
        pos_layout.addWidget(self.spin_x, 0, 1)
        
        pos_layout.addWidget(QLabel("Y:"), 1, 0)
        self.spin_y = QSpinBox()
        self.spin_y.setRange(0, Ny-1)
        pos_layout.addWidget(self.spin_y, 1, 1)
        
        pos_layout.addWidget(QLabel("Z:"), 2, 0)
        self.spin_z = QSpinBox()
        self.spin_z.setRange(0, Nz-1)
        pos_layout.addWidget(self.spin_z, 2, 1)
        
        pos_group.setLayout(pos_layout)
        layout.addWidget(pos_group)

        # Module properties group
        props_group = QGroupBox("Module Properties")
        props_layout = QGridLayout()
        
        # Enable/disable
        self.enabled_check = QCheckBox("Enabled")
        self.enabled_check.setChecked(True)
        props_layout.addWidget(self.enabled_check, 0, 0, 1, 2)
        
        # Module type
        props_layout.addWidget(QLabel("Type:"), 1, 0)
        self.type_box = QComboBox()
        self.type_box.addItems(["cylinder", "cone", "box", "sphere", "torus", "wedge"])
        props_layout.addWidget(self.type_box, 1, 1)

        # Radius and height
        props_layout.addWidget(QLabel("Radius:"), 2, 0)
        self.radius_spin = QDoubleSpinBox()
        self.radius_spin.setSingleStep(0.05)
        self.radius_spin.setRange(0.01, 5)
        self.radius_spin.setDecimals(3)
        props_layout.addWidget(self.radius_spin, 2, 1)
        
        props_layout.addWidget(QLabel("Height:"), 3, 0)
        self.height_spin = QDoubleSpinBox()
        self.height_spin.setSingleStep(0.05)
        self.height_spin.setRange(0.01, 5)
        self.height_spin.setDecimals(3)
        props_layout.addWidget(self.height_spin, 3, 1)

        # Scale controls
        props_layout.addWidget(QLabel("Scale X:"), 4, 0)
        self.scale_x_spin = QDoubleSpinBox()
        self.scale_x_spin.setSingleStep(0.1)
        self.scale_x_spin.setRange(0.1, 5)
        self.scale_x_spin.setValue(1.0)
        props_layout.addWidget(self.scale_x_spin, 4, 1)
        
        # Color selection
        self.color_btn = QPushButton("Select Color")
        props_layout.addWidget(self.color_btn, 5, 0, 1, 2)
        
        props_group.setLayout(props_layout)
        layout.addWidget(props_group)

        # View controls group
        view_group = QGroupBox("View Controls")
        view_layout = QVBoxLayout()
        
        self.wireframe_btn = QPushButton("Toggle Wireframe")
        self.lighting_btn = QPushButton("Toggle Lighting")
        self.auto_rotate_btn = QPushButton("Auto Rotate")
        
        view_layout.addWidget(self.wireframe_btn)
        view_layout.addWidget(self.lighting_btn)
        view_layout.addWidget(self.auto_rotate_btn)
        
        view_group.setLayout(view_layout)
        layout.addWidget(view_group)

        # Action buttons
        action_group = QGroupBox("Actions")
        action_layout = QVBoxLayout()
        
        self.update_btn = QPushButton("Update Module")
        self.generate_ref_btn = QPushButton("Generate Reference Image")
        self.randomize_btn = QPushButton("Randomize Ship")
        self.save_btn = QPushButton("Save Grid")
        self.load_btn = QPushButton("Load Grid")
        self.export_btn = QPushButton("Export 3D Model")
        
        action_layout.addWidget(self.update_btn)
        action_layout.addWidget(self.generate_ref_btn)
        action_layout.addWidget(self.randomize_btn)
        action_layout.addWidget(self.save_btn)
        action_layout.addWidget(self.load_btn)
        action_layout.addWidget(self.export_btn)
        
        action_group.setLayout(action_layout)
        layout.addWidget(action_group)

        self.setLayout(layout)
        self.color = QColor(60, 80, 120)

        # Connect signals
        self.update_btn.clicked.connect(self.update_module)
        self.generate_ref_btn.clicked.connect(self.generate_reference)
        self.randomize_btn.clicked.connect(self.randomize_ship)
        self.save_btn.clicked.connect(self.save_grid)
        self.load_btn.clicked.connect(self.load_grid)
        self.export_btn.clicked.connect(self.export_mesh)
        self.color_btn.clicked.connect(self.select_color)
        self.wireframe_btn.clicked.connect(self.mesh_widget.toggle_wireframe)
        self.lighting_btn.clicked.connect(self.mesh_widget.toggle_lighting)
        self.auto_rotate_btn.clicked.connect(self.mesh_widget.toggle_auto_rotate)
        
        self.spin_x.valueChanged.connect(self.update_current)
        self.spin_y.valueChanged.connect(self.update_current)
        self.spin_z.valueChanged.connect(self.update_current)

        self.update_current()

    def update_current(self):
        """Update UI to reflect currently selected module"""
        self.current_x = self.spin_x.value()
        self.current_y = self.spin_y.value()
        self.current_z = self.spin_z.value()
        
        module = grid[self.current_x, self.current_y, self.current_z]
        
        self.enabled_check.setChecked(module.get("enabled", True))
        self.type_box.setCurrentText(module["type"])
        self.radius_spin.setValue(module["radius"])
        self.height_spin.setValue(module["height"])
        
        scale = module.get("scale", [1.0, 1.0, 1.0])
        self.scale_x_spin.setValue(scale[0])
        
        color = module.get("color", [60, 80, 120])
        self.color = QColor(*color[:3])

    def select_color(self):
        c = QColorDialog.getColor(self.color)
        if c.isValid():
            self.color = c

    def update_module(self):
        """Update the currently selected module with UI values"""
        module = grid[self.current_x, self.current_y, self.current_z]
        
        module["enabled"] = self.enabled_check.isChecked()
        module["type"] = self.type_box.currentText()
        module["radius"] = self.radius_spin.value()
        module["height"] = self.height_spin.value()
        module["scale"] = [self.scale_x_spin.value(), 1.0, 1.0]
        module["color"] = [self.color.red(), self.color.green(), self.color.blue()]
        
        # Update mesh in real-time
        self.mesh_widget.update_mesh()

    def generate_reference(self):
        """Generate reference image of the spaceship"""
        try:
            ref_path = generate_reference_image(grid)
            print(f"Reference image saved as: {ref_path}")
        except Exception as e:
            print(f"Error generating reference image: {e}")

    def randomize_ship(self):
        """Generate a new random spaceship"""
        global grid
        grid = init_grid()
        self.update_current()
        self.mesh_widget.update_mesh()

    def save_grid(self):
        """Save current grid to file"""
        try:
            save_grid(grid)
            print("Grid saved successfully!")
        except Exception as e:
            print(f"Error saving grid: {e}")

    def load_grid(self):
        """Load grid from file"""
        global grid
        try:
            filename, _ = QFileDialog.getOpenFileName(
                self, "Load Grid", "", "JSON Files (*.json)"
            )
            if filename:
                with open(filename, "r") as f:
                    data = json.load(f)
                    new_grid = np.empty((len(data), len(data[0]), len(data[0][0])), dtype=object)
                    for x in range(len(data)):
                        for y in range(len(data[x])):
                            for z in range(len(data[x][y])):
                                new_grid[x, y, z] = data[x][y][z]
                    grid = new_grid
                    self.update_current()
                    self.mesh_widget.update_mesh()
                    print("Grid loaded successfully!")
        except Exception as e:
            print(f"Error loading grid: {e}")

    def export_mesh(self):
        """Export the current mesh to various formats"""
        try:
            m = generate_mesh(grid)
            filename, _ = QFileDialog.getSaveFileName(
                self, "Export Mesh", "spaceship", 
                "STL Files (*.stl);;GLB Files (*.glb);;OBJ Files (*.obj);;PLY Files (*.ply)"
            )
            if filename:
                m.export(filename)
                print(f"Mesh exported as: {filename}")
        except Exception as e:
            print(f"Error exporting mesh: {e}")

class ReferenceImageWidget(QWidget):
    """Widget to display the reference image"""
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Matplotlib canvas for reference image
        self.figure = Figure(figsize=(8, 4))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
        # Button to generate reference
        self.generate_btn = QPushButton("Generate Reference Image")
        self.generate_btn.clicked.connect(self.generate_reference)
        layout.addWidget(self.generate_btn)
        
        self.setLayout(layout)
        
    def generate_reference(self):
        """Generate and display reference image"""
        try:
            self.figure.clear()
            
            # Create reference views
            ax1 = self.figure.add_subplot(121)
            ax2 = self.figure.add_subplot(122)
            
            # Top view
            top_view = np.zeros((Nx, Nz, 3))
            for x in range(Nx):
                for z in range(Nz):
                    avg_color = [0, 0, 0]
                    count = 0
                    for y in range(Ny):
                        if grid[x, y, z].get("enabled", True):
                            color = grid[x, y, z]["color"]
                            avg_color = [avg_color[i] + color[i]/255.0 for i in range(3)]
                            count += 1
                    if count > 0:
                        top_view[x, z] = [c/count for c in avg_color]
            
            ax1.imshow(top_view, origin='lower', aspect='auto')
            ax1.set_title("Spaceship Top View")
            ax1.set_xlabel("Z (Front-Back)")
            ax1.set_ylabel("X (Left-Right)")
            
            # Side view
            side_view = np.zeros((Ny, Nz, 3))
            for y in range(Ny):
                for z in range(Nz):
                    avg_color = [0, 0, 0]
                    count = 0
                    for x in range(Nx):
                        if grid[x, y, z].get("enabled", True):
                            color = grid[x, y, z]["color"]
                            avg_color = [avg_color[i] + color[i]/255.0 for i in range(3)]
                            count += 1
                    if count > 0:
                        side_view[y, z] = [c/count for c in avg_color]
            
            ax2.imshow(side_view, origin='lower', aspect='auto')
            ax2.set_title("Spaceship Side View")
            ax2.set_xlabel("Z (Front-Back)")
            ax2.set_ylabel("Y (Up-Down)")
            
            self.figure.tight_layout()
            self.canvas.draw()
            
        except Exception as e:
            print(f"Error generating reference: {e}")


# ----------------------------
# 5. Main Window with Tabs
# ----------------------------
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Advanced Spaceship Designer - v2.0")
        self.setMinimumSize(1400, 900)
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout()
        
        # Left side: 3D preview (takes most space)
        self.mesh_widget = MeshGLWidget()
        main_layout.addWidget(self.mesh_widget, 3)
        
        # Right side: Tabbed control panel
        self.tab_widget = QTabWidget()
        
        # Module Editor Tab
        self.controls = ControlPanel(self.mesh_widget)
        self.tab_widget.addTab(self.controls, "Module Editor")
        
        # Reference Image Tab
        self.ref_widget = ReferenceImageWidget()
        self.tab_widget.addTab(self.ref_widget, "Reference Image")
        
        # Info Tab
        self.info_widget = InfoWidget()
        self.tab_widget.addTab(self.info_widget, "Info & Stats")
        
        main_layout.addWidget(self.tab_widget, 1)
        
        self.setLayout(main_layout)
        
        # Generate initial reference image
        self.ref_widget.generate_reference()

class InfoWidget(QWidget):
    """Widget showing information and statistics about the spaceship"""
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Spaceship Designer v2.0")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        # Instructions
        instructions = QTextEdit()
        instructions.setReadOnly(True)
        instructions.setMaximumHeight(200)
        instructions.setPlainText("""
CONTROLS:
• Mouse: Rotate view (left click & drag)
• Mouse Wheel: Zoom in/out
• Right Click + Drag: Pan view

FEATURES:
• Real-time 3D preview with lighting
• Multiple primitive types (cylinder, cone, box, sphere, torus, wedge)
• Color customization per module
• Export to STL, GLB, OBJ, PLY formats
• Save/load configurations
• Reference image generation
• Wireframe and lighting toggles
• Auto-rotation mode

WORKFLOW:
1. Select a position in the grid (X,Y,Z)
2. Choose module type and properties
3. Click "Update Module" to apply changes
4. Use view controls for better visualization
5. Generate reference images for documentation
6. Export your spaceship as 3D model
        """)
        layout.addWidget(instructions)
        
        # Statistics
        stats_group = QGroupBox("Current Ship Statistics")
        stats_layout = QVBoxLayout()
        
        self.stats_label = QLabel()
        self.update_stats()
        stats_layout.addWidget(self.stats_label)
        
        # Update button
        update_stats_btn = QPushButton("Update Statistics")
        update_stats_btn.clicked.connect(self.update_stats)
        stats_layout.addWidget(update_stats_btn)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        # Progress bar for operations
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        layout.addStretch()
        self.setLayout(layout)
        
    def update_stats(self):
        """Update and display statistics about the current spaceship"""
        try:
            total_modules = Nx * Ny * Nz
            enabled_modules = 0
            module_types = {}
            
            for x in range(Nx):
                for y in range(Ny):
                    for z in range(Nz):
                        module = grid[x, y, z]
                        if module.get("enabled", True):
                            enabled_modules += 1
                            mod_type = module["type"]
                            module_types[mod_type] = module_types.get(mod_type, 0) + 1
            
            # Generate mesh stats
            mesh = generate_mesh(grid)
            vertex_count = len(mesh.vertices) if hasattr(mesh, 'vertices') else 0
            face_count = len(mesh.faces) if hasattr(mesh, 'faces') else 0
            
            stats_text = f"""
Grid Size: {Nx} × {Ny} × {Nz} = {total_modules} positions
Enabled Modules: {enabled_modules}
Disabled Modules: {total_modules - enabled_modules}

Module Types:
"""
            for mod_type, count in module_types.items():
                stats_text += f"• {mod_type.capitalize()}: {count}\n"
            
            stats_text += f"""
Mesh Statistics:
• Vertices: {vertex_count:,}
• Faces: {face_count:,}
• Approximate Volume: {mesh.volume:.3f}
            """
            
            self.stats_label.setText(stats_text)
            
        except Exception as e:
            self.stats_label.setText(f"Error calculating stats: {e}")


# ----------------------------
# 6. Application Entry Point
# ----------------------------
def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("Spaceship Designer")
    app.setApplicationVersion("2.0")
    
    # Set application style
    app.setStyle('Fusion')
    
    # Apply dark theme
    palette = app.palette()
    palette.setColor(palette.ColorRole.Window, QColor(53, 53, 53))
    palette.setColor(palette.ColorRole.WindowText, QColor(255, 255, 255))
    palette.setColor(palette.ColorRole.Base, QColor(25, 25, 25))
    palette.setColor(palette.ColorRole.AlternateBase, QColor(53, 53, 53))
    palette.setColor(palette.ColorRole.ToolTipBase, QColor(0, 0, 0))
    palette.setColor(palette.ColorRole.ToolTipText, QColor(255, 255, 255))
    palette.setColor(palette.ColorRole.Text, QColor(255, 255, 255))
    palette.setColor(palette.ColorRole.Button, QColor(53, 53, 53))
    palette.setColor(palette.ColorRole.ButtonText, QColor(255, 255, 255))
    palette.setColor(palette.ColorRole.BrightText, QColor(255, 0, 0))
    palette.setColor(palette.ColorRole.Link, QColor(42, 130, 218))
    palette.setColor(palette.ColorRole.Highlight, QColor(42, 130, 218))
    palette.setColor(palette.ColorRole.HighlightedText, QColor(0, 0, 0))
    app.setPalette(palette)
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Generate initial reference image
    try:
        generate_reference_image(grid)
        print("Initial reference image generated: spaceship_reference.png")
    except Exception as e:
        print(f"Could not generate initial reference: {e}")
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
