#!/usr/bin/env python3
"""
REFACTORED SPACESHIP DESIGNER - OPTIMIZED PERFORMANCE
Integrated with optimized ship generation engine and enhanced MCP server
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

import json
import time
import traceback
from typing import Dict, List, Any, Optional
import threading
import subprocess
import socket
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
import uuid
from datetime import datetime

# PyQt6 imports
try:
    from PyQt6.QtWidgets import *
    from PyQt6.QtCore import *
    from PyQt6.QtGui import *
    from PyQt6.QtOpenGL import QOpenGLWidget
    from PyQt6.QtOpenGLWidgets import QOpenGLWidget
except ImportError as e:
    print(f"PyQt6 import error: {e}")
    print("Please install PyQt6: pip install PyQt6 PyQt6-tools")
    sys.exit(1)

# OpenGL imports
try:
    from OpenGL.GL import *
    from OpenGL.GLU import *
    import numpy as np
except ImportError as e:
    print(f"OpenGL import error: {e}")
    print("Please install PyOpenGL: pip install PyOpenGL PyOpenGL_accelerate")
    sys.exit(1)

# Import optimized ship engine
try:
    from optimized_ship_engine import OptimizedSpaceshipEngine, ShipArchitecture
except ImportError as e:
    print(f"Ship engine import error: {e}")
    traceback.print_exc()
    sys.exit(1)

class MCPCommandHandler(BaseHTTPRequestHandler):
    """Enhanced HTTP handler for MCP commands with performance tracking"""
    
    def __init__(self, app_instance, *args, **kwargs):
        self.app_instance = app_instance
        super().__init__(*args, **kwargs)
    
    def do_POST(self):
        """Handle POST requests with command tracking"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            command_data = json.loads(post_data.decode('utf-8'))
            
            # Track command
            self.app_instance.track_mcp_command(command_data)
            
            # Process command
            response = self.app_instance.process_mcp_command(command_data)
            
            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            self.send_error(500, f"Command processing error: {str(e)}")
    
    def log_message(self, format, *args):
        """Suppress default logging"""
        pass

class IntegratedMCPManager:
    """Enhanced MCP server manager with session persistence and performance optimization"""
    
    def __init__(self, app_instance):
        self.app_instance = app_instance
        self.server = None
        self.server_thread = None
        self.port = 8765
        self.is_running = False
        self.session_id = str(uuid.uuid4())
        self.command_history = []
        self.max_history = 100
        self.performance_metrics = {
            'commands_processed': 0,
            'session_start_time': time.time(),
            'average_response_time': 0.0,
            'total_response_time': 0.0
        }
    
    def _find_available_port(self, start_port=8765, max_attempts=10):
        """Find available port with optimization"""
        for i in range(max_attempts):
            port = start_port + i
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('localhost', port))
                    return port
            except OSError:
                continue
        raise Exception("No available ports found")
    
    def _check_existing_mcp_server(self):
        """Check for existing MCP servers with enhanced detection"""
        existing_servers = []
        for port in range(8765, 8775):
            try:
                response = requests.get(f'http://localhost:{port}/status', timeout=1)
                if response.status_code == 200:
                    existing_servers.append(port)
            except:
                continue
        return existing_servers
    
    def start_server(self):
        """Start MCP server with session persistence"""
        if self.is_running:
            self.app_instance.log_message("MCP server already running", "info")
            return True
        
        try:
            # Check for existing servers
            existing = self._check_existing_mcp_server()
            if existing:
                self.port = existing[0]
                self.app_instance.log_message(f"Reusing existing MCP server on port {self.port}", "info")
                self.is_running = True
                return True
            
            # Find available port
            self.port = self._find_available_port()
            
            # Create server with app instance binding
            def handler_factory(*args, **kwargs):
                return MCPCommandHandler(self.app_instance, *args, **kwargs)
            
            self.server = HTTPServer(('localhost', self.port), handler_factory)
            
            # Start server thread
            self.server_thread = threading.Thread(target=self._run_server, daemon=True)
            self.server_thread.start()
            
            self.is_running = True
            self.app_instance.log_message(f"MCP server started on port {self.port}", "success")
            self.app_instance.update_operations_display(f"🚀 MCP Session {self.session_id[:8]} active on port {self.port}")
            
            return True
            
        except Exception as e:
            self.app_instance.log_message(f"Failed to start MCP server: {str(e)}", "error")
            return False
    
    def _run_server(self):
        """Run server with error handling"""
        try:
            self.server.serve_forever()
        except Exception as e:
            self.app_instance.log_message(f"MCP server error: {str(e)}", "error")
    
    def stop_server(self):
        """Stop MCP server with graceful cleanup"""
        if not self.is_running:
            return
        
        try:
            if self.server:
                self.server.shutdown()
                self.server.server_close()
            
            if self.server_thread and self.server_thread.is_alive():
                self.server_thread.join(timeout=2)
            
            self.is_running = False
            self.app_instance.log_message("MCP server stopped", "info")
            self.app_instance.update_operations_display("🔴 MCP Session ended")
            
        except Exception as e:
            self.app_instance.log_message(f"Error stopping MCP server: {str(e)}", "error")
    
    def add_command_to_history(self, command_data: Dict[str, Any]):
        """Add command to history with performance tracking"""
        start_time = time.time()
        
        self.command_history.append({
            'timestamp': datetime.now().isoformat(),
            'session_id': self.session_id,
            'command': command_data,
            'processing_time': 0.0
        })
        
        # Maintain history size
        if len(self.command_history) > self.max_history:
            self.command_history.pop(0)
        
        # Update metrics
        processing_time = time.time() - start_time
        self.performance_metrics['commands_processed'] += 1
        self.performance_metrics['total_response_time'] += processing_time
        self.performance_metrics['average_response_time'] = (
            self.performance_metrics['total_response_time'] / 
            self.performance_metrics['commands_processed']
        )
        
        return processing_time
    
    def get_session_info(self) -> Dict[str, Any]:
        """Get comprehensive session information"""
        uptime = time.time() - self.performance_metrics['session_start_time']
        return {
            'session_id': self.session_id,
            'port': self.port,
            'is_running': self.is_running,
            'uptime_seconds': uptime,
            'commands_processed': self.performance_metrics['commands_processed'],
            'average_response_time': self.performance_metrics['average_response_time'],
            'command_rate': self.performance_metrics['commands_processed'] / max(1, uptime / 60),  # commands per minute
            'recent_commands': self.command_history[-5:] if self.command_history else []
        }

class OptimizedSpaceshipViewer(QOpenGLWidget):
    """High-performance OpenGL viewer with optimization features"""
    
    def __init__(self):
        super().__init__()
        self.mesh_data = None
        self.rotation_x = 0
        self.rotation_y = 0
        self.zoom = -10
        self.wireframe_mode = False
        self.lighting_enabled = True
        self.last_pos = QPoint()
        
        # Performance optimization
        self.display_list = None
        self.mesh_dirty = True
        self.frame_rate = 60
        self.setMinimumSize(600, 400)
    
    def initializeGL(self):
        """Initialize OpenGL with performance settings"""
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        
        # Optimize for performance
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        glShadeModel(GL_SMOOTH)
        
        # Set background color
        glClearColor(0.1, 0.1, 0.2, 1.0)
        
        # Setup lighting
        glLightfv(GL_LIGHT0, GL_POSITION, [1.0, 1.0, 1.0, 0.0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 1.0, 1.0])
    
    def resizeGL(self, width, height):
        """Resize viewport"""
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, width / height, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)
    
    def paintGL(self):
        """Optimized rendering with display lists"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        # Apply transformations
        glTranslatef(0.0, 0.0, self.zoom)
        glRotatef(self.rotation_x, 1.0, 0.0, 0.0)
        glRotatef(self.rotation_y, 0.0, 1.0, 0.0)
        
        # Toggle wireframe
        if self.wireframe_mode:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        
        # Toggle lighting
        if self.lighting_enabled:
            glEnable(GL_LIGHTING)
        else:
            glDisable(GL_LIGHTING)
        
        # Render mesh using display list for performance
        if self.mesh_data is not None:
            if self.display_list is None or self.mesh_dirty:
                self._create_display_list()
            
            if self.display_list is not None:
                glCallList(self.display_list)
    
    def _create_display_list(self):
        """Create optimized display list"""
        if self.display_list is not None:
            glDeleteLists(self.display_list, 1)
        
        self.display_list = glGenLists(1)
        glNewList(self.display_list, GL_COMPILE)
        
        try:
            vertices = self.mesh_data['mesh'].vertices
            faces = self.mesh_data['mesh'].faces
            
            # Get face normals for lighting
            if hasattr(self.mesh_data['mesh'], 'face_normals'):
                face_normals = self.mesh_data['mesh'].face_normals
            else:
                face_normals = None
            
            glBegin(GL_TRIANGLES)
            for i, face in enumerate(faces):
                if face_normals is not None:
                    glNormal3fv(face_normals[i])
                
                # Set color based on mesh material or default
                if hasattr(self.mesh_data['mesh'].visual, 'face_colors') and len(self.mesh_data['mesh'].visual.face_colors) > i:
                    color = self.mesh_data['mesh'].visual.face_colors[i] / 255.0
                    glColor3f(color[0], color[1], color[2])
                else:
                    glColor3f(0.7, 0.7, 0.8)
                
                for vertex_idx in face:
                    glVertex3fv(vertices[vertex_idx])
            glEnd()
        except Exception as e:
            print(f"Display list creation error: {e}")
            # Fallback rendering
            glColor3f(1.0, 0.0, 0.0)
            glBegin(GL_TRIANGLES)
            glVertex3f(-1, -1, 0)
            glVertex3f(1, -1, 0)
            glVertex3f(0, 1, 0)
            glEnd()
        
        glEndList()
        self.mesh_dirty = False
    
    def update_mesh(self, mesh_data):
        """Update mesh with performance optimization"""
        self.mesh_data = mesh_data
        self.mesh_dirty = True
        self.update()
    
    def mousePressEvent(self, event):
        """Handle mouse press for rotation"""
        self.last_pos = event.position().toPoint()
    
    def mouseMoveEvent(self, event):
        """Handle mouse movement for rotation"""
        dx = event.position().x() - self.last_pos.x()
        dy = event.position().y() - self.last_pos.y()
        
        if event.buttons() & Qt.MouseButton.LeftButton:
            self.rotation_x += dy * 0.5
            self.rotation_y += dx * 0.5
            self.update()
        
        self.last_pos = event.position().toPoint()
    
    def wheelEvent(self, event):
        """Handle zoom with mouse wheel"""
        delta = event.angleDelta().y()
        self.zoom += delta * 0.01
        self.zoom = max(-50, min(-2, self.zoom))
        self.update()
    
    def keyPressEvent(self, event):
        """Handle keyboard shortcuts"""
        if event.key() == Qt.Key.Key_W:
            self.wireframe_mode = not self.wireframe_mode
            self.update()
        elif event.key() == Qt.Key.Key_L:
            self.lighting_enabled = not self.lighting_enabled
            self.update()
        elif event.key() == Qt.Key.Key_R:
            self.rotation_x = 0
            self.rotation_y = 0
            self.zoom = -10
            self.update()

class RefactoredSpaceshipDesigner(QMainWindow):
    """Main application with integrated optimized ship engine and enhanced MCP"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize optimized ship engine
        self.ship_engine = OptimizedSpaceshipEngine()
        
        # Initialize MCP manager
        self.mcp_manager = IntegratedMCPManager(self)
        
        # UI components
        self.viewer = None
        self.operations_display = None
        self.error_log_display = None
        self.chat_display = None
        self.status_bar = None
        
        # Application state
        self.current_ship_data = None
        self.recent_commands = []
        self.max_recent_commands = 3
        
        self.setup_ui()
        self.setup_connections()
        self.start_mcp_server()
        
        # Initial ship generation
        self.generate_new_ship()
    
    def setup_ui(self):
        """Setup enhanced UI with performance monitoring"""
        self.setWindowTitle("Refactored Spaceship Designer - Optimized Performance")
        self.setGeometry(100, 100, 1400, 900)
        
        # Create central widget with splitter
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left panel - Controls
        left_panel = self.create_control_panel()
        splitter.addWidget(left_panel)
        
        # Right panel - 3D Viewer
        self.viewer = OptimizedSpaceshipViewer()
        splitter.addWidget(self.viewer)
        
        # Set splitter proportions
        splitter.setStretchFactor(0, 0)  # Fixed width for controls
        splitter.setStretchFactor(1, 1)  # Expandable viewer
        splitter.setSizes([400, 1000])
        
        # Status bar with performance info
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.update_status_bar()
    
    def create_control_panel(self):
        """Create enhanced control panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Ship Generation Section
        gen_group = QGroupBox("🚀 Ship Generation")
        gen_layout = QVBoxLayout(gen_group)
        
        # Ship class selection
        class_layout = QHBoxLayout()
        class_layout.addWidget(QLabel("Ship Class:"))
        self.ship_class_combo = QComboBox()
        self.ship_class_combo.addItems(["fighter", "cruiser", "capital"])
        self.ship_class_combo.setCurrentText("cruiser")
        class_layout.addWidget(self.ship_class_combo)
        gen_layout.addLayout(class_layout)
        
        # Generation button
        self.generate_btn = QPushButton("Generate New Ship")
        self.generate_btn.setStyleSheet("QPushButton { font-weight: bold; padding: 8px; }")
        gen_layout.addWidget(self.generate_btn)
        
        layout.addWidget(gen_group)
        
        # Controls Section
        controls_group = QGroupBox("🎮 View Controls")
        controls_layout = QVBoxLayout(controls_group)
        
        # Wireframe toggle
        self.wireframe_btn = QPushButton("Toggle Wireframe (W)")
        controls_layout.addWidget(self.wireframe_btn)
        
        # Lighting toggle
        self.lighting_btn = QPushButton("Toggle Lighting (L)")
        controls_layout.addWidget(self.lighting_btn)
        
        # Reset view
        self.reset_btn = QPushButton("Reset View (R)")
        controls_layout.addWidget(self.reset_btn)
        
        layout.addWidget(controls_group)
        
        # Operations Display Section
        ops_group = QGroupBox("📡 MCP Operations")
        ops_layout = QVBoxLayout(ops_group)
        
        self.operations_display = QTextEdit()
        self.operations_display.setMaximumHeight(100)
        self.operations_display.setReadOnly(True)
        self.operations_display.setStyleSheet("background-color: #2b2b2b; color: #00ff00; font-family: monospace;")
        ops_layout.addWidget(self.operations_display)
        
        layout.addWidget(ops_group)
        
        # Performance Metrics Section
        perf_group = QGroupBox("⚡ Performance Metrics")
        perf_layout = QVBoxLayout(perf_group)
        
        self.performance_display = QTextEdit()
        self.performance_display.setMaximumHeight(120)
        self.performance_display.setReadOnly(True)
        perf_layout.addWidget(self.performance_display)
        
        layout.addWidget(perf_group)
        
        # Export Section
        export_group = QGroupBox("💾 Export")
        export_layout = QVBoxLayout(export_group)
        
        # Format selection
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Format:"))
        self.export_format_combo = QComboBox()
        self.export_format_combo.addItems(["STL", "OBJ", "GLB", "PLY"])
        format_layout.addWidget(self.export_format_combo)
        export_layout.addLayout(format_layout)
        
        # Export button
        self.export_btn = QPushButton("Export Ship")
        export_layout.addWidget(self.export_btn)
        
        layout.addWidget(export_group)
        
        # Error Log Section
        error_group = QGroupBox("⚠️ System Log")
        error_layout = QVBoxLayout(error_group)
        
        self.error_log_display = QTextEdit()
        self.error_log_display.setMaximumHeight(80)
        self.error_log_display.setReadOnly(True)
        error_layout.addWidget(self.error_log_display)
        
        layout.addWidget(error_group)
        
        layout.addStretch()
        return panel
    
    def setup_connections(self):
        """Setup signal-slot connections"""
        self.generate_btn.clicked.connect(self.generate_new_ship)
        self.wireframe_btn.clicked.connect(self.toggle_wireframe)
        self.lighting_btn.clicked.connect(self.toggle_lighting) 
        self.reset_btn.clicked.connect(self.reset_view)
        self.export_btn.clicked.connect(self.export_ship)
        
        # Performance update timer
        self.performance_timer = QTimer()
        self.performance_timer.timeout.connect(self.update_performance_display)
        self.performance_timer.start(2000)  # Update every 2 seconds
    
    def generate_new_ship(self):
        """Generate new ship using optimized engine"""
        try:
            self.log_message("Generating new ship...", "info")
            
            ship_class = self.ship_class_combo.currentText()
            self.current_ship_data = self.ship_engine.generate_random_ship(ship_class)
            
            # Update viewer
            self.viewer.update_mesh(self.current_ship_data)
            
            # Log success
            vertices = self.current_ship_data['vertices']
            faces = self.current_ship_data['faces']
            gen_time = self.current_ship_data['generation_time']
            
            self.log_message(
                f"✅ {ship_class.title()} generated: {vertices} vertices, {faces} faces in {gen_time:.3f}s",
                "success"
            )
            
            self.update_operations_display(f"🎯 Generated {ship_class} ship ({vertices}v, {faces}f)")
            self.update_status_bar()
            
        except Exception as e:
            self.log_message(f"❌ Ship generation failed: {str(e)}", "error")
            traceback.print_exc()
    
    def toggle_wireframe(self):
        """Toggle wireframe mode"""
        self.viewer.wireframe_mode = not self.viewer.wireframe_mode
        self.viewer.update()
        self.update_operations_display(f"🔲 Wireframe: {'ON' if self.viewer.wireframe_mode else 'OFF'}")
    
    def toggle_lighting(self):
        """Toggle lighting"""
        self.viewer.lighting_enabled = not self.viewer.lighting_enabled
        self.viewer.update()
        self.update_operations_display(f"💡 Lighting: {'ON' if self.viewer.lighting_enabled else 'OFF'}")
    
    def reset_view(self):
        """Reset view parameters"""
        self.viewer.rotation_x = 0
        self.viewer.rotation_y = 0
        self.viewer.zoom = -10
        self.viewer.update()
        self.update_operations_display("🔄 View reset to default")
    
    def export_ship(self):
        """Export current ship"""
        if not self.current_ship_data:
            self.log_message("❌ No ship to export", "error")
            return
        
        try:
            # Get export parameters
            format_str = self.export_format_combo.currentText().lower()
            
            # Create exports directory
            exports_dir = Path("exports")
            exports_dir.mkdir(exist_ok=True)
            
            # Generate filename
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            ship_class = self.ship_class_combo.currentText()
            filename = f"spaceship_{ship_class}_{timestamp}"
            filepath = exports_dir / filename
            
            # Export using ship engine
            success = self.ship_engine.export_ship(self.current_ship_data, filepath, format_str)
            
            if success:
                self.log_message(f"✅ Ship exported: {filepath.with_suffix('.' + format_str)}", "success")
                self.update_operations_display(f"💾 Exported as {format_str.upper()}")
            else:
                self.log_message("❌ Export failed", "error")
                
        except Exception as e:
            self.log_message(f"❌ Export error: {str(e)}", "error")
    
    def start_mcp_server(self):
        """Start MCP server with session management"""
        success = self.mcp_manager.start_server()
        if success:
            self.log_message("🚀 MCP server started with session persistence", "success")
        else:
            self.log_message("❌ Failed to start MCP server", "error")
    
    def track_mcp_command(self, command_data: Dict[str, Any]):
        """Track MCP command for display"""
        processing_time = self.mcp_manager.add_command_to_history(command_data)
        
        # Update recent commands for display
        command_summary = command_data.get('action', 'Unknown')
        self.recent_commands.append(f"🤖 {command_summary}")
        
        if len(self.recent_commands) > self.max_recent_commands:
            self.recent_commands.pop(0)
        
        # Update operations display
        commands_text = "\\n".join(self.recent_commands)
        self.update_operations_display(commands_text)
    
    def process_mcp_command(self, command_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process MCP command and return response"""
        try:
            action = command_data.get('action', '')
            
            if action == 'generate_ship':
                ship_class = command_data.get('ship_class', 'cruiser')
                self.ship_class_combo.setCurrentText(ship_class)
                self.generate_new_ship()
                return {'status': 'success', 'message': f'Generated {ship_class} ship'}
            
            elif action == 'toggle_wireframe':
                self.toggle_wireframe()
                return {'status': 'success', 'message': 'Wireframe toggled'}
            
            elif action == 'export_ship':
                format_str = command_data.get('format', 'stl')
                self.export_format_combo.setCurrentText(format_str.upper())
                self.export_ship()
                return {'status': 'success', 'message': f'Ship exported as {format_str}'}
            
            elif action == 'get_ship_info':
                if self.current_ship_data:
                    return {
                        'status': 'success',
                        'ship_info': {
                            'vertices': self.current_ship_data['vertices'],
                            'faces': self.current_ship_data['faces'],
                            'generation_time': self.current_ship_data['generation_time']
                        }
                    }
                else:
                    return {'status': 'error', 'message': 'No ship loaded'}
            
            elif action == 'get_performance':
                return {
                    'status': 'success',
                    'performance': self.ship_engine.get_performance_report(),
                    'session_info': self.mcp_manager.get_session_info()
                }
            
            else:
                return {'status': 'error', 'message': f'Unknown action: {action}'}
                
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def update_operations_display(self, message: str):
        """Update operations display with new message"""
        if self.operations_display:
            timestamp = time.strftime("%H:%M:%S")
            formatted_message = f"[{timestamp}] {message}"
            self.operations_display.append(formatted_message)
            
            # Scroll to bottom
            scrollbar = self.operations_display.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
    
    def update_performance_display(self):
        """Update performance metrics display"""
        try:
            # Get performance reports
            ship_performance = self.ship_engine.get_performance_report()
            session_info = self.mcp_manager.get_session_info()
            
            # Format display text
            perf_text = f"""Ship Engine Performance:
• Ships Generated: {ship_performance['generation_stats']['ships_generated']}
• Average Generation Time: {ship_performance['generation_stats']['average_generation_time']:.4f}s
• Cache Hit Rate: {ship_performance['cache_performance']['hit_rate']:.1%}
• Cached Primitives: {ship_performance['memory_usage']['cached_primitives']}

MCP Session Info:
• Session ID: {session_info['session_id'][:8]}...
• Commands Processed: {session_info['commands_processed']}
• Command Rate: {session_info['command_rate']:.1f}/min
• Average Response: {session_info['average_response_time']:.4f}s"""
            
            self.performance_display.setPlainText(perf_text)
            
        except Exception as e:
            self.performance_display.setPlainText(f"Performance data unavailable: {str(e)}")
    
    def update_status_bar(self):
        """Update status bar with current info"""
        if self.current_ship_data:
            vertices = self.current_ship_data['vertices']
            faces = self.current_ship_data['faces']
            status_text = f"Ship: {vertices} vertices, {faces} faces"
        else:
            status_text = "No ship loaded"
        
        # Add MCP status
        if self.mcp_manager.is_running:
            status_text += f" | MCP: Port {self.mcp_manager.port}"
        else:
            status_text += " | MCP: Offline"
        
        self.status_bar.showMessage(status_text)
    
    def log_message(self, message: str, level: str = "info"):
        """Log message to error display"""
        if self.error_log_display:
            timestamp = time.strftime("%H:%M:%S")
            level_icons = {
                "info": "ℹ️",
                "success": "✅",
                "error": "❌",
                "warning": "⚠️"
            }
            icon = level_icons.get(level, "📝")
            formatted_message = f"[{timestamp}] {icon} {message}"
            self.error_log_display.append(formatted_message)
            
            # Scroll to bottom
            scrollbar = self.error_log_display.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
    
    def closeEvent(self, event):
        """Handle application close with cleanup"""
        self.log_message("Shutting down application...", "info")
        
        # Stop MCP server
        self.mcp_manager.stop_server()
        
        # Clear caches
        self.ship_engine.clear_caches()
        
        self.log_message("✅ Cleanup completed", "success")
        event.accept()

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("Refactored Spaceship Designer")
    
    try:
        window = RefactoredSpaceshipDesigner()
        window.show()
        
        print("🚀 REFACTORED SPACESHIP DESIGNER")
        print("="*50)
        print("✅ Optimized ship generation engine loaded")
        print("✅ Enhanced MCP server with session persistence")
        print("✅ High-performance OpenGL viewer")
        print("✅ Real-time performance monitoring")
        print("="*50)
        
        return app.exec()
        
    except Exception as e:
        print(f"❌ Application startup failed: {e}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())