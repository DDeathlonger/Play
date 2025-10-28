#!/usr/bin/env python3
"""
UI SYSTEM - ISOLATED MODULE
PyQt6 user interface components and layout management
"""

import sys
from typing import Dict, List, Any, Optional, Callable
from pathlib import Path

# PyQt6 imports with error handling
try:
    from PyQt6.QtWidgets import *
    from PyQt6.QtCore import *
    from PyQt6.QtGui import *
    HAS_PYQT6 = True
except ImportError as e:
    print(f"PyQt6 not available: {e}")
    HAS_PYQT6 = False

class UIEventManager:
    """Manages UI events and callbacks"""
    
    def __init__(self):
        self.callbacks = {}
    
    def register_callback(self, event_name: str, callback: Callable):
        """Register event callback"""
        if event_name not in self.callbacks:
            self.callbacks[event_name] = []
        self.callbacks[event_name].append(callback)
    
    def emit_event(self, event_name: str, *args, **kwargs):
        """Emit event to all registered callbacks"""
        if event_name in self.callbacks:
            for callback in self.callbacks[event_name]:
                try:
                    callback(*args, **kwargs)
                except Exception as e:
                    print(f"Event callback error: {e}")

class StatusDisplay(QWidget):
    """Status and performance display widget"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        """Setup status display UI"""
        layout = QVBoxLayout(self)
        
        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("font-weight: bold; color: green;")
        layout.addWidget(self.status_label)
        
        # Performance metrics
        self.performance_display = QTextEdit()
        self.performance_display.setMaximumHeight(120)
        self.performance_display.setReadOnly(True)
        self.performance_display.setStyleSheet("font-family: monospace; font-size: 10px;")
        layout.addWidget(self.performance_display)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
    
    def update_status(self, message: str, status_type: str = "info"):
        """Update status message"""
        colors = {
            "info": "blue",
            "success": "green", 
            "error": "red",
            "warning": "orange"
        }
        color = colors.get(status_type, "blue")
        self.status_label.setText(message)
        self.status_label.setStyleSheet(f"font-weight: bold; color: {color};")
    
    def update_performance(self, metrics: Dict[str, Any]):
        """Update performance metrics display"""
        text_lines = []
        for key, value in metrics.items():
            if isinstance(value, dict):
                text_lines.append(f"{key}:")
                for sub_key, sub_value in value.items():
                    text_lines.append(f"  {sub_key}: {sub_value}")
            else:
                text_lines.append(f"{key}: {value}")
        
        self.performance_display.setPlainText("\n".join(text_lines))
    
    def show_progress(self, value: int, maximum: int = 100):
        """Show progress bar with value"""
        self.progress_bar.setMaximum(maximum)
        self.progress_bar.setValue(value)
        self.progress_bar.setVisible(True)
    
    def hide_progress(self):
        """Hide progress bar"""
        self.progress_bar.setVisible(False)

class OperationsLog(QWidget):
    """Operations log widget for MCP commands and system events"""
    
    def __init__(self, max_entries: int = 100):
        super().__init__()
        self.max_entries = max_entries
        self.entries = []
        self.setup_ui()
    
    def setup_ui(self):
        """Setup operations log UI"""
        layout = QVBoxLayout(self)
        
        # Log display
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setMaximumHeight(100)
        self.log_display.setStyleSheet(
            "background-color: #2b2b2b; color: #00ff00; "
            "font-family: monospace; font-size: 10px;"
        )
        layout.addWidget(self.log_display)
        
        # Clear button
        self.clear_btn = QPushButton("Clear Log")
        self.clear_btn.clicked.connect(self.clear_log)
        layout.addWidget(self.clear_btn)
    
    def add_entry(self, message: str, entry_type: str = "info"):
        """Add log entry"""
        import time
        timestamp = time.strftime("%H:%M:%S")
        
        icons = {
            "info": "ℹ️",
            "success": "✅",
            "error": "❌",
            "warning": "⚠️",
            "mcp": "📡"
        }
        
        icon = icons.get(entry_type, "📝")
        formatted_entry = f"[{timestamp}] {icon} {message}"
        
        self.entries.append(formatted_entry)
        
        # Maintain max entries
        if len(self.entries) > self.max_entries:
            self.entries.pop(0)
        
        # Update display
        self.log_display.setPlainText("\n".join(self.entries))
        
        # Scroll to bottom
        scrollbar = self.log_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def clear_log(self):
        """Clear log entries"""
        self.entries.clear()
        self.log_display.clear()
    
    def get_recent_entries(self, count: int = 3) -> List[str]:
        """Get recent log entries"""
        return self.entries[-count:] if self.entries else []

class ControlPanel(QWidget):
    """Main control panel with generation and export controls"""
    
    def __init__(self, event_manager: UIEventManager):
        super().__init__()
        self.event_manager = event_manager
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """Setup control panel UI"""
        layout = QVBoxLayout(self)
        
        # Ship Generation Section
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
        
        # Component count for custom ships
        self.component_count_layout = QHBoxLayout()
        self.component_count_layout.addWidget(QLabel("Components:"))
        self.component_count_spin = QSpinBox()
        self.component_count_spin.setRange(3, 12)
        self.component_count_spin.setValue(5)
        self.component_count_layout.addWidget(self.component_count_spin)
        gen_layout.addLayout(self.component_count_layout)
        
        # Generation options
        self.randomize_check = QCheckBox("Randomize variations")
        self.randomize_check.setChecked(True)
        gen_layout.addWidget(self.randomize_check)
        
        # Generation button
        self.generate_btn = QPushButton("Generate New Ship")
        self.generate_btn.setStyleSheet("QPushButton { font-weight: bold; padding: 8px; }")
        gen_layout.addWidget(self.generate_btn)
        
        layout.addWidget(gen_group)
        
        # View Controls Section
        controls_group = QGroupBox("🎮 View Controls")
        controls_layout = QVBoxLayout(controls_group)
        
        self.wireframe_btn = QPushButton("Toggle Wireframe (W)")
        self.lighting_btn = QPushButton("Toggle Lighting (L)")
        self.reset_btn = QPushButton("Reset View (R)")
        
        controls_layout.addWidget(self.wireframe_btn)
        controls_layout.addWidget(self.lighting_btn)
        controls_layout.addWidget(self.reset_btn)
        
        layout.addWidget(controls_group)
        
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
        
        # Configuration Section
        config_group = QGroupBox("⚙️ Configuration")
        config_layout = QVBoxLayout(config_group)
        
        self.save_config_btn = QPushButton("Save Configuration")
        self.load_config_btn = QPushButton("Load Configuration")
        
        config_layout.addWidget(self.save_config_btn)
        config_layout.addWidget(self.load_config_btn)
        
        layout.addWidget(config_group)
        
        layout.addStretch()
        
        # Update component count visibility
        self.update_component_count_visibility()
    
    def setup_connections(self):
        """Setup signal-slot connections"""
        self.generate_btn.clicked.connect(self.on_generate_ship)
        self.wireframe_btn.clicked.connect(self.on_toggle_wireframe)
        self.lighting_btn.clicked.connect(self.on_toggle_lighting)
        self.reset_btn.clicked.connect(self.on_reset_view)
        self.export_btn.clicked.connect(self.on_export_ship)
        self.save_config_btn.clicked.connect(self.on_save_config)
        self.load_config_btn.clicked.connect(self.on_load_config)
        
        self.ship_class_combo.currentTextChanged.connect(self.update_component_count_visibility)
    
    def update_component_count_visibility(self):
        """Update component count controls visibility"""
        is_custom = self.ship_class_combo.currentText() == "custom"
        for i in range(self.component_count_layout.count()):
            widget = self.component_count_layout.itemAt(i).widget()
            if widget:
                widget.setVisible(is_custom)
    
    def on_generate_ship(self):
        """Handle ship generation"""
        ship_class = self.ship_class_combo.currentText()
        randomize = self.randomize_check.isChecked()
        component_count = self.component_count_spin.value() if ship_class == "custom" else None
        
        self.event_manager.emit_event('generate_ship', 
                                    ship_class=ship_class, 
                                    randomize=randomize,
                                    component_count=component_count)
    
    def on_toggle_wireframe(self):
        """Handle wireframe toggle"""
        self.event_manager.emit_event('toggle_wireframe')
    
    def on_toggle_lighting(self):
        """Handle lighting toggle"""
        self.event_manager.emit_event('toggle_lighting')
    
    def on_reset_view(self):
        """Handle view reset"""
        self.event_manager.emit_event('reset_view')
    
    def on_export_ship(self):
        """Handle ship export"""
        format_str = self.export_format_combo.currentText().lower()
        self.event_manager.emit_event('export_ship', format=format_str)
    
    def on_save_config(self):
        """Handle configuration save"""
        self.event_manager.emit_event('save_config')
    
    def on_load_config(self):
        """Handle configuration load"""
        self.event_manager.emit_event('load_config')

class UILayoutManager:
    """Manages UI layout and component arrangement"""
    
    def __init__(self):
        self.components = {}
        self.event_manager = UIEventManager()
    
    def create_main_layout(self, parent: QWidget) -> QLayout:
        """Create main application layout"""
        # Main horizontal layout
        main_layout = QHBoxLayout(parent)
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left panel - Controls and status
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)
        
        # Right panel placeholder (for 3D viewer)
        right_panel = QWidget()
        right_panel.setMinimumSize(600, 400)
        right_panel.setStyleSheet("background-color: #1e1e1e; border: 1px solid #555;")
        splitter.addWidget(right_panel)
        
        # Set splitter proportions
        splitter.setStretchFactor(0, 0)  # Fixed width for controls
        splitter.setStretchFactor(1, 1)  # Expandable viewer
        splitter.setSizes([400, 800])
        
        return main_layout
    
    def create_left_panel(self) -> QWidget:
        """Create left control panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Control panel
        self.components['control_panel'] = ControlPanel(self.event_manager)
        layout.addWidget(self.components['control_panel'])
        
        # Operations log
        ops_group = QGroupBox("📡 Operations")
        ops_layout = QVBoxLayout(ops_group)
        self.components['operations_log'] = OperationsLog()
        ops_layout.addWidget(self.components['operations_log'])
        layout.addWidget(ops_group)
        
        # Status display
        status_group = QGroupBox("📊 Status")
        status_layout = QVBoxLayout(status_group)
        self.components['status_display'] = StatusDisplay()
        status_layout.addWidget(self.components['status_display'])
        layout.addWidget(status_group)
        
        return panel
    
    def get_component(self, name: str) -> Optional[QWidget]:
        """Get UI component by name"""
        return self.components.get(name)
    
    def get_event_manager(self) -> UIEventManager:
        """Get event manager"""
        return self.event_manager

class UIThemeManager:
    """Manages UI themes and styling"""
    
    @staticmethod
    def apply_dark_theme(app: QApplication):
        """Apply dark theme to application"""
        if not HAS_PYQT6:
            return
        
        dark_stylesheet = """
        QMainWindow {
            background-color: #2b2b2b;
            color: #ffffff;
        }
        QWidget {
            background-color: #2b2b2b;
            color: #ffffff;
        }
        QGroupBox {
            font-weight: bold;
            border: 2px solid #555;
            border-radius: 5px;
            margin: 5px 0px;
            padding-top: 10px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0px 5px 0px 5px;
        }
        QPushButton {
            background-color: #404040;
            border: 1px solid #555;
            padding: 5px;
            border-radius: 3px;
        }
        QPushButton:hover {
            background-color: #505050;
        }
        QPushButton:pressed {
            background-color: #303030;
        }
        QComboBox, QSpinBox {
            background-color: #404040;
            border: 1px solid #555;
            padding: 3px;
        }
        QTextEdit {
            background-color: #1e1e1e;
            border: 1px solid #555;
        }
        QCheckBox::indicator {
            width: 13px;
            height: 13px;
        }
        QCheckBox::indicator:unchecked {
            border: 1px solid #555;
            background-color: #2b2b2b;
        }
        QCheckBox::indicator:checked {
            border: 1px solid #555;
            background-color: #0078d4;
        }
        """
        app.setStyleSheet(dark_stylesheet)

class UIApplication:
    """Main UI application manager"""
    
    def __init__(self):
        self.app = None
        self.main_window = None
        self.layout_manager = None
        
        if HAS_PYQT6:
            self.app = QApplication.instance()
            if self.app is None:
                self.app = QApplication(sys.argv)
            
            # Apply dark theme
            UIThemeManager.apply_dark_theme(self.app)
    
    def create_main_window(self, title: str = "Spaceship Designer UI") -> Optional[QMainWindow]:
        """Create main application window"""
        if not HAS_PYQT6:
            print("PyQt6 not available, cannot create UI")
            return None
        
        self.main_window = QMainWindow()
        self.main_window.setWindowTitle(title)
        self.main_window.setGeometry(100, 100, 1200, 800)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.main_window.setCentralWidget(central_widget)
        
        # Create layout manager
        self.layout_manager = UILayoutManager()
        self.layout_manager.create_main_layout(central_widget)
        
        # Create status bar
        status_bar = QStatusBar()
        self.main_window.setStatusBar(status_bar)
        status_bar.showMessage("UI System Ready")
        
        return self.main_window
    
    def get_layout_manager(self) -> Optional[UILayoutManager]:
        """Get layout manager"""
        return self.layout_manager
    
    def run(self) -> int:
        """Run the UI application"""
        if not self.app or not self.main_window:
            print("UI not properly initialized")
            return 1
        
        self.main_window.show()
        return self.app.exec()
    
    def quit(self):
        """Quit the application"""
        if self.app:
            self.app.quit()

# Factory functions for easy instantiation
def create_ui_application() -> UIApplication:
    """Create UI application instance"""
    return UIApplication()

def create_event_manager() -> UIEventManager:
    """Create event manager instance"""
    return UIEventManager()

if __name__ == "__main__":
    # Demo usage
    print("🎮 UI SYSTEM - ISOLATED MODULE TEST")
    print("=" * 50)
    
    if HAS_PYQT6:
        # Create and run UI
        ui_app = create_ui_application()
        main_window = ui_app.create_main_window("UI System Test")
        
        if main_window:
            print("✅ UI system initialized successfully")
            print("✅ Main window created")
            print("✅ Dark theme applied")
            print("✅ Layout manager active")
            
            # Show window briefly for testing
            main_window.show()
            
            # Don't run full event loop in test
            print("✅ UI components ready")
        else:
            print("❌ Failed to create main window")
    else:
        print("❌ PyQt6 not available - UI system cannot be tested")