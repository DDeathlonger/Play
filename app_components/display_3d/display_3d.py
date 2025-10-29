#!/usr/bin/env python3
"""
3D DISPLAY MODULE - ISOLATED MODULE
OpenGL 3D rendering and visualization system
"""

import sys
from typing import Dict, List, Any, Optional, Tuple
import time

# OpenGL imports with error handling
try:
    from OpenGL.GL import *
    from OpenGL.GLU import *
    import numpy as np
    HAS_OPENGL = True
except ImportError as e:
    print(f"OpenGL not available: {e}")
    HAS_OPENGL = False

# PyQt6 OpenGL imports with error handling
try:
    from PyQt6.QtOpenGL import QOpenGLWidget
    from PyQt6.QtOpenGLWidgets import QOpenGLWidget
    from PyQt6.QtCore import *
    from PyQt6.QtGui import *
    HAS_PYQT6_OPENGL = True
except ImportError as e:
    print(f"PyQt6 OpenGL not available: {e}")
    HAS_PYQT6_OPENGL = False
    # Fallback base class
    class QOpenGLWidget:
        def __init__(self):
            pass

class RenderSettings:
    """3D rendering configuration settings"""
    
    def __init__(self):
        self.wireframe_mode = False
        self.lighting_enabled = True
        self.show_grid = True
        self.show_axes = True
        self.background_color = (0.1, 0.1, 0.2, 1.0)
        self.grid_color = (0.3, 0.3, 0.3, 0.5)
        self.axes_length = 5.0
        self.enable_culling = True
        self.enable_depth_test = True
        self.smooth_shading = True
    
    def toggle_wireframe(self):
        """Toggle wireframe rendering mode"""
        self.wireframe_mode = not self.wireframe_mode
        return self.wireframe_mode
    
    def toggle_lighting(self):
        """Toggle lighting"""
        self.lighting_enabled = not self.lighting_enabled
        return self.lighting_enabled
    
    def toggle_grid(self):
        """Toggle grid display"""
        self.show_grid = not self.show_grid
        return self.show_grid

class CameraController:
    """3D camera control system"""
    
    def __init__(self):
        self.rotation_x = 0.0
        self.rotation_y = 0.0
        self.zoom = -10.0
        self.pan_x = 0.0
        self.pan_y = 0.0
        
        # Constraints
        self.min_zoom = -50.0
        self.max_zoom = -2.0
        self.max_rotation_x = 90.0
        
        # Mouse interaction state
        self.last_mouse_pos = None
        self.is_rotating = False
        self.is_panning = False
    
    def reset_view(self):
        """Reset camera to default position"""
        self.rotation_x = 0.0
        self.rotation_y = 0.0
        self.zoom = -10.0
        self.pan_x = 0.0
        self.pan_y = 0.0
    
    def rotate(self, delta_x: float, delta_y: float, sensitivity: float = 0.5):
        """Apply rotation based on mouse movement"""
        self.rotation_y += delta_x * sensitivity
        self.rotation_x += delta_y * sensitivity
        
        # Constrain rotation
        self.rotation_x = max(-self.max_rotation_x, min(self.max_rotation_x, self.rotation_x))
    
    def zoom_by_delta(self, delta: float, sensitivity: float = 0.01):
        """Apply zoom based on wheel delta"""
        self.zoom += delta * sensitivity
        self.zoom = max(self.min_zoom, min(self.max_zoom, self.zoom))
    
    def pan(self, delta_x: float, delta_y: float, sensitivity: float = 0.01):
        """Apply panning based on mouse movement"""
        self.pan_x += delta_x * sensitivity
        self.pan_y -= delta_y * sensitivity  # Invert Y for natural feel
    
    def apply_transforms(self):
        """Apply camera transforms to OpenGL matrix"""
        if not HAS_OPENGL:
            return
        
        glTranslatef(self.pan_x, self.pan_y, self.zoom)
        glRotatef(self.rotation_x, 1.0, 0.0, 0.0)
        glRotatef(self.rotation_y, 0.0, 1.0, 0.0)
    
    def get_state(self) -> Dict[str, float]:
        """Get current camera state"""
        return {
            'rotation_x': self.rotation_x,
            'rotation_y': self.rotation_y,
            'zoom': self.zoom,
            'pan_x': self.pan_x,
            'pan_y': self.pan_y
        }
    
    def set_state(self, state: Dict[str, float]):
        """Set camera state"""
        self.rotation_x = state.get('rotation_x', 0.0)
        self.rotation_y = state.get('rotation_y', 0.0)
        self.zoom = state.get('zoom', -10.0)
        self.pan_x = state.get('pan_x', 0.0)
        self.pan_y = state.get('pan_y', 0.0)

class MeshRenderer:
    """Optimized mesh rendering system"""
    
    def __init__(self):
        self.display_lists = {}
        self.mesh_dirty_flags = {}
        self.render_stats = {
            'triangles_rendered': 0,
            'vertices_processed': 0,
            'display_list_cache_hits': 0,
            'display_list_rebuilds': 0
        }
    
    def _create_display_list(self, mesh_id: str, mesh_data: Dict[str, Any]) -> Optional[int]:
        """Create optimized display list for mesh"""
        if not HAS_OPENGL:
            return None
        
        try:
            mesh = mesh_data.get('mesh')
            if not mesh or not hasattr(mesh, 'vertices') or not hasattr(mesh, 'faces'):
                return None
            
            # Delete existing display list
            if mesh_id in self.display_lists:
                glDeleteLists(self.display_lists[mesh_id], 1)
            
            # Create new display list
            display_list = glGenLists(1)
            glNewList(display_list, GL_COMPILE)
            
            vertices = mesh.vertices
            faces = mesh.faces
            
            # Get face normals for lighting
            face_normals = None
            if hasattr(mesh, 'face_normals'):
                face_normals = mesh.face_normals
            
            # Get vertex normals for smooth shading
            vertex_normals = None
            if hasattr(mesh, 'vertex_normals'):
                vertex_normals = mesh.vertex_normals
            
            glBegin(GL_TRIANGLES)
            
            for i, face in enumerate(faces):
                # Set face normal if available
                if face_normals is not None and i < len(face_normals):
                    glNormal3fv(face_normals[i])
                
                # Set color based on mesh material or default
                if hasattr(mesh.visual, 'face_colors') and len(mesh.visual.face_colors) > i:
                    color = mesh.visual.face_colors[i] / 255.0
                    glColor3f(color[0], color[1], color[2])
                else:
                    glColor3f(0.7, 0.7, 0.8)
                
                # Render triangle vertices
                for vertex_idx in face:
                    if vertex_normals is not None and vertex_idx < len(vertex_normals):
                        glNormal3fv(vertex_normals[vertex_idx])
                    glVertex3fv(vertices[vertex_idx])
            
            glEnd()
            glEndList()
            
            self.display_lists[mesh_id] = display_list
            self.mesh_dirty_flags[mesh_id] = False
            self.render_stats['display_list_rebuilds'] += 1
            
            return display_list
            
        except Exception as e:
            print(f"Display list creation error: {e}")
            return None
    
    def render_mesh(self, mesh_id: str, mesh_data: Dict[str, Any]) -> bool:
        """Render mesh using display list optimization"""
        if not HAS_OPENGL:
            return False
        
        try:
            # Check if display list needs update
            needs_update = (
                mesh_id not in self.display_lists or
                self.mesh_dirty_flags.get(mesh_id, True)
            )
            
            if needs_update:
                self._create_display_list(mesh_id, mesh_data)
            else:
                self.render_stats['display_list_cache_hits'] += 1
            
            # Render using display list
            if mesh_id in self.display_lists:
                glCallList(self.display_lists[mesh_id])
                
                # Update stats
                mesh = mesh_data.get('mesh')
                if mesh and hasattr(mesh, 'faces'):
                    self.render_stats['triangles_rendered'] += len(mesh.faces)
                    if hasattr(mesh, 'vertices'):
                        self.render_stats['vertices_processed'] += len(mesh.vertices)
                
                return True
            
            return False
            
        except Exception as e:
            print(f"Mesh render error: {e}")
            return False
    
    def mark_mesh_dirty(self, mesh_id: str):
        """Mark mesh as needing display list update"""
        self.mesh_dirty_flags[mesh_id] = True
    
    def clear_mesh(self, mesh_id: str):
        """Clear mesh from renderer"""
        if mesh_id in self.display_lists:
            if HAS_OPENGL:
                glDeleteLists(self.display_lists[mesh_id], 1)
            del self.display_lists[mesh_id]
        
        if mesh_id in self.mesh_dirty_flags:
            del self.mesh_dirty_flags[mesh_id]
    
    def clear_all_meshes(self):
        """Clear all meshes and display lists"""
        if HAS_OPENGL:
            for display_list in self.display_lists.values():
                glDeleteLists(display_list, 1)
        
        self.display_lists.clear()
        self.mesh_dirty_flags.clear()
    
    def get_render_stats(self) -> Dict[str, int]:
        """Get rendering statistics"""
        return self.render_stats.copy()

class GridRenderer:
    """Grid and axes rendering system"""
    
    def __init__(self):
        self.grid_display_list = None
        self.axes_display_list = None
    
    def _create_grid_display_list(self, size: int = 10, spacing: float = 1.0):
        """Create display list for grid"""
        if not HAS_OPENGL:
            return
        
        if self.grid_display_list is not None:
            glDeleteLists(self.grid_display_list, 1)
        
        self.grid_display_list = glGenLists(1)
        glNewList(self.grid_display_list, GL_COMPILE)
        
        glColor3f(0.3, 0.3, 0.3)
        glBegin(GL_LINES)
        
        # Grid lines
        for i in range(-size, size + 1):
            x = i * spacing
            # Lines parallel to X axis
            glVertex3f(-size * spacing, 0, x)
            glVertex3f(size * spacing, 0, x)
            # Lines parallel to Z axis
            glVertex3f(x, 0, -size * spacing)
            glVertex3f(x, 0, size * spacing)
        
        glEnd()
        glEndList()
    
    def _create_axes_display_list(self, length: float = 5.0):
        """Create display list for coordinate axes"""
        if not HAS_OPENGL:
            return
        
        if self.axes_display_list is not None:
            glDeleteLists(self.axes_display_list, 1)
        
        self.axes_display_list = glGenLists(1)
        glNewList(self.axes_display_list, GL_COMPILE)
        
        glBegin(GL_LINES)
        
        # X axis - Red
        glColor3f(1.0, 0.0, 0.0)
        glVertex3f(0, 0, 0)
        glVertex3f(length, 0, 0)
        
        # Y axis - Green
        glColor3f(0.0, 1.0, 0.0)
        glVertex3f(0, 0, 0)
        glVertex3f(0, length, 0)
        
        # Z axis - Blue
        glColor3f(0.0, 0.0, 1.0)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 0, length)
        
        glEnd()
        glEndList()
    
    def render_grid(self, size: int = 10, spacing: float = 1.0):
        """Render grid"""
        if not HAS_OPENGL:
            return
        
        if self.grid_display_list is None:
            self._create_grid_display_list(size, spacing)
        
        if self.grid_display_list is not None:
            glCallList(self.grid_display_list)
    
    def render_axes(self, length: float = 5.0):
        """Render coordinate axes"""
        if not HAS_OPENGL:
            return
        
        if self.axes_display_list is None:
            self._create_axes_display_list(length)
        
        if self.axes_display_list is not None:
            glCallList(self.axes_display_list)
    
    def cleanup(self):
        """Clean up display lists"""
        if HAS_OPENGL:
            if self.grid_display_list is not None:
                glDeleteLists(self.grid_display_list, 1)
            if self.axes_display_list is not None:
                glDeleteLists(self.axes_display_list, 1)

class Spaceship3DViewer(QOpenGLWidget):
    """High-performance 3D spaceship viewer widget"""
    
    def __init__(self):
        super().__init__()
        
        # Core components
        self.camera = CameraController()
        self.render_settings = RenderSettings()
        self.mesh_renderer = MeshRenderer()
        self.grid_renderer = GridRenderer()
        
        # Mesh data
        self.current_mesh_data = None
        
        # Performance tracking
        self.frame_count = 0
        self.fps_timer = time.time()
        self.current_fps = 0.0
        
        # Widget settings
        self.setMinimumSize(600, 400)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)  # Enable keyboard events
    
    def initializeGL(self):
        """Initialize OpenGL settings"""
        if not HAS_OPENGL:
            return
        
        # Enable depth testing
        if self.render_settings.enable_depth_test:
            glEnable(GL_DEPTH_TEST)
        
        # Enable face culling for performance
        if self.render_settings.enable_culling:
            glEnable(GL_CULL_FACE)
            glCullFace(GL_BACK)
        
        # Lighting setup
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        
        # Shading model
        if self.render_settings.smooth_shading:
            glShadeModel(GL_SMOOTH)
        else:
            glShadeModel(GL_FLAT)
        
        # Set background color
        bg = self.render_settings.background_color
        glClearColor(bg[0], bg[1], bg[2], bg[3])
        
        # Setup lighting
        glLightfv(GL_LIGHT0, GL_POSITION, [1.0, 1.0, 1.0, 0.0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 1.0, 1.0])
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
    
    def resizeGL(self, width, height):
        """Handle window resize"""
        if not HAS_OPENGL:
            return
        
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        
        # Set perspective
        aspect_ratio = width / max(height, 1)
        gluPerspective(45.0, aspect_ratio, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)
    
    def paintGL(self):
        """Main rendering function"""
        if not HAS_OPENGL:
            return
        
        # Clear buffers
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        # Apply camera transformations
        self.camera.apply_transforms()
        
        # Configure rendering mode
        if self.render_settings.wireframe_mode:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        
        # Toggle lighting
        if self.render_settings.lighting_enabled:
            glEnable(GL_LIGHTING)
        else:
            glDisable(GL_LIGHTING)
        
        # Render grid
        if self.render_settings.show_grid:
            glDisable(GL_LIGHTING)  # Grid should not be lit
            self.grid_renderer.render_grid()
            if self.render_settings.lighting_enabled:
                glEnable(GL_LIGHTING)
        
        # Render axes
        if self.render_settings.show_axes:
            glDisable(GL_LIGHTING)  # Axes should not be lit
            self.grid_renderer.render_axes(self.render_settings.axes_length)
            if self.render_settings.lighting_enabled:
                glEnable(GL_LIGHTING)
        
        # Render main mesh
        if self.current_mesh_data is not None:
            self.mesh_renderer.render_mesh("main_ship", self.current_mesh_data)
        
        # Update FPS counter
        self._update_fps_counter()
    
    def _update_fps_counter(self):
        """Update FPS counter"""
        self.frame_count += 1
        current_time = time.time()
        
        if current_time - self.fps_timer >= 1.0:  # Update every second
            self.current_fps = self.frame_count / (current_time - self.fps_timer)
            self.frame_count = 0
            self.fps_timer = current_time
    
    def update_mesh(self, mesh_data: Dict[str, Any]):
        """Update the displayed mesh"""
        self.current_mesh_data = mesh_data
        self.mesh_renderer.mark_mesh_dirty("main_ship")
        self.update()
    
    def clear_mesh(self):
        """Clear the current mesh"""
        self.current_mesh_data = None
        self.mesh_renderer.clear_mesh("main_ship")
        self.update()
    
    def toggle_wireframe(self) -> bool:
        """Toggle wireframe mode"""
        self.render_settings.toggle_wireframe()
        self.update()
        return self.render_settings.wireframe_mode
    
    def toggle_lighting(self) -> bool:
        """Toggle lighting"""
        self.render_settings.toggle_lighting()
        self.update()
        return self.render_settings.lighting_enabled
    
    def toggle_grid(self) -> bool:
        """Toggle grid display"""
        self.render_settings.toggle_grid()
        self.update()
        return self.render_settings.show_grid
    
    def reset_view(self):
        """Reset camera view"""
        self.camera.reset_view()
        self.update()
    
    def get_camera_state(self) -> Dict[str, float]:
        """Get current camera state"""
        return self.camera.get_state()
    
    def set_camera_state(self, state: Dict[str, float]):
        """Set camera state"""
        self.camera.set_state(state)
        self.update()
    
    def get_render_stats(self) -> Dict[str, Any]:
        """Get rendering statistics"""
        stats = self.mesh_renderer.get_render_stats()
        stats['fps'] = self.current_fps
        return stats
    
    # Mouse and keyboard event handlers
    def mousePressEvent(self, event):
        """Handle mouse press events"""
        if not HAS_PYQT6_OPENGL:
            return
        
        self.camera.last_mouse_pos = event.position().toPoint()
        
        if event.button() == Qt.MouseButton.LeftButton:
            self.camera.is_rotating = True
        elif event.button() == Qt.MouseButton.MiddleButton:
            self.camera.is_panning = True
    
    def mouseMoveEvent(self, event):
        """Handle mouse move events"""
        if not HAS_PYQT6_OPENGL or not self.camera.last_mouse_pos:
            return
        
        current_pos = event.position().toPoint()
        dx = current_pos.x() - self.camera.last_mouse_pos.x()
        dy = current_pos.y() - self.camera.last_mouse_pos.y()
        
        if self.camera.is_rotating:
            self.camera.rotate(dx, dy)
            self.update()
        elif self.camera.is_panning:
            self.camera.pan(dx, dy)
            self.update()
        
        self.camera.last_mouse_pos = current_pos
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release events"""
        if not HAS_PYQT6_OPENGL:
            return
        
        self.camera.is_rotating = False
        self.camera.is_panning = False
    
    def wheelEvent(self, event):
        """Handle mouse wheel events for zooming"""
        if not HAS_PYQT6_OPENGL:
            return
        
        delta = event.angleDelta().y()
        self.camera.zoom_by_delta(delta)
        self.update()
    
    def keyPressEvent(self, event):
        """Handle keyboard events"""
        if not HAS_PYQT6_OPENGL:
            return
        
        key = event.key()
        
        if key == Qt.Key.Key_W:
            self.toggle_wireframe()
        elif key == Qt.Key.Key_L:
            self.toggle_lighting()
        elif key == Qt.Key.Key_G:
            self.toggle_grid()
        elif key == Qt.Key.Key_R:
            self.reset_view()
        elif key == Qt.Key.Key_Escape:
            self.reset_view()
    
    def cleanup(self):
        """Clean up OpenGL resources"""
        self.mesh_renderer.clear_all_meshes()
        self.grid_renderer.cleanup()

# Factory functions for easy instantiation
def create_3d_viewer() -> Spaceship3DViewer:
    """Create 3D viewer instance"""
    return Spaceship3DViewer()

def create_camera_controller() -> CameraController:
    """Create camera controller instance"""
    return CameraController()

def create_render_settings() -> RenderSettings:
    """Create render settings instance"""
    return RenderSettings()

if __name__ == "__main__":
    # Demo usage
    print("🎮 3D DISPLAY MODULE - ISOLATED MODULE TEST")
    print("=" * 50)
    
    if HAS_OPENGL and HAS_PYQT6_OPENGL:
        print("✅ OpenGL available")
        print("✅ PyQt6 OpenGL available")
        
        # Test component creation
        camera = create_camera_controller()
        settings = create_render_settings()
        
        print("✅ Camera controller created")
        print("✅ Render settings created")
        
        # Test camera operations
        camera.rotate(45, 30)
        camera.zoom_by_delta(100)
        state = camera.get_state()
        
        print(f"✅ Camera state: rotation_y={state['rotation_y']:.1f}, zoom={state['zoom']:.1f}")
        
        # Test settings
        wireframe = settings.toggle_wireframe()
        lighting = settings.toggle_lighting()
        
        print(f"✅ Render settings: wireframe={wireframe}, lighting={lighting}")
        
        print("✅ 3D display system ready")
    else:
        missing = []
        if not HAS_OPENGL:
            missing.append("OpenGL")
        if not HAS_PYQT6_OPENGL:
            missing.append("PyQt6 OpenGL")
        
        print(f"❌ Missing dependencies: {', '.join(missing)}")
        print("Install with: pip install PyOpenGL PyOpenGL_accelerate PyQt6")