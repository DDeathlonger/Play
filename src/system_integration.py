#!/usr/bin/env python3
"""
SYSTEM INTEGRATION - ISOLATED MODULE
Binds all modular systems together while maintaining isolation
"""

import sys
import os
import time
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable

# Add src to path for module imports
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# Import isolated modules
try:
    from mcp_tools import MCPServer, MCPClient, create_mcp_server
    HAS_MCP_TOOLS = True
except ImportError as e:
    print(f"MCP Tools module not available: {e}")
    HAS_MCP_TOOLS = False

try:
    from ship_generation import ShipGenerator, create_ship_generator, ShipConfiguration
    HAS_SHIP_GENERATION = True
except ImportError as e:
    print(f"Ship Generation module not available: {e}")
    HAS_SHIP_GENERATION = False

try:
    from ui_system import UIApplication, create_ui_application
    HAS_UI_SYSTEM = True
except ImportError as e:
    print(f"UI System module not available: {e}")
    HAS_UI_SYSTEM = False

try:
    from display_3d import Spaceship3DViewer, create_3d_viewer
    HAS_3D_DISPLAY = True
except ImportError as e:
    print(f"3D Display module not available: {e}")
    HAS_3D_DISPLAY = False

class ModuleRegistry:
    """Registry for all system modules"""
    
    def __init__(self):
        self.modules = {}
        self.module_status = {}
        self.dependencies_checked = False
    
    def register_module(self, name: str, instance: Any, status: str = "available"):
        """Register a system module"""
        self.modules[name] = instance
        self.module_status[name] = status
    
    def get_module(self, name: str) -> Optional[Any]:
        """Get module by name"""
        return self.modules.get(name)
    
    def is_module_available(self, name: str) -> bool:
        """Check if module is available"""
        return self.module_status.get(name) == "available"
    
    def get_available_modules(self) -> List[str]:
        """Get list of available module names"""
        return [name for name, status in self.module_status.items() if status == "available"]
    
    def get_module_status(self) -> Dict[str, str]:
        """Get status of all modules"""
        return self.module_status.copy()

class SystemEventBus:
    """Event bus for inter-module communication"""
    
    def __init__(self):
        self.event_handlers = {}
        self.event_history = []
        self.max_history = 100
    
    def subscribe(self, event_type: str, handler: Callable, priority: int = 0):
        """Subscribe to system events"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        
        self.event_handlers[event_type].append((priority, handler))
        # Sort by priority (higher priority first)
        self.event_handlers[event_type].sort(key=lambda x: x[0], reverse=True)
    
    def publish(self, event_type: str, data: Any = None, source: str = "unknown"):
        """Publish system event"""
        event_info = {
            'type': event_type,
            'data': data,
            'source': source,
            'timestamp': time.time()
        }
        
        # Add to history
        self.event_history.append(event_info)
        if len(self.event_history) > self.max_history:
            self.event_history.pop(0)
        
        # Call handlers
        if event_type in self.event_handlers:
            for priority, handler in self.event_handlers[event_type]:
                try:
                    handler(event_info)
                except Exception as e:
                    print(f"Event handler error: {e}")
    
    def get_recent_events(self, count: int = 10) -> List[Dict[str, Any]]:
        """Get recent events"""
        return self.event_history[-count:] if self.event_history else []

class IntegratedSpaceshipDesigner:
    """Main integrated application class"""
    
    def __init__(self):
        # Core systems
        self.registry = ModuleRegistry()
        self.event_bus = SystemEventBus()
        
        # Initialize modules
        self._initialize_modules()
        self._setup_event_handlers()
        self._setup_mcp_handlers()
        
        # Application state
        self.current_ship_data = None
        self.is_running = False
        self.startup_time = None
    
    def _initialize_modules(self):
        """Initialize all available modules"""
        print("🔧 Initializing modular systems...")
        
        # Initialize MCP Tools
        if HAS_MCP_TOOLS:
            try:
                mcp_server = create_mcp_server()
                self.registry.register_module("mcp_server", mcp_server, "available")
                print("✅ MCP Tools module loaded")
            except Exception as e:
                print(f"❌ MCP Tools initialization failed: {e}")
                self.registry.register_module("mcp_server", None, "failed")
        else:
            self.registry.register_module("mcp_server", None, "unavailable")
        
        # Initialize Ship Generation
        if HAS_SHIP_GENERATION:
            try:
                ship_generator = create_ship_generator()
                self.registry.register_module("ship_generator", ship_generator, "available")
                print("✅ Ship Generation module loaded")
            except Exception as e:
                print(f"❌ Ship Generation initialization failed: {e}")
                self.registry.register_module("ship_generator", None, "failed")
        else:
            self.registry.register_module("ship_generator", None, "unavailable")
        
        # Initialize UI System
        if HAS_UI_SYSTEM:
            try:
                ui_app = create_ui_application()
                self.registry.register_module("ui_system", ui_app, "available")
                print("✅ UI System module loaded")
            except Exception as e:
                print(f"❌ UI System initialization failed: {e}")
                self.registry.register_module("ui_system", None, "failed")
        else:
            self.registry.register_module("ui_system", None, "unavailable")
        
        # Initialize 3D Display
        if HAS_3D_DISPLAY:
            try:
                viewer_3d = create_3d_viewer()
                self.registry.register_module("3d_viewer", viewer_3d, "available")
                print("✅ 3D Display module loaded")
            except Exception as e:
                print(f"❌ 3D Display initialization failed: {e}")
                self.registry.register_module("3d_viewer", None, "failed")
        else:
            self.registry.register_module("3d_viewer", None, "unavailable")
    
    def _setup_event_handlers(self):
        """Setup inter-module event handlers"""
        # Ship generation events
        self.event_bus.subscribe("ship_generation_requested", self._handle_ship_generation, priority=10)
        self.event_bus.subscribe("ship_generated", self._handle_ship_generated, priority=10)
        
        # UI events
        self.event_bus.subscribe("ui_action", self._handle_ui_action, priority=10)
        self.event_bus.subscribe("view_control", self._handle_view_control, priority=10)
        
        # System events
        self.event_bus.subscribe("system_status_update", self._handle_status_update, priority=5)
        self.event_bus.subscribe("performance_metrics", self._handle_performance_metrics, priority=5)
    
    def _setup_mcp_handlers(self):
        """Setup MCP command handlers"""
        mcp_server = self.registry.get_module("mcp_server")
        if mcp_server:
            # Register MCP command handlers
            mcp_server.register_handler("generate_ship", self._mcp_generate_ship)
            mcp_server.register_handler("toggle_wireframe", self._mcp_toggle_wireframe)
            mcp_server.register_handler("toggle_lighting", self._mcp_toggle_lighting)
            mcp_server.register_handler("reset_view", self._mcp_reset_view)
            mcp_server.register_handler("export_ship", self._mcp_export_ship)
            mcp_server.register_handler("get_ship_info", self._mcp_get_ship_info)
            mcp_server.register_handler("get_system_status", self._mcp_get_system_status)
    
    def _handle_ship_generation(self, event_info: Dict[str, Any]):
        """Handle ship generation request"""
        ship_generator = self.registry.get_module("ship_generator")
        if not ship_generator:
            return
        
        try:
            data = event_info.get('data', {})
            ship_class = data.get('ship_class', 'cruiser')
            randomize = data.get('randomize', True)
            component_count = data.get('component_count')
            
            # Generate ship based on request
            if ship_class == 'custom' and component_count:
                ship_data = ship_generator.generate_custom_ship(component_count)
            else:
                ship_data = ship_generator.generate_ship_by_class(ship_class, randomize)
            
            self.current_ship_data = ship_data
            
            # Publish ship generated event
            self.event_bus.publish("ship_generated", ship_data, "ship_generator")
            
        except Exception as e:
            print(f"Ship generation error: {e}")
            self.event_bus.publish("system_error", str(e), "ship_generator")
    
    def _handle_ship_generated(self, event_info: Dict[str, Any]):
        """Handle ship generation completion"""
        ship_data = event_info.get('data')
        if not ship_data:
            return
        
        # Update 3D viewer
        viewer_3d = self.registry.get_module("3d_viewer")
        if viewer_3d and hasattr(viewer_3d, 'update_mesh'):
            viewer_3d.update_mesh(ship_data)
        
        # Log success
        vertices = ship_data.get('vertices', 0)
        faces = ship_data.get('faces', 0)
        gen_time = ship_data.get('generation_time', 0.0)
        
        self.event_bus.publish("system_status_update", {
            'message': f"Ship generated: {vertices} vertices, {faces} faces in {gen_time:.3f}s",
            'type': 'success'
        }, "integration")
    
    def _handle_ui_action(self, event_info: Dict[str, Any]):
        """Handle UI action events"""
        data = event_info.get('data', {})
        action = data.get('action')
        
        if action == 'generate_ship':
            self.event_bus.publish("ship_generation_requested", data, "ui")
        elif action == 'export_ship':
            self._export_current_ship(data.get('format', 'stl'))
        elif action == 'save_config':
            self._save_configuration()
        elif action == 'load_config':
            self._load_configuration()
    
    def _handle_view_control(self, event_info: Dict[str, Any]):
        """Handle 3D view control events"""
        viewer_3d = self.registry.get_module("3d_viewer")
        if not viewer_3d:
            return
        
        data = event_info.get('data', {})
        control = data.get('control')
        
        if control == 'toggle_wireframe':
            if hasattr(viewer_3d, 'toggle_wireframe'):
                wireframe = viewer_3d.toggle_wireframe()
                self.event_bus.publish("system_status_update", {
                    'message': f"Wireframe: {'ON' if wireframe else 'OFF'}",
                    'type': 'info'
                }, "3d_viewer")
        
        elif control == 'toggle_lighting':
            if hasattr(viewer_3d, 'toggle_lighting'):
                lighting = viewer_3d.toggle_lighting()
                self.event_bus.publish("system_status_update", {
                    'message': f"Lighting: {'ON' if lighting else 'OFF'}",
                    'type': 'info'
                }, "3d_viewer")
        
        elif control == 'reset_view':
            if hasattr(viewer_3d, 'reset_view'):
                viewer_3d.reset_view()
                self.event_bus.publish("system_status_update", {
                    'message': "View reset to default",
                    'type': 'info'
                }, "3d_viewer")
    
    def _handle_status_update(self, event_info: Dict[str, Any]):
        """Handle system status updates"""
        # This would update UI status displays
        pass
    
    def _handle_performance_metrics(self, event_info: Dict[str, Any]):
        """Handle performance metrics updates"""
        # This would update performance displays
        pass
    
    # MCP Command Handlers
    def _mcp_generate_ship(self, command_data: Dict[str, Any]) -> Dict[str, Any]:
        """MCP handler for ship generation"""
        try:
            ship_class = command_data.get('ship_class', 'cruiser')
            randomize = command_data.get('randomize', True)
            component_count = command_data.get('component_count')
            
            self.event_bus.publish("ship_generation_requested", {
                'ship_class': ship_class,
                'randomize': randomize,
                'component_count': component_count
            }, "mcp")
            
            return {'status': 'success', 'message': f'Generating {ship_class} ship'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def _mcp_toggle_wireframe(self, command_data: Dict[str, Any]) -> Dict[str, Any]:
        """MCP handler for wireframe toggle"""
        try:
            self.event_bus.publish("view_control", {'control': 'toggle_wireframe'}, "mcp")
            return {'status': 'success', 'message': 'Wireframe toggled'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def _mcp_toggle_lighting(self, command_data: Dict[str, Any]) -> Dict[str, Any]:
        """MCP handler for lighting toggle"""
        try:
            self.event_bus.publish("view_control", {'control': 'toggle_lighting'}, "mcp")
            return {'status': 'success', 'message': 'Lighting toggled'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def _mcp_reset_view(self, command_data: Dict[str, Any]) -> Dict[str, Any]:
        """MCP handler for view reset"""
        try:
            self.event_bus.publish("view_control", {'control': 'reset_view'}, "mcp")
            return {'status': 'success', 'message': 'View reset'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def _mcp_export_ship(self, command_data: Dict[str, Any]) -> Dict[str, Any]:
        """MCP handler for ship export"""
        try:
            format_str = command_data.get('format', 'stl')
            success = self._export_current_ship(format_str)
            
            if success:
                return {'status': 'success', 'message': f'Ship exported as {format_str.upper()}'}
            else:
                return {'status': 'error', 'message': 'Export failed'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def _mcp_get_ship_info(self, command_data: Dict[str, Any]) -> Dict[str, Any]:
        """MCP handler for ship information"""
        if self.current_ship_data:
            return {
                'status': 'success',
                'ship_info': {
                    'vertices': self.current_ship_data.get('vertices', 0),
                    'faces': self.current_ship_data.get('faces', 0),
                    'generation_time': self.current_ship_data.get('generation_time', 0.0),
                    'components': self.current_ship_data.get('components', 0)
                }
            }
        else:
            return {'status': 'error', 'message': 'No ship loaded'}
    
    def _mcp_get_system_status(self, command_data: Dict[str, Any]) -> Dict[str, Any]:
        """MCP handler for system status"""
        return {
            'status': 'success',
            'system_status': {
                'modules': self.registry.get_module_status(),
                'available_modules': self.registry.get_available_modules(),
                'uptime': time.time() - self.startup_time if self.startup_time else 0,
                'current_ship_loaded': self.current_ship_data is not None
            }
        }
    
    def _export_current_ship(self, format_str: str = 'stl') -> bool:
        """Export current ship to file"""
        if not self.current_ship_data:
            return False
        
        ship_generator = self.registry.get_module("ship_generator")
        if not ship_generator:
            return False
        
        try:
            # Create exports directory
            exports_dir = Path("exports")
            exports_dir.mkdir(exist_ok=True)
            
            # Generate filename
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"spaceship_{timestamp}"
            filepath = exports_dir / filename
            
            # Export using ship generator
            success = ship_generator.export_ship(self.current_ship_data, filepath, format_str)
            
            if success:
                self.event_bus.publish("system_status_update", {
                    'message': f"Ship exported: {filepath.with_suffix('.' + format_str)}",
                    'type': 'success'
                }, "integration")
            
            return success
            
        except Exception as e:
            print(f"Export error: {e}")
            return False
    
    def _save_configuration(self) -> bool:
        """Save current configuration"""
        if not self.current_ship_data:
            return False
        
        try:
            config_dir = Path("configs")
            config_dir.mkdir(exist_ok=True)
            
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            config_file = config_dir / f"ship_config_{timestamp}.json"
            
            success = ShipConfiguration.save_ship_config(self.current_ship_data, config_file)
            
            if success:
                self.event_bus.publish("system_status_update", {
                    'message': f"Configuration saved: {config_file}",
                    'type': 'success'
                }, "integration")
            
            return success
            
        except Exception as e:
            print(f"Config save error: {e}")
            return False
    
    def _load_configuration(self) -> bool:
        """Load configuration (placeholder for file dialog)"""
        # This would typically open a file dialog
        # For now, just return False
        self.event_bus.publish("system_status_update", {
            'message': "Configuration load not implemented",
            'type': 'warning'
        }, "integration")
        return False
    
    def start_application(self) -> bool:
        """Start the integrated application"""
        if self.is_running:
            return True
        
        try:
            self.startup_time = time.time()
            
            # Start MCP server
            mcp_server = self.registry.get_module("mcp_server")
            if mcp_server:
                mcp_success = mcp_server.start()
                if mcp_success:
                    print(f"✅ MCP server started on port {mcp_server.port}")
                    
                    self.event_bus.publish("system_status_update", {
                        'message': f"MCP server active on port {mcp_server.port}",
                        'type': 'success'
                    }, "integration")
                else:
                    print("❌ Failed to start MCP server")
            
            # Generate initial ship
            self.event_bus.publish("ship_generation_requested", {
                'ship_class': 'cruiser',
                'randomize': True
            }, "integration")
            
            self.is_running = True
            
            self.event_bus.publish("system_status_update", {
                'message': "Integrated Spaceship Designer started",
                'type': 'success'
            }, "integration")
            
            return True
            
        except Exception as e:
            print(f"Application start error: {e}")
            return False
    
    def stop_application(self):
        """Stop the integrated application"""
        if not self.is_running:
            return
        
        try:
            # Stop MCP server
            mcp_server = self.registry.get_module("mcp_server")
            if mcp_server:
                mcp_server.stop()
            
            # Clear ship generator caches
            ship_generator = self.registry.get_module("ship_generator")
            if ship_generator:
                ship_generator.clear_caches()
            
            # Cleanup 3D viewer
            viewer_3d = self.registry.get_module("3d_viewer")
            if viewer_3d and hasattr(viewer_3d, 'cleanup'):
                viewer_3d.cleanup()
            
            self.is_running = False
            
            self.event_bus.publish("system_status_update", {
                'message': "Application stopped",
                'type': 'info'
            }, "integration")
            
        except Exception as e:
            print(f"Application stop error: {e}")
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information"""
        return {
            'modules': self.registry.get_module_status(),
            'available_modules': self.registry.get_available_modules(),
            'is_running': self.is_running,
            'startup_time': self.startup_time,
            'uptime': time.time() - self.startup_time if self.startup_time else 0,
            'current_ship_loaded': self.current_ship_data is not None,
            'recent_events': self.event_bus.get_recent_events(5)
        }

# Factory function
def create_integrated_spaceship_designer() -> IntegratedSpaceshipDesigner:
    """Create integrated spaceship designer instance"""
    return IntegratedSpaceshipDesigner()

if __name__ == "__main__":
    # Demo usage
    print("🔧 SYSTEM INTEGRATION - ISOLATED MODULE TEST")
    print("=" * 50)
    
    # Create integrated system
    designer = create_integrated_spaceship_designer()
    
    # Get system info
    info = designer.get_system_info()
    
    print("📊 SYSTEM STATUS:")
    print(f"Available modules: {', '.join(info['available_modules'])}")
    
    for module, status in info['modules'].items():
        status_icon = "✅" if status == "available" else "❌"
        print(f"{status_icon} {module}: {status}")
    
    # Test application lifecycle
    print("\n🚀 TESTING APPLICATION LIFECYCLE:")
    
    if designer.start_application():
        print("✅ Application started successfully")
        
        # Wait a moment
        time.sleep(1)
        
        # Get updated info
        info = designer.get_system_info()
        print(f"✅ Uptime: {info['uptime']:.2f} seconds")
        print(f"✅ Ship loaded: {info['current_ship_loaded']}")
        
        designer.stop_application()
        print("✅ Application stopped cleanly")
    else:
        print("❌ Application start failed")
    
    print("\n✅ System integration test complete")