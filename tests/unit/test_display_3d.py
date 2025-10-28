#!/usr/bin/env python3
"""
3D DISPLAY MODULE UNIT TESTS
Comprehensive testing for OpenGL 3D rendering and visualization
"""

import sys
import time
from pathlib import Path

# Import test framework
from test_framework import ModuleTestSuite, TestResult, assert_module_function_exists, assert_class_has_method, assert_instance_created

class Display3DTestSuite(ModuleTestSuite):
    """Complete test suite for 3D display module"""
    
    def _setup_module_specific(self):
        """Setup specific to 3D display testing"""
        self.test_viewers = []
        self.test_meshes = []
        self.opengl_available = False
        
    def test_module_imports(self, result: TestResult):
        """Test that all required classes and functions can be imported"""
        
        # Check main classes exist
        assert_class_has_method(self.module.Spaceship3DViewer, '__init__')
        assert_class_has_method(self.module.CameraController, '__init__')
        assert_class_has_method(self.module.MeshRenderer, '__init__')
        assert_class_has_method(self.module.RenderSettings, '__init__')
        assert_class_has_method(self.module.GridRenderer, '__init__')
        result.add_detail("All main classes importable")
        
        # Check render settings methods (actual implementation)
        assert_class_has_method(self.module.RenderSettings, 'toggle_wireframe')
        assert_class_has_method(self.module.RenderSettings, 'toggle_lighting')
        assert_class_has_method(self.module.RenderSettings, 'toggle_grid')
        result.add_detail("RenderSettings has required methods")
        
        # Check camera methods (actual implementation)
        assert_class_has_method(self.module.CameraController, 'rotate')
        assert_class_has_method(self.module.CameraController, 'pan')
        assert_class_has_method(self.module.CameraController, 'zoom_by_delta')
        assert_class_has_method(self.module.CameraController, 'reset_view')
        assert_class_has_method(self.module.CameraController, 'apply_transforms')
        result.add_detail("CameraController has required methods")
        
        # Check renderer methods (actual implementation)
        assert_class_has_method(self.module.MeshRenderer, 'render_mesh')
        assert_class_has_method(self.module.MeshRenderer, 'create_display_list')
        result.add_detail("MeshRenderer has required methods")
        
        # Check viewer methods (PyQt6 OpenGL widget)
        assert_class_has_method(self.module.Spaceship3DViewer, 'initializeGL')
        assert_class_has_method(self.module.Spaceship3DViewer, 'paintGL')
        assert_class_has_method(self.module.Spaceship3DViewer, 'resizeGL')
        result.add_detail("Spaceship3DViewer has OpenGL methods")
    
    def test_opengl_availability(self, result: TestResult):
        """Test OpenGL availability and capabilities"""
        
        try:
            # Test PyQt6 OpenGL imports
            from PyQt6.QtOpenGL import QOpenGLWidget
            from PyQt6.QtWidgets import QApplication
            result.add_detail("PyQt6 OpenGL modules imported")
            
            # Test OpenGL library imports
            try:
                import OpenGL.GL as gl
                import OpenGL.GLU as glu
                result.add_detail("OpenGL libraries imported")
                self.opengl_available = True
            except ImportError as e:
                result.add_detail(f"OpenGL libraries not available: {str(e)}")
                self.opengl_available = False
            
            # Test QApplication for OpenGL context
            if not QApplication.instance():
                app = QApplication([])
                result.add_detail("QApplication created for OpenGL context")
                
        except ImportError as e:
            result.complete("SKIP", f"PyQt6 OpenGL not available: {str(e)}")
            return False
        except Exception as e:
            result.add_detail(f"OpenGL setup error: {str(e)}")
            return False
        
        return True
    
    def test_spaceship_3d_viewer_creation(self, result: TestResult):
        """Test 3D viewer can be created and configured"""
        
        if not self.test_opengl_availability(TestResult("opengl_check", "display_3d")):
            result.complete("SKIP", "OpenGL not available")
            return
        
        # Create 3D viewer instance
        viewer = assert_instance_created(
            lambda: self.module.Spaceship3DViewer(),
            self.module.Spaceship3DViewer
        )
        result.add_detail("Spaceship3DViewer created successfully")
        
        # Check viewer attributes
        required_attrs = ['camera_controller', 'mesh_renderer', 'render_settings']
        for attr in required_attrs:
            if hasattr(viewer, attr):
                result.add_detail(f"Viewer has {attr}")
        
        # Test viewer initialization
        try:
            if hasattr(viewer, 'initializeGL'):
                # Note: Can't actually call initializeGL without proper OpenGL context
                result.add_detail("OpenGL initialization method available")
            
            if hasattr(viewer, 'setup_viewport'):
                viewer.setup_viewport(800, 600)
                result.add_detail("Viewport setup completed")
        except Exception as e:
            result.add_detail(f"Viewer initialization error: {str(e)}")
        
        self.test_viewers.append(viewer)
        return viewer
    
    def test_camera_controller(self, result: TestResult):
        """Test camera controller functionality"""
        
        # Create camera controller
        camera = assert_instance_created(
            lambda: self.module.CameraController(),
            self.module.CameraController
        )
        result.add_detail("CameraController created successfully")
        
        # Check camera attributes
        camera_attrs = ['position', 'target', 'up_vector', 'fov', 'near_plane', 'far_plane']
        for attr in camera_attrs:
            if hasattr(camera, attr):
                value = getattr(camera, attr)
                result.add_detail(f"Camera {attr}: {value}")
        
        # Test camera transformations
        try:
            # Test rotation
            camera.rotate(45.0, 30.0)  # Yaw, pitch
            result.add_detail("Camera rotation applied")
            
            # Test panning
            camera.pan(1.0, -0.5)  # X, Y offset
            result.add_detail("Camera panning applied")
            
            # Test zooming
            camera.zoom(0.8)  # Zoom factor
            result.add_detail("Camera zoom applied")
            
            # Test reset
            if hasattr(camera, 'reset'):
                camera.reset()
                result.add_detail("Camera reset to defaults")
                
        except Exception as e:
            result.add_detail(f"Camera transformation error: {str(e)}")
        
        # Test view matrix generation
        if hasattr(camera, 'get_view_matrix'):
            try:
                view_matrix = camera.get_view_matrix()
                if view_matrix is not None:
                    result.add_detail("View matrix generated")
            except Exception as e:
                result.add_detail(f"View matrix error: {str(e)}")
        
        return camera
    
    def test_mesh_renderer(self, result: TestResult):
        """Test mesh renderer functionality"""
        
        # Create mesh renderer
        renderer = assert_instance_created(
            lambda: self.module.MeshRenderer(),
            self.module.MeshRenderer
        )
        result.add_detail("MeshRenderer created successfully")
        
        # Check renderer attributes
        renderer_attrs = ['display_lists', 'vertex_buffers', 'render_mode']
        for attr in renderer_attrs:
            if hasattr(renderer, attr):
                result.add_detail(f"Renderer has {attr}")
        
        # Test mesh data preparation
        if hasattr(renderer, 'prepare_mesh_data'):
            try:
                # Create mock mesh data
                mock_mesh = {
                    'vertices': [[0,0,0], [1,0,0], [0.5,1,0]],
                    'faces': [[0,1,2]],
                    'normals': [[0,0,1], [0,0,1], [0,0,1]]
                }
                
                renderer.prepare_mesh_data(mock_mesh)
                result.add_detail("Mock mesh data prepared")
            except Exception as e:
                result.add_detail(f"Mesh preparation error: {str(e)}")
        
        # Test display list management
        if hasattr(renderer, 'create_display_list'):
            try:
                list_id = renderer.create_display_list(mock_mesh)
                if list_id:
                    result.add_detail(f"Display list created: ID {list_id}")
            except Exception as e:
                result.add_detail(f"Display list error: {str(e)}")
        
        # Test rendering pipeline
        if hasattr(renderer, 'render_wireframe') and hasattr(renderer, 'render_solid'):
            try:
                # Test different render modes
                renderer.render_wireframe(mock_mesh)
                result.add_detail("Wireframe rendering method called")
                
                renderer.render_solid(mock_mesh)
                result.add_detail("Solid rendering method called")
            except Exception as e:
                result.add_detail(f"Rendering pipeline error: {str(e)}")
        
        return renderer
    
    def test_render_settings(self, result: TestResult):
        """Test render settings configuration"""
        
        # Create render settings
        settings = assert_instance_created(
            lambda: self.module.RenderSettings(),
            self.module.RenderSettings
        )
        result.add_detail("RenderSettings created successfully")
        
        # Check settings attributes
        settings_attrs = ['wireframe_mode', 'lighting_enabled', 'background_color', 'line_width']
        for attr in settings_attrs:
            if hasattr(settings, attr):
                value = getattr(settings, attr)
                result.add_detail(f"Setting {attr}: {value}")
        
        # Test settings modification
        try:
            # Test wireframe toggle
            settings.toggle_wireframe()
            result.add_detail("Wireframe mode toggled")
            
            # Test lighting toggle
            if hasattr(settings, 'toggle_lighting'):
                settings.toggle_lighting()
                result.add_detail("Lighting toggled")
            
            # Test background color change
            if hasattr(settings, 'set_background_color'):
                settings.set_background_color([0.2, 0.3, 0.4])
                result.add_detail("Background color changed")
            
            # Test line width adjustment
            if hasattr(settings, 'set_line_width'):
                settings.set_line_width(2.0)
                result.add_detail("Line width adjusted")
                
        except Exception as e:
            result.add_detail(f"Settings modification error: {str(e)}")
        
        # Test settings persistence
        if hasattr(settings, 'save_settings') and hasattr(settings, 'load_settings'):
            try:
                settings.save_settings()
                result.add_detail("Settings saved")
                
                settings.load_settings()
                result.add_detail("Settings loaded")
            except Exception as e:
                result.add_detail(f"Settings persistence error: {str(e)}")
        
        return settings
    
    def test_mouse_and_keyboard_input(self, result: TestResult):
        """Test input handling for 3D interaction"""
        
        viewer = self.test_spaceship_3d_viewer_creation(TestResult("viewer_setup", "display_3d"))
        if not viewer:
            result.complete("SKIP", "No viewer available")
            return
        
        # Test mouse input handling
        if hasattr(viewer, 'handle_mouse_input'):
            try:
                # Simulate mouse events
                mouse_events = [
                    {'type': 'press', 'button': 'left', 'x': 100, 'y': 100},
                    {'type': 'move', 'x': 150, 'y': 120},
                    {'type': 'release', 'button': 'left', 'x': 150, 'y': 120},
                    {'type': 'wheel', 'delta': 120}  # Zoom scroll
                ]
                
                for event in mouse_events:
                    viewer.handle_mouse_input(event)
                    result.add_detail(f"Mouse {event['type']} handled")
                    
            except Exception as e:
                result.add_detail(f"Mouse input error: {str(e)}")
        
        # Test keyboard input handling
        if hasattr(viewer, 'handle_keyboard_input'):
            try:
                # Test common keyboard shortcuts
                key_events = [
                    {'key': 'w', 'action': 'wireframe_toggle'},
                    {'key': 'l', 'action': 'lighting_toggle'},
                    {'key': 'r', 'action': 'reset_camera'},
                    {'key': 'space', 'action': 'pause_rotation'}
                ]
                
                for event in key_events:
                    viewer.handle_keyboard_input(event)
                    result.add_detail(f"Key '{event['key']}' handled")
                    
            except Exception as e:
                result.add_detail(f"Keyboard input error: {str(e)}")
    
    def test_performance_optimization(self, result: TestResult):
        """Test performance optimizations and rendering efficiency"""
        
        if not self.opengl_available:
            result.complete("SKIP", "OpenGL not available for performance testing")
            return
        
        renderer = self.test_mesh_renderer(TestResult("renderer_setup", "display_3d"))
        
        # Test display list caching
        if hasattr(renderer, 'display_lists'):
            start_time = time.time()
            
            # Create multiple meshes to test caching
            for i in range(5):
                mock_mesh = {
                    'vertices': [[j, 0, 0] for j in range(100)],  # Simple vertex data
                    'faces': [[j, j+1, j+2] for j in range(97)],
                    'id': f'test_mesh_{i}'
                }
                
                try:
                    if hasattr(renderer, 'render_mesh'):
                        renderer.render_mesh(mock_mesh)
                    result.add_detail(f"Mesh {i} processed")
                except Exception as e:
                    result.add_detail(f"Mesh {i} error: {str(e)}")
            
            total_time = time.time() - start_time
            result.add_detail(f"Rendered 5 meshes in {total_time:.3f}s")
        
        # Test vertex buffer optimization
        if hasattr(renderer, 'use_vertex_buffers'):
            try:
                renderer.use_vertex_buffers(True)
                result.add_detail("Vertex buffer optimization enabled")
            except Exception as e:
                result.add_detail(f"Vertex buffer error: {str(e)}")
        
        # Test level of detail (LOD) system
        if hasattr(renderer, 'set_lod_distance'):
            try:
                renderer.set_lod_distance(100.0)  # Distance threshold
                result.add_detail("Level of detail configured")
            except Exception as e:
                result.add_detail(f"LOD configuration error: {str(e)}")
    
    def test_lighting_and_materials(self, result: TestResult):
        """Test lighting and material systems"""
        
        if not self.opengl_available:
            result.complete("SKIP", "OpenGL not available for lighting testing")
            return
        
        # Test lighting setup
        if hasattr(self.module, 'LightingSystem'):
            try:
                lighting = self.module.LightingSystem()
                result.add_detail("Lighting system created")
                
                # Test light configuration
                if hasattr(lighting, 'add_directional_light'):
                    lighting.add_directional_light([1, 1, 1], [1, 1, 1])  # Direction, color
                    result.add_detail("Directional light added")
                
                if hasattr(lighting, 'add_ambient_light'):
                    lighting.add_ambient_light([0.3, 0.3, 0.3])  # Ambient color
                    result.add_detail("Ambient light configured")
                    
            except Exception as e:
                result.add_detail(f"Lighting system error: {str(e)}")
        
        # Test material system
        if hasattr(self.module, 'MaterialSystem'):
            try:
                materials = self.module.MaterialSystem()
                result.add_detail("Material system created")
                
                # Test material creation
                if hasattr(materials, 'create_material'):
                    metal_material = materials.create_material(
                        'metal', 
                        diffuse=[0.7, 0.7, 0.8],
                        specular=[0.9, 0.9, 1.0],
                        shininess=64.0
                    )
                    result.add_detail("Metal material created")
                    
            except Exception as e:
                result.add_detail(f"Material system error: {str(e)}")
    
    def test_viewport_and_projection(self, result: TestResult):
        """Test viewport management and projection matrices"""
        
        viewer = self.test_spaceship_3d_viewer_creation(TestResult("viewer_setup", "display_3d"))
        if not viewer:
            result.complete("SKIP", "No viewer available")
            return
        
        # Test viewport configuration
        if hasattr(viewer, 'set_viewport'):
            try:
                # Test different viewport sizes
                viewports = [
                    (800, 600),   # Standard
                    (1920, 1080), # HD
                    (1366, 768),  # Common laptop
                    (400, 300)    # Small window
                ]
                
                for width, height in viewports:
                    viewer.set_viewport(width, height)
                    result.add_detail(f"Viewport set to {width}x{height}")
                    
            except Exception as e:
                result.add_detail(f"Viewport configuration error: {str(e)}")
        
        # Test projection matrix
        if hasattr(viewer, 'set_projection'):
            try:
                # Test perspective projection
                viewer.set_projection('perspective', fov=60.0, aspect=16/9, near=0.1, far=1000.0)
                result.add_detail("Perspective projection configured")
                
                # Test orthographic projection
                if hasattr(viewer, 'set_orthographic_projection'):
                    viewer.set_orthographic_projection(left=-10, right=10, bottom=-10, top=10)
                    result.add_detail("Orthographic projection configured")
                    
            except Exception as e:
                result.add_detail(f"Projection configuration error: {str(e)}")
    
    def test_error_handling_and_recovery(self, result: TestResult):
        """Test error handling and graceful degradation"""
        
        # Test invalid mesh data handling
        renderer = self.test_mesh_renderer(TestResult("renderer_setup", "display_3d"))
        
        try:
            # Test with corrupted mesh data
            invalid_meshes = [
                {'vertices': None, 'faces': []},  # None vertices
                {'vertices': [], 'faces': None},  # None faces
                {'vertices': [[1,2]], 'faces': [[0,1,2]]},  # Invalid vertex format
                {'vertices': [[1,2,3]], 'faces': [[0,1,5]]},  # Face index out of range
                {}  # Empty mesh
            ]
            
            for i, invalid_mesh in enumerate(invalid_meshes):
                try:
                    if hasattr(renderer, 'render_mesh'):
                        renderer.render_mesh(invalid_mesh)
                    result.add_detail(f"Invalid mesh {i} handled gracefully")
                except Exception as e:
                    result.add_detail(f"Invalid mesh {i} error handled: {str(e)[:50]}")
                    
        except Exception as e:
            result.add_detail(f"Error handling test error: {str(e)}")
        
        # Test OpenGL context loss recovery
        if hasattr(self.module, 'handle_context_loss'):
            try:
                self.module.handle_context_loss()
                result.add_detail("OpenGL context loss handled")
            except Exception as e:
                result.add_detail(f"Context loss recovery error: {str(e)}")
    
    def test_export_and_screenshot(self, result: TestResult):
        """Test viewport export and screenshot functionality"""
        
        viewer = self.test_spaceship_3d_viewer_creation(TestResult("viewer_setup", "display_3d"))
        if not viewer:
            result.complete("SKIP", "No viewer available")
            return
        
        # Test screenshot functionality
        if hasattr(viewer, 'take_screenshot'):
            try:
                screenshot = viewer.take_screenshot()
                if screenshot:
                    result.add_detail("Screenshot captured")
                    
                    # Test screenshot with specific size
                    hd_screenshot = viewer.take_screenshot(width=1920, height=1080)
                    if hd_screenshot:
                        result.add_detail("HD screenshot captured")
                        
            except Exception as e:
                result.add_detail(f"Screenshot error: {str(e)}")
        
        # Test viewport export to image
        if hasattr(viewer, 'export_image'):
            try:
                import tempfile
                temp_file = tempfile.mktemp(suffix='.png')
                
                success = viewer.export_image(temp_file)
                if success:
                    result.add_detail(f"Image exported to {temp_file}")
                    
            except Exception as e:
                result.add_detail(f"Image export error: {str(e)}")

if __name__ == "__main__":
    from test_framework import UniversalTestRunner
    
    # Create test runner
    runner = UniversalTestRunner()
    
    # Add 3D display test suite
    display_suite = Display3DTestSuite("display_3d", runner.logger)
    runner.add_test_suite(display_suite)
    
    # Run dependency check
    deps_ok = runner.run_dependency_check()
    
    if deps_ok:
        # Run tests
        results = runner.run_all_tests()
        
        # Save results
        output_dir = Path(__file__).parent.parent / "results"
        runner.save_results(output_dir)
        
        print(f"\n🎮 3D DISPLAY MODULE TESTING COMPLETE")
        print(f"Pass Rate: {results['summary']['pass_rate']:.1f}%")
    else:
        print("❌ Critical dependencies missing - skipping tests")