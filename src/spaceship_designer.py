#!/usr/bin/env python3
"""
Optimized Spaceship Designer
High-performance 3D spaceship modeling with GPU acceleration and simplified UI
"""

import sys
import os
import numpy as np
import trimesh
from typing import Dict, Tuple, Optional

# Import shared utilities
try:
    from .spaceship_utils import SpaceshipModule, MeshUtils, ConfigUtils, PerformanceUtils
except ImportError:
    # Fallback for standalone execution
    from spaceship_utils import SpaceshipModule, MeshUtils, ConfigUtils, PerformanceUtils

# Try to import Qt libraries with fallback
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
        print("Install with: pip install PyQt6 PyOpenGL")
        sys.exit(1)

try:
    from OpenGL.GL import *
    from OpenGL.GLU import *
    import OpenGL.GL as gl
except ImportError:
    print("Error: PyOpenGL not found!")
    print("Install with: pip install PyOpenGL")
    sys.exit(1)

# Configuration
DEFAULT_GRID_SIZE = (6, 3, 8)  # Smaller default for better performance
CONFIG_FILE = "spaceship_config.json"

class OptimizedSpaceshipGenerator:
    """Optimized spaceship generator with performance focus"""
    
    def __init__(self, grid_size: Tuple[int, int, int] = DEFAULT_GRID_SIZE):
        self.grid_size = grid_size
        self.grid = ConfigUtils.create_default_grid(grid_size)
        self.cached_mesh = None
        self.mesh_dirty = True
        
    def generate_mesh(self, use_cache: bool = True) -> trimesh.Trimesh:
        """Generate optimized spaceship mesh with caching"""
        if use_cache and not self.mesh_dirty and self.cached_mesh is not None:
            return self.cached_mesh
            
        print("Generating optimized spaceship mesh...")
        meshes = []
        
        # Generate module meshes
        for position, module in self.grid.items():
            if not module.enabled:
                continue
                
            try:
                # Create simple, low-poly primitive
                mesh = MeshUtils.create_simple_primitive(module.type, module.radius, module.height)
                
                # Apply transformations
                world_pos = self._grid_to_world_position(position)
                mesh = MeshUtils.apply_module_transform(mesh, module, world_pos)
                
                # Add vertex colors
                if hasattr(mesh.visual, 'vertex_colors'):
                    colors = np.full((len(mesh.vertices), 4), [*module.color, 255], dtype=np.uint8)
                    mesh.visual.vertex_colors = colors
                
                meshes.append(mesh)
                
            except Exception as e:
                print(f"Error creating module at {position}: {e}")
                continue
        
        # Generate connectors (simplified)
        connectors = self._generate_simple_connectors()
        meshes.extend(connectors)
        
        # Combine all meshes
        if meshes:
            try:
                combined = trimesh.util.concatenate(meshes)
                # Optimize for display
                combined = PerformanceUtils.optimize_mesh_for_display(combined, max_faces=15000)
                
                self.cached_mesh = combined
                self.mesh_dirty = False
                
                stats = PerformanceUtils.get_mesh_stats(combined)
                print(f"Generated mesh: {stats['vertices']} vertices, {stats['faces']} faces")
                
                return combined
            except Exception as e:
                print(f"Error combining meshes: {e}")
                return trimesh.Trimesh()  # Empty mesh
        
        return trimesh.Trimesh()  # Empty mesh
    
    def _grid_to_world_position(self, grid_pos: Tuple[int, int, int]) -> Tuple[float, float, float]:
        """Convert grid position to world coordinates with proper spacing"""
        x, y, z = grid_pos
        spacing = 1.5  # Reduced spacing for more compact ships
        return (x * spacing, y * spacing, z * spacing)
    
    def _generate_simple_connectors(self) -> list:
        """Generate simple connectors between adjacent modules"""
        connectors = []
        
        for position, module in self.grid.items():
            if not module.enabled:
                continue
                
            x, y, z = position
            world_pos = self._grid_to_world_position(position)
            
            # Check only immediate neighbors (not all directions for performance)
            neighbors = [
                (x + 1, y, z),  # Right
                (x, y, z + 1),  # Forward
            ]
            
            for neighbor_pos in neighbors:
                if (neighbor_pos in self.grid and 
                    self.grid[neighbor_pos].enabled):
                    
                    neighbor_world_pos = self._grid_to_world_position(neighbor_pos)
                    connector = MeshUtils.create_connector(world_pos, neighbor_world_pos, radius=0.15)
                    
                    if connector is not None:
                        # Add connector color
                        if hasattr(connector.visual, 'vertex_colors'):
                            colors = np.full((len(connector.vertices), 4), [80, 80, 80, 255], dtype=np.uint8)
                            connector.visual.vertex_colors = colors
                        connectors.append(connector)
        
        return connectors
    
    def update_module(self, position: Tuple[int, int, int], module: SpaceshipModule):
        """Update a module and mark mesh as dirty"""
        if position in self.grid:
            self.grid[position] = module
            self.mesh_dirty = True
    
    def save_configuration(self, filename: str = CONFIG_FILE) -> bool:
        """Save current configuration"""
        return ConfigUtils.save_grid_config(self.grid, filename)
    
    def load_configuration(self, filename: str = CONFIG_FILE) -> bool:
        """Load configuration from file"""
        try:
            self.grid = ConfigUtils.load_grid_config(filename, self.grid_size)
            self.mesh_dirty = True
            return True
        except Exception as e:
            print(f"Error loading configuration: {e}")
            return False

class HighPerformanceViewer(QOpenGLWidget):
    """High-performance OpenGL viewer with GPU acceleration"""
    
    def __init__(self):
        super().__init__()
        self.mesh = None
        self.rotation_x = -20
        self.rotation_y = 45  
        self.rotation_z = 0
        self.zoom = -15
        self.pan_x = 0
        self.pan_y = 0
        
        self.last_mouse_pos = None
        self.wireframe_mode = False
        self.lighting_enabled = True
        
        # Performance settings
        self.setUpdateBehavior(QOpenGLWidget.UpdateBehavior.NoPartialUpdate)
        
        # Auto-update timer (only when needed)
        self.timer = QTimer()
        self.timer.timeout.connect(self.conditional_update)
        self.auto_rotate = False  # Only update when rotating
        # Don't start timer automatically - only when needed
        
    def initializeGL(self):
        """Initialize OpenGL with performance optimizations"""
        gl.glClearColor(0.1, 0.1, 0.15, 1.0)
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glEnable(gl.GL_CULL_FACE)
        gl.glCullFace(gl.GL_BACK)
        
        # Enable GPU optimizations if available
        if PerformanceUtils.is_gpu_available():
            gl.glEnable(gl.GL_MULTISAMPLE)
            print("GPU acceleration enabled")
        
        # Lighting setup
        gl.glEnable(gl.GL_LIGHTING)
        gl.glEnable(gl.GL_LIGHT0)
        gl.glLightfv(gl.GL_LIGHT0, gl.GL_POSITION, [5.0, 5.0, 10.0, 1.0])
        gl.glLightfv(gl.GL_LIGHT0, gl.GL_AMBIENT, [0.2, 0.2, 0.3, 1.0])
        gl.glLightfv(gl.GL_LIGHT0, gl.GL_DIFFUSE, [0.8, 0.8, 0.9, 1.0])
        
    def resizeGL(self, width, height):
        """Handle window resize"""
        if height == 0:
            height = 1
        gl.glViewport(0, 0, width, height)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gluPerspective(45.0, width / height, 0.1, 100.0)
        
    def conditional_update(self):
        """Only update when actually needed"""
        if self.auto_rotate:
            self.rotation_y += 1.0  # Slow rotation
            self.update()
    
    def paintGL(self):
        """Render the scene with optimizations and error handling"""
        try:
            gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
            gl.glMatrixMode(gl.GL_MODELVIEW)
            gl.glLoadIdentity()
            
            # Apply transformations
            gl.glTranslatef(self.pan_x, self.pan_y, self.zoom)
            gl.glRotatef(self.rotation_x, 1, 0, 0)
            gl.glRotatef(self.rotation_y, 0, 1, 0)
            gl.glRotatef(self.rotation_z, 0, 0, 1)
            
            # Render mesh
            if self.mesh is not None:
                self._render_mesh_optimized()
                
        except Exception as e:
            print(f"OpenGL render error: {e}")
            # Don't crash - just skip this frame
    
    def _render_mesh_optimized(self):
        """Optimized mesh rendering with error handling"""
        try:
            if not hasattr(self.mesh, 'vertices') or len(self.mesh.vertices) == 0:
                return  # Skip rendering if no mesh data
                
            # Enable/disable lighting
            if self.lighting_enabled:
                gl.glEnable(gl.GL_LIGHTING)
                gl.glEnable(gl.GL_COLOR_MATERIAL)
                gl.glColorMaterial(gl.GL_FRONT_AND_BACK, gl.GL_AMBIENT_AND_DIFFUSE)
            else:
                gl.glDisable(gl.GL_LIGHTING)
            
            # Set wireframe or solid mode
            if self.wireframe_mode:
                gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_LINE)
                gl.glDisable(gl.GL_CULL_FACE)
            else:
                gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_FILL)
                gl.glEnable(gl.GL_CULL_FACE)
            
            # Render using vertex arrays for performance
            vertices = self.mesh.vertices.astype(np.float32)
            faces = self.mesh.faces.astype(np.uint32)
            
            gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
            gl.glVertexPointer(3, gl.GL_FLOAT, 0, vertices)
            
            # Add normals if available
            if hasattr(self.mesh.visual, 'face_normals') and len(self.mesh.visual.face_normals) > 0:
                normals = self.mesh.vertex_normals.astype(np.float32)
                gl.glEnableClientState(gl.GL_NORMAL_ARRAY)
                gl.glNormalPointer(gl.GL_FLOAT, 0, normals)
            
            # Add colors if available
            if hasattr(self.mesh.visual, 'vertex_colors') and len(self.mesh.visual.vertex_colors) > 0:
                colors = (self.mesh.visual.vertex_colors[:, :3] / 255.0).astype(np.float32)
                gl.glEnableClientState(gl.GL_COLOR_ARRAY)
                gl.glColorPointer(3, gl.GL_FLOAT, 0, colors)
            else:
                gl.glColor3f(0.7, 0.8, 0.9)  # Default color
            
            # Draw elements
            gl.glDrawElements(gl.GL_TRIANGLES, len(faces) * 3, gl.GL_UNSIGNED_INT, faces)
            
            # Cleanup
            gl.glDisableClientState(gl.GL_VERTEX_ARRAY)
            gl.glDisableClientState(gl.GL_NORMAL_ARRAY) 
            gl.glDisableClientState(gl.GL_COLOR_ARRAY)
            
        except Exception as e:
            print(f"Render error: {e}")
    
    def update_mesh(self, mesh):
        """Update the mesh for rendering"""
        self.mesh = mesh
        self.update()
        
    def mousePressEvent(self, event):
        """Handle mouse press for interaction"""
        self.last_mouse_pos = event.position() if hasattr(event, 'position') else event.pos()
        
    def mouseMoveEvent(self, event):
        """Handle mouse movement for camera control"""
        if self.last_mouse_pos is None:
            return
            
        current_pos = event.position() if hasattr(event, 'position') else event.pos()
        dx = current_pos.x() - self.last_mouse_pos.x()
        dy = current_pos.y() - self.last_mouse_pos.y()
        
        # Only update if there's significant movement
        if abs(dx) > 1 or abs(dy) > 1:
            if event.buttons() == Qt.MouseButton.LeftButton:
                # Rotation
                self.rotation_y += dx * 0.5
                self.rotation_x += dy * 0.5
                self.update()  # Only update when actually rotating
            elif event.buttons() == Qt.MouseButton.RightButton:
                # Panning
                self.pan_x += dx * 0.01
                self.pan_y -= dy * 0.01
                self.update()  # Only update when actually panning
        
        self.last_mouse_pos = current_pos
        
    def wheelEvent(self, event):
        """Handle mouse wheel for zoom"""
        delta = event.angleDelta().y() / 120.0
        old_zoom = self.zoom
        self.zoom += delta * 0.5
        self.zoom = max(-50, min(-2, self.zoom))  # Clamp zoom
        
        # Only update if zoom actually changed
        if abs(self.zoom - old_zoom) > 0.01:
            self.update()
        
    def keyPressEvent(self, event):
        """Handle keyboard shortcuts"""
        key = event.key()
        if key == Qt.Key.Key_W:
            self.wireframe_mode = not self.wireframe_mode
            print("Wireframe mode:", "ON" if self.wireframe_mode else "OFF")
        elif key == Qt.Key.Key_L:
            self.lighting_enabled = not self.lighting_enabled
            print("Lighting:", "ON" if self.lighting_enabled else "OFF")
        elif key == Qt.Key.Key_R:
            # Reset view
            self.rotation_x = -20
            self.rotation_y = 45
            self.rotation_z = 0
            self.zoom = -15
            self.pan_x = 0
            self.pan_y = 0
            print("View reset")
        elif key == Qt.Key.Key_A:
            # Toggle auto-rotation
            self.auto_rotate = not self.auto_rotate
            if self.auto_rotate:
                self.timer.start(50)  # Start animation timer
                print("Auto-rotation: ON")
            else:
                self.timer.stop()
                print("Auto-rotation: OFF")
                
        self.update()  # Single update after key press

class SimplifiedControlPanel(QWidget):
    """Simplified control panel with essential tools only"""
    
    def __init__(self, generator, viewer):
        super().__init__()
        self.generator = generator
        self.viewer = viewer
        self.current_position = (0, 0, 0)
        self.updating_ui = False  # Flag to prevent recursive updates
        self.init_ui()
        
    def init_ui(self):
        """Initialize simplified UI"""
        layout = QVBoxLayout(self)
        
        # Position selection
        pos_group = QGroupBox("Module Position")
        pos_layout = QFormLayout()
        
        self.pos_x = QSpinBox()
        self.pos_x.setRange(0, self.generator.grid_size[0] - 1)
        self.pos_y = QSpinBox()
        self.pos_y.setRange(0, self.generator.grid_size[1] - 1)
        self.pos_z = QSpinBox()  
        self.pos_z.setRange(0, self.generator.grid_size[2] - 1)
        
        pos_layout.addRow("X:", self.pos_x)
        pos_layout.addRow("Y:", self.pos_y)
        pos_layout.addRow("Z:", self.pos_z)
        pos_group.setLayout(pos_layout)
        
        # Module properties
        props_group = QGroupBox("Module Properties")
        props_layout = QFormLayout()
        
        self.type_combo = QComboBox()
        self.type_combo.addItems(["cylinder", "cone", "box", "sphere", "wedge"])
        
        self.enabled_check = QCheckBox()
        self.enabled_check.setChecked(True)
        
        self.radius_spin = QDoubleSpinBox()
        self.radius_spin.setRange(0.1, 2.0)
        self.radius_spin.setValue(0.5)
        self.radius_spin.setSingleStep(0.1)
        
        props_layout.addRow("Type:", self.type_combo)
        props_layout.addRow("Enabled:", self.enabled_check)
        props_layout.addRow("Size:", self.radius_spin)
        props_group.setLayout(props_layout)
        
        # Actions
        actions_group = QGroupBox("Actions")
        actions_layout = QVBoxLayout()
        
        self.update_btn = QPushButton("Update Module")
        self.generate_btn = QPushButton("🎲 Generate")
        self.random_btn = QPushButton("🔀 Random")
        self.clear_btn = QPushButton("🗑️ Clear")
        self.save_btn = QPushButton("💾 Save Design")
        self.load_btn = QPushButton("📁 Load Design") 
        self.export_btn = QPushButton("📤 Export STL")
        
        # Enhanced button styling
        button_style = """
            QPushButton {
                font-weight: bold;
                padding: 8px 16px;
                border: 2px solid #555;
                border-radius: 4px;
                background-color: #f0f0f0;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
                border-color: #333;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
        """
        
        for btn in [self.update_btn, self.generate_btn, self.random_btn, self.clear_btn, 
                    self.save_btn, self.load_btn, self.export_btn]:
            btn.setStyleSheet(button_style)
        
        actions_layout.addWidget(self.update_btn)
        actions_layout.addWidget(self.generate_btn)
        actions_layout.addWidget(self.random_btn)
        actions_layout.addWidget(self.clear_btn)
        actions_layout.addWidget(self.save_btn)
        actions_layout.addWidget(self.load_btn)
        actions_layout.addWidget(self.export_btn)
        
        # Navigation helper
        self.find_enabled_btn = QPushButton("Find Enabled Module")
        self.find_enabled_btn.setToolTip("Jump to next position with an enabled module")
        actions_layout.addWidget(self.find_enabled_btn)
        
        actions_group.setLayout(actions_layout)
        
        # Stats
        stats_group = QGroupBox("Statistics")
        stats_layout = QVBoxLayout()
        self.stats_label = QLabel("No mesh loaded")
        stats_layout.addWidget(self.stats_label)
        stats_group.setLayout(stats_layout)
        
        # Instructions
        instructions_group = QGroupBox("Controls")
        instructions_layout = QVBoxLayout()
        instructions_text = QLabel(
            "Mouse Controls:\n"
            "• Left drag: Rotate\n"
            "• Right drag: Pan\n"
            "• Wheel: Zoom\n\n"
            "Keyboard:\n"
            "• W: Wireframe\n"
            "• L: Lighting\n"
            "• R: Reset view"
        )
        instructions_text.setWordWrap(True)
        instructions_text.setStyleSheet("font-size: 11px; color: #888;")
        instructions_layout.addWidget(instructions_text)
        instructions_group.setLayout(instructions_layout)
        
        # Add to main layout
        layout.addWidget(pos_group)
        layout.addWidget(props_group) 
        layout.addWidget(actions_group)
        layout.addWidget(stats_group)
        layout.addWidget(instructions_group)
        layout.addStretch()
        
        # Connect signals (disconnect first to avoid multiple connections)
        self.pos_x.valueChanged.connect(self.position_changed)
        self.pos_y.valueChanged.connect(self.position_changed)
        self.pos_z.valueChanged.connect(self.position_changed)
        self.update_btn.clicked.connect(self.update_module)
        self.generate_btn.clicked.connect(self.generate_default_ship)
        self.random_btn.clicked.connect(self.generate_new_ship)
        self.clear_btn.clicked.connect(self.clear_ship)
        self.save_btn.clicked.connect(self.save_design)
        self.load_btn.clicked.connect(self.load_design)
        self.export_btn.clicked.connect(self.export_stl)
        self.find_enabled_btn.clicked.connect(self.find_enabled_module)
        
        # Load initial module
        self.position_changed()
        
    def position_changed(self):
        """Handle position change"""
        if self.updating_ui:
            return
            
        self.current_position = (self.pos_x.value(), self.pos_y.value(), self.pos_z.value())
        
        if self.current_position in self.generator.grid:
            module = self.generator.grid[self.current_position]
            
            # Provide visual feedback about module state
            status = "ENABLED" if module.enabled else "DISABLED"
            print(f"Position changed to: {self.current_position} - {status} {module.type}")
            
            # Update UI to reflect current module (prevent recursive calls)
            self.updating_ui = True
            self.type_combo.setCurrentText(module.type)
            self.enabled_check.setChecked(module.enabled)
            self.radius_spin.setValue(module.radius)
            
            # Visual feedback: Change spinbox style based on enabled state
            style = "background-color: #e8f5e8;" if module.enabled else "background-color: #f5f5f5;"
            self.radius_spin.setStyleSheet(style)
            
            self.updating_ui = False
            
    def update_module(self):
        """Update the current module"""
        print(f"Updating module at position {self.current_position}")
        
        if self.current_position in self.generator.grid:
            # Auto-enable module when user makes changes (better UX)
            is_enabled = self.enabled_check.isChecked()
            if not is_enabled:
                # If user is modifying a disabled module, auto-enable it for immediate feedback
                old_module = self.generator.grid[self.current_position]
                current_type = self.type_combo.currentText()
                current_radius = self.radius_spin.value()
                
                # Check if user changed anything from defaults
                if (current_type != old_module.type or 
                    abs(current_radius - old_module.radius) > 0.01):
                    is_enabled = True
                    self.enabled_check.setChecked(True)
                    print(f"Auto-enabled module due to user modifications")
            
            # Create new module with current UI values
            module = SpaceshipModule(
                type=self.type_combo.currentText(),
                enabled=is_enabled,
                radius=self.radius_spin.value(),
                height=self.radius_spin.value() * 1.2,  # Height proportional to radius
                color=[
                    120 + (hash(self.current_position) % 100), 
                    140 + (hash(self.current_position) % 100), 
                    160 + (hash(self.current_position) % 80)
                ]  # Position-based color variation
            )
            
            print(f"Created module: type={module.type}, enabled={module.enabled}, radius={module.radius}")
            
            self.generator.update_module(self.current_position, module)
            self.refresh_mesh()
        else:
            print(f"Position {self.current_position} not found in grid!")
            
    def find_enabled_module(self):
        """Find and jump to the next enabled module position"""
        enabled_positions = []
        
        # Find all enabled positions
        for position, module in self.generator.grid.items():
            if module.enabled:
                enabled_positions.append(position)
        
        if not enabled_positions:
            print("No enabled modules found!")
            return
        
        # Sort positions for consistent navigation
        enabled_positions.sort()
        
        # Find current position index or start from beginning
        try:
            current_index = enabled_positions.index(self.current_position)
            next_index = (current_index + 1) % len(enabled_positions)
        except ValueError:
            next_index = 0
        
        # Jump to next enabled position
        next_position = enabled_positions[next_index]
        
        # Update UI
        self.updating_ui = True
        self.pos_x.setValue(next_position[0])
        self.pos_y.setValue(next_position[1])  
        self.pos_z.setValue(next_position[2])
        self.updating_ui = False
        
        # Trigger position change
        self.position_changed()
        
        print(f"Jumped to enabled module at {next_position} ({next_index + 1}/{len(enabled_positions)})")

    def generate_default_ship(self):
        """Generate a new default spaceship configuration"""
        print("Generating new default spaceship...")
        self.generator.grid = ConfigUtils.create_default_grid(self.generator.grid_size)
        self.generator.mesh_dirty = True
        self.refresh_mesh()
        self.position_changed()  # Refresh UI
        print("Default spaceship generated!")
        
    def clear_ship(self):
        """Clear all modules from the spaceship"""
        print("Clearing spaceship...")
        # Set all modules to disabled
        for pos in self.generator.grid:
            self.generator.grid[pos].enabled = False
        self.generator.mesh_dirty = True
        self.refresh_mesh()
        self.position_changed()  # Refresh UI
        print("Spaceship cleared!")

    def generate_new_ship(self):
        """Generate a new random spaceship"""
        print("Generating new random spaceship...")
        self.generator.grid = ConfigUtils.create_random_grid(self.generator.grid_size)
        self.generator.mesh_dirty = True
        self.refresh_mesh()
        self.position_changed()  # Refresh UI
        print("New spaceship generated!")
        
    def refresh_mesh(self):
        """Refresh the 3D mesh display"""
        try:
            mesh = self.generator.generate_mesh()
            self.viewer.update_mesh(mesh)
            
            # Update stats
            stats = PerformanceUtils.get_mesh_stats(mesh)
            self.stats_label.setText(
                f"Vertices: {stats['vertices']}\n"
                f"Faces: {stats['faces']}\n"
                f"Watertight: {'Yes' if stats['watertight'] else 'No'}"
            )
        except Exception as e:
            print(f"Error refreshing mesh: {e}")
            self.stats_label.setText("Error generating mesh")
            
    def save_design(self):
        """Save the current design"""
        if self.generator.save_configuration():
            QMessageBox.information(self, "Success", "Design saved successfully!")
        else:
            QMessageBox.warning(self, "Error", "Failed to save design")
            
    def load_design(self):
        """Load a design"""
        if self.generator.load_configuration():
            self.refresh_mesh()
            self.position_changed()  # Refresh UI
            QMessageBox.information(self, "Success", "Design loaded successfully!")
        else:
            QMessageBox.warning(self, "Error", "Failed to load design")
            
    def export_stl(self):
        """Export current design as STL"""
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self, "Export STL", "spaceship.stl", "STL Files (*.stl)")
            
            if filename:
                mesh = self.generator.generate_mesh()
                mesh.export(filename)
                QMessageBox.information(self, "Success", f"Exported to {filename}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Export failed: {e}")

class OptimizedSpaceshipApp(QMainWindow):
    """Main application window with optimizations"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Spaceship Designer - Optimized")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create generator and viewer
        self.generator = OptimizedSpaceshipGenerator()
        self.viewer = HighPerformanceViewer()
        self.control_panel = SimplifiedControlPanel(self.generator, self.viewer)
        
        self.setup_ui()
        self.setup_menu()
        
        # Initial mesh generation
        QTimer.singleShot(500, self.initial_mesh_generation)  # Longer delay to avoid startup issues
        
    def setup_ui(self):
        """Set up the main UI layout"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QHBoxLayout(central_widget)
        
        # 3D viewer takes most space
        layout.addWidget(self.viewer, 3)
        
        # Control panel
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.control_panel)
        scroll_area.setWidgetResizable(True)
        scroll_area.setMaximumWidth(300)
        layout.addWidget(scroll_area, 1)
        
    def setup_menu(self):
        """Set up the menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        new_action = QAction('New Ship', self)
        new_action.triggered.connect(self.control_panel.generate_new_ship)
        file_menu.addAction(new_action)
        
        save_action = QAction('Save', self)
        save_action.triggered.connect(self.control_panel.save_design)
        file_menu.addAction(save_action)
        
        load_action = QAction('Load', self)
        load_action.triggered.connect(self.control_panel.load_design)
        file_menu.addAction(load_action)
        
        file_menu.addSeparator()
        
        export_menu = file_menu.addMenu('Export')
        
        export_stl = QAction('STL', self)
        export_stl.triggered.connect(self.control_panel.export_stl)
        export_menu.addAction(export_stl)
        
        # View menu
        view_menu = menubar.addMenu('View')
        
        wireframe_action = QAction('Toggle Wireframe (W)', self)
        wireframe_action.triggered.connect(self.toggle_wireframe)
        view_menu.addAction(wireframe_action)
        
        lighting_action = QAction('Toggle Lighting (L)', self)
        lighting_action.triggered.connect(self.toggle_lighting)
        view_menu.addAction(lighting_action)
        
        reset_view_action = QAction('Reset View (R)', self)
        reset_view_action.triggered.connect(self.reset_view)
        view_menu.addAction(reset_view_action)
        
    def initial_mesh_generation(self):
        """Generate initial mesh after UI is ready"""
        self.control_panel.refresh_mesh()
    
    def toggle_wireframe(self):
        """Toggle wireframe mode"""
        self.viewer.wireframe_mode = not self.viewer.wireframe_mode
        self.viewer.update()
        
    def toggle_lighting(self):
        """Toggle lighting"""
        self.viewer.lighting_enabled = not self.viewer.lighting_enabled
        self.viewer.update()
        
    def reset_view(self):
        """Reset view to default"""
        self.viewer.rotation_x = -20
        self.viewer.rotation_y = 45
        self.viewer.rotation_z = 0
        self.viewer.zoom = -15
        self.viewer.pan_x = 0
        self.viewer.pan_y = 0
        self.viewer.update()

def apply_dark_theme(app):
    """Apply a dark theme for better visibility"""
    palette = QPalette()
    
    # Window colors
    palette.setColor(QPalette.ColorRole.Window, QColor(45, 45, 48))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
    
    # Base colors
    palette.setColor(QPalette.ColorRole.Base, QColor(35, 35, 38))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(55, 55, 58))
    
    # Text colors
    palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
    
    # Button colors
    palette.setColor(QPalette.ColorRole.Button, QColor(60, 60, 63))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
    
    # Highlight colors
    palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
    
    app.setPalette(palette)

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    
    # Apply dark theme
    apply_dark_theme(app)
    
    # Create and show main window
    window = OptimizedSpaceshipApp()
    window.show()
    
    print("=" * 60)
    print("Optimized Spaceship Designer Started")
    print("=" * 60)
    print("Controls:")
    print("- Left Mouse + Drag: Rotate view")
    print("- Right Mouse + Drag: Pan view") 
    print("- Mouse Wheel: Zoom")
    print("- W: Toggle wireframe")
    print("- L: Toggle lighting")
    print("- R: Reset view")
    print("=" * 60)
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())