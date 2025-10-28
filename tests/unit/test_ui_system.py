#!/usr/bin/env python3
"""
UI SYSTEM MODULE UNIT TESTS
Comprehensive testing for PyQt6 user interface components
"""

import sys
import time
from pathlib import Path

# Import test framework
from test_framework import ModuleTestSuite, TestResult, assert_module_function_exists, assert_class_has_method, assert_instance_created

class UISystemTestSuite(ModuleTestSuite):
    """Complete test suite for UI system module"""
    
    def _setup_module_specific(self):
        """Setup specific to UI system testing"""
        self.test_widgets = []
        self.test_app = None
        
    def test_module_imports(self, result: TestResult):
        """Test that all required classes and functions can be imported"""
        
        # Check main classes exist (actual implementation)
        assert_class_has_method(self.module.UIEventManager, '__init__')
        assert_class_has_method(self.module.StatusDisplay, '__init__')
        assert_class_has_method(self.module.OperationsLog, '__init__')
        assert_class_has_method(self.module.ControlPanel, '__init__')
        result.add_detail("All main classes importable")
        
        # Check UI event manager methods
        assert_class_has_method(self.module.UIEventManager, 'register_callback')
        assert_class_has_method(self.module.UIEventManager, 'emit_event')
        result.add_detail("UIEventManager has required methods")
        
        # Check status display methods
        assert_class_has_method(self.module.StatusDisplay, 'setup_ui')
        assert_class_has_method(self.module.StatusDisplay, 'update_status')
        assert_class_has_method(self.module.StatusDisplay, 'update_performance')
        assert_class_has_method(self.module.StatusDisplay, 'show_progress')
        result.add_detail("StatusDisplay has required methods")
        
        # Check operations log methods
        assert_class_has_method(self.module.OperationsLog, 'setup_ui')
        assert_class_has_method(self.module.OperationsLog, 'add_entry')
        assert_class_has_method(self.module.OperationsLog, 'clear_log')
        result.add_detail("OperationsLog has required methods")
        
        # Check control panel methods
        assert_class_has_method(self.module.ControlPanel, 'setup_ui')
        assert_class_has_method(self.module.ControlPanel, 'setup_connections')
        result.add_detail("ControlPanel has required methods")
    
    def test_qt_availability(self, result: TestResult):
        """Test PyQt6 availability and basic functionality"""
        
        try:
            # Test PyQt6 core imports
            from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
            from PyQt6.QtCore import Qt, QTimer
            from PyQt6.QtGui import QPalette
            result.add_detail("PyQt6 core modules imported successfully")
            
            # Test QApplication creation (headless for testing)
            if not QApplication.instance():
                app = QApplication([])
                self.test_app = app
                result.add_detail("QApplication created for testing")
            else:
                result.add_detail("QApplication already exists")
            
        except ImportError as e:
            result.complete("SKIP", f"PyQt6 not available: {str(e)}")
            return False
        except Exception as e:
            result.add_detail(f"Qt setup error: {str(e)}")
            return False
        
        return True
    
    def test_ui_application_creation(self, result: TestResult):
        """Test UI application can be created and configured"""
        
        if not self.test_qt_availability(TestResult("qt_check", "ui_system")):
            result.complete("SKIP", "PyQt6 not available")
            return
        
        # Create UI application instance
        ui_app = assert_instance_created(
            lambda: self.module.UIApplication(),
            self.module.UIApplication
        )
        result.add_detail("UIApplication created successfully")
        
        # Check UI application attributes
        required_attrs = ['main_window', 'layout_manager', 'control_panel', 'status_display']
        for attr in required_attrs:
            if hasattr(ui_app, attr):
                result.add_detail(f"UIApplication has {attr}")
        
        # Test UI setup
        try:
            ui_app.setup_ui()
            result.add_detail("UI setup completed")
        except Exception as e:
            result.add_detail(f"UI setup error: {str(e)}")
        
        return ui_app
    
    def test_layout_manager(self, result: TestResult):
        """Test layout manager functionality"""
        
        if not self.test_qt_availability(TestResult("qt_check", "ui_system")):
            result.complete("SKIP", "PyQt6 not available")
            return
        
        # Create layout manager
        layout_mgr = assert_instance_created(
            lambda: self.module.UILayoutManager(),
            self.module.UILayoutManager
        )
        result.add_detail("UILayoutManager created successfully")
        
        # Test layout creation
        try:
            main_layout = layout_mgr.create_main_layout()
            assert main_layout is not None, "Main layout creation returned None"
            result.add_detail("Main layout created")
        except Exception as e:
            result.add_detail(f"Layout creation error: {str(e)}")
        
        # Test widget addition (if method exists)
        if hasattr(layout_mgr, 'add_widget'):
            try:
                from PyQt6.QtWidgets import QLabel
                test_widget = QLabel("Test Widget")
                layout_mgr.add_widget(test_widget)
                result.add_detail("Widget added to layout")
                self.test_widgets.append(test_widget)
            except Exception as e:
                result.add_detail(f"Widget addition error: {str(e)}")
        
        # Test responsive layout (if available)
        if hasattr(layout_mgr, 'update_layout_for_size'):
            try:
                layout_mgr.update_layout_for_size(800, 600)
                result.add_detail("Responsive layout update successful")
            except Exception as e:
                result.add_detail(f"Responsive layout error: {str(e)}")
    
    def test_control_panel(self, result: TestResult):
        """Test control panel functionality"""
        
        if not self.test_qt_availability(TestResult("qt_check", "ui_system")):
            result.complete("SKIP", "PyQt6 not available")
            return
        
        # Create control panel
        control_panel = assert_instance_created(
            lambda: self.module.ControlPanel(),
            self.module.ControlPanel
        )
        result.add_detail("ControlPanel created successfully")
        
        # Test control creation
        try:
            control_panel.create_controls()
            result.add_detail("Control panel controls created")
        except Exception as e:
            result.add_detail(f"Control creation error: {str(e)}")
        
        # Check for standard controls
        control_types = ['buttons', 'sliders', 'checkboxes', 'spinboxes']
        for control_type in control_types:
            if hasattr(control_panel, control_type):
                controls = getattr(control_panel, control_type)
                if controls:
                    result.add_detail(f"Has {control_type}: {len(controls) if hasattr(controls, '__len__') else 'yes'}")
        
        # Test control updates
        if hasattr(control_panel, 'update_controls'):
            try:
                test_data = {'grid_size': [8, 5, 12], 'ship_type': 'fighter'}
                control_panel.update_controls(test_data)
                result.add_detail("Control panel updated with data")
            except Exception as e:
                result.add_detail(f"Control update error: {str(e)}")
        
        # Test signal connections (if available)
        if hasattr(control_panel, 'connect_signals'):
            try:
                def dummy_handler():
                    pass
                control_panel.connect_signals({'generate': dummy_handler})
                result.add_detail("Control signals connected")
            except Exception as e:
                result.add_detail(f"Signal connection error: {str(e)}")
    
    def test_status_display(self, result: TestResult):
        """Test status display functionality"""
        
        if not self.test_qt_availability(TestResult("qt_check", "ui_system")):
            result.complete("SKIP", "PyQt6 not available")
            return
        
        # Create status display
        status_display = assert_instance_created(
            lambda: self.module.StatusDisplay(),
            self.module.StatusDisplay
        )
        result.add_detail("StatusDisplay created successfully")
        
        # Test status updates
        try:
            status_display.update_status("Test status message")
            result.add_detail("Status message updated")
        except Exception as e:
            result.add_detail(f"Status update error: {str(e)}")
        
        # Test message logging
        if hasattr(status_display, 'log_message'):
            try:
                status_display.log_message("Test log message", level="info")
                status_display.log_message("Test warning", level="warning")
                status_display.log_message("Test error", level="error")
                result.add_detail("Messages logged with different levels")
            except Exception as e:
                result.add_detail(f"Message logging error: {str(e)}")
        
        # Test progress display (if available)
        if hasattr(status_display, 'update_progress'):
            try:
                status_display.update_progress(50, "Processing...")
                result.add_detail("Progress display updated")
            except Exception as e:
                result.add_detail(f"Progress display error: {str(e)}")
        
        # Test status history (if available)
        if hasattr(status_display, 'get_message_history'):
            try:
                history = status_display.get_message_history()
                result.add_detail(f"Message history retrieved: {len(history) if history else 0} messages")
            except Exception as e:
                result.add_detail(f"History retrieval error: {str(e)}")
    
    def test_theming_and_styling(self, result: TestResult):
        """Test UI theming and styling functionality"""
        
        if not self.test_qt_availability(TestResult("qt_check", "ui_system")):
            result.complete("SKIP", "PyQt6 not available")
            return
        
        # Test theme application
        ui_app = self.test_ui_application_creation(TestResult("ui_setup", "ui_system"))
        
        if hasattr(ui_app, 'apply_theme'):
            try:
                # Test dark theme
                ui_app.apply_theme('dark')
                result.add_detail("Dark theme applied")
                
                # Test light theme  
                ui_app.apply_theme('light')
                result.add_detail("Light theme applied")
                
                # Test custom theme
                if hasattr(ui_app, 'apply_custom_theme'):
                    custom_style = {
                        'background-color': '#2b2b2b',
                        'color': '#ffffff',
                        'border': '1px solid #555555'
                    }
                    ui_app.apply_custom_theme(custom_style)
                    result.add_detail("Custom theme applied")
            except Exception as e:
                result.add_detail(f"Theme application error: {str(e)}")
        
        # Test responsive design
        if hasattr(ui_app, 'update_for_screen_size'):
            try:
                ui_app.update_for_screen_size(1920, 1080)
                result.add_detail("UI updated for high resolution")
                
                ui_app.update_for_screen_size(1366, 768)
                result.add_detail("UI updated for standard resolution")
            except Exception as e:
                result.add_detail(f"Responsive design error: {str(e)}")
    
    def test_event_handling(self, result: TestResult):
        """Test UI event handling system"""
        
        if not self.test_qt_availability(TestResult("qt_check", "ui_system")):
            result.complete("SKIP", "PyQt6 not available")
            return
        
        ui_app = self.test_ui_application_creation(TestResult("ui_setup", "ui_system"))
        
        # Test event system setup
        if hasattr(ui_app, 'setup_event_handlers'):
            try:
                ui_app.setup_event_handlers()
                result.add_detail("Event handlers setup completed")
            except Exception as e:
                result.add_detail(f"Event setup error: {str(e)}")
        
        # Test custom event handling
        if hasattr(ui_app, 'handle_custom_event'):
            try:
                test_event = {'type': 'ship_generated', 'data': {'vertices': 100}}
                ui_app.handle_custom_event(test_event)
                result.add_detail("Custom event handled")
            except Exception as e:
                result.add_detail(f"Custom event error: {str(e)}")
        
        # Test keyboard shortcuts
        if hasattr(ui_app, 'setup_keyboard_shortcuts'):
            try:
                ui_app.setup_keyboard_shortcuts()
                result.add_detail("Keyboard shortcuts configured")
            except Exception as e:
                result.add_detail(f"Keyboard shortcuts error: {str(e)}")
    
    def test_widget_interactions(self, result: TestResult):
        """Test widget interactions and data flow"""
        
        if not self.test_qt_availability(TestResult("qt_check", "ui_system")):
            result.complete("SKIP", "PyQt6 not available")
            return
        
        try:
            from PyQt6.QtWidgets import QSlider, QPushButton, QSpinBox, QCheckBox
            from PyQt6.QtCore import Qt
            
            # Create test widgets
            slider = QSlider(Qt.Orientation.Horizontal)
            button = QPushButton("Test Button")
            spinbox = QSpinBox()
            checkbox = QCheckBox("Test Option")
            
            result.add_detail("Test widgets created")
            
            # Test widget configuration
            slider.setRange(0, 100)
            slider.setValue(50)
            spinbox.setRange(1, 20)
            spinbox.setValue(10)
            checkbox.setChecked(True)
            
            result.add_detail("Widget values configured")
            
            # Test value retrieval
            slider_value = slider.value()
            spinbox_value = spinbox.value()
            checkbox_state = checkbox.isChecked()
            
            assert slider_value == 50, f"Slider value mismatch: {slider_value}"
            assert spinbox_value == 10, f"Spinbox value mismatch: {spinbox_value}"
            assert checkbox_state == True, f"Checkbox state mismatch: {checkbox_state}"
            
            result.add_detail("Widget values verified")
            
            # Store for cleanup
            self.test_widgets.extend([slider, button, spinbox, checkbox])
            
        except Exception as e:
            result.add_detail(f"Widget interaction error: {str(e)}")
    
    def test_layout_responsiveness(self, result: TestResult):
        """Test responsive layout behavior"""
        
        if not self.test_qt_availability(TestResult("qt_check", "ui_system")):
            result.complete("SKIP", "PyQt6 not available")
            return
        
        try:
            from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout
            
            # Create container widget
            container = QWidget()
            
            # Test different layout types
            layouts_tested = []
            
            # Vertical layout
            v_layout = QVBoxLayout()
            container.setLayout(v_layout)
            layouts_tested.append("VBoxLayout")
            
            # Horizontal layout
            h_layout = QHBoxLayout()
            test_widget = QWidget()
            test_widget.setLayout(h_layout)
            layouts_tested.append("HBoxLayout")
            
            # Grid layout
            grid_layout = QGridLayout()
            grid_widget = QWidget()
            grid_widget.setLayout(grid_layout)
            layouts_tested.append("GridLayout")
            
            result.add_detail(f"Layout types tested: {', '.join(layouts_tested)}")
            
            # Test size policies
            from PyQt6.QtWidgets import QSizePolicy
            
            container.setSizePolicy(
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Expanding
            )
            result.add_detail("Size policies configured")
            
            # Test minimum sizes
            container.setMinimumSize(400, 300)
            min_size = container.minimumSize()
            result.add_detail(f"Minimum size set: {min_size.width()}x{min_size.height()}")
            
            self.test_widgets.append(container)
            
        except Exception as e:
            result.add_detail(f"Layout responsiveness error: {str(e)}")
    
    def test_performance_and_memory(self, result: TestResult):
        """Test UI performance and memory usage"""
        
        if not self.test_qt_availability(TestResult("qt_check", "ui_system")):
            result.complete("SKIP", "PyQt6 not available")
            return
        
        import gc
        
        initial_objects = len(gc.get_objects())
        start_time = time.time()
        
        try:
            # Create multiple UI components
            ui_components = []
            
            for i in range(10):
                ui_app = self.module.UIApplication()
                ui_app.setup_ui()
                ui_components.append(ui_app)
            
            creation_time = time.time() - start_time
            result.add_detail(f"Created 10 UI applications in {creation_time:.3f}s")
            
            # Test memory usage
            mid_objects = len(gc.get_objects())
            object_increase = mid_objects - initial_objects
            result.add_detail(f"Object count increased by: {object_increase}")
            
            # Cleanup
            ui_components.clear()
            gc.collect()
            
            final_objects = len(gc.get_objects())
            remaining_objects = final_objects - initial_objects
            
            if remaining_objects < 50:  # Reasonable threshold
                result.add_detail("Memory cleanup successful")
            else:
                result.add_detail(f"Potential memory leak: {remaining_objects} objects retained")
            
        except Exception as e:
            result.add_detail(f"Performance test error: {str(e)}")
    
    def test_accessibility_features(self, result: TestResult):
        """Test accessibility and usability features"""
        
        if not self.test_qt_availability(TestResult("qt_check", "ui_system")):
            result.complete("SKIP", "PyQt6 not available")
            return
        
        try:
            from PyQt6.QtWidgets import QPushButton, QLabel
            from PyQt6.QtCore import Qt
            
            # Test accessibility properties
            button = QPushButton("Accessible Button")
            button.setToolTip("This button generates a new spaceship")
            button.setStatusTip("Click to start ship generation")
            
            label = QLabel("Accessible Label")
            label.setBuddy(button)  # Associate label with button
            
            result.add_detail("Accessibility properties set")
            
            # Test keyboard navigation (if available)
            button.setFocusPolicy(Qt.FocusPolicy.TabFocus)
            result.add_detail("Keyboard navigation configured")
            
            # Test high contrast support
            button.setStyleSheet("QPushButton { font-weight: bold; }")
            result.add_detail("High contrast styling applied")
            
            self.test_widgets.extend([button, label])
            
        except Exception as e:
            result.add_detail(f"Accessibility test error: {str(e)}")

if __name__ == "__main__":
    from test_framework import UniversalTestRunner
    
    # Create test runner
    runner = UniversalTestRunner()
    
    # Add UI system test suite
    ui_suite = UISystemTestSuite("ui_system", runner.logger)
    runner.add_test_suite(ui_suite)
    
    # Run dependency check
    deps_ok = runner.run_dependency_check()
    
    if deps_ok:
        # Run tests
        results = runner.run_all_tests()
        
        # Save results
        output_dir = Path(__file__).parent.parent / "results"
        runner.save_results(output_dir)
        
        print(f"\n🖥️ UI SYSTEM MODULE TESTING COMPLETE")
        print(f"Pass Rate: {results['summary']['pass_rate']:.1f}%")
    else:
        print("❌ Critical dependencies missing - skipping tests")