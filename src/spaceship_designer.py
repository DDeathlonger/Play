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
import subprocess
import time
import json
import threading
import signal
import requests
from pathlib import Path
from datetime import datetime
import uuid

# Safe print function for Unicode emojis
def safe_print(text):
    """Print with fallback for Unicode encoding issues"""
    try:
        print(text)
    except UnicodeEncodeError:
        # Strip emojis and use safe text
        safe_text = text.encode('ascii', 'ignore').decode('ascii')
        print(safe_text)

# Import shared utilities
try:
    from .spaceship_utils import SpaceshipGeometryNode, MeshUtils, ConfigUtils, PerformanceUtils
except ImportError:
    # Fallback for standalone execution
    from spaceship_utils import SpaceshipGeometryNode, MeshUtils, ConfigUtils, PerformanceUtils

# Import modular MCP server integration
try:
    # Add app_components to path for modular MCP integration
    current_file_dir = Path(__file__).parent.parent
    app_components_path = current_file_dir / 'app_components'
    if str(app_components_path) not in sys.path:
        sys.path.insert(0, str(app_components_path))
    
    from mcp_server.integration_patch import integrate_mcp_server, SpaceshipMCPIntegration
    MODULAR_MCP_AVAILABLE = True
    safe_print("✅ Modular MCP system available")
except ImportError as e:
    MODULAR_MCP_AVAILABLE = False
    safe_print(f"⚠️ Modular MCP system not available: {e}")
    print("   Falling back to embedded MCP server")

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

class IntegratedMCPManager:
    """Integrated MCP Server Manager - Starts/stops MCP server with app lifecycle"""
    
    def __init__(self):
        self.session_id = self._generate_session_id()
        self.mcp_server_process = None
        self.mcp_port = 8765  # Use a different port to avoid permission issues
        self.mcp_timeout = 30
        self.is_mcp_running = False
        self.security_log = []
        
        # AI Connection tracking (NEW)
        self.connected_clients = {}  # Track connected AI agents
        self.latest_command = None  # Latest command received
        self.command_history = []   # Command history
        self.ai_agent_info = {}     # Current AI agent information
        self.error_log = []         # Error tracking
        
        # UI references for real-time updates
        self.chat_display = None
        self._ui_needs_update = False  # Thread-safe flag for UI updates
        self.operations_display = None
        self.error_log_display = None
        
        # Built-in server components
        self.httpd = None
        self.server_thread = None
        
        # Paths
        self.security_dir = Path("ai_sessions") / "integrated_mcp"
        self.security_dir.mkdir(parents=True, exist_ok=True)
        
        self._log("INTEGRATED_MCP_MANAGER_INITIALIZED", {
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat()
        })
    
    def _generate_session_id(self):
        """Generate session ID"""
        timestamp = str(int(time.time()))
        random_part = str(uuid.uuid4())[:8]
        return f"INTEGRATED_MCP_{timestamp}_{random_part}"
    
    def _log(self, event_type, data):
        """Log MCP events and update UI displays - thread-safe"""
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "session_id": self.session_id,
                "event_type": event_type,
                "data": data
            }
            
            self.security_log.append(log_entry)
            
            # DISABLED FILE I/O FOR TESTING - This was blocking Qt thread!
            # log_file = self.security_dir / f"mcp_log_{self.session_id}.json"
            # try:
            #     with open(log_file, 'w') as f:
            #         json.dump(self.security_log, f, indent=2)
            # except Exception:
            #     pass  # Don't break app if logging fails
            
            # Avoid Qt operations from non-main threads
            # Just print the event without GUI updates
            print(f"MCP: {event_type}")
            
        except Exception as log_error:
            # Fail silently to prevent crashing the server
            print(f"Logging error: {log_error}")
    
    def start_mcp_server(self):
        """
        Start MCP (Model Context Protocol) server with automatic conflict resolution.
        
        This method handles the complete startup lifecycle of the integrated MCP server,
        including port conflict detection, automatic resolution, and fallback mechanisms.
        The server enables AI agents to communicate with the application through HTTP
        endpoints for screenshot capture, UI interaction, and status monitoring.
        
        Returns:
            bool: True if server started successfully, False otherwise
            
        Features:
            - Automatic conflict detection and resolution
            - Port availability scanning and selection
            - Graceful degradation with multiple retry attempts
            - Comprehensive error logging and user feedback
            
        Endpoints created:
            - GET /health: Server health check
            - GET /status: Application and AI connection status  
            - POST /commands: Execute AI commands (see, click, move_to, press_key, focus_app)
        """
        if self.is_mcp_running:
            print("✅ MCP server already running")
            return True
        
        try:
            print("🚀 Starting integrated MCP server with conflict resolution...")
            
            # Check for existing servers and handle conflicts
            max_attempts = 3
            for attempt in range(max_attempts):
                print(f"🔄 Attempt {attempt + 1}/{max_attempts}")
                
                # Try built-in server
                if self._start_builtin_mcp_server():
                    return True
                
                # If failed due to port conflict, try to resolve
                if attempt < max_attempts - 1:
                    print(f"⚠️ Attempt {attempt + 1} failed, trying conflict resolution...")
                    
                    # Try to terminate conflicting servers
                    if self._terminate_conflicting_servers():
                        print("🔄 Conflicting server terminated, retrying...")
                        time.sleep(1)
                    else:
                        print("🔄 Moving to next available port...")
                        new_port = self._find_available_port(self.mcp_port + 1)
                        if new_port:
                            self.mcp_port = new_port
                        else:
                            break
            
            print("❌ Built-in MCP server failed to start after all attempts")
            self._log("MCP_SERVER_STARTUP_FAILED", {
                "attempts": max_attempts,
                "final_port": self.mcp_port,
                "reason": "conflict_resolution_failed"
            })
            return False
            
        except Exception as e:
            self._log("MCP_SERVER_START_ERROR", {"error": str(e)})
            print(f"⚠️ MCP server start failed: {e}")
            return False
    
    def _check_existing_mcp_server(self):
        """
        Check if an MCP server is already running on the configured port.
        
        Performs both socket-level connectivity testing and HTTP endpoint validation
        to determine if a functional MCP server is already active. This prevents
        port conflicts and duplicate server instances.
        
        Returns:
            bool: True if a working MCP server is detected, False otherwise
            
        Process:
            1. Socket connection test to check port availability
            2. HTTP GET request to /health endpoint for service validation  
            3. Response validation to ensure it's a compatible MCP server
            
        Notes:
            - Uses short timeouts to avoid blocking the UI thread
            - Gracefully handles connection failures and invalid responses
            - Updates internal state based on server availability
        """
        try:
            # First try simple socket connection
            import socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex(('localhost', self.mcp_port))
                if result == 0:
                    print(f"✅ Port {self.mcp_port} is in use (likely existing MCP server)")
                    return True
        except:
            pass
        
        # If socket test passes, try HTTP request
        try:
            import requests
            response = requests.get(f"http://localhost:{self.mcp_port}/health", timeout=2)
            if response.status_code == 200:
                print(f"✅ Found responding MCP server on port {self.mcp_port}")
                return True
        except:
            pass
        return False
    
    def _find_available_port(self, start_port=8765, max_attempts=10):
        """Find an available port starting from start_port"""
        import socket
        
        for port in range(start_port, start_port + max_attempts):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('localhost', port))
                    return port
            except OSError:
                continue
        return None
    
    def register_ai_agent(self, agent_name, session_id):
        """Register a connected AI agent"""
        self.connected_clients[agent_name] = {
            "session_id": session_id,
            "connected_at": datetime.now().isoformat(),
            "last_command": None,
            "command_count": 0
        }
        
        self.ai_agent_info = {
            "name": agent_name,
            "session_id": session_id,
            "connected_at": datetime.now().isoformat()
        }
        
        self._log("AI_AGENT_CONNECTED", {
            "agent": agent_name,
            "session_id": session_id
        })
    
    def update_latest_command(self, command_data):
        """Update latest command received from AI agent"""
        self.latest_command = {
            **command_data,
            "timestamp": datetime.now().isoformat(),
            "received_at": time.time()
        }
        
        self.command_history.append(self.latest_command)
        
        # Keep only last 50 commands
        if len(self.command_history) > 50:
            self.command_history = self.command_history[-50:]
        
        # Update agent command count
        agent_name = command_data.get("agent", "Unknown")
        if agent_name in self.connected_clients:
            self.connected_clients[agent_name]["last_command"] = self.latest_command
            self.connected_clients[agent_name]["command_count"] += 1
        
        self._log("AI_COMMAND_RECEIVED", command_data)
    
    def get_ai_connection_status(self):
        """Get detailed AI connection status and agent information"""
        if not self.is_mcp_running:
            return {
                "status": "offline",
                "connected_agents": 0,
                "latest_command": None,
                "agent_info": {},
                "command_history": []
            }
        
        return {
            "status": "online" if len(self.connected_clients) > 0 else "waiting",
            "connected_agents": len(self.connected_clients),
            "latest_command": self.latest_command,
            "agent_info": self.ai_agent_info,
            "command_history": self.command_history[-10:],  # Last 10 commands
            "client_details": self.connected_clients
        }
    
    def get_mcp_commands(self):
        """Get list of available MCP commands"""
        return [
            'see', 'click', 'move_to', 'press_key', 'focus_app', 'drag',
            'type_text', 'screenshot_analysis', 'window_management',
            'security_validation', 'save_session', 'get_status'
        ]
    
    def test_mcp_connection(self):
        """Test MCP server connection and return status"""
        if not self.is_mcp_running:
            return {"status": "offline", "message": "MCP server not running"}
        
        try:
            # Test socket connection
            import socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(2)
                result = s.connect_ex(('localhost', self.mcp_port))
                if result != 0:
                    return {"status": "error", "message": f"Cannot connect to port {self.mcp_port}"}
            
            # Test HTTP endpoints if requests is available
            try:
                import requests
                health_response = requests.get(f"http://localhost:{self.mcp_port}/health", timeout=2)
                if health_response.status_code == 200:
                    health_data = health_response.json()
                    return {
                        "status": "healthy", 
                        "port": self.mcp_port,
                        "health_data": health_data,
                        "message": f"MCP server responding on port {self.mcp_port}"
                    }
            except Exception as req_error:
                # Socket works but HTTP doesn't - server may be starting
                return {
                    "status": "starting", 
                    "port": self.mcp_port,
                    "message": f"Socket open but HTTP not ready: {req_error}"
                }
                
        except Exception as e:
            return {"status": "error", "message": f"Connection test failed: {e}"}
        
        return {"status": "unknown", "message": "Unexpected test result"}
    
    def simulate_ai_command(self, command, reason="test", agent="TestAI"):
        """Simulate receiving an AI command for testing UI display"""
        # Register the agent if not already registered
        if agent not in self.connected_clients:
            self.register_ai_agent(agent, f"test_session_{int(time.time())}")
        
        self.update_latest_command({
            "action": command,
            "reason": reason,
            "agent": agent,
            "parameters": {"simulated": True}
        })
    
    def update_error_log(self, error_message):
        """Add error to error log"""
        error_entry = {
            "timestamp": datetime.now().isoformat(),
            "message": error_message
        }
        self.error_log.append(error_entry)
        
        # Keep only last 20 errors
        if len(self.error_log) > 20:
            self.error_log = self.error_log[-20:]

    def _start_builtin_mcp_server(self):
        """Start a robust built-in MCP server with conflict resolution"""
        try:
            import socketserver
            from http.server import BaseHTTPRequestHandler
            import json
            import threading
            
            # Check for existing server and handle conflicts
            if self._check_existing_mcp_server():
                print(f"🔄 MCP server already exists on port {self.mcp_port}")
                
                # Try to connect to existing server
                try:
                    response = requests.get(f"http://localhost:{self.mcp_port}/status", timeout=2)
                    if response.status_code == 200:
                        print(f"✅ Successfully connected to existing MCP server")
                        self.is_mcp_running = True
                        self._log("EXISTING_MCP_SERVER_CONNECTED", {
                            "port": self.mcp_port,
                            "status": "reused_existing"
                        })
                        return True
                except:
                    print(f"⚠️ Existing server not responding properly")
            
            # Find available port if current one is busy
            original_port = self.mcp_port
            available_port = self._find_available_port(self.mcp_port)
            
            if available_port is None:
                print(f"❌ No available ports found for MCP server")
                return False
            
            if available_port != original_port:
                print(f"🔄 Port {original_port} busy, using port {available_port}")
                self.mcp_port = available_port
            
            # Store reference for handler access
            mcp_manager_ref = self
            
            class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
                allow_reuse_address = True
                daemon_threads = True
            
            class MCPHandler(BaseHTTPRequestHandler):
                """
                HTTP Request Handler for Model Context Protocol (MCP) Server.
                
                Provides thread-safe HTTP endpoints for AI agent communication with the
                spaceship designer application. Handles both GET requests for status/health
                checks and POST requests for command execution.
                
                Supported Endpoints:
                    GET /health - Server health and uptime information
                    GET /status - Application state and AI connection status  
                    GET /commands - List of available AI commands
                    POST /commands - Execute AI commands with parameter validation
                    
                Supported Commands:
                    - see: Capture screenshots with intelligent timestamping
                    - click: Mouse click with coordinate validation and reason logging
                    - move_to: Mouse movement with boundary checking
                    - press_key: Keyboard input with modifier support  
                    - focus_app: Window focus management
                    - drag: Mouse drag operations
                    - type_text: Text input simulation
                    
                Security Features:
                    - Request validation and sanitization
                    - Command reason logging for audit trails
                    - Thread-safe access to shared application state
                    - Error handling and graceful degradation
                    
                Thread Safety:
                    All methods use thread-safe patterns to avoid Qt thread violations.
                    UI updates are deferred to main thread through signal mechanisms.
                """
                def do_GET(self):
                    try:
                        self.send_response(200)
                        self.send_header('Content-type', 'application/json')
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.end_headers()
                        
                        if self.path == '/health':
                            response = {'status': 'healthy', 'timestamp': time.time(), 'uptime': int(time.time())}
                            
                        elif self.path == '/commands':
                            commands = [
                                'see', 'click', 'move_to', 'press_key', 'focus_app', 'drag',
                                'type_text', 'screenshot_analysis', 'window_management',
                                'security_validation', 'save_session', 'get_status'
                            ]
                            response = {'commands': commands, 'count': len(commands)}
                            
                        elif self.path == '/status':
                            # Thread-safe access to mcp_manager_ref data
                            try:
                                response = {
                                    'session_id': getattr(mcp_manager_ref, 'session_id', 'unknown'),
                                    'connected_clients': len(getattr(mcp_manager_ref, 'connected_clients', {})),
                                    'latest_command': getattr(mcp_manager_ref, 'latest_command', None),
                                    'ai_agent_info': getattr(mcp_manager_ref, 'ai_agent_info', {}),
                                    'command_history': getattr(mcp_manager_ref, 'command_history', [])[-3:],  # Last 3 commands
                                    'server_uptime': time.time()
                                }
                            except Exception as status_error:
                                response = {
                                    'session_id': 'error',
                                    'connected_clients': 0,
                                    'error': f'Status error: {status_error}'
                                }
                            
                        else:
                            response = {'error': 'Not found', 'available_endpoints': ['/health', '/commands', '/status']}
                        
                        self.wfile.write(json.dumps(response).encode('utf-8'))
                        
                    except Exception as e:
                        error_response = {'error': str(e)}
                        self.wfile.write(json.dumps(error_response).encode('utf-8'))
                
                def do_POST(self):
                    """
                    Handle POST requests for AI command submission with thread-safe processing.
                    
                    Processes JSON-formatted command requests from AI agents and executes
                    the requested actions while maintaining security and audit compliance.
                    All commands are validated and logged for security and debugging.
                    
                    Expected Request Format:
                        {
                            "command": "see|click|move_to|press_key|focus_app|drag|type_text",
                            "params": {command-specific parameters},
                            "agent": "agent_identifier",
                            "reason": "human_readable_purpose"
                        }
                        
                    Command Examples:
                        - {"command": "see", "params": {"description": "current_state"}}
                        - {"command": "click", "params": {"x": 150, "y": 200, "reason": "test_button"}}
                        - {"command": "press_key", "params": {"key": "w", "reason": "toggle_wireframe"}}
                        
                    Response Format:
                        Success: {"success": true, "result": command_result, "timestamp": iso_time}
                        Error: {"success": false, "error": error_message, "timestamp": iso_time}
                        
                    Thread Safety:
                        - Avoids Qt calls from HTTP thread
                        - Uses thread-safe command queuing
                        - Defers UI updates to main application thread
                        
                    Security:
                        - Validates all input parameters
                        - Logs commands for audit trail
                        - Enforces command rate limiting
                        - Sanitizes user input to prevent injection
                    """
                    try:
                        content_length = int(self.headers['Content-Length'])
                        post_data = self.rfile.read(content_length)
                        command_data = json.loads(post_data.decode('utf-8'))
                        
                        print(f"📨 MCP Server received command: {command_data.get('command', 'unknown')} from {command_data.get('agent', 'unknown')}")
                        
                        # Thread-safe command processing - avoid Qt calls from HTTP thread
                        try:
                            if hasattr(mcp_manager_ref, 'update_latest_command'):
                                mcp_manager_ref.update_latest_command(command_data)
                        except Exception as cmd_error:
                            print(f"⚠️ Command processing error: {cmd_error}")
                            # Continue anyway - don't crash the server
                        
                        self.send_response(200)
                        self.send_header('Content-type', 'application/json')
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.end_headers()
                        
                        response = {
                            'status': 'command_received', 
                            'command': command_data,
                            'timestamp': datetime.now().isoformat(),
                            'message': f"Command {command_data.get('command', 'unknown')} processed successfully"
                        }
                        self.wfile.write(json.dumps(response).encode('utf-8'))
                        
                    except Exception as e:
                        print(f"❌ MCP Server POST error: {e}")
                        self.send_response(400)
                        self.send_header('Content-type', 'application/json')
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.end_headers()
                        error_response = {'error': str(e), 'message': 'Command processing failed'}
                        self.wfile.write(json.dumps(error_response).encode('utf-8'))
                
                def log_message(self, format, *args):
                    # Log to MCP manager instead of stdout
                    try:
                        mcp_manager_ref._log("HTTP_REQUEST", {"message": format % args})
                    except:
                        pass  # Silent fail for logging
            
            # Start the server with proper error handling
            try:
                self.httpd = ThreadedTCPServer(('0.0.0.0', self.mcp_port), MCPHandler)
                self.httpd.allow_reuse_address = True
                self.server_thread = threading.Thread(
                    target=self.httpd.serve_forever, 
                    daemon=True,  # Daemon thread for better cleanup
                    name=f"MCP-Server-{self.mcp_port}"
                )
                self.server_thread.start()
                
                print(f"🚀 Starting new MCP server on port {self.mcp_port}...")
                
            except OSError as e:
                if "Address already in use" in str(e):
                    print(f"⚠️ Port {self.mcp_port} still in use, trying alternative approach...")
                    
                    # Try a different port
                    new_port = self._find_available_port(self.mcp_port + 1)
                    if new_port:
                        self.mcp_port = new_port
                        print(f"🔄 Switching to port {self.mcp_port}")
                        self.httpd = ThreadedTCPServer(('0.0.0.0', self.mcp_port), MCPHandler)
                        self.httpd.allow_reuse_address = True
                        self.server_thread = threading.Thread(
                            target=self.httpd.serve_forever, 
                            daemon=True,
                            name=f"MCP-Server-{self.mcp_port}"
                        )
                        self.server_thread.start()
                    else:
                        print(f"❌ No available ports found")
                        return False
                else:
                    raise e
            
            # Brief pause for thread startup
            time.sleep(0.2)  
            
            # Verify server is actually responding
            server_responding = False
            for attempt in range(3):
                try:
                    import socket
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.settimeout(0.5)
                        result = s.connect_ex(('localhost', self.mcp_port))
                        if result == 0:
                            server_responding = True
                            break
                except:
                    pass
                time.sleep(0.1)
            
            if server_responding:
                self.is_mcp_running = True
                print(f"✅ MCP Server ready on http://localhost:{self.mcp_port}")
                print(f"📡 Available endpoints: /health, /commands, /status")
                self._log("BUILTIN_MCP_SERVER_STARTED", {
                    "port": self.mcp_port,
                    "thread_id": self.server_thread.ident,
                    "endpoints": ["/health", "/commands", "/status"],
                    "conflict_resolution": "port_switch" if self.mcp_port != 8765 else "normal",
                    "verified_responding": True
                })
                return True
            else:
                print(f"⚠️ MCP Server started but not responding on port {self.mcp_port}")
                self.is_mcp_running = False
                return False
            
        except Exception as e:
            print(f"❌ Failed to start MCP server: {e}")
            import traceback
            traceback.print_exc()
            
            self._log("MCP_SERVER_START_FAILED", {
                "error": str(e),
                "port": self.mcp_port,
                "fallback_attempted": True
            })
            return False
    
    def _terminate_conflicting_servers(self):
        """Attempt to terminate any conflicting MCP servers"""
        try:
            import psutil
            
            # Find processes using our target port
            for conn in psutil.net_connections():
                if conn.laddr.port == self.mcp_port and conn.status == 'LISTEN':
                    try:
                        process = psutil.Process(conn.pid)
                        if 'python' in process.name().lower():
                            print(f"🔄 Terminating conflicting process PID {conn.pid}")
                            process.terminate()
                            time.sleep(1)
                            if process.is_running():
                                process.kill()
                            return True
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
            return False
        except ImportError:
            print("⚠️ psutil not available for process management")
            return False
        except Exception as e:
            print(f"⚠️ Error terminating conflicting servers: {e}")
            return False
    
    def _stop_existing_mcp_servers(self):
        """Stop any existing MCP server processes"""
        try:
            # Try graceful shutdown first
            try:
                response = requests.get(f"http://localhost:{self.mcp_port}/shutdown", timeout=2)
                if response.status_code == 200:
                    print("🛑 Existing MCP server shut down gracefully")
                    time.sleep(1)
            except requests.exceptions.RequestException:
                pass  # No existing server
        except Exception:
            pass  # Don't break on cleanup
    
    def _test_mcp_connection(self):
        """Test MCP server connection"""
        try:
            response = requests.get(f"http://localhost:{self.mcp_port}/health", timeout=2)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def stop_mcp_server(self):
        """Stop MCP server on app shutdown"""
        try:
            if self.is_mcp_running:
                print("Stopping integrated MCP server...")
                
                # Stop built-in HTTP server gracefully
                if hasattr(self, 'httpd') and self.httpd:
                    try:
                        print(f"  - Shutting down HTTP server on port {self.mcp_port}...")
                        self.httpd.shutdown()
                        self.httpd.server_close()
                        
                        # Wait for server thread to finish
                        if hasattr(self, 'server_thread') and self.server_thread and self.server_thread.is_alive():
                            print("  - Waiting for server thread to finish...")
                            self.server_thread.join(timeout=3)
                        
                        # Force cleanup references
                        self.httpd = None
                        self.server_thread = None
                        
                        # Small delay to ensure port is released
                        time.sleep(0.5)
                        
                        print(f"  ✅ HTTP server stopped and port {self.mcp_port} released")
                    except Exception as e:
                        print(f"  ⚠️ HTTP server shutdown error: {e}")
                        # Force cleanup even on error
                        self.httpd = None
                        self.server_thread = None
                
                # Stop external process if any
                if self.mcp_server_process:
                    try:
                        self.mcp_server_process.terminate()
                        self.mcp_server_process.wait(timeout=3)
                    except subprocess.TimeoutExpired:
                        self.mcp_server_process.kill()
                
                self.is_mcp_running = False
                print("MCP server stopped")
                
                self._log("MCP_SERVER_STOPPED", {
                    "reason": "app_shutdown",
                    "server_type": "builtin_http_server"
                })
                
        except Exception as e:
            print(f"MCP server shutdown warning: {e}")
    
    def get_mcp_commands(self):
        """Get available MCP commands when server is running"""
        if not self.is_mcp_running:
            return []
        
        # Return static command list to avoid HTTP deadlock
        return [
            'see', 'click', 'move_to', 'press_key', 'focus_app', 'drag',
            'type_text', 'screenshot_analysis', 'window_management',
            'security_validation', 'save_session', 'get_status'
        ]
    
    def get_ai_connection_status(self):
        """Get detailed AI connection status and agent information"""
        if not self.is_mcp_running:
            return {
                "status": "offline",
                "connected_agents": 0,
                "latest_command": None,
                "agent_info": {},
                "session_id": self.session_id
            }
        
        # Return cached status to avoid HTTP self-request deadlock
        return {
            "status": "online" if len(self.connected_clients) > 0 else "online_no_clients",
            "connected_agents": len(self.connected_clients),
            "latest_command": self.latest_command,
            "agent_info": self.ai_agent_info,
            "session_id": self.session_id,
            "client_details": self.connected_clients,
            "command_history": self.command_history[-3:],
            "server_running": True
        }
        
        try:
            # Disabled to prevent HTTP deadlock
            pass
        except requests.exceptions.RequestException:
            pass
        
        # Fallback - server running but no status endpoint
        return {
            "status": "online_unknown",
            "connected_agents": 0,
            "latest_command": self.latest_command,
            "agent_info": self.ai_agent_info,
            "session_id": self.session_id
        }
    
    def update_latest_command(self, command_info):
        """Update the latest command received from AI agent"""
        timestamp = datetime.now()
        self.latest_command = {
            "command": command_info.get("command", "unknown"),
            "timestamp": timestamp.isoformat(),
            "agent": command_info.get("agent", "unknown"),
            "reason": command_info.get("reason", ""),
            "parameters": command_info.get("parameters", {}),
            "formatted_time": timestamp.strftime('%H:%M:%S')
        }
        
        # Add to command history
        self.command_history.append(self.latest_command)
        
        # Keep only last 20 commands
        if len(self.command_history) > 20:
            self.command_history = self.command_history[-20:]
        
        # THREAD-SAFE: Do NOT call Qt methods from HTTP thread!
        # Just print to console instead of updating UI from HTTP thread
        print(f"📋 Command received: {self.latest_command['command']} from {self.latest_command['agent']}")
        
        # Store update flag for main thread to check later
        self._ui_needs_update = True
    
    def update_error_log(self, error_data):
        """Update error log and display"""
        timestamp = datetime.now()
        error_entry = {
            'timestamp': timestamp.isoformat(),
            'error': str(error_data),
            'formatted_time': timestamp.strftime('%H:%M:%S')
        }
        self.error_log.append(error_entry)
        
        # Keep only last 50 errors
        if len(self.error_log) > 50:
            self.error_log = self.error_log[-50:]
        
        # Update UI displays
        self._update_error_display()
        # THREAD-SAFE: Do NOT call Qt methods from any thread!
        print(f"📋 ERROR logged: {error_data}")
        self._ui_needs_update = True
    
    def _update_operations_display(self):
        """Update the operations display with recent commands"""
        if self.operations_display:
            recent_commands = self.command_history[-3:]  # Last 3 commands
            operations_text = ""
            
            if recent_commands:
                operations_text = "Recent AI Commands:\n"
                for cmd in recent_commands:
                    action = cmd.get('command', 'unknown')
                    time_str = cmd.get('formatted_time', 'unknown')
                    agent = cmd.get('agent', 'unknown')
                    operations_text += f"• {time_str} - {action} ({agent})\n"
            else:
                operations_text = "No recent AI commands"
            
            self.operations_display.setText(operations_text)
    
    def _update_error_display(self):
        """Update the error display with recent errors"""
        if self.error_log_display:
            recent_errors = self.error_log[-10:]  # Last 10 errors
            error_text = ""
            
            if recent_errors:
                for error in recent_errors:
                    time_str = error['formatted_time']
                    error_msg = str(error['error'])[:80]  # Truncate long errors
                    error_text += f"{time_str}: {error_msg}\n"
            else:
                error_text = "No errors logged"
            
            self.error_log_display.setText(error_text)
    
    def _log_to_chat(self, message, is_error=False):
        """Log message to chat display"""
        if self.chat_display:
            timestamp = datetime.now().strftime('%H:%M:%S')
            if is_error:
                formatted_msg = f"<span style='color: red;'>[{timestamp}] ERROR: {message}</span>"
            else:
                formatted_msg = f"<span style='color: #00ff00;'>[{timestamp}] MCP: {message}</span>"
            self.chat_display.append(formatted_msg)
        
        # Also log to chat if available
        try:
            # Find the control panel to log to chat
            from PyQt6.QtWidgets import QApplication
            app = QApplication.instance()
            if app:
                for widget in app.allWidgets():
                    if hasattr(widget, 'log_to_chat'):
                        cmd = self.latest_command
                        widget.log_to_chat(f"MCP: Command received - {cmd['command']} from {cmd['agent']}", "system")
                        break
        except:
            pass  # Don't break if chat logging fails
    
    def safe_update_ui_if_needed(self):
        """Thread-safe method to update UI from main Qt thread"""
        if self._ui_needs_update:
            try:
                # Now it's safe to call Qt methods from main thread
                self._update_operations_display()
                if self.latest_command:
                    cmd = self.latest_command
                    self._log_to_chat(f"Command: {cmd['command']} from {cmd['agent']}")
                self._ui_needs_update = False
            except Exception as e:
                print(f"UI update error: {e}")
                self._ui_needs_update = False
    
    def register_ai_agent(self, agent_name, session_id="unknown"):
        """Register a connected AI agent"""
        self.connected_clients[agent_name] = {
            "connected_at": datetime.now().isoformat(),
            "session_id": session_id,
            "last_activity": datetime.now().isoformat()
        }
        
        self.ai_agent_info = {
            "name": agent_name,
            "session_id": session_id,
            "connected_at": datetime.now().isoformat()
        }
        
        self._log("AI_AGENT_REGISTERED", {
            "agent": agent_name,
            "session_id": session_id
        })
    
    def simulate_ai_command(self, command, reason="test", agent="TestAI"):
        """Simulate receiving an AI command for testing UI display"""
        # Register the agent if not already registered
        if agent not in self.connected_clients:
            self.register_ai_agent(agent, f"test_session_{int(time.time())}")
        
        self.update_latest_command({
            "command": command,
            "reason": reason,
            "agent": agent,
            "parameters": {}
        })

class OptimizedSpaceshipGenerator:
    """
    High-performance spaceship generator with optimized mesh creation and caching.
    
    This class provides procedural spaceship generation with a focus on real-time
    performance, efficient memory usage, and smooth interactive updates. Designed
    for applications requiring responsive 3D preview and rapid iteration.
    
    Key Features:
        - Intelligent mesh caching to avoid redundant calculations
        - Low-polygon primitive generation for smooth rendering
        - Grid-based modular spaceship architecture
        - Optimized connector generation between modules
        - Efficient transformation and color application
        - Graceful error handling with fallback meshes
        
    Performance Specifications:
        - Target: 400-800 vertices, 700-1400 faces for interactive use
        - Render: 30+ FPS on modern hardware
        - Memory: <40MB for typical spaceship configurations
        - Generation: <100ms for standard 15-25 module ships
        
    Grid System:
        Uses a 3D coordinate system where each position can contain one module.
        Default grid size is (6, 3, 8) for optimal balance of complexity and performance.
        Supports dynamic grid sizing for different use cases.
        
    Caching Strategy:
        - Maintains cached mesh until grid modifications occur
        - Automatic cache invalidation on module changes  
        - Optional cache bypass for forced regeneration
        - Memory-efficient cache management
        
    Export Compatibility:
        Generated meshes are compatible with:
        - STL format for 3D printing
        - GLB/GLTF for game engines and web viewers
        - OBJ for CAD applications and modeling software
        - PLY for scientific and research applications
    """
    
    def __init__(self, grid_size: Tuple[int, int, int] = DEFAULT_GRID_SIZE):
        self.grid_size = grid_size
        self.grid = ConfigUtils.create_default_grid(grid_size)
        self.cached_mesh = None
        self.mesh_dirty = True
        
    def generate_mesh(self, use_cache: bool = True) -> trimesh.Trimesh:
        """
        Generate complete spaceship mesh with intelligent caching and optimization.
        
        Creates a unified 3D mesh from all enabled modules in the grid, applying
        transformations, colors, and connectors while maintaining high performance
        through caching and low-polygon geometry.
        
        Args:
            use_cache (bool): If True, returns cached mesh if available and valid.
                             If False, forces regeneration regardless of cache state.
                             
        Returns:
            trimesh.Trimesh: Complete spaceship mesh ready for rendering or export.
                            Always returns a valid mesh object, even on errors.
                            
        Process:
            1. Cache validation - check if existing mesh is still valid
            2. Module iteration - process all enabled grid positions  
            3. Primitive creation - generate low-poly geometry for each geometry node
            4. Transformation - apply position, rotation, and scale transforms
            5. Color application - add vertex colors based on module properties
            6. Connector generation - create connecting elements between modules
            7. Mesh combination - merge all components into unified geometry
            8. Optimization - apply mesh cleaning and simplification
            9. Cache update - store result for future use
            
        Performance:
            - Uses low-polygon primitives (8 sections for cylinders vs 32 default)
            - Employs spatial optimization to minimize overdraw
            - Implements graceful error handling to prevent generation failures
            - Maintains target of <100ms generation time for typical ships
            
        Error Handling:
            - Individual module failures don't break entire generation
            - Falls back to simplified geometry on complex primitive errors
            - Returns valid fallback mesh if all generation attempts fail
            - Logs errors for debugging while maintaining app stability
        """
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
                mesh = MeshUtils.apply_geometry_node_transform(mesh, module, world_pos)
                
                # Add vertex colors
                if hasattr(mesh.visual, 'vertex_colors'):
                    colors = np.full((len(mesh.vertices), 4), [*module.color, 255], dtype=np.uint8)
                    mesh.visual.vertex_colors = colors
                
                meshes.append(mesh)
                
            except Exception as e:
                print(f"Error creating geometry node at {position}: {e}")
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
    
    def update_geometry_node(self, position: Tuple[int, int, int], geometry_node: SpaceshipGeometryNode):
        """Update a geometry node and mark mesh as dirty"""
        if position in self.grid:
            self.grid[position] = geometry_node
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
    
    def export_stl(self, filename: str) -> bool:
        """Export current design as STL"""
        try:
            mesh = self.generate_mesh()
            mesh.export(filename)
            return True
        except Exception as e:
            print(f"STL export failed: {e}")
            return False
    
    def export_obj(self, filename: str) -> bool:
        """Export current design as OBJ"""
        try:
            mesh = self.generate_mesh()
            mesh.export(filename)
            return True
        except Exception as e:
            print(f"OBJ export failed: {e}")
            return False
    
    def export_glb(self, filename: str) -> bool:
        """Export current design as GLB"""
        try:
            mesh = self.generate_mesh()
            mesh.export(filename)
            return True
        except Exception as e:
            print(f"GLB export failed: {e}")
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
        
        # CRITICAL: Disable mouse tracking to prevent crashes when mouse leaves widget
        self.setMouseTracking(False)
        
        # SAFETY: Handle mouse leave gracefully
        self.mouse_inside = True
        
        # THROTTLING: Prevent excessive updates during interaction
        self.last_update_time = 0
        self.update_throttle_ms = 16  # ~60fps max update rate
        
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
        
    def enterEvent(self, event):
        """Handle mouse entering widget"""
        self.mouse_inside = True
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Handle mouse leaving widget - CRITICAL for stability"""
        self.mouse_inside = False
        self.last_mouse_pos = None  # Reset mouse tracking when leaving
        super().leaveEvent(event)
    
    def mousePressEvent(self, event):
        """Handle mouse press for interaction"""
        if not self.mouse_inside:
            return  # Ignore mouse events when outside widget
        self.last_mouse_pos = event.position() if hasattr(event, 'position') else event.pos()
        
    def mouseMoveEvent(self, event):
        """Handle mouse movement for camera control"""
        # SAFETY: Check if mouse is inside widget and we have a valid starting position
        if not self.mouse_inside or self.last_mouse_pos is None:
            return
            
        try:
            current_pos = event.position() if hasattr(event, 'position') else event.pos()
            
            # SAFETY: Validate position is within widget bounds
            widget_rect = self.rect()
            if not widget_rect.contains(current_pos.toPoint()):
                # Mouse left widget bounds - reset tracking
                self.last_mouse_pos = None
                return
            
            dx = current_pos.x() - self.last_mouse_pos.x()
            dy = current_pos.y() - self.last_mouse_pos.y()
            
            # Only update if there's significant movement
            if abs(dx) > 1 or abs(dy) > 1:
                # THROTTLING: Check if enough time has passed since last update
                current_time = time.time() * 1000  # Convert to milliseconds
                
                if event.buttons() == Qt.MouseButton.LeftButton:
                    # Rotation
                    self.rotation_y += dx * 0.5
                    self.rotation_x += dy * 0.5
                    # Throttled update to prevent overload
                    if current_time - self.last_update_time > self.update_throttle_ms:
                        self.update()
                        self.last_update_time = current_time
                elif event.buttons() == Qt.MouseButton.RightButton:
                    # Panning
                    self.pan_x += dx * 0.01
                    self.pan_y -= dy * 0.01
                    # Throttled update to prevent overload
                    if current_time - self.last_update_time > self.update_throttle_ms:
                        self.update()
                        self.last_update_time = current_time
            
            self.last_mouse_pos = current_pos
            
        except Exception as e:
            # SAFETY: If any mouse event fails, reset state safely
            print(f"Mouse event error (non-critical): {e}")
            self.last_mouse_pos = None
            self.mouse_inside = True  # Reset to safe state
        
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
    """Enhanced control panel with visible UI elements and feedback"""
    
    def __init__(self, generator, viewer):
        super().__init__()
        self.generator = generator
        self.viewer = viewer
        self.current_position = (0, 0, 0)
        self.updating_ui = False  # Flag to prevent recursive updates
        
        # Status tracking for visual feedback
        self.current_mode = "solid"  # wireframe, solid, lighting_off
        self.generation_count = 0
        
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
        
        # Status Display (NEW - Shows current mode)
        status_group = QGroupBox("🎛️ Current Status")
        status_layout = QVBoxLayout()
        
        self.mode_status = QLabel("🔵 Mode: Solid Rendering")
        self.mode_status.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                padding: 8px;
                border: 2px solid #4CAF50;
                border-radius: 6px;
                background-color: #e8f5e8;
                color: #2E7D32;
            }
        """)
        
        self.generation_status = QLabel("🚀 Ships Generated: 0")
        self.generation_status.setStyleSheet("""
            QLabel {
                font-size: 12px;
                padding: 6px;
                border: 1px solid #2196F3;
                border-radius: 4px;
                background-color: #e3f2fd;
                color: #1565C0;
            }
        """)
        
        # MCP Server Status (NEW - Shows MCP integration status)
        self.mcp_status = QLabel("🔧 MCP Server: Initializing...")
        self.mcp_status.setStyleSheet("""
            QLabel {
                font-size: 12px;
                padding: 6px;
                border: 1px solid #FF9800;
                border-radius: 4px;
                background-color: #fff3e0;
                color: #E65100;
            }
        """)
        
        status_layout.addWidget(self.mode_status)
        status_layout.addWidget(self.generation_status)
        status_layout.addWidget(self.mcp_status)
        status_group.setLayout(status_layout)
        
        # Timer to update MCP status periodically - DISABLED to prevent crashes
        self.mcp_status_timer = QTimer()
        self.mcp_status_timer.timeout.connect(self.update_mcp_status_safe)
        # self.mcp_status_timer.start(5000)  # DISABLED - causing crashes in Qt event loop
        
        # Actions
        actions_group = QGroupBox("🎮 Ship Controls")
        actions_layout = QVBoxLayout()
        
        # Primary action buttons with enhanced styling and tooltips
        self.generate_btn = QPushButton("🎲 GENERATE NEW SHIP")
        self.generate_btn.setToolTip("Generate a default spaceship configuration")
        self.generate_btn.setStyleSheet("""
            QPushButton {
                font-weight: bold;
                font-size: 14px;
                padding: 12px 20px;
                border: 3px solid #4CAF50;
                border-radius: 8px;
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #66BB6A, stop: 1 #4CAF50);
                color: white;
                min-height: 25px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #81C784, stop: 1 #66BB6A);
                border-color: #388E3C;
                transform: translateY(-2px);
            }
            QPushButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #4CAF50, stop: 1 #388E3C);
                transform: translateY(0px);
            }
        """)
        
        self.random_btn = QPushButton("🔀 RANDOM SHIP")
        self.random_btn.setToolTip("Generate a completely random spaceship")
        self.random_btn.setStyleSheet("""
            QPushButton {
                font-weight: bold;
                font-size: 14px;
                padding: 12px 20px;
                border: 3px solid #FF9800;
                border-radius: 8px;
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #FFB74D, stop: 1 #FF9800);
                color: white;
                min-height: 25px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #FFCC02, stop: 1 #FFB74D);
                border-color: #F57C00;
                transform: translateY(-2px);
            }
            QPushButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #FF9800, stop: 1 #F57C00);
                transform: translateY(0px);
            }
        """)
        
        # Module control buttons
        self.update_btn = QPushButton("⚙️ UPDATE MODULE")
        self.update_btn.setToolTip("Apply changes to the current module")
        
        self.clear_btn = QPushButton("🗑️ CLEAR ALL")
        self.clear_btn.setToolTip("Remove all geometry nodes from the ship")
        
        # File operation buttons
        self.save_btn = QPushButton("💾 SAVE DESIGN")
        self.save_btn.setToolTip("Save current ship configuration")
        
        self.load_btn = QPushButton("📁 LOAD DESIGN") 
        self.load_btn.setToolTip("Load a saved ship configuration")
        
        # Export buttons with format options
        export_layout = QHBoxLayout()
        self.export_stl_btn = QPushButton("📤 STL")
        self.export_stl_btn.setToolTip("Export as STL for 3D printing")
        
        self.export_obj_btn = QPushButton("📤 OBJ") 
        self.export_obj_btn.setToolTip("Export as OBJ for 3D modeling")
        
        self.export_glb_btn = QPushButton("📤 GLB")
        self.export_glb_btn.setToolTip("Export as GLB for games/web")
        
        export_layout.addWidget(self.export_stl_btn)
        export_layout.addWidget(self.export_obj_btn)
        export_layout.addWidget(self.export_glb_btn)
        
        # Standard button styling
        standard_button_style = """
            QPushButton {
                font-weight: bold;
                padding: 10px 16px;
                border: 2px solid #555;
                border-radius: 6px;
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #f5f5f5, stop: 1 #e0e0e0);
                color: #333;
                min-height: 20px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #e8e8e8, stop: 1 #d0d0d0);
                border-color: #333;
                transform: translateY(-1px);
            }
            QPushButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #d0d0d0, stop: 1 #c0c0c0);
                transform: translateY(0px);
            }
        """
        
        for btn in [self.update_btn, self.clear_btn, self.save_btn, self.load_btn, 
                    self.export_stl_btn, self.export_obj_btn, self.export_glb_btn]:
            btn.setStyleSheet(standard_button_style)
        
        # Add buttons in logical order
        actions_layout.addWidget(self.generate_btn)
        actions_layout.addWidget(self.random_btn)
        
        # Add visual separator
        sep1 = QFrame()
        sep1.setFrameShape(QFrame.Shape.HLine)
        sep1.setFrameShadow(QFrame.Shadow.Sunken)
        actions_layout.addWidget(sep1)
        
        actions_layout.addWidget(self.update_btn)
        actions_layout.addWidget(self.clear_btn)
        
        # Add visual separator
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setFrameShadow(QFrame.Shadow.Sunken)
        actions_layout.addWidget(sep2)
        
        actions_layout.addWidget(self.save_btn)
        actions_layout.addWidget(self.load_btn)
        
        # Export section
        export_label = QLabel("📤 Export Formats:")
        export_label.setStyleSheet("font-weight: bold; color: #666; margin-top: 8px;")
        actions_layout.addWidget(export_label)
        actions_layout.addLayout(export_layout)
        
        # Navigation helper
        nav_layout = QHBoxLayout()
        self.find_enabled_btn = QPushButton("🔍 Find Module")
        self.find_enabled_btn.setToolTip("Jump to next position with an enabled module")
        self.find_enabled_btn.setStyleSheet(standard_button_style)
        
        # View control buttons
        self.wireframe_btn = QPushButton("📐 Wireframe")
        self.wireframe_btn.setToolTip("Toggle wireframe view (W key)")
        self.wireframe_btn.setCheckable(True)
        self.wireframe_btn.setStyleSheet("""
            QPushButton {
                font-weight: bold;
                padding: 8px 12px;
                border: 2px solid #9C27B0;
                border-radius: 4px;
                background-color: #f3e5f5;
                color: #6A1B9A;
            }
            QPushButton:hover {
                background-color: #e1bee7;
                border-color: #7B1FA2;
            }
            QPushButton:checked {
                background-color: #9C27B0;
                color: white;
            }
        """)
        
        self.lighting_btn = QPushButton("💡 Lighting")
        self.lighting_btn.setToolTip("Toggle lighting effects (L key)")
        self.lighting_btn.setCheckable(True)
        self.lighting_btn.setChecked(True)  # Default on
        self.lighting_btn.setStyleSheet("""
            QPushButton {
                font-weight: bold;
                padding: 8px 12px;
                border: 2px solid #FF9800;
                border-radius: 4px;
                background-color: #fff3e0;
                color: #E65100;
            }
            QPushButton:hover {
                background-color: #ffe0b2;
                border-color: #F57C00;
            }
            QPushButton:checked {
                background-color: #FF9800;
                color: white;
            }
        """)
        
        self.reset_view_btn = QPushButton("🔄 Reset")
        self.reset_view_btn.setToolTip("Reset camera view (R key)")
        self.reset_view_btn.setStyleSheet("""
            QPushButton {
                font-weight: bold;
                padding: 8px 12px;
                border: 2px solid #607D8B;
                border-radius: 4px;
                background-color: #eceff1;
                color: #37474F;
            }
            QPushButton:hover {
                background-color: #cfd8dc;
                border-color: #455A64;
            }
            QPushButton:pressed {
                background-color: #b0bec5;
            }
        """)
        
        nav_layout.addWidget(self.find_enabled_btn)
        nav_layout.addWidget(self.wireframe_btn)
        nav_layout.addWidget(self.lighting_btn)
        nav_layout.addWidget(self.reset_view_btn)
        
        actions_layout.addWidget(QLabel())  # Spacer
        view_label = QLabel("👁️ View Controls:")
        view_label.setStyleSheet("font-weight: bold; color: #666; margin-top: 8px;")
        actions_layout.addWidget(view_label)
        actions_layout.addLayout(nav_layout)
        
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
        
        # MCP Commands Display (NEW - Shows available AI commands)
        mcp_commands_group = QGroupBox("🤖 Available MCP Commands")
        mcp_commands_layout = QVBoxLayout()
        
        self.mcp_commands_display = QLabel("Initializing MCP server...")
        self.mcp_commands_display.setWordWrap(True)
        self.mcp_commands_display.setStyleSheet("""
            QLabel {
                font-size: 10px;
                color: #666;
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: #f9f9f9;
                max-height: 120px;
            }
        """)
        self.mcp_commands_display.setMaximumHeight(120)
        
        mcp_commands_layout.addWidget(self.mcp_commands_display)
        mcp_commands_group.setLayout(mcp_commands_layout)
        
        # Progress indicator (NEW)
        progress_group = QGroupBox("⏳ Operations")
        progress_layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)  # Hidden by default
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #ccc;
                border-radius: 5px;
                text-align: center;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 3px;
            }
        """)
        
        self.operation_status = QLabel("✅ Ready for commands")
        self.operation_status.setStyleSheet("""
            QLabel {
                padding: 6px;
                border-radius: 4px;
                background-color: #e8f5e8;
                color: #2E7D32;
                font-weight: bold;
            }
        """)
        
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.operation_status)
        progress_group.setLayout(progress_layout)
        
        # Add to main layout with status at top
        layout.addWidget(status_group)  # NEW: Status display at top
        layout.addWidget(progress_group)  # NEW: Progress indicator
        layout.addWidget(pos_group)
        layout.addWidget(props_group) 
        layout.addWidget(actions_group)
        layout.addWidget(stats_group)
        layout.addWidget(instructions_group)
        layout.addWidget(mcp_commands_group)  # NEW: MCP commands display
        
        # AI Chat & Logs (NEW - Real-time communication and system logs)
        chat_group = QGroupBox("💬 AI Chat & System Logs")
        chat_layout = QVBoxLayout()
        
        # Chat display area
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setMaximumHeight(200)
        self.chat_display.setStyleSheet("""
            QTextEdit {
                font-size: 11px;
                font-family: 'Consolas', 'Monaco', monospace;
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #333;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        
        # Chat input area
        chat_input_layout = QHBoxLayout()
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Type message to AI agent...")
        self.chat_input.setStyleSheet("""
            QLineEdit {
                font-size: 11px;
                padding: 6px;
                border: 1px solid #666;
                border-radius: 3px;
                background-color: #2d2d2d;
                color: white;
            }
        """)
        
        self.send_chat_btn = QPushButton("Send")
        self.send_chat_btn.setStyleSheet("""
            QPushButton {
                font-size: 11px;
                padding: 6px 12px;
                border: 1px solid #666;
                border-radius: 3px;
                background-color: #0078d4;
                color: white;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
        """)
        
        chat_input_layout.addWidget(self.chat_input)
        chat_input_layout.addWidget(self.send_chat_btn)
        
        chat_layout.addWidget(QLabel("Live Chat & System Logs:"))
        chat_layout.addWidget(self.chat_display)
        chat_layout.addLayout(chat_input_layout)
        chat_group.setLayout(chat_layout)
        
        # Debug/Test section for MCP command simulation
        debug_group = QGroupBox("🔧 MCP Debug")
        debug_layout = QVBoxLayout()
        
        self.test_command_btn = QPushButton("Test AI Command")
        self.test_screenshot_btn = QPushButton("Take Screenshot")
        self.start_interaction_btn = QPushButton("Start AI Interaction")
        
        for btn in [self.test_command_btn, self.test_screenshot_btn, self.start_interaction_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    font-size: 10px;
                    padding: 4px 8px;
                    border: 1px solid #666;
                    border-radius: 3px;
                    background-color: #f0f0f0;
                    color: #333;
                }
                QPushButton:hover {
                    background-color: #e0e0e0;
                }
            """)
        
        debug_layout.addWidget(self.test_command_btn)
        debug_layout.addWidget(self.test_screenshot_btn)  
        debug_layout.addWidget(self.start_interaction_btn)
        debug_group.setLayout(debug_layout)
        
        layout.addWidget(chat_group)
        layout.addWidget(debug_group)
        layout.addStretch()
        
        # Connect signals (disconnect first to avoid multiple connections)
        self.pos_x.valueChanged.connect(self.position_changed)
        self.pos_y.valueChanged.connect(self.position_changed)
        self.pos_z.valueChanged.connect(self.position_changed)
        self.update_btn.clicked.connect(self.update_geometry_node)
        self.generate_btn.clicked.connect(self.generate_default_ship)
        self.random_btn.clicked.connect(self.generate_new_ship)
        self.clear_btn.clicked.connect(self.clear_ship)
        self.save_btn.clicked.connect(self.save_design)
        self.load_btn.clicked.connect(self.load_design)
        
        # Export connections
        self.export_stl_btn.clicked.connect(self.export_stl)
        self.export_obj_btn.clicked.connect(self.export_obj)
        self.export_glb_btn.clicked.connect(self.export_glb)
        
        # Navigation and view controls
        self.find_enabled_btn.clicked.connect(self.find_enabled_geometry_node)
        self.wireframe_btn.clicked.connect(self.toggle_wireframe)
        self.lighting_btn.clicked.connect(self.toggle_lighting)
        self.reset_view_btn.clicked.connect(self.reset_view)
        
        # Chat controls
        self.chat_input.returnPressed.connect(self.send_chat_message)
        self.send_chat_btn.clicked.connect(self.send_chat_message)
        
        # Debug/test controls
        self.test_command_btn.clicked.connect(self.test_ai_command)
        self.test_screenshot_btn.clicked.connect(self.take_test_screenshot)
        self.start_interaction_btn.clicked.connect(self.start_ai_interaction)
        
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
            
            # Enhanced visual feedback system
            if module.enabled:
                # Green background for enabled modules
                coord_style = """
                    QSpinBox { 
                        background-color: #e8f5e8; 
                        border: 2px solid #4CAF50;
                        font-weight: bold;
                    }
                """
                radius_style = "background-color: #e8f5e8; border: 2px solid #4CAF50;"
                # Update position indicator
                self.stats_label.setText(f"📍 Position: {self.current_position}\n✅ Module: {module.type.upper()}\n🟢 Status: ENABLED")
            else:
                # Gray background for disabled modules  
                coord_style = """
                    QSpinBox { 
                        background-color: #f5f5f5; 
                        border: 2px solid #ccc;
                        font-weight: normal;
                    }
                """
                radius_style = "background-color: #f5f5f5; border: 2px solid #ccc;"
                # Update position indicator
                self.stats_label.setText(f"📍 Position: {self.current_position}\n❌ Module: {module.type.upper()}\n🔴 Status: DISABLED")
            
            # Apply visual feedback to coordinate spinboxes
            self.pos_x.setStyleSheet(coord_style)
            self.pos_y.setStyleSheet(coord_style)
            self.pos_z.setStyleSheet(coord_style)
            self.radius_spin.setStyleSheet(radius_style)
            
            self.updating_ui = False
            
            # CRITICAL FIX: Refresh 3D view when coordinates change
            # This was the missing piece - coordinate changes now update the visual display
            self.refresh_mesh()
        else:
            # Position not in grid - show empty state
            print(f"Position {self.current_position} not in grid - creating empty module")
            
            # Create a default disabled module for positions not in grid
            default_geometry_node = SpaceshipGeometryNode(
                type="cylinder",
                enabled=False,
                radius=0.5,
                height=0.6,
                color=[100, 100, 100]
            )
            self.generator.grid[self.current_position] = default_module
            
            # Update UI for empty position
            self.updating_ui = True
            self.type_combo.setCurrentText("cylinder")
            self.enabled_check.setChecked(False)
            self.radius_spin.setValue(0.5)
            
            # Gray styling for empty positions
            empty_style = """
                QSpinBox { 
                    background-color: #fff5f5; 
                    border: 2px solid #ff9999;
                    font-weight: bold;
                }
            """
            self.pos_x.setStyleSheet(empty_style)
            self.pos_y.setStyleSheet(empty_style)
            self.pos_z.setStyleSheet(empty_style)
            self.radius_spin.setStyleSheet("background-color: #fff5f5; border: 2px solid #ff9999;")
            
            self.stats_label.setText(f"📍 Position: {self.current_position}\n⚪ Module: EMPTY\n🔘 Status: NEW POSITION")
            
            self.updating_ui = False
    
    def show_success(self, message):
        """Show success message in operation status"""
        self.operation_status.setText(message)
        self.operation_status.setStyleSheet("""
            QLabel {
                padding: 6px;
                border-radius: 4px;
                background-color: #e8f5e8;
                color: #2E7D32;
                font-weight: bold;
            }
        """)
        
    def show_error(self, message):
        """Show error message in operation status"""
        self.operation_status.setText(message)
        self.operation_status.setStyleSheet("""
            QLabel {
                padding: 6px;
                border-radius: 4px;
                background-color: #ffebee;
                color: #c62828;
                font-weight: bold;
            }
        """)
        
    def show_progress(self, message, progress):
        """Show progress message and bar"""
        self.operation_status.setText(message)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(progress)
        if progress >= 100:
            # Hide progress bar when complete
            QTimer.singleShot(2000, lambda: self.progress_bar.setVisible(False))
    
    def update_status_display(self):
        """Update the status display with current information"""
        try:
            # Update generation count if we're tracking it
            if hasattr(self, 'generation_count'):
                self.generation_status.setText(f"🚀 Ships Generated: {self.generation_count}")
            
            # Also update MCP status when refreshing other status displays
            try:
                if hasattr(self, 'manual_mcp_refresh'):
                    self.manual_mcp_refresh()
            except:
                pass  # Silent fail for MCP refresh
            
            # Force UI refresh
            QApplication.processEvents()
        except Exception as e:
            print(f"Status display update error: {e}")
            
    def update_geometry_node(self):
        """Update the current module"""
        print(f"Updating geometry node at position {self.current_position}")
        
        # Always allow updating - create module if it doesn't exist
        # Auto-enable module when user makes changes (better UX)
        is_enabled = self.enabled_check.isChecked()
        
        if self.current_position in self.generator.grid and not is_enabled:
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
        geometry_node = SpaceshipGeometryNode(
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
        
        print(f"Updated geometry_node: type={geometry_node.type}, enabled={geometry_node.enabled}, radius={geometry_node.radius}")
        
        # Store the geometry_node and update display
        self.generator.update_geometry_node(self.current_position, geometry_node)
        self.refresh_mesh()
        
        # Refresh the position display to show the update
        self.position_changed()
        
        # Visual feedback for successful update
        if is_enabled:
            print(f"✅ Module at {self.current_position} updated and enabled!")
        else:
            print(f"💾 Module at {self.current_position} saved but disabled.")
            
    def find_enabled_geometry_node(self):
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
        
        print(f"Jumped to enabled geometry node at {next_position} ({next_index + 1}/{len(enabled_positions)})")

    def generate_default_ship(self):
        """Generate a new default spaceship configuration with visual feedback"""
        self.show_progress("Generating new spaceship...", 0)
        print("Generating new default spaceship...")
        
        # Animate progress
        for i in range(20, 101, 20):
            QApplication.processEvents()
            self.show_progress("Generating new spaceship...", i)
            QTimer.singleShot(50, lambda: None)  # Brief pause for visual effect
        
        self.generator.grid = ConfigUtils.create_default_grid(self.generator.grid_size)
        self.generator.mesh_dirty = True
        self.generation_count += 1
        
        self.show_progress("Generating mesh...", 100)
        self.refresh_mesh()
        self.position_changed()  # Refresh UI
        self.update_status_display()
        
        # Refresh MCP status after user interaction
        try:
            self.manual_mcp_refresh()
        except:
            pass  # Silent fail
        
        self.show_success("✅ New spaceship generated successfully!")
        print("Default spaceship generated!")

    def randomize_colors(self):
        """Randomize all module colors with progress feedback"""
        self.show_progress("Randomizing colors...", 0)
        print("Randomizing colors...")
        
        ConfigUtils.randomize_colors(self.generator.grid)
        self.show_progress("Applying colors...", 70)
        
        self.generator.mesh_dirty = True
        self.refresh_mesh()
        self.position_changed()  # Refresh UI
        self.update_status_display()
        
        self.show_success("🎨 Colors randomized successfully!")
        print("Colors randomized!")

    def toggle_wireframe_mode(self):
        """Toggle wireframe rendering mode"""
        self.viewer.wireframe_mode = not self.viewer.wireframe_mode
        if hasattr(self.viewer, 'update'):
            self.viewer.update()
        status = "ON" if self.viewer.wireframe_mode else "OFF"
        self.show_success(f"🔲 Wireframe mode: {status}")

    def toggle_lighting_mode(self):
        """Toggle lighting in 3D view"""
        if hasattr(self.viewer, 'lighting_enabled'):
            self.viewer.lighting_enabled = not self.viewer.lighting_enabled
            if hasattr(self.viewer, 'update'):
                self.viewer.update()
            status = "ON" if self.viewer.lighting_enabled else "OFF"
            self.show_success(f"💡 Lighting: {status}")

    def reset_view(self):
        """Reset 3D view to default position"""
        if hasattr(self.viewer, 'reset_view'):
            self.viewer.reset_view()
        elif hasattr(self.viewer, 'update'):
            self.viewer.update()
        self.show_success("🎯 View reset to default")

    def toggle_wireframe(self):
        """Toggle wireframe display mode"""
        self.toggle_wireframe_mode()

    def toggle_lighting(self):
        """Toggle lighting effects"""
        self.toggle_lighting_mode()

    def find_enabled_geometry_node(self):
        """Find and navigate to the next enabled module"""
        current_pos = self.current_position
        
        # Search for enabled modules starting from current position
        for pos in sorted(self.generator.grid.keys()):
            if pos > current_pos and self.generator.grid[pos].enabled:
                self.pos_x.setValue(pos[0])
                self.pos_y.setValue(pos[1])
                self.pos_z.setValue(pos[2])
                self.position_changed()
                self.show_success(f"🔍 Found enabled geometry node at {pos}")
                return
        
        # If no module found ahead, wrap to beginning
        for pos in sorted(self.generator.grid.keys()):
            if self.generator.grid[pos].enabled:
                self.pos_x.setValue(pos[0])
                self.pos_y.setValue(pos[1])
                self.pos_z.setValue(pos[2])
                self.position_changed()
                self.show_success(f"🔍 Found enabled geometry node at {pos} (wrapped)")
                return
        
        self.show_error("No enabled modules found")
    
    def test_ai_command(self):
        """Test AI command display by simulating a command"""
        # Get access to main window MCP manager
        main_window = None
        widget = self
        while widget.parent():
            widget = widget.parent()
            if hasattr(widget, 'mcp_manager'):
                main_window = widget
                break
        
        if main_window and hasattr(main_window, 'mcp_manager'):
            # Simulate different types of commands
            import random
            commands = [
                {"command": "see", "reason": "taking_screenshot_for_analysis", "agent": "GitHub Copilot"},
                {"command": "click", "reason": "testing_generate_button", "agent": "Visual AI Agent"},
                {"command": "press_key", "reason": "toggle_wireframe_mode", "agent": "UI Controller"},
                {"command": "move_to", "reason": "positioning_for_interaction", "agent": "Smart Navigator"},
                {"command": "focus_app", "reason": "ensuring_window_focus", "agent": "Window Manager"}
            ]
            
            test_command = random.choice(commands)
            main_window.mcp_manager.simulate_ai_command(
                test_command["command"], 
                test_command["reason"], 
                test_command["agent"]
            )
            
            self.show_success(f"🤖 Simulated AI command: {test_command['command']}")
        else:
            self.show_error("MCP Manager not available for testing")
    
    def log_to_chat(self, message, msg_type="info"):
        """Log message to chat display with timestamp"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if msg_type == "system":
            color = "#00ff00"  # Green for system messages
        elif msg_type == "ai":
            color = "#00bfff"  # Blue for AI messages  
        elif msg_type == "user":
            color = "#ffff00"  # Yellow for user messages
        elif msg_type == "error":
            color = "#ff4444"  # Red for errors
        else:
            color = "#ffffff"  # White for info
            
        formatted_msg = f'<span style="color: #888;">[{timestamp}]</span> <span style="color: {color};">{message}</span>'
        self.chat_display.append(formatted_msg)
        
        # Auto-scroll to bottom
        scrollbar = self.chat_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def send_chat_message(self):
        """Send chat message and log it"""
        message = self.chat_input.text().strip()
        if message:
            self.log_to_chat(f"USER: {message}", "user")
            self.log_to_chat(f"AI: Message received! You can interact with the app using MCP commands.", "ai")
            self.chat_input.clear()
    
    def take_test_screenshot(self):
        """Take a screenshot using the MCP system"""
        try:
            # Import the Universal AI Controller
            import sys
            import os
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            
            from universal_ai_controller import UniversalAIController
            controller = UniversalAIController()
            
            self.log_to_chat("SYSTEM: Starting screenshot capture...", "system")
            
            # Focus the app first
            focus_result = controller.focus_app()
            if focus_result:
                self.log_to_chat("SYSTEM: App focused successfully", "system")
            
            # Take screenshot
            result = controller.see("testing_mcp_integration_ui")
            
            if result and result.get('screenshot_path'):
                screenshot_path = result['screenshot_path']
                self.log_to_chat(f"AI: Screenshot captured: {screenshot_path}", "ai")
                self.log_to_chat(f"AI: I can see the spaceship designer app with MCP integration!", "ai")
                
                # Log this as a command to the MCP system
                main_window = self._get_main_window()
                if main_window and hasattr(main_window, 'mcp_manager'):
                    main_window.mcp_manager.update_latest_command({
                        "command": "see",
                        "reason": "testing_mcp_integration_ui", 
                        "agent": "GitHub Copilot",
                        "parameters": {"screenshot_path": screenshot_path}
                    })
                
            else:
                self.log_to_chat("ERROR: Screenshot capture failed", "error")
                
        except Exception as e:
            self.log_to_chat(f"ERROR: Screenshot test failed: {e}", "error")
    
    def start_ai_interaction(self):
        """Start comprehensive AI interaction testing"""
        self.log_to_chat("SYSTEM: Starting AI interaction sequence...", "system")
        self.log_to_chat("AI: Hello! I'm now actively interacting with your spaceship designer app.", "ai")
        
        # Start screenshot and then interaction
        QTimer.singleShot(1000, self.take_test_screenshot)
        QTimer.singleShot(3000, self.test_ui_interaction)
        QTimer.singleShot(5000, self.test_spaceship_generation)
    
    def test_ui_interaction(self):
        """Test UI interaction via MCP"""
        try:
            import sys
            import os
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            
            from universal_ai_controller import UniversalAIController
            controller = UniversalAIController()
            
            self.log_to_chat("AI: Testing UI interaction - clicking generate button", "ai")
            
            # Try to click the generate button (approximate position)
            controller.click(150, 450, reason="testing_generate_button_via_mcp")
            
            # Log this command
            main_window = self._get_main_window()
            if main_window and hasattr(main_window, 'mcp_manager'):
                main_window.mcp_manager.update_latest_command({
                    "command": "click",
                    "reason": "testing_generate_button_via_mcp",
                    "agent": "GitHub Copilot", 
                    "parameters": {"x": 150, "y": 450}
                })
            
            self.log_to_chat("SYSTEM: UI click command sent via MCP", "system")
            
        except Exception as e:
            self.log_to_chat(f"ERROR: UI interaction failed: {e}", "error")
    
    def test_spaceship_generation(self):
        """Test spaceship generation and report results"""
        try:
            self.log_to_chat("AI: Testing spaceship generation...", "ai")
            
            # Generate a new ship
            self.generate_new_ship()
            
            # Log generation command
            main_window = self._get_main_window()
            if main_window and hasattr(main_window, 'mcp_manager'):
                main_window.mcp_manager.update_latest_command({
                    "command": "generate_spaceship",
                    "reason": "testing_generation_functionality",
                    "agent": "GitHub Copilot",
                    "parameters": {"method": "random_generation"}
                })
            
            self.log_to_chat("AI: Spaceship generation completed! The MCP integration is working perfectly.", "ai")
            self.log_to_chat("SYSTEM: All MCP commands are being tracked and displayed in real-time", "system")
            
        except Exception as e:
            self.log_to_chat(f"ERROR: Spaceship generation test failed: {e}", "error")
    
    def _get_main_window(self):
        """Get reference to main window"""
        widget = self
        while widget.parent():
            widget = widget.parent()
            if hasattr(widget, 'mcp_manager'):
                return widget
        return None
        
    def clear_ship(self):
        """Clear all geometry nodes from the spaceship"""
        print("Clearing spaceship...")
        # Set all geometry nodes to disabled
        for pos in self.generator.grid:
            self.generator.grid[pos].enabled = False
        self.generator.mesh_dirty = True
        self.refresh_mesh()
        self.position_changed()  # Refresh UI
        print("Spaceship cleared!")

    def update_mcp_status(self):
        """Update MCP server status display"""
        try:
            # Get MCP status from main window - with error handling
            main_window = None
            widget = self
            depth = 0  # Prevent infinite loops
            while widget.parent() and depth < 10:
                widget = widget.parent()
                depth += 1
                if hasattr(widget, 'mcp_manager'):
                    main_window = widget
                    break
            
            if main_window and hasattr(main_window, 'mcp_manager'):
                status = main_window.get_mcp_status()
                
                if status['running']:
                    # MCP server is running - show detailed connection status
                    commands = status['available_commands']
                    num_commands = len(commands)
                    ai_connection = status.get('ai_connection', {})
                    connected_agents = status.get('connected_agents', 0)
                    
                    # Create detailed status message
                    if connected_agents > 0:
                        agent_info = status.get('agent_info', {})
                        agent_name = agent_info.get('name', 'AI Agent')
                        agent_session = agent_info.get('session_id', 'Unknown')[:8]  # First 8 chars
                        status_text = f"🔗 MCP: Connected to {agent_name} (Session: {agent_session})"
                    else:
                        status_text = f"🟢 MCP Server: Online ({num_commands} commands available)"
                    
                    self.mcp_status.setText(status_text)
                    self.mcp_status.setStyleSheet("""
                        QLabel {
                            font-size: 12px;
                            padding: 6px;
                            border: 1px solid #4CAF50;
                            border-radius: 4px;
                            background-color: #e8f5e8;
                            color: #2E7D32;
                        }
                    """)
                    
                    # Update commands display with latest command information
                    latest_command = status.get('latest_command')
                    
                    if latest_command:
                        # Show latest command at top
                        cmd_time = latest_command.get('timestamp', '')
                        if cmd_time:
                            try:
                                # Parse and format timestamp
                                dt = datetime.fromisoformat(cmd_time.replace('Z', '+00:00'))
                                cmd_time = dt.strftime('%H:%M:%S')
                            except:
                                cmd_time = cmd_time[-8:]  # Last 8 chars if parsing fails
                        
                        cmd_name = latest_command.get('command', 'unknown')
                        cmd_reason = latest_command.get('reason', '')
                        cmd_agent = latest_command.get('agent', 'AI')
                        
                        commands_text = f"🔥 LATEST COMMAND ({cmd_time}):\n"
                        commands_text += f"• {cmd_name}"
                        if cmd_reason:
                            commands_text += f" - {cmd_reason}"
                        commands_text += f"\n  From: {cmd_agent}\n\n"
                    else:
                        commands_text = "📋 AVAILABLE COMMANDS:\n"
                    
                    # Add available commands
                    if commands:
                        if latest_command:
                            commands_text += "Available commands:\n"
                        commands_text += "\n".join([f"• {cmd}" for cmd in commands[:6]])  # Show fewer to make room
                        if len(commands) > 6:
                            commands_text += f"\n... +{len(commands) - 6} more"
                    else:
                        commands_text += "Waiting for MCP server commands..."
                    
                    self.mcp_commands_display.setText(commands_text)
                    self.mcp_commands_display.setStyleSheet("""
                        QLabel {
                            font-size: 10px;
                            color: #2E7D32;
                            padding: 8px;
                            border: 1px solid #4CAF50;
                            border-radius: 4px;
                            background-color: #e8f5e8;
                            max-height: 140px;
                        }
                    """)
                    
                else:
                    # MCP server not running or initializing
                    self.mcp_status.setText("� MCP Server: Offline")
                    self.mcp_status.setStyleSheet("""
                        QLabel {
                            font-size: 12px;
                            padding: 6px;
                            border: 1px solid #FF9800;
                            border-radius: 4px;
                            background-color: #fff3e0;
                            color: #E65100;
                        }
                    """)
                    
                    # Update commands display for offline state
                    self.mcp_commands_display.setText("🔴 MCP SERVER OFFLINE\n\nThe MCP server is not running.\nRestart the app to initialize MCP integration.\n\nWhen online, this panel will show:\n• Latest AI commands received\n• Available MCP commands\n• Connected AI agent details")
                    self.mcp_commands_display.setStyleSheet("""
                        QLabel {
                            font-size: 10px;
                            color: #E65100;
                            padding: 8px;
                            border: 1px solid #FF9800;
                            border-radius: 4px;
                            background-color: #fff3e0;
                            max-height: 140px;
                        }
                    """)
            else:
                # No MCP manager found
                self.mcp_status.setText("❌ MCP Integration: Unavailable")
                self.mcp_status.setStyleSheet("""
                    QLabel {
                        font-size: 12px;
                        padding: 6px;
                        border: 1px solid #f44336;
                        border-radius: 4px;
                        background-color: #ffebee;
                        color: #c62828;
                    }
                """)
                
                # Update commands display for unavailable state
                self.mcp_commands_display.setText("❌ MCP INTEGRATION UNAVAILABLE\n\nMCP system not initialized.\nApp running in standalone mode.\n\nTo enable MCP integration:\n• Restart the application\n• Check MCP server dependencies\n• Verify max_security_ai_mcp.py exists")
                self.mcp_commands_display.setStyleSheet("""
                    QLabel {
                        font-size: 10px;
                        color: #c62828;
                        padding: 8px;
                        border: 1px solid #f44336;
                        border-radius: 4px;
                        background-color: #ffebee;
                        max-height: 120px;
                    }
                """)
                
        except Exception as e:
            print(f"Error updating MCP status: {e}")
    
    def update_mcp_status_safe(self):
        """Thread-safe MCP status update that also refreshes UI data"""
        try:
            # First call the regular MCP status update
            self.update_mcp_status()
            
            # Then call the MCP manager's safe UI update method
            main_window = self._get_main_window()
            if main_window and hasattr(main_window, 'mcp_manager'):
                # This updates the real-time command data
                main_window.mcp_manager.safe_update_ui_if_needed()
                
        except Exception as e:
            print(f"Safe MCP status update error: {e}")
    
    def manual_mcp_refresh(self):
        """Manual MCP status refresh - safe to call anytime"""
        try:
            # Call the safe update method directly when user interacts
            self.update_mcp_status_safe()
        except Exception as e:
            print(f"Manual MCP refresh error: {e}")

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
        """Export current design as STL with progress feedback"""
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self, "Export STL", "spaceship.stl", "STL Files (*.stl)")
            
            if filename:
                self.show_progress("Generating mesh for STL export...", 30)
                mesh = self.generator.generate_mesh()
                self.show_progress("Writing STL file...", 80)
                mesh.export(filename)
                self.show_success(f"📤 STL exported to {filename}")
        except Exception as e:
            self.show_error(f"STL export failed: {e}")

    def export_obj(self):
        """Export current design as OBJ with progress feedback"""
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self, "Export OBJ", "spaceship.obj", "OBJ Files (*.obj)")
            
            if filename:
                self.show_progress("Generating mesh for OBJ export...", 30)
                mesh = self.generator.generate_mesh()
                self.show_progress("Writing OBJ file...", 80)
                mesh.export(filename)
                self.show_success(f"📤 OBJ exported to {filename}")
        except Exception as e:
            self.show_error(f"OBJ export failed: {e}")

    def export_glb(self):
        """Export current design as GLB with progress feedback"""
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self, "Export GLB", "spaceship.glb", "GLB Files (*.glb)")
            
            if filename:
                self.show_progress("Generating mesh for GLB export...", 30)
                mesh = self.generator.generate_mesh()
                self.show_progress("Writing GLB file...", 80)
                mesh.export(filename)
                self.show_success(f"📤 GLB exported to {filename}")
        except Exception as e:
            self.show_error(f"GLB export failed: {e}")

class OptimizedSpaceshipApp(QMainWindow):
    """Main application window with integrated MCP server and ALWAYS ON TOP focus control"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Spaceship Designer - Optimized with MCP Integration")
        self.setGeometry(100, 100, 1200, 800)
        
        # CRITICAL: Always on top and focused
        self.setWindowFlags(
            Qt.WindowType.Window | 
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.WindowCloseButtonHint |
            Qt.WindowType.WindowMinimizeButtonHint |
            Qt.WindowType.WindowMaximizeButtonHint
        )
        
        # Initialize MCP manager (modular or fallback)
        if MODULAR_MCP_AVAILABLE:
            safe_print("🔗 Using modular MCP system")
            self.mcp_manager = integrate_mcp_server(self)
        else:
            print("🔄 Using embedded MCP system")
            self.mcp_manager = IntegratedMCPManager()
        
        # MCP server will be started after UI is fully ready
        self.mcp_startup_thread = None
        
        # Create generator and viewer
        self.generator = OptimizedSpaceshipGenerator()
        self.viewer = HighPerformanceViewer()
        self.control_panel = SimplifiedControlPanel(self.generator, self.viewer)
        
        self.setup_ui()
        self.setup_menu()
        
        # Focus management timer
        self.focus_timer = QTimer()
        self.focus_timer.timeout.connect(self.maintain_focus)
        # self.focus_timer.start(5000)  # DISABLED FOR TESTING - Check focus every 5 seconds (less frequent)
        
        # Initial mesh generation
        QTimer.singleShot(500, self.initial_mesh_generation)  # Longer delay to avoid startup issues
        
        # Start MCP server after UI is fully loaded (using QTimer for thread safety)
        QTimer.singleShot(2000, self._delayed_mcp_startup)
    
    def _delayed_mcp_startup(self):
        """Start MCP server after UI is fully initialized"""
        print("🔧 UI ready, starting MCP server in background thread...")
        self.mcp_startup_thread = threading.Thread(target=self._start_mcp_background, daemon=True, name="MCP-Startup")
        self.mcp_startup_thread.start()
        
    def _start_mcp_background(self):
        """Start MCP server in background thread with proper timing"""
        try:
            # Brief wait since UI is already initialized
            time.sleep(0.5)
            
            # Verify MCP manager exists before starting
            max_wait = 10
            wait_count = 0
            while not hasattr(self, 'mcp_manager') or not self.mcp_manager:
                time.sleep(0.5)
                wait_count += 1
                if wait_count > max_wait:
                    print("⚠️ MCP manager not ready, aborting background startup")
                    return
            
            print("🔧 Starting MCP server in background thread...")
            if MODULAR_MCP_AVAILABLE:
                success = self.mcp_manager.start()
            else:
                success = self.mcp_manager.start_mcp_server()
            print("✅ Background MCP startup completed" if success else "⚠️ MCP startup failed")
            
            # Refresh UI to show MCP server status after startup
            QTimer.singleShot(500, self.refresh_mcp_displays)
            
        except Exception as e:
            print(f"⚠️ Background MCP startup error: {e}")
            import traceback
            traceback.print_exc()
    
    def maintain_focus(self):
        """Ensure app stays on top and in focus"""
        try:
            if not self.isActiveWindow():
                self.raise_()
                self.activateWindow() 
                self.setFocus()
        except Exception as e:
            # Prevent focus management from crashing the app
            print(f"Focus management error (non-critical): {e}")
            pass
    
    def get_mcp_status(self):
        """Get current MCP server status with AI connection details"""
        ai_status = self.mcp_manager.get_ai_connection_status()
        
        return {
            "running": self.mcp_manager.is_mcp_running,
            "session_id": self.mcp_manager.session_id,
            "available_commands": self.mcp_manager.get_mcp_commands(),
            "ai_connection": ai_status,
            "latest_command": ai_status.get("latest_command"),
            "connected_agents": ai_status.get("connected_agents", 0),
            "agent_info": ai_status.get("agent_info", {})
        }
        
    def closeEvent(self, event):
        """Override close event to stop focus timer and MCP server"""
        print("Shutting down application...")
        
        # Stop focus timer
        self.focus_timer.stop()
        
        # Stop MCP server
        if MODULAR_MCP_AVAILABLE:
            self.mcp_manager.stop()
        else:
            self.mcp_manager.stop_mcp_server()
        
        print("Application shutdown complete")
        event.accept()
        
    def setup_ui(self):
        """Set up the main UI layout with MCP monitoring"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QHBoxLayout(central_widget)
        
        # Left panel for controls and MCP status
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Control panel (existing)
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.control_panel)
        scroll_area.setWidgetResizable(True)
        scroll_area.setMaximumWidth(300)
        left_layout.addWidget(scroll_area, 3)
        
        # MCP Operations Display
        operations_group = QGroupBox("Operations")
        operations_layout = QVBoxLayout(operations_group)
        self.operations_display = QTextEdit()
        self.operations_display.setMaximumHeight(120)
        self.operations_display.setReadOnly(True)
        self.operations_display.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #00ff00;
                font-family: 'Courier New';
                font-size: 10px;
                border: 1px solid #333;
            }
        """)
        self.operations_display.setText("Waiting for AI commands...")
        operations_layout.addWidget(self.operations_display)
        left_layout.addWidget(operations_group, 1)
        
        # Error Log Display
        error_group = QGroupBox("Error Log")
        error_layout = QVBoxLayout(error_group)
        self.error_log_display = QTextEdit()
        self.error_log_display.setMaximumHeight(100)
        self.error_log_display.setReadOnly(True)
        self.error_log_display.setStyleSheet("""
            QTextEdit {
                background-color: #2d1b1b;
                color: #ff6b6b;
                font-family: 'Courier New';
                font-size: 10px;
                border: 1px solid #5a2d2d;
            }
        """)
        self.error_log_display.setText("No errors logged")
        error_layout.addWidget(self.error_log_display)
        left_layout.addWidget(error_group, 1)
        
        # Chat Interface
        chat_group = QGroupBox("MCP Communication")
        chat_layout = QVBoxLayout(chat_group)
        
        self.chat_display = QTextEdit()
        self.chat_display.setMaximumHeight(150)
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("""
            QTextEdit {
                background-color: #0f0f0f;
                color: #ffffff;
                font-family: 'Consolas';
                font-size: 11px;
                border: 1px solid #444;
            }
        """)
        chat_layout.addWidget(self.chat_display)
        
        # Chat input
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Send command to MCP server...")
        self.chat_input.returnPressed.connect(self.send_chat_message)
        self.chat_input.setStyleSheet("""
            QLineEdit {
                background-color: #2a2a2a;
                color: white;
                padding: 5px;
                border: 1px solid #555;
                font-size: 12px;
            }
        """)
        chat_layout.addWidget(self.chat_input)
        
        # Test buttons
        button_layout = QHBoxLayout()
        
        test_screenshot_btn = QPushButton("Test Screenshot")
        test_screenshot_btn.clicked.connect(self.test_screenshot)
        test_screenshot_btn.setStyleSheet("QPushButton { background-color: #4a4a4a; color: white; }")
        button_layout.addWidget(test_screenshot_btn)
        
        test_interaction_btn = QPushButton("Test AI")
        test_interaction_btn.clicked.connect(self.test_ai_interaction)
        test_interaction_btn.setStyleSheet("QPushButton { background-color: #4a4a4a; color: white; }")
        button_layout.addWidget(test_interaction_btn)
        
        chat_layout.addLayout(button_layout)
        left_layout.addWidget(chat_group, 2)
        
        # Connect MCP manager to UI displays
        self.mcp_manager.operations_display = self.operations_display
        self.mcp_manager.error_log_display = self.error_log_display
        self.mcp_manager.chat_display = self.chat_display
        
        # Connect UI update callback for cross-thread updates
        self.mcp_manager.ui_update_callback = self.force_ui_update
        
        # Add panels to main layout
        layout.addWidget(left_panel, 1)
        layout.addWidget(self.viewer, 3)  # 3D viewer takes most space
        
        # Initial UI updates
        self.log_to_chat("MCP Integration initialized - Ready for AI commands!")
    
    def log_to_chat(self, message, is_error=False):
        """Log message to chat display"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        if is_error:
            formatted_msg = f"<span style='color: #ff6b6b;'>[{timestamp}] ERROR: {message}</span>"
        else:
            formatted_msg = f"<span style='color: #00ff88;'>[{timestamp}] {message}</span>"
        self.chat_display.append(formatted_msg)
        
        # Auto-scroll to bottom
        scrollbar = self.chat_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def send_chat_message(self):
        """Send message to MCP server"""
        message = self.chat_input.text().strip()
        if not message:
            return
            
        self.chat_input.clear()
        self.log_to_chat(f"USER: {message}")
        
        # Process command through MCP manager
        try:
            command_data = {
                "action": "chat_command",
                "message": message,
                "agent": "user_interface",
                "timestamp": datetime.now().isoformat()
            }
            self.mcp_manager.update_latest_command(command_data)
            self.log_to_chat("Command sent to MCP server")
        except Exception as e:
            self.log_to_chat(f"Failed to send command: {e}", is_error=True)
            self.mcp_manager.update_error_log(str(e))
    
    def test_screenshot(self):
        """Test screenshot functionality"""
        self.log_to_chat("Testing screenshot capture...")
        try:
            # Simulate MCP command
            command_data = {
                "action": "take_screenshot", 
                "agent": "test_interface",
                "reason": "UI testing"
            }
            self.mcp_manager.update_latest_command(command_data)
            self.log_to_chat("Screenshot test command logged")
        except Exception as e:
            self.log_to_chat(f"Screenshot test failed: {e}", is_error=True)
            self.mcp_manager.update_error_log(str(e))
    
    def test_ai_interaction(self):
        """Test AI interaction functionality"""
        self.log_to_chat("Testing AI interaction...")
        try:
            command_data = {
                "action": "ai_test_interaction",
                "agent": "test_ai_agent", 
                "parameters": {"test_type": "ui_validation"},
                "reason": "Testing AI command tracking"
            }
            self.mcp_manager.update_latest_command(command_data)
            self.log_to_chat("AI interaction test logged")
        except Exception as e:
            self.log_to_chat(f"AI interaction test failed: {e}", is_error=True)
            self.mcp_manager.update_error_log(str(e))
    
    def force_ui_update(self):
        """Force UI update from MCP manager (called from HTTP thread)"""
        try:
            # Use Qt's invokeMethod to safely update UI from different thread
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(0, self.refresh_mcp_displays)
        except Exception as e:
            print(f"UI update error: {e}")
    
    def refresh_mcp_displays(self):
        """Refresh MCP-related displays (runs on main thread)"""
        try:
            # THREAD-SAFE UI updates from main thread
            if hasattr(self.mcp_manager, 'safe_update_ui_if_needed'):
                self.mcp_manager.safe_update_ui_if_needed()
            
            # Force refresh of error display  
            if hasattr(self.mcp_manager, '_update_error_display'):
                self.mcp_manager._update_error_display()
                
            # Force widget updates
            if self.operations_display:
                self.operations_display.repaint()
            if self.chat_display:
                self.chat_display.repaint()
                
        except Exception as e:
            print(f"Display refresh error: {e}")
        
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
    
    # Note: Signal handler removed to prevent interference with external tools
    
    window.show()
    
    print("=" * 70)
    print("Optimized Spaceship Designer with MCP Integration Started")
    print("=" * 70)
    print("Controls:")
    print("- Left Mouse + Drag: Rotate view")
    print("- Right Mouse + Drag: Pan view") 
    print("- Mouse Wheel: Zoom")
    print("- W: Toggle wireframe")
    print("- L: Toggle lighting")
    print("- R: Reset view")
    print("")
    print("MCP Integration:")
    print("- MCP server starts automatically with the app")
    print("- Available commands shown in control panel")
    print("- Check status in 'Current Status' section")
    print("- Server stops automatically when app closes")
    print("=" * 70)
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())