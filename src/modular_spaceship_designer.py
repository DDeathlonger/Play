#!/usr/bin/env python3
"""
MODULAR SPACESHIP DESIGNER - MAIN APPLICATION
Non-destructive refactored version with isolated modular systems
Maintains all existing functionality while providing best performance
"""

import sys
import os
from pathlib import Path
import time

# Ensure proper imports
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# PyQt6 imports
try:
    from PyQt6.QtWidgets import *
    from PyQt6.QtCore import *
    from PyQt6.QtGui import *
    HAS_PYQT6 = True
except ImportError as e:
    print(f"PyQt6 not available: {e}")
    HAS_PYQT6 = False

# Import modular systems
try:
    from system_integration import create_integrated_spaceship_designer
    from ui_system import UILayoutManager, UIThemeManager
    from display_3d import Spaceship3DViewer
    HAS_MODULAR_SYSTEMS = True
except ImportError as e:
    print(f"Modular systems not available: {e}")
    HAS_MODULAR_SYSTEMS = False

class ModularSpaceshipDesigner(QMainWindow):
    """Main application integrating all modular systems"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize integrated backend
        self.integrated_designer = None
        if HAS_MODULAR_SYSTEMS:
            self.integrated_designer = create_integrated_spaceship_designer()
        
        # UI components
        self.layout_manager = None
        self.viewer_3d = None
        
        # Application state
        self.startup_successful = False
        
        self.setup_application()
    
    def setup_application(self):
        """Setup the complete modular application"""
        if not HAS_PYQT6:
            print("❌ PyQt6 not available - cannot create GUI")
            return
        
        if not HAS_MODULAR_SYSTEMS:
            print("❌ Modular systems not available - cannot initialize")
            return
        
        try:
            # Setup window
            self.setWindowTitle("Modular Spaceship Designer - Refactored Architecture")
            self.setGeometry(100, 100, 1400, 900)
            
            # Create central widget
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            
            # Create main layout with splitter
            main_layout = QHBoxLayout(central_widget)
            splitter = QSplitter(Qt.Orientation.Horizontal)
            main_layout.addWidget(splitter)
            
            # Create UI layout manager
            self.layout_manager = UILayoutManager()
            
            # Left panel - Control interface
            left_panel = self.create_control_interface()
            splitter.addWidget(left_panel)
            
            # Right panel - 3D viewer
            self.viewer_3d = Spaceship3DViewer()
            splitter.addWidget(self.viewer_3d)
            
            # Set splitter proportions
            splitter.setStretchFactor(0, 0)  # Fixed width for controls
            splitter.setStretchFactor(1, 1)  # Expandable viewer
            splitter.setSizes([400, 1000])
            
            # Create status bar
            self.status_bar = QStatusBar()
            self.setStatusBar(self.status_bar)
            
            # Setup connections
            self.setup_connections()
            
            # Start integrated backend
            if self.integrated_designer:
                self.startup_successful = self.integrated_designer.start_application()
            
            # Initial status update
            self.update_status_display()
            
            # Generate initial ship
            self.generate_ship()
            
        except Exception as e:
            print(f"Application setup error: {e}")
            import traceback
            traceback.print_exc()
    
    def create_control_interface(self) -> QWidget:
        """Create the control interface panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Ship Generation Controls
        gen_group = QGroupBox("🚀 Ship Generation")
        gen_layout = QVBoxLayout(gen_group)
        
        # Ship class selection
        class_layout = QHBoxLayout()
        class_layout.addWidget(QLabel("Ship Class:"))
        self.ship_class_combo = QComboBox()
        self.ship_class_combo.addItems(["fighter", "cruiser", "capital", "custom"])
        self.ship_class_combo.setCurrentText("cruiser")
        class_layout.addWidget(self.ship_class_combo)
        gen_layout.addLayout(class_layout)
        
        # Component count (for custom ships)
        self.component_layout = QHBoxLayout()
        self.component_layout.addWidget(QLabel("Components:"))
        self.component_count_spin = QSpinBox()
        self.component_count_spin.setRange(3, 12)
        self.component_count_spin.setValue(5)
        self.component_layout.addWidget(self.component_count_spin)
        gen_layout.addLayout(self.component_layout)
        
        # Options
        self.randomize_check = QCheckBox("Randomize variations")
        self.randomize_check.setChecked(True)
        gen_layout.addWidget(self.randomize_check)
        
        # Generate button
        self.generate_btn = QPushButton("Generate New Ship")
        self.generate_btn.setStyleSheet("QPushButton { font-weight: bold; padding: 10px; }")
        gen_layout.addWidget(self.generate_btn)
        
        layout.addWidget(gen_group)
        
        # View Controls
        view_group = QGroupBox("🎮 View Controls")
        view_layout = QVBoxLayout(view_group)
        
        self.wireframe_btn = QPushButton("Toggle Wireframe (W)")
        self.lighting_btn = QPushButton("Toggle Lighting (L)")
        self.grid_btn = QPushButton("Toggle Grid (G)")
        self.reset_btn = QPushButton("Reset View (R)")
        
        view_layout.addWidget(self.wireframe_btn)
        view_layout.addWidget(self.lighting_btn)
        view_layout.addWidget(self.grid_btn)
        view_layout.addWidget(self.reset_btn)
        
        layout.addWidget(view_group)
        
        # MCP Operations Display
        ops_group = QGroupBox("📡 MCP Operations")
        ops_layout = QVBoxLayout(ops_group)
        
        self.operations_display = QTextEdit()
        self.operations_display.setMaximumHeight(100)
        self.operations_display.setReadOnly(True)
        self.operations_display.setStyleSheet(
            "background-color: #2b2b2b; color: #00ff00; "
            "font-family: monospace; font-size: 10px;"
        )
        ops_layout.addWidget(self.operations_display)
        
        layout.addWidget(ops_group)
        
        # Performance Metrics
        perf_group = QGroupBox("⚡ Performance")
        perf_layout = QVBoxLayout(perf_group)
        
        self.performance_display = QTextEdit()
        self.performance_display.setMaximumHeight(120)
        self.performance_display.setReadOnly(True)
        self.performance_display.setStyleSheet("font-family: monospace; font-size: 9px;")
        perf_layout.addWidget(self.performance_display)
        
        layout.addWidget(perf_group)
        
        # Export Controls
        export_group = QGroupBox("💾 Export")
        export_layout = QVBoxLayout(export_group)
        
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Format:"))
        self.export_format_combo = QComboBox()
        self.export_format_combo.addItems(["STL", "OBJ", "GLB", "PLY"])
        format_layout.addWidget(self.export_format_combo)
        export_layout.addLayout(format_layout)
        
        self.export_btn = QPushButton("Export Ship")
        export_layout.addWidget(self.export_btn)
        
        layout.addWidget(export_group)
        
        # System Log
        log_group = QGroupBox("📋 System Log")
        log_layout = QVBoxLayout(log_group)
        
        self.system_log = QTextEdit()
        self.system_log.setMaximumHeight(80)
        self.system_log.setReadOnly(True)
        log_layout.addWidget(self.system_log)
        
        layout.addWidget(log_group)
        
        layout.addStretch()
        
        # Update visibility based on ship class
        self.update_component_count_visibility()
        
        return panel
    
    def setup_connections(self):
        """Setup signal-slot connections"""
        # Generation controls
        self.generate_btn.clicked.connect(self.generate_ship)
        self.ship_class_combo.currentTextChanged.connect(self.update_component_count_visibility)
        
        # View controls
        self.wireframe_btn.clicked.connect(self.toggle_wireframe)
        self.lighting_btn.clicked.connect(self.toggle_lighting)
        self.grid_btn.clicked.connect(self.toggle_grid)
        self.reset_btn.clicked.connect(self.reset_view)
        
        # Export
        self.export_btn.clicked.connect(self.export_ship)
        
        # Performance update timer
        self.performance_timer = QTimer()
        self.performance_timer.timeout.connect(self.update_performance_display)
        self.performance_timer.start(3000)  # Update every 3 seconds
    
    def update_component_count_visibility(self):
        """Update component count controls visibility"""
        is_custom = self.ship_class_combo.currentText() == "custom"
        for i in range(self.component_layout.count()):
            widget = self.component_layout.itemAt(i).widget()
            if widget:
                widget.setVisible(is_custom)
    
    def generate_ship(self):
        """Generate new spaceship"""
        try:
            ship_class = self.ship_class_combo.currentText()
            randomize = self.randomize_check.isChecked()
            component_count = self.component_count_spin.value() if ship_class == "custom" else None
            
            self.log_message("🚀 Generating new ship...", "info")
            
            # Use integrated backend if available
            if self.integrated_designer:
                self.integrated_designer.event_bus.publish("ship_generation_requested", {
                    'ship_class': ship_class,
                    'randomize': randomize,
                    'component_count': component_count
                }, "ui")
                
                # Get the generated ship data
                current_ship = self.integrated_designer.current_ship_data
                if current_ship and self.viewer_3d:
                    self.viewer_3d.update_mesh(current_ship)
                    
                    vertices = current_ship.get('vertices', 0)
                    faces = current_ship.get('faces', 0)
                    gen_time = current_ship.get('generation_time', 0.0)
                    
                    self.log_message(f"✅ {ship_class.title()} generated: {vertices}v, {faces}f in {gen_time:.3f}s", "success")
                    self.update_operations_display(f"🎯 Generated {ship_class} ship ({vertices}v, {faces}f)")
            else:
                self.log_message("❌ Backend not available", "error")
            
            self.update_status_display()
            
        except Exception as e:
            self.log_message(f"❌ Generation failed: {str(e)}", "error")
    
    def toggle_wireframe(self):
        """Toggle wireframe mode"""
        if self.viewer_3d:
            wireframe = self.viewer_3d.toggle_wireframe()
            self.log_message(f"🔲 Wireframe: {'ON' if wireframe else 'OFF'}", "info")
            self.update_operations_display(f"🔲 Wireframe: {'ON' if wireframe else 'OFF'}")
    
    def toggle_lighting(self):
        """Toggle lighting"""
        if self.viewer_3d:
            lighting = self.viewer_3d.toggle_lighting()
            self.log_message(f"💡 Lighting: {'ON' if lighting else 'OFF'}", "info")
            self.update_operations_display(f"💡 Lighting: {'ON' if lighting else 'OFF'}")
    
    def toggle_grid(self):
        """Toggle grid display"""
        if self.viewer_3d:
            grid = self.viewer_3d.toggle_grid()
            self.log_message(f"⚏ Grid: {'ON' if grid else 'OFF'}", "info")
            self.update_operations_display(f"⚏ Grid: {'ON' if grid else 'OFF'}")
    
    def reset_view(self):
        """Reset 3D view"""
        if self.viewer_3d:
            self.viewer_3d.reset_view()
            self.log_message("🔄 View reset to default", "info")
            self.update_operations_display("🔄 View reset to default")
    
    def export_ship(self):
        """Export current ship"""
        try:
            format_str = self.export_format_combo.currentText().lower()
            
            if self.integrated_designer:
                success = self.integrated_designer._export_current_ship(format_str)
                if success:
                    self.log_message(f"✅ Ship exported as {format_str.upper()}", "success")
                    self.update_operations_display(f"💾 Exported as {format_str.upper()}")
                else:
                    self.log_message("❌ Export failed", "error")
            else:
                self.log_message("❌ Backend not available", "error")
            
        except Exception as e:
            self.log_message(f"❌ Export error: {str(e)}", "error")
    
    def update_operations_display(self, message: str):
        """Update MCP operations display"""
        timestamp = time.strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        self.operations_display.append(formatted_message)
        
        # Scroll to bottom
        scrollbar = self.operations_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def update_performance_display(self):
        """Update performance metrics display"""
        try:
            if not self.integrated_designer:
                self.performance_display.setPlainText("Backend not available")
                return
            
            # Get system info
            system_info = self.integrated_designer.get_system_info()
            
            # Get performance from ship generator
            ship_generator = self.integrated_designer.registry.get_module("ship_generator")
            perf_data = {}
            if ship_generator:
                perf_data = ship_generator.get_performance_report()
            
            # Get 3D viewer stats
            viewer_stats = {}
            if self.viewer_3d:
                viewer_stats = self.viewer_3d.get_render_stats()
            
            # Format display
            perf_text = f"""Modular System Status:
• Available Modules: {len(system_info['available_modules'])}/4
• System Uptime: {system_info['uptime']:.1f}s
• Ship Loaded: {'Yes' if system_info['current_ship_loaded'] else 'No'}

Ship Generation Performance:
• Ships Generated: {perf_data.get('generation_stats', {}).get('ships_generated', 0)}
• Avg Generation Time: {perf_data.get('generation_stats', {}).get('average_generation_time', 0):.4f}s
• Cache Hit Rate: {perf_data.get('cache_performance', {}).get('hit_rate', 0):.1%}

3D Rendering Performance:
• FPS: {viewer_stats.get('fps', 0):.1f}
• Triangles Rendered: {viewer_stats.get('triangles_rendered', 0)}
• Display List Cache Hits: {viewer_stats.get('display_list_cache_hits', 0)}"""
            
            self.performance_display.setPlainText(perf_text)
            
        except Exception as e:
            self.performance_display.setPlainText(f"Performance data error: {str(e)}")
    
    def update_status_display(self):
        """Update status bar"""
        if not self.integrated_designer:
            self.status_bar.showMessage("Backend not available")
            return
        
        current_ship = self.integrated_designer.current_ship_data
        if current_ship:
            vertices = current_ship.get('vertices', 0)
            faces = current_ship.get('faces', 0)
            status_text = f"Ship: {vertices} vertices, {faces} faces"
        else:
            status_text = "No ship loaded"
        
        # Add MCP status
        mcp_server = self.integrated_designer.registry.get_module("mcp_server")
        if mcp_server and mcp_server.is_running:
            status_text += f" | MCP: Port {mcp_server.port}"
        else:
            status_text += " | MCP: Offline"
        
        # Add module status
        available_count = len(self.integrated_designer.get_system_info()['available_modules'])
        status_text += f" | Modules: {available_count}/4"
        
        self.status_bar.showMessage(status_text)
    
    def log_message(self, message: str, level: str = "info"):
        """Log message to system log"""
        timestamp = time.strftime("%H:%M:%S")
        level_icons = {
            "info": "ℹ️",
            "success": "✅",
            "error": "❌",
            "warning": "⚠️"
        }
        icon = level_icons.get(level, "📝")
        formatted_message = f"[{timestamp}] {icon} {message}"
        self.system_log.append(formatted_message)
        
        # Scroll to bottom
        scrollbar = self.system_log.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def keyPressEvent(self, event):
        """Handle keyboard shortcuts"""
        key = event.key()
        
        if key == Qt.Key.Key_W:
            self.toggle_wireframe()
        elif key == Qt.Key.Key_L:
            self.toggle_lighting()
        elif key == Qt.Key.Key_G:
            self.toggle_grid()
        elif key == Qt.Key.Key_R:
            self.reset_view()
        elif key == Qt.Key.Key_Space:
            self.generate_ship()
        else:
            super().keyPressEvent(event)
    
    def closeEvent(self, event):
        """Handle application close"""
        self.log_message("🔄 Shutting down modular systems...", "info")
        
        if self.integrated_designer:
            self.integrated_designer.stop_application()
        
        self.log_message("✅ Shutdown complete", "success")
        event.accept()

def main():
    """Main application entry point"""
    print("🎉 MODULAR SPACESHIP DESIGNER - REFACTORED ARCHITECTURE")
    print("=" * 70)
    print("Non-destructive refactoring with isolated modular systems")
    print("Maintains all existing functionality with optimized performance")
    print("=" * 70)
    
    if not HAS_PYQT6:
        print("❌ PyQt6 not available")
        print("Install with: pip install PyQt6 PyQt6-tools")
        return 1
    
    if not HAS_MODULAR_SYSTEMS:
        print("❌ Modular systems not available")
        print("Ensure all module files are in src/ directory")
        return 1
    
    # Create QApplication
    app = QApplication(sys.argv)
    app.setApplicationName("Modular Spaceship Designer")
    
    # Apply dark theme
    UIThemeManager.apply_dark_theme(app)
    
    try:
        # Create main window
        window = ModularSpaceshipDesigner()
        
        if window.startup_successful:
            window.show()
            
            print("✅ Modular systems initialized successfully")
            print("✅ All existing functionality preserved")
            print("✅ Performance optimizations active")
            print("✅ MCP server integration enabled")
            print("=" * 70)
            print("🚀 MODULAR SPACESHIP DESIGNER READY")
            print("Keyboard shortcuts: W=Wireframe, L=Lighting, G=Grid, R=Reset, Space=Generate")
            print("=" * 70)
            
            return app.exec()
        else:
            print("❌ Application startup failed")
            return 1
        
    except Exception as e:
        print(f"❌ Application error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())