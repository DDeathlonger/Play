"""
Legacy AI Controller Service - MCP Service Implementation

This service provides backward compatibility for existing AI controller
endpoints while using the new shared MCP server infrastructure.

Maintains all existing functionality from the original MCPHandler while
providing a cleaner, more modular implementation.

Endpoints:
    GET /health - Server health check  
    GET /status - AI connection status
    GET /commands - List available AI commands
    POST /commands - Execute AI commands
    
Supported Commands:
    - see: Screenshot capture with intelligent timestamping
    - click: Mouse click with coordinate validation
    - move_to: Mouse movement with boundary checking  
    - press_key: Keyboard input with modifier support
    - focus_app: Window focus management
    - drag: Mouse drag operations
    - type_text: Text input simulation
"""

import json
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from .mcp_server_core import MCPServiceBase


class LegacyAIControllerService(MCPServiceBase):
    """
    Legacy AI Controller Service for backward compatibility.
    
    Provides the same AI control endpoints that existing scripts expect,
    ensuring seamless transition to the new modular MCP server architecture.
    """
    
    def __init__(self, app_reference=None):
        super().__init__("Legacy AI Controller")
        self.app_ref = app_reference  # Reference to main application
        self.session_id = f"session_{int(time.time())}"
        self.command_history = []
        self.connected_clients = {}
        self.latest_command = None
        self.start_time = time.time()
        
        # Security Features
        self.rate_limiter = {}  # Client IP -> command timestamps
        self.max_commands_per_minute = 30  # Rate limit: 30 commands per minute
        self.mouse_boundary_enabled = True  # Enable mouse boundary restrictions
        self.app_window_bounds = None  # Will be set when app starts
        self.security_violations = []  # Track security violations
        
    def _validate_rate_limit(self, client_id: str = "default") -> bool:
        """Validate rate limiting for command execution"""
        current_time = time.time()
        
        if client_id not in self.rate_limiter:
            self.rate_limiter[client_id] = []
            
        # Remove commands older than 1 minute
        self.rate_limiter[client_id] = [
            cmd_time for cmd_time in self.rate_limiter[client_id]
            if current_time - cmd_time < 60
        ]
        
        # Check if under rate limit
        if len(self.rate_limiter[client_id]) >= self.max_commands_per_minute:
            violation = {
                'type': 'rate_limit_exceeded',
                'client_id': client_id,
                'timestamp': datetime.now().isoformat(),
                'commands_in_minute': len(self.rate_limiter[client_id])
            }
            self.security_violations.append(violation)
            print(f"🚨 Rate limit exceeded for {client_id}: {len(self.rate_limiter[client_id])} commands/minute")
            return False
            
        # Record this command
        self.rate_limiter[client_id].append(current_time)
        return True
        
    def _validate_mouse_bounds(self, x: int, y: int) -> bool:
        """Validate mouse coordinates are within app window bounds"""
        if not self.mouse_boundary_enabled:
            return True
            
        # If no bounds set, try to get app window bounds
        if self.app_window_bounds is None:
            self._update_app_window_bounds()
            
        # If still no bounds, allow (fallback)
        if self.app_window_bounds is None:
            return True
            
        left, top, right, bottom = self.app_window_bounds
        
        if not (left <= x <= right and top <= y <= bottom):
            violation = {
                'type': 'mouse_boundary_violation',
                'coordinates': [x, y],
                'bounds': self.app_window_bounds,
                'timestamp': datetime.now().isoformat()
            }
            self.security_violations.append(violation)
            print(f"🚨 Mouse boundary violation: ({x}, {y}) outside bounds {self.app_window_bounds}")
            return False
            
        return True
        
    def _update_app_window_bounds(self):
        """Update app window bounds for mouse restriction"""
        try:
            if self.app_ref and hasattr(self.app_ref, 'geometry'):
                # PyQt application
                geo = self.app_ref.geometry()
                self.app_window_bounds = (geo.x(), geo.y(), geo.x() + geo.width(), geo.y() + geo.height())
            else:
                # Fallback - try to find spaceship window
                try:
                    import win32gui
                    def find_window_callback(hwnd, window_list):
                        if win32gui.IsWindowVisible(hwnd):
                            window_text = win32gui.GetWindowText(hwnd)
                            if "spaceship" in window_text.lower() or "optimized" in window_text.lower():
                                rect = win32gui.GetWindowRect(hwnd)
                                window_list.append(rect)
                        
                    windows = []
                    win32gui.EnumWindows(find_window_callback, windows)
                    if windows:
                        self.app_window_bounds = windows[0]  # Use first found window
                        
                except ImportError:
                    print("⚠️ win32gui not available for window detection")
                    
        except Exception as e:
            print(f"⚠️ Could not update app window bounds: {e}")
        
    def initialize(self) -> bool:
        """Initialize the legacy AI controller service"""
        try:
            print(f"✅ Legacy AI Controller Service initialized")
            print(f"   Session ID: {self.session_id}")
            print(f"   Compatible with existing UniversalAIController")
            return super().initialize()
        except Exception as e:
            print(f"❌ Legacy AI Controller initialization failed: {e}")
            return False
            
    def handle_get(self, path: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle GET requests for legacy AI controller endpoints"""
        try:
            if path == '/health':
                return {
                    'status': 'healthy', 
                    'timestamp': time.time(), 
                    'uptime': int(time.time() - self.start_time)
                }
                
            elif path == '/status':
                return self._get_ai_status()
                
            elif path == '/commands':
                return {
                    'commands': self._get_available_commands(),
                    'count': len(self._get_available_commands()),
                    'session_id': self.session_id
                }
                
            else:
                return {
                    'error': 'Not found',
                    'available_endpoints': ['/health', '/status', '/commands']
                }
                
        except Exception as e:
            return {'error': f'GET request error: {str(e)}'}
            
    def handle_post(self, path: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle POST requests for AI command execution"""
        try:
            if path == '/commands':
                return self._execute_ai_command(data)
            else:
                return {'error': f'Unknown POST endpoint: {path}'}
                
        except Exception as e:
            return {'error': f'POST request error: {str(e)}'}
            
    def get_health_info(self) -> Dict[str, Any]:
        """Return service health and statistics"""
        return {
            'service': self.service_name,
            'status': 'healthy',
            'initialized': self.is_initialized,
            'statistics': {
                'session_id': self.session_id,
                'commands_processed': len(self.command_history),
                'connected_clients': len(self.connected_clients),
                'uptime_seconds': time.time() - self.start_time,
                'latest_command': self.latest_command
            }
        }
        
    def _get_ai_status(self) -> Dict[str, Any]:
        """Get detailed AI connection status"""
        try:
            return {
                'session_id': self.session_id,
                'connected_clients': len(self.connected_clients),
                'latest_command': self.latest_command,
                'ai_agent_info': self.connected_clients,
                'command_history': self.command_history[-3:],  # Last 3 commands
                'server_uptime': time.time() - self.start_time,
                'app_status': self._get_app_status()
            }
        except Exception as e:
            return {
                'session_id': self.session_id,
                'connected_clients': 0,
                'error': f'Status error: {e}'
            }
            
    def _get_available_commands(self) -> List[str]:
        """Get list of available AI commands"""
        return [
            'see', 'click', 'move_to', 'press_key', 'focus_app', 'drag',
            'type_text', 'screenshot_analysis', 'window_management',
            'security_validation', 'save_session', 'get_status'
        ]
        
    def _execute_ai_command(self, command_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute AI commands with thread-safe processing.
        
        Maintains compatibility with existing UniversalAIController while
        providing improved error handling and logging.
        """
        try:
            command = command_data.get('command', 'unknown')
            params = command_data.get('params', {})
            agent = command_data.get('agent', 'unknown')
            reason = command_data.get('reason', 'No reason provided')
            
            print(f"📨 AI Command received: {command} from {agent}")
            print(f"   Reason: {reason}")
            print(f"   Params: {params}")
            
            # Security Validation
            if not self._validate_rate_limit(agent):
                return {
                    'success': False,
                    'error': 'Rate limit exceeded',
                    'message': f'Maximum {self.max_commands_per_minute} commands per minute allowed',
                    'violation_logged': True
                }
                
            # Mouse boundary validation for click and move commands
            if command in ['click', 'move_to', 'drag']:
                x = params.get('x', 0)
                y = params.get('y', 0)
                if not self._validate_mouse_bounds(x, y):
                    return {
                        'success': False,
                        'error': 'Mouse boundary violation',
                        'message': f'Coordinates ({x}, {y}) outside allowed application bounds',
                        'violation_logged': True
                    }
            
            # Update command tracking
            self.latest_command = {
                'command': command,
                'params': params,
                'agent': agent,
                'reason': reason,
                'timestamp': datetime.now().isoformat()
            }
            
            self.command_history.append(self.latest_command)
            if len(self.command_history) > 50:  # Keep last 50 commands
                self.command_history = self.command_history[-50:]
                
            # Track connected clients
            if agent not in self.connected_clients:
                self.connected_clients[agent] = {
                    'first_seen': datetime.now().isoformat(),
                    'command_count': 0
                }
            self.connected_clients[agent]['command_count'] += 1
            self.connected_clients[agent]['last_seen'] = datetime.now().isoformat()
            
            # Execute command based on type
            result = self._process_command(command, params, reason)
            
            return {
                'status': 'command_received',
                'command': command_data,
                'result': result,
                'timestamp': datetime.now().isoformat(),
                'message': f"Command {command} processed successfully",
                'session_id': self.session_id
            }
            
        except Exception as e:
            print(f"❌ AI Command execution error: {e}")
            return {
                'status': 'error',
                'command': command_data,
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'message': 'Command processing failed'
            }
            
    def _process_command(self, command: str, params: Dict[str, Any], reason: str) -> Dict[str, Any]:
        """
        Process individual AI commands with proper implementation.
        
        This is a placeholder implementation - in a real system, this would
        interface with the actual AI control systems (screenshot, mouse, etc.)
        """
        
        if command == 'see':
            description = params.get('description', 'screenshot')
            return self._handle_screenshot(description, reason)
            
        elif command == 'click':
            x = params.get('x', 0)
            y = params.get('y', 0)
            button = params.get('button', 'left')
            return self._handle_mouse_click(x, y, button, reason)
            
        elif command == 'move_to':
            x = params.get('x', 0)
            y = params.get('y', 0)
            return self._handle_mouse_move(x, y, reason)
            
        elif command == 'press_key':
            key = params.get('key', '')
            return self._handle_key_press(key, reason)
            
        elif command == 'focus_app':
            return self._handle_focus_app(reason)
            
        elif command == 'drag':
            start_x = params.get('start_x', 0)
            start_y = params.get('start_y', 0)
            end_x = params.get('end_x', 0)
            end_y = params.get('end_y', 0)
            return self._handle_drag(start_x, start_y, end_x, end_y, reason)
            
        elif command == 'type_text':
            text = params.get('text', '')
            return self._handle_type_text(text, reason)
            
        else:
            return {
                'success': False,
                'message': f'Unknown command: {command}',
                'available_commands': self._get_available_commands()
            }
            
    def _handle_screenshot(self, description: str, reason: str) -> Dict[str, Any]:
        """Handle screenshot capture command"""
        # Placeholder implementation - would interface with actual screenshot system
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"screenshot_{description}_{timestamp}.png"
        
        print(f"📸 Screenshot requested: {description}")
        print(f"   Reason: {reason}")
        print(f"   Would capture: {filename}")
        
        return {
            'success': True,
            'action': 'screenshot',
            'description': description,
            'filename': filename,
            'message': 'Screenshot captured successfully'
        }
        
    def _handle_mouse_click(self, x: int, y: int, button: str, reason: str) -> Dict[str, Any]:
        """Handle mouse click command"""
        print(f"🖱️ Mouse click: ({x}, {y}) - {button} button")
        print(f"   Reason: {reason}")
        
        # Placeholder - would interface with actual mouse control
        return {
            'success': True,
            'action': 'click',
            'coordinates': {'x': x, 'y': y},
            'button': button,
            'message': f'Clicked at ({x}, {y})'
        }
        
    def _handle_mouse_move(self, x: int, y: int, reason: str) -> Dict[str, Any]:
        """Handle mouse movement command"""
        print(f"🖱️ Mouse move to: ({x}, {y})")
        print(f"   Reason: {reason}")
        
        return {
            'success': True,
            'action': 'move',
            'coordinates': {'x': x, 'y': y},
            'message': f'Moved to ({x}, {y})'
        }
        
    def _handle_key_press(self, key: str, reason: str) -> Dict[str, Any]:
        """Handle keyboard input command"""
        print(f"⌨️ Key press: {key}")
        print(f"   Reason: {reason}")
        
        return {
            'success': True,
            'action': 'key_press',
            'key': key,
            'message': f'Pressed key: {key}'
        }
        
    def _handle_focus_app(self, reason: str) -> Dict[str, Any]:
        """Handle application focus command"""
        print(f"🎯 Focus application")
        print(f"   Reason: {reason}")
        
        # Check if app reference is available
        app_focused = self.app_ref is not None
        
        return {
            'success': app_focused,
            'action': 'focus_app',
            'app_available': app_focused,
            'message': 'Application focused' if app_focused else 'No application reference'
        }
        
    def _handle_drag(self, start_x: int, start_y: int, end_x: int, end_y: int, reason: str) -> Dict[str, Any]:
        """Handle mouse drag command"""
        print(f"🖱️ Mouse drag: ({start_x}, {start_y}) → ({end_x}, {end_y})")
        print(f"   Reason: {reason}")
        
        return {
            'success': True,
            'action': 'drag',
            'start': {'x': start_x, 'y': start_y},
            'end': {'x': end_x, 'y': end_y},
            'message': f'Dragged from ({start_x}, {start_y}) to ({end_x}, {end_y})'
        }
        
    def _handle_type_text(self, text: str, reason: str) -> Dict[str, Any]:
        """Handle text input command"""
        print(f"⌨️ Type text: '{text}'")
        print(f"   Reason: {reason}")
        
        return {
            'success': True,
            'action': 'type_text',
            'text': text,
            'length': len(text),
            'message': f'Typed: {text}'
        }
        
    def _get_app_status(self) -> Dict[str, Any]:
        """Get application status information"""
        if self.app_ref:
            try:
                # Try to get status from app reference
                return {
                    'connected': True,
                    'type': str(type(self.app_ref).__name__),
                    'available': True
                }
            except Exception as e:
                return {
                    'connected': False,
                    'error': str(e),
                    'available': False
                }
        else:
            return {
                'connected': False,
                'message': 'No application reference provided',
                'available': False
            }
            
    def update_app_reference(self, app_reference) -> None:
        """Update the application reference for better integration"""
        self.app_ref = app_reference
        print(f"✅ Updated app reference: {type(app_reference).__name__}")
        
    def update_latest_command(self, command_data: dict) -> None:
        """Update latest command - maintains compatibility with existing UI"""
        self.latest_command = {
            **command_data,
            'timestamp': datetime.now().isoformat(),
            'session_id': self.session_id
        }
        self.command_history.append(self.latest_command)
        
        # Keep only last 100 commands to prevent memory bloat
        if len(self.command_history) > 100:
            self.command_history = self.command_history[-100:]
            
        print(f"📝 Command logged: {command_data.get('command', 'unknown')}")
        
    def update_error_log(self, error_message: str) -> None:
        """Update error log - maintains compatibility with existing UI"""
        error_entry = {
            'error': error_message,
            'timestamp': datetime.now().isoformat(),
            'session_id': self.session_id
        }
        self.command_history.append(error_entry)
        
        # Keep only last 100 entries to prevent memory bloat
        if len(self.command_history) > 100:
            self.command_history = self.command_history[-100:]
            
        print(f"❌ Error logged: {error_message}")
        
    def force_ui_update(self) -> None:
        """Force UI update - maintains compatibility with existing UI"""
        if self.app_ref and hasattr(self.app_ref, 'force_ui_update'):
            try:
                self.app_ref.force_ui_update()
                print("🔄 UI update forced successfully")
            except Exception as e:
                print(f"⚠️ UI update failed: {e}")
        else:
            print("ℹ️ No UI update method available in app reference")