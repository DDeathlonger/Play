#!/usr/bin/env python3
"""
Advanced Spaceship 3D Model Generator
Creates sophisticated, connected spaceship meshes with real-time preview and editing.
"""

import sys
import json
import numpy as np
import trimesh
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt

# Try to import Qt libraries
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
        print("Please install PyQt6: pip install PyQt6 PyOpenGL")
        sys.exit(1)

try:
    from OpenGL.GL import *
    from OpenGL.GLU import *
except ImportError:
    print("Error: PyOpenGL not found!")
    print("Please install PyOpenGL: pip install PyOpenGL")
    sys.exit(1)

# Configuration
GRID_SIZE = (8, 5, 12)  # X, Y, Z dimensions
GRID_FILE = "spaceship_config.json"

class SpaceshipModule:
    """Represents a single module in the spaceship grid"""
    def __init__(self, mod_type="cylinder", radius=0.5, height=1.0, color=None):
        self.type = mod_type
        self.radius = radius
        self.height = height
        self.color = color or [100, 150, 200]
        self.enabled = True
        self.rotation = [0, 0, 0]
        self.scale = [1.0, 1.0, 1.0]
        
    def to_dict(self):
        return {
            "type": self.type,
            "radius": self.radius,
            "height": self.height,
            "color": self.color,
            "enabled": self.enabled,
            "rotation": self.rotation,
            "scale": self.scale
        }
    
    @classmethod
    def from_dict(cls, data):
        module = cls()
        module.type = data.get("type", "cylinder")
        module.radius = data.get("radius", 0.5)
        module.height = data.get("height", 1.0)
        module.color = data.get("color", [100, 150, 200])
        module.enabled = data.get("enabled", True)
        module.rotation = data.get("rotation", [0, 0, 0])  
        module.scale = data.get("scale", [1.0, 1.0, 1.0])
        return module

class SpaceshipGenerator:
    """Main class for generating spaceship geometry"""
    
    def __init__(self, grid_size=GRID_SIZE):
        self.grid_size = grid_size
        self.grid = self.create_default_spaceship()
    
    def create_default_spaceship(self):
        """Create a sophisticated default spaceship configuration"""
        nx, ny, nz = self.grid_size
        grid = {}
        
        for x in range(nx):
            for y in range(ny):
                for z in range(nz):
                    # Calculate position factors for ship design
                    center_x = abs(x - nx//2) / (nx//2) if nx > 1 else 0
                    center_y = abs(y - ny//2) / (ny//2) if ny > 1 else 0
                    front_factor = z / (nz - 1) if nz > 1 else 0
                    
                    # Create different sections of the spaceship
                    if z < nz * 0.15:  # Engine section - rear
                        if center_x < 0.5 and center_y < 0.7:
                            mod_type = "cylinder"
                            radius = 0.5 + 0.3 * (1 - center_x) * (1 - center_y)
                            height = 1.5
                            color = [180, 60, 255]  # Purple/magenta engines
                        else:
                            mod_type = "cone"
                            radius = 0.3
                            height = 0.8
                            color = [120, 40, 180]
                            
                    elif z < nz * 0.35:  # Main hull
                        mod_type = "box"
                        radius = 0.7 + 0.4 * (1 - center_x) * (1 - center_y)
                        height = 1.8
                        color = [80, 120, 200]  # Blue hull
                        
                    elif z < nz * 0.6:  # Mid section with details
                        if np.random.random() < 0.7:  # Not all positions filled
                            mod_type = np.random.choice(["cylinder", "box", "sphere"])
                            radius = 0.4 + 0.4 * (1 - center_x) * (1 - center_y)
                            height = 1.2
                            color = [140, 140, 160]  # Gray details
                        else:
                            continue  # Skip this position
                            
                    elif z < nz * 0.8:  # Forward section
                        mod_type = "cone" if center_x > 0.6 else "cylinder"
                        radius = 0.3 + 0.6 * (1 - center_x) * (1 - center_y) * (1 - front_factor * 0.5)
                        height = 1.0
                        color = [100, 140, 180]  # Light blue
                        
                    else:  # Cockpit/nose
                        mod_type = "wedge" if z > nz * 0.9 else "cone"
                        radius = 0.15 + 0.4 * (1 - center_x) * (1 - center_y) * (1 - front_factor)
                        height = 0.7
                        color = [60, 80, 140]  # Dark blue cockpit
                    
                    # Add variation and details
                    radius *= (0.7 + 0.6 * np.random.random())
                    height *= (0.7 + 0.6 * np.random.random())
                    
                    # Ensure minimum sizes
                    radius = max(0.1, radius)
                    height = max(0.2, height)
                    
                    # Add color variation
                    color = [max(20, min(255, int(c + 40 * np.random.randn()))) for c in color]
                    
                    grid[(x, y, z)] = SpaceshipModule(mod_type, radius, height, color)
        
        return grid
    
    def create_primitive(self, module):
        """Create a 3D primitive based on module type"""
        if not module.enabled:
            return None
            
        try:
            if module.type == "cylinder":
                mesh = trimesh.creation.cylinder(
                    radius=module.radius, 
                    height=module.height, 
                    sections=20
                )
            elif module.type == "cone":
                mesh = trimesh.creation.cone(
                    radius=module.radius, 
                    height=module.height, 
                    sections=16
                )
            elif module.type == "sphere":
                mesh = trimesh.creation.icosphere(
                    subdivisions=2, 
                    radius=module.radius
                )
            elif module.type == "torus":
                mesh = trimesh.creation.torus(
                    major_radius=module.radius, 
                    minor_radius=module.radius * 0.3,
                    major_sections=16,
                    minor_sections=8
                )
            elif module.type == "wedge":
                # Create aerodynamic wedge shape
                mesh = trimesh.creation.box(extents=[module.radius*2, module.height, module.radius*2])
                vertices = mesh.vertices.copy()
                for i, vertex in enumerate(vertices):
                    if vertex[2] > 0:  # Taper the front part
                        scale_factor = 1 - 0.9 * (vertex[2] / module.radius)
                        vertices[i][0] *= scale_factor
                        vertices[i][1] *= scale_factor * 0.7  # More aggressive taper on Y
                mesh.vertices = vertices
            else:  # box - default
                mesh = trimesh.creation.box(
                    extents=[module.radius*2, module.height, module.radius*2]
                )
            
            return mesh
            
        except Exception as e:
            print(f"Error creating primitive {module.type}: {e}")
            return trimesh.creation.box(extents=[0.2, 0.2, 0.2])
    
    def create_connector(self, pos1, pos2, module1, module2):
        """Create connecting geometry between adjacent modules"""
        try:
            # Calculate positions
            nx, ny, nz = self.grid_size
            world_pos1 = [(pos1[i] - self.grid_size[i]//2) * 1.5 for i in range(3)]
            world_pos2 = [(pos2[i] - self.grid_size[i]//2) * 1.5 for i in range(3)]
            
            direction = np.array(world_pos2) - np.array(world_pos1)
            distance = np.linalg.norm(direction)
            
            if distance < 0.5:  # Too close, don't connect
                return None
            
            # Create connector cylinder
            connector_radius = min(0.15, min(module1.radius, module2.radius) * 0.3)
            connector = trimesh.creation.cylinder(
                radius=connector_radius,
                height=distance * 0.8,  # Slightly shorter than full distance
                sections=8
            )
            
            # Orient connector
            if distance > 0.001:
                direction_norm = direction / distance
                z_axis = np.array([0, 0, 1])
                
                if not np.allclose(direction_norm, z_axis):
                    rotation_axis = np.cross(z_axis, direction_norm)
                    rotation_angle = np.arccos(np.clip(np.dot(z_axis, direction_norm), -1, 1))
                    
                    if np.linalg.norm(rotation_axis) > 0.001:
                        rotation_matrix = trimesh.transformations.rotation_matrix(
                            rotation_angle, rotation_axis
                        )
                        connector.apply_transform(rotation_matrix)
            
            # Position connector
            center_pos = (np.array(world_pos1) + np.array(world_pos2)) / 2
            connector.apply_translation(center_pos)
            
            # Color the connector
            connector_color = [90, 90, 90, 255]  # Gray connectors
            vertex_colors = np.tile(connector_color, (len(connector.vertices), 1))
            connector.visual.vertex_colors = vertex_colors
            
            return connector
            
        except Exception as e:
            print(f"Error creating connector: {e}")
            return None
    
    def generate_mesh(self):
        """Generate the complete spaceship mesh with connections"""
        nx, ny, nz = self.grid_size
        meshes = []
        
        # First pass: create all module meshes
        module_positions = {}
        
        for (x, y, z), module in self.grid.items():
            if not module.enabled:
                continue
                
            mesh = self.create_primitive(module)
            if mesh is None:
                continue
            
            # Apply scaling
            scale = module.scale
            if any(s != 1.0 for s in scale):
                mesh.apply_scale(scale)
            
            # Apply rotation
            for i, angle in enumerate(module.rotation):
                if abs(angle) > 0.001:
                    axis = [0, 0, 0]
                    axis[i] = 1
                    mesh.apply_transform(
                        trimesh.transformations.rotation_matrix(np.radians(angle), axis)
                    )
            
            # Position the mesh in world space
            pos_x = (x - nx//2) * 1.5
            pos_y = (y - ny//2) * 1.5  
            pos_z = (z - nz//2) * 1.2
            world_pos = [pos_x, pos_y, pos_z]
            mesh.apply_translation(world_pos)
            
            # Store position for connector generation
            module_positions[(x, y, z)] = (world_pos, module)
            
            # Set colors
            color = module.color + [255]
            vertex_colors = np.tile(color, (len(mesh.vertices), 1))
            mesh.visual.vertex_colors = vertex_colors
            
            meshes.append(mesh)
        
        # Second pass: create connectors between adjacent modules
        for (x, y, z), (pos, module) in module_positions.items():
            # Check adjacent positions
            for dx, dy, dz in [(1, 0, 0), (0, 1, 0), (0, 0, 1), (-1, 0, 0), (0, -1, 0), (0, 0, -1)]:
                adj_pos = (x + dx, y + dy, z + dz)
                
                if adj_pos in module_positions:
                    adj_world_pos, adj_module = module_positions[adj_pos]
                    
                    # Only create connector once per pair
                    if (x + y + z) < (adj_pos[0] + adj_pos[1] + adj_pos[2]):
                        connector = self.create_connector(
                            (x, y, z), adj_pos, module, adj_module
                        )
                        if connector is not None:
                            meshes.append(connector)
        
        if not meshes:
            print("No valid meshes created, returning default box")
            return trimesh.creation.box(extents=[2, 2, 2])
        
        # Combine all meshes
        try:
            print(f"Combining {len(meshes)} mesh components...")
            combined = trimesh.util.concatenate(meshes)
            
            # Optional: smooth the combined mesh for better appearance
            if hasattr(combined, 'smoothed'):
                try:
                    combined = combined.smoothed()
                except:
                    pass  # Smoothing failed, use original
            
            print(f"Final mesh: {len(combined.vertices)} vertices, {len(combined.faces)} faces")
            return combined
            
        except Exception as e:
            print(f"Error combining meshes: {e}")
            return meshes[0] if meshes else trimesh.creation.box(extents=[1, 1, 1])
    
    def generate_reference_image(self):
        """Generate reference images of the spaceship"""
        try:
            fig, axes = plt.subplots(2, 2, figsize=(12, 10))
            nx, ny, nz = self.grid_size
            
            # Top view (X-Z plane)
            top_view = np.zeros((nx, nz, 3))
            for x in range(nx):
                for z in range(nz):
                    colors = []
                    for y in range(ny):
                        pos = (x, y, z)
                        if pos in self.grid and self.grid[pos].enabled:
                            color = np.array(self.grid[pos].color) / 255.0
                            colors.append(color)
                    if colors:
                        top_view[x, z] = np.mean(colors, axis=0)
            
            axes[0, 0].imshow(top_view, origin='lower', aspect='auto')
            axes[0, 0].set_title("Top View (X-Z)")
            axes[0, 0].set_xlabel("Z (Front-Back)")
            axes[0, 0].set_ylabel("X (Left-Right)")
            
            # Side view (Y-Z plane)
            side_view = np.zeros((ny, nz, 3))
            for y in range(ny):
                for z in range(nz):
                    colors = []
                    for x in range(nx):
                        pos = (x, y, z)
                        if pos in self.grid and self.grid[pos].enabled:
                            color = np.array(self.grid[pos].color) / 255.0
                            colors.append(color)
                    if colors:
                        side_view[y, z] = np.mean(colors, axis=0)
            
            axes[0, 1].imshow(side_view, origin='lower', aspect='auto')
            axes[0, 1].set_title("Side View (Y-Z)")
            axes[0, 1].set_xlabel("Z (Front-Back)")
            axes[0, 1].set_ylabel("Y (Up-Down)")
            
            # Front view (X-Y plane)
            front_view = np.zeros((nx, ny, 3))
            for x in range(nx):
                for y in range(ny):
                    colors = []
                    for z in range(nz):
                        pos = (x, y, z)
                        if pos in self.grid and self.grid[pos].enabled:
                            color = np.array(self.grid[pos].color) / 255.0
                            colors.append(color)
                    if colors:
                        front_view[x, y] = np.mean(colors, axis=0)
            
            axes[1, 0].imshow(front_view, origin='lower', aspect='auto')
            axes[1, 0].set_title("Front View (X-Y)")
            axes[1, 0].set_xlabel("Y (Up-Down)")
            axes[1, 0].set_ylabel("X (Left-Right)")
            
            # Statistics
            total_modules = len(self.grid)
            enabled_modules = sum(1 for m in self.grid.values() if m.enabled)
            module_types = {}
            for module in self.grid.values():
                if module.enabled:
                    module_types[module.type] = module_types.get(module.type, 0) + 1
            
            stats_text = f"Total Modules: {total_modules}\n"
            stats_text += f"Enabled: {enabled_modules}\n"
            stats_text += f"Disabled: {total_modules - enabled_modules}\n\n"
            stats_text += "Module Types:\n"
            for mod_type, count in module_types.items():
                stats_text += f"  {mod_type}: {count}\n"
            
            axes[1, 1].text(0.1, 0.9, stats_text, transform=axes[1, 1].transAxes, 
                           fontsize=10, verticalalignment='top', fontfamily='monospace')
            axes[1, 1].set_title("Statistics")
            axes[1, 1].axis('off')
            
            plt.tight_layout()
            plt.savefig("spaceship_reference.png", dpi=150, bbox_inches='tight')
            plt.close()
            
            print("Reference image saved as: spaceship_reference.png")
            return "spaceship_reference.png"
            
        except Exception as e:
            print(f"Error generating reference image: {e}")
            return None
    
    def save_configuration(self, filename=None):
        """Save the current spaceship configuration"""
        filename = filename or GRID_FILE
        
        config = {
            "grid_size": self.grid_size,
            "modules": {}
        }
        
        for pos, module in self.grid.items():
            config["modules"][str(pos)] = module.to_dict()
        
        try:
            with open(filename, 'w') as f:
                json.dump(config, f, indent=2)
            print(f"Configuration saved to: {filename}")
        except Exception as e:
            print(f"Error saving configuration: {e}")
    
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
                self.grid[pos] = SpaceshipModule.from_dict(module_data)
            
            print(f"Configuration loaded from: {filename}")
                
        except FileNotFoundError:
            print(f"Configuration file {filename} not found, creating default.")
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
        self.rot_x = 15
        self.rot_y = 45
        self.zoom = -20
        self.last_pos = None
        self.wireframe = False
        self.lighting = True
        self.auto_rotate = False
        self.update_mesh()
        
        # Auto-update timer for smooth rotation
        self.timer = QTimer()
        self.timer.timeout.connect(self.animate)
        self.timer.start(50)  # 20 FPS
    
    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Enhanced lighting setup
        glLightfv(GL_LIGHT0, GL_POSITION, [10.0, 10.0, 10.0, 1.0])
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.3, 0.3, 0.4, 1.0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8, 0.8, 0.9, 1.0])
        glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
        
        # Material properties
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [0.5, 0.5, 0.5, 1.0])
        glMaterialfv(GL_FRONT_AND_BACK, GL_SHININESS, [50.0])
        
        glClearColor(0.02, 0.02, 0.08, 1.0)  # Deep space background
    
    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, w/h if h > 0 else 1, 0.1, 200)
        glMatrixMode(GL_MODELVIEW)
    
    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        # Camera transformations
        glTranslatef(0, 0, self.zoom)
        glRotatef(self.rot_x, 1, 0, 0)
        glRotatef(self.rot_y, 0, 1, 0)
        
        # Rendering mode toggles
        if self.wireframe:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
            glLineWidth(1.5)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        
        if self.lighting:
            glEnable(GL_LIGHTING)
        else:
            glDisable(GL_LIGHTING)
        
        self.render_mesh()
        self.render_coordinate_system()
    
    def render_mesh(self):
        """Render the spaceship mesh"""
        if self.mesh is None:
            return
        
        vertices = np.array(self.mesh.vertices)
        faces = np.array(self.mesh.faces)
        
        try:
            normals = np.array(self.mesh.vertex_normals)
        except:
            normals = np.zeros_like(vertices)
        
        # Render all triangles
        glBegin(GL_TRIANGLES)
        for face in faces:
            for vertex_idx in face:
                if vertex_idx < len(vertices):
                    # Set normal for lighting
                    if vertex_idx < len(normals):
                        normal = normals[vertex_idx]
                        glNormal3f(normal[0], normal[1], normal[2])
                    
                    # Set vertex color
                    if (hasattr(self.mesh.visual, 'vertex_colors') and 
                        vertex_idx < len(self.mesh.visual.vertex_colors)):
                        color = self.mesh.visual.vertex_colors[vertex_idx][:3] / 255.0
                        glColor3f(color[0], color[1], color[2])
                    else:
                        glColor3f(0.7, 0.8, 0.9)  # Default light blue
                    
                    # Set vertex position
                    vertex = vertices[vertex_idx]
                    glVertex3f(vertex[0], vertex[1], vertex[2])
        glEnd()
    
    def render_coordinate_system(self):
        """Render XYZ coordinate axes for reference"""
        glDisable(GL_LIGHTING)
        glLineWidth(3.0)
        glBegin(GL_LINES)
        
        # X axis - Red
        glColor3f(1.0, 0.0, 0.0)
        glVertex3f(0, 0, 0)
        glVertex3f(5, 0, 0)
        
        # Y axis - Green
        glColor3f(0.0, 1.0, 0.0)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 5, 0)
        
        # Z axis - Blue
        glColor3f(0.0, 0.0, 1.0)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 0, 5)
        
        glEnd()
        glLineWidth(1.0)
        
        if self.lighting:
            glEnable(GL_LIGHTING)
    
    def animate(self):
        """Animation loop for auto-rotation"""
        if self.auto_rotate:
            self.rot_y += 1.0
            if self.rot_y >= 360:
                self.rot_y -= 360
        self.update()
    
    def update_mesh(self):
        """Regenerate mesh from current configuration"""
        print("Updating mesh...")
        self.mesh = self.generator.generate_mesh()
        self.update()
    
    def get_mouse_pos(self, event):
        """Get mouse position in a Qt version-agnostic way"""
        if QT_VERSION == 6:
            return event.position().toPoint()
        else:  # PyQt5
            return event.pos()
    
    def mousePressEvent(self, event):
        self.last_pos = self.get_mouse_pos(event)
    
    def mouseMoveEvent(self, event):
        if self.last_pos is None:
            return
            
        pos = self.get_mouse_pos(event)
        dx = pos.x() - self.last_pos.x()
        dy = pos.y() - self.last_pos.y()
        
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.rot_x += dy * 0.5
            self.rot_y += dx * 0.5
        elif event.buttons() == Qt.MouseButton.RightButton:
            self.zoom += dy * 0.1
        
        self.last_pos = pos
        self.update()
    
    def wheelEvent(self, event):
        if hasattr(event, 'angleDelta'):
            delta = event.angleDelta().y()
        else:  # PyQt5
            delta = event.delta()
            
        self.zoom += delta * 0.01
        self.zoom = max(-100, min(-2, self.zoom))
        self.update()
    
    def toggle_wireframe(self):
        self.wireframe = not self.wireframe
        self.update()
    
    def toggle_lighting(self):
        self.lighting = not self.lighting  
        self.update()
    
    def toggle_auto_rotate(self):
        self.auto_rotate = not self.auto_rotate

# ... [Previous ControlWidget and MainWindow classes remain the same, continuing in next part]

class ControlWidget(QWidget):
    """Control panel for editing spaceship modules"""
    
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
        self.radius_spin.setRange(0.01, 10.0)
        self.radius_spin.setSingleStep(0.05)
        self.radius_spin.setDecimals(3)
        props_layout.addWidget(QLabel("Radius:"), 2, 0)
        props_layout.addWidget(self.radius_spin, 2, 1)
        
        self.height_spin = QDoubleSpinBox()
        self.height_spin.setRange(0.01, 10.0)
        self.height_spin.setSingleStep(0.05)
        self.height_spin.setDecimals(3)
        props_layout.addWidget(QLabel("Height:"), 3, 0)
        props_layout.addWidget(self.height_spin, 3, 1)
        
        self.scale_spin = QDoubleSpinBox()
        self.scale_spin.setRange(0.1, 5.0)
        self.scale_spin.setSingleStep(0.1)
        self.scale_spin.setValue(1.0)
        props_layout.addWidget(QLabel("Scale:"), 4, 0)
        props_layout.addWidget(self.scale_spin, 4, 1)
        
        self.color_btn = QPushButton("Choose Color")
        props_layout.addWidget(self.color_btn, 5, 0, 1, 2)
        
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
        
        for btn in [self.update_btn, self.randomize_btn, self.save_btn, 
                   self.load_btn, self.export_btn, self.reference_btn]:
            action_layout.addWidget(btn)
        
        action_group.setLayout(action_layout)
        layout.addWidget(action_group)
        
        # View controls
        view_group = QGroupBox("View Controls")
        view_layout = QVBoxLayout()
        
        self.wireframe_btn = QPushButton("Toggle Wireframe")
        self.lighting_btn = QPushButton("Toggle Lighting")
        self.auto_rotate_btn = QPushButton("Auto Rotate")
        
        for btn in [self.wireframe_btn, self.lighting_btn, self.auto_rotate_btn]:
            view_layout.addWidget(btn)
        
        view_group.setLayout(view_layout)
        layout.addWidget(view_group)
        
        layout.addStretch()
        self.setLayout(layout)
        
        # Connect all signals
        self.connect_signals()
        self.update_ui()
    
    def connect_signals(self):
        """Connect all widget signals to handlers"""
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
        
        self.wireframe_btn.clicked.connect(self.viewer.toggle_wireframe)
        self.lighting_btn.clicked.connect(self.viewer.toggle_lighting)
        self.auto_rotate_btn.clicked.connect(self.viewer.toggle_auto_rotate)
    
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
            self.scale_spin.setValue(module.scale[0])  # Uniform scaling for simplicity
        else:
            # Create new module at this position
            self.generator.grid[self.current_pos] = SpaceshipModule()
            self.update_ui()
    
    def update_module(self):
        """Update the current module with UI values"""
        if self.current_pos not in self.generator.grid:
            self.generator.grid[self.current_pos] = SpaceshipModule()
        
        module = self.generator.grid[self.current_pos]
        module.enabled = self.enabled_check.isChecked()
        module.type = self.type_combo.currentText()
        module.radius = self.radius_spin.value()
        module.height = self.height_spin.value()
        scale_val = self.scale_spin.value()
        module.scale = [scale_val, scale_val, scale_val]
        
        print(f"Updated module at {self.current_pos}: {module.type}, enabled: {module.enabled}")
        self.viewer.update_mesh()
    
    def choose_color(self):
        """Open color picker dialog"""
        if self.current_pos not in self.generator.grid:
            self.generator.grid[self.current_pos] = SpaceshipModule()
            
        module = self.generator.grid[self.current_pos]
        current_color = QColor(*module.color[:3])
        color = QColorDialog.getColor(current_color, self)
        
        if color.isValid():
            module.color = [color.red(), color.green(), color.blue()]
            self.viewer.update_mesh()
    
    def randomize_ship(self):
        """Generate a new random spaceship"""
        print("Generating new spaceship...")
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
                print(f"Exporting mesh to {filename}...")
                mesh = self.generator.generate_mesh()
                mesh.export(filename)
                QMessageBox.information(self, "Exported", f"Model exported to {filename}")
                print(f"Export successful: {filename}")
            except Exception as e:
                error_msg = f"Failed to export: {e}"
                print(error_msg)
                QMessageBox.critical(self, "Export Error", error_msg)
    
    def generate_reference(self):
        """Generate reference image"""
        try:
            print("Generating reference image...")
            ref_path = self.generator.generate_reference_image()
            if ref_path:
                QMessageBox.information(self, "Reference Generated", 
                                      f"Reference image saved as {ref_path}")
            else:
                QMessageBox.warning(self, "Reference Error", "Failed to generate reference image")
        except Exception as e:
            error_msg = f"Failed to generate reference: {e}"
            print(error_msg)
            QMessageBox.critical(self, "Reference Error", error_msg)

class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Advanced Spaceship Designer v3.0")
        self.setMinimumSize(1400, 900)
        
        # Create generator and UI components
        print("Initializing spaceship generator...")
        self.generator = SpaceshipGenerator()
        
        print("Setting up 3D viewer...")
        self.viewer = SpaceshipViewer(self.generator)
        
        print("Setting up control panel...")
        self.controls = ControlWidget(self.generator, self.viewer)
        
        self.setup_ui()
        self.create_menu_bar()
        
        print("Application ready!")
    
    def setup_ui(self):
        """Setup the main UI layout"""
        central_widget = QWidget()
        layout = QHBoxLayout()
        
        # 3D viewer gets most of the space
        layout.addWidget(self.viewer, 3)
        
        # Control panel gets smaller portion
        layout.addWidget(self.controls, 1)
        
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        
        # Status bar
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready - Left click & drag to rotate, scroll to zoom, right click & drag to pan")
    
    def create_menu_bar(self):
        """Create application menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        new_action = QAction('New Spaceship', self)
        new_action.setShortcut('Ctrl+N')
        new_action.triggered.connect(self.controls.randomize_ship)
        file_menu.addAction(new_action)
        
        file_menu.addSeparator()
        
        save_action = QAction('Save Configuration', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.controls.save_config)
        file_menu.addAction(save_action)
        
        load_action = QAction('Load Configuration', self)
        load_action.setShortcut('Ctrl+O')
        load_action.triggered.connect(self.controls.load_config)
        file_menu.addAction(load_action)
        
        file_menu.addSeparator()
        
        export_action = QAction('Export 3D Model', self)
        export_action.setShortcut('Ctrl+E')
        export_action.triggered.connect(self.controls.export_model)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        quit_action = QAction('Quit', self)
        quit_action.setShortcut('Ctrl+Q')
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)
        
        # View menu
        view_menu = menubar.addMenu('View')
        
        wireframe_action = QAction('Toggle Wireframe', self)
        wireframe_action.setShortcut('W')
        wireframe_action.triggered.connect(self.viewer.toggle_wireframe)
        view_menu.addAction(wireframe_action)
        
        lighting_action = QAction('Toggle Lighting', self)
        lighting_action.setShortcut('L')
        lighting_action.triggered.connect(self.viewer.toggle_lighting)
        view_menu.addAction(lighting_action)
        
        rotate_action = QAction('Toggle Auto-Rotate', self)
        rotate_action.setShortcut('R')
        rotate_action.triggered.connect(self.viewer.toggle_auto_rotate)
        view_menu.addAction(rotate_action)
        
        # Tools menu
        tools_menu = menubar.addMenu('Tools')
        
        reference_action = QAction('Generate Reference Image', self)
        reference_action.triggered.connect(self.controls.generate_reference)
        tools_menu.addAction(reference_action)
        
        # Help menu
        help_menu = menubar.addMenu('Help')
        
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def show_about(self):
        """Show about dialog"""
        about_text = """
        <h2>Advanced Spaceship Designer v3.0</h2>
        <p>A sophisticated 3D spaceship modeling tool with real-time preview.</p>
        
        <h3>Features:</h3>
        <ul>
        <li>Real-time 3D preview with OpenGL</li>
        <li>Multiple primitive types (cylinder, cone, box, sphere, torus, wedge)</li>
        <li>Connected mesh generation</li>
        <li>Color customization</li>
        <li>Export to STL, GLB, OBJ, PLY formats</li>
        <li>Reference image generation</li>
        <li>Save/load configurations</li>
        </ul>
        
        <h3>Controls:</h3>
        <ul>
        <li>Left Mouse: Rotate view</li>
        <li>Right Mouse: Pan view</li>
        <li>Mouse Wheel: Zoom</li>
        <li>W: Toggle wireframe</li>
        <li>L: Toggle lighting</li>
        <li>R: Toggle auto-rotate</li>
        </ul>
        """
        
        QMessageBox.about(self, "About Spaceship Designer", about_text)

def main():
    """Main application entry point"""
    print("=" * 60)
    print("Advanced Spaceship Designer v3.0")
    print("=" * 60)
    print(f"Grid size: {GRID_SIZE}")
    print("Initializing application...")
    
    app = QApplication(sys.argv)
    app.setApplicationName("Spaceship Designer")
    app.setApplicationVersion("3.0")
    
    # Apply modern dark theme
    app.setStyle('Fusion')
    palette = QPalette()
    
    # Dark theme colors
    palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(0, 0, 0))
    palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
    palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
    
    app.setPalette(palette)
    
    # Create and show main window
    try:
        window = MainWindow()
        window.show()
        
        # Load existing configuration or use default
        try:
            window.generator.load_configuration()
            window.viewer.update_mesh()
        except:
            print("Using default spaceship configuration")
        
        # Generate initial reference image
        try:
            window.generator.generate_reference_image()
        except Exception as e:
            print(f"Could not generate initial reference: {e}")
        
        print("Application started successfully!")
        print("\nControls:")
        print("- Left Mouse + Drag: Rotate view")
        print("- Right Mouse + Drag: Pan view")  
        print("- Mouse Wheel: Zoom in/out")
        print("- W: Toggle wireframe mode")
        print("- L: Toggle lighting")
        print("- R: Toggle auto-rotation")
        print("- Use the control panel to edit modules")
        print("- Export your spaceship to various 3D formats")
        print("-" * 60)
        
        return app.exec()
        
    except Exception as e:
        print(f"Error starting application: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
